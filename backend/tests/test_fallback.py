"""
Unit tests for CooldownTracker and call_llm_with_fallback in app.llm.client.

Covers:
  - CooldownTracker operations (set, check, get remaining, reset)
  - LLM_PROVIDER_MODE=manual directly invokes complete() with no fallback
  - LLM_PROVIDER_MODE=auto iterates provider chain on failure
  - Failing provider receives cooldown and next provider is called for SAME prompt
  - Cooled-down provider is skipped on subsequent calls
  - All providers failing raises AllProvidersExhaustedError
  - Last serving provider tracking
"""

from unittest.mock import MagicMock, patch

import pytest

from app.core.config import ProviderConfig
from app.llm.client import (
    CooldownTracker,
    call_llm_with_fallback,
    cooldown_tracker,
    get_last_serving_provider,
)
from app.llm.errors import (
    AllProvidersExhaustedError,
    AuthError,
    RateLimitError,
    ServerError,
)


@pytest.fixture(autouse=True)
def reset_cooldown():
    """Ensure clean cooldown tracker state for every test."""
    cooldown_tracker.reset()
    yield
    cooldown_tracker.reset()


# ---------------------------------------------------------------------------
# CooldownTracker Unit Tests
# ---------------------------------------------------------------------------

def test_cooldown_tracker_basic():
    tracker = CooldownTracker()
    assert not tracker.is_cooling_down("gemini")
    assert tracker.get_remaining_cooldown("gemini") == 0.0

    # Set cooldown for 60 seconds
    tracker.set_cooldown("gemini", duration_sec=60.0, now=100.0)
    assert tracker.is_cooling_down("gemini", now=120.0)
    assert tracker.get_remaining_cooldown("gemini", now=120.0) == 40.0

    # Past cooldown expiration
    assert not tracker.is_cooling_down("gemini", now=165.0)
    assert tracker.get_remaining_cooldown("gemini", now=165.0) == 0.0


def test_cooldown_tracker_reset():
    tracker = CooldownTracker()
    tracker.set_cooldown("gemini", 60.0, now=100.0)
    tracker.set_cooldown("nvidia_nim", 60.0, now=100.0)

    tracker.reset("gemini")
    assert not tracker.is_cooling_down("gemini", now=110.0)
    assert tracker.is_cooling_down("nvidia_nim", now=110.0)

    tracker.reset()
    assert not tracker.is_cooling_down("nvidia_nim", now=110.0)


# ---------------------------------------------------------------------------
# call_llm_with_fallback: Manual Mode Tests
# ---------------------------------------------------------------------------

def test_fallback_manual_mode_calls_complete_directly():
    """In manual mode, calls complete() with zero fallback or chain logic."""
    with patch("app.llm.client.settings") as mock_settings:
        mock_settings.llm_provider_mode = "manual"
        mock_settings.llm_provider = "deepseek"
        mock_settings.provider_chain = ["nvidia_nim", "gemini"]

        with patch("app.llm.client.complete", return_value="Manual result") as mock_complete:
            with patch("app.llm.client.get_adapter") as mock_get_adapter:
                res = call_llm_with_fallback("Test prompt")
                assert res == "Manual result"
                mock_complete.assert_called_once_with("Test prompt", provider="default")
                # Fallback chain adapter should NOT be called at all
                mock_get_adapter.assert_not_called()
                assert get_last_serving_provider() == "deepseek"


def test_fallback_specific_provider_calls_complete_directly():
    """When a specific provider (e.g. anthropic) is specified, complete() is called directly."""
    with patch("app.llm.client.settings") as mock_settings:
        mock_settings.llm_provider_mode = "auto"
        with patch("app.llm.client.complete", return_value="Claude reply") as mock_complete:
            res = call_llm_with_fallback("Prompt", provider="anthropic")
            assert res == "Claude reply"
            mock_complete.assert_called_once_with("Prompt", provider="anthropic")


# ---------------------------------------------------------------------------
# call_llm_with_fallback: Auto Mode Success & Failover Tests
# ---------------------------------------------------------------------------

def test_fallback_auto_mode_first_provider_succeeds():
    """In auto mode, first provider in chain succeeds and returns result."""
    with patch("app.llm.client.settings") as mock_settings:
        mock_settings.llm_provider_mode = "auto"
        mock_settings.provider_chain = ["nvidia_nim", "openrouter"]
        mock_settings.llm_provider_cooldown_sec = 60
        mock_settings.llm_provider_max_retries_per_call = 4

        mock_config = ProviderConfig(name="nvidia_nim", api_key="k", model="m")
        mock_settings.get_provider_config.return_value = mock_config

        mock_adapter = MagicMock(return_value="NIM success output")
        with patch("app.llm.client.get_adapter", return_value=mock_adapter):
            res = call_llm_with_fallback("Analyze")
            assert res == "NIM success output"
            assert get_last_serving_provider() == "nvidia_nim"
            assert not cooldown_tracker.is_cooling_down("nvidia_nim")


def test_fallback_auto_mode_rate_limit_fails_over_to_next_provider():
    """When provider 1 hits RateLimitError, it cools down and provider 2 answers."""
    with patch("app.llm.client.settings") as mock_settings:
        mock_settings.llm_provider_mode = "auto"
        mock_settings.provider_chain = ["nvidia_nim", "openrouter"]
        mock_settings.llm_provider_cooldown_sec = 45
        mock_settings.llm_provider_max_retries_per_call = 4
        mock_settings.get_provider_config.side_effect = lambda p: ProviderConfig(name=p, api_key="k", model="m")

        def adapter_dispatch(provider_name):
            if provider_name == "nvidia_nim":
                def failing_adapter(prompt, cfg):
                    raise RateLimitError("429 Too Many Requests", provider="nvidia_nim", retry_after=30.0)
                return failing_adapter
            else:
                def succeeding_adapter(prompt, cfg):
                    return "OpenRouter failover success"
                return succeeding_adapter

        with patch("app.llm.client.get_adapter", side_effect=adapter_dispatch):
            res = call_llm_with_fallback("Run assessment")
            assert res == "OpenRouter failover success"
            assert get_last_serving_provider() == "openrouter"

            # Check that provider 1 was marked cooling down
            assert cooldown_tracker.is_cooling_down("nvidia_nim")
            assert not cooldown_tracker.is_cooling_down("openrouter")


def test_fallback_skips_provider_in_cooldown():
    """A provider currently in cooldown is skipped without attempting adapter execution."""
    cooldown_tracker.set_cooldown("nvidia_nim", duration_sec=60.0)

    with patch("app.llm.client.settings") as mock_settings:
        mock_settings.llm_provider_mode = "auto"
        mock_settings.provider_chain = ["nvidia_nim", "gemini"]
        mock_settings.llm_provider_cooldown_sec = 60
        mock_settings.llm_provider_max_retries_per_call = 4
        mock_settings.get_provider_config.side_effect = lambda p: ProviderConfig(name=p, api_key="k", model="m")

        called_providers = []

        def adapter_dispatch(provider_name):
            called_providers.append(provider_name)
            return lambda prompt, cfg: f"{provider_name} response"

        with patch("app.llm.client.get_adapter", side_effect=adapter_dispatch):
            res = call_llm_with_fallback("Prompt")
            assert res == "gemini response"
            # nvidia_nim was skipped, only gemini was called
            assert called_providers == ["gemini"]
            assert get_last_serving_provider() == "gemini"


def test_fallback_all_providers_exhausted_raises_error():
    """When all providers in chain fail, AllProvidersExhaustedError is raised."""
    with patch("app.llm.client.settings") as mock_settings:
        mock_settings.llm_provider_mode = "auto"
        mock_settings.provider_chain = ["nvidia_nim", "openrouter"]
        mock_settings.llm_provider_cooldown_sec = 30
        mock_settings.llm_provider_max_retries_per_call = 4
        mock_settings.get_provider_config.side_effect = lambda p: ProviderConfig(name=p, api_key="k", model="m")

        def failing_adapter(name):
            def _fn(prompt, cfg):
                raise ServerError(f"500 from {name}", provider=name)
            return _fn

        with patch("app.llm.client.get_adapter", side_effect=failing_adapter):
            with pytest.raises(AllProvidersExhaustedError) as exc_info:
                call_llm_with_fallback("Prompt")

            assert "All LLM providers in fallback chain exhausted" in str(exc_info.value)
            assert cooldown_tracker.is_cooling_down("nvidia_nim")
            assert cooldown_tracker.is_cooling_down("openrouter")
