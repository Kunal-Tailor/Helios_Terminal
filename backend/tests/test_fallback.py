"""
Unit tests for multi-provider fallback chain and cooldown management.

Specifically verifies Task 10.3.7 requirements:
  (a) Forced RateLimitError on provider 1 falls through to provider 2
  (b) All providers exhausted raises AllProvidersExhaustedError
  (c) A provider within cooldown is skipped without being called again
  (d) LLM_PROVIDER_MODE=manual never invokes chain/cooldown logic
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

def test_cooldown_tracker_set_and_check():
    """CooldownTracker accurately tracks expiration and remaining time."""
    tracker = CooldownTracker()
    assert not tracker.is_cooling_down("nvidia_nim")
    assert tracker.get_remaining_cooldown("nvidia_nim") == 0.0

    tracker.set_cooldown("nvidia_nim", duration_sec=60.0, now=100.0)
    assert tracker.is_cooling_down("nvidia_nim", now=120.0)
    assert tracker.get_remaining_cooldown("nvidia_nim", now=120.0) == 40.0

    # Cooldown expires after 60s
    assert not tracker.is_cooling_down("nvidia_nim", now=161.0)
    assert tracker.get_remaining_cooldown("nvidia_nim", now=161.0) == 0.0


def test_cooldown_tracker_reset_individual_and_all():
    """CooldownTracker resets individual providers or all providers."""
    tracker = CooldownTracker()
    tracker.set_cooldown("nvidia_nim", 60.0, now=100.0)
    tracker.set_cooldown("gemini", 60.0, now=100.0)

    tracker.reset("nvidia_nim")
    assert not tracker.is_cooling_down("nvidia_nim", now=110.0)
    assert tracker.is_cooling_down("gemini", now=110.0)

    tracker.reset()
    assert not tracker.is_cooling_down("gemini", now=110.0)


# ---------------------------------------------------------------------------
# Requirement (a): Forced RateLimitError on provider 1 falls through to provider 2
# ---------------------------------------------------------------------------

def test_forced_rate_limit_error_on_provider_1_falls_through_to_provider_2():
    """(a) Forced RateLimitError on provider 1 falls through to provider 2 for the same prompt."""
    with patch("app.llm.client.settings") as mock_settings:
        mock_settings.llm_provider_mode = "auto"
        mock_settings.provider_chain = ["nvidia_nim", "openrouter"]
        mock_settings.llm_provider_cooldown_sec = 45
        mock_settings.llm_provider_max_retries_per_call = 4
        mock_settings.get_provider_config.side_effect = lambda p: ProviderConfig(name=p, api_key="k", model="m")

        call_log = []

        def adapter_dispatch(provider_name):
            if provider_name == "nvidia_nim":
                def failing_adapter(prompt, cfg):
                    call_log.append(("nvidia_nim", prompt))
                    raise RateLimitError("429 rate limit exceeded", provider="nvidia_nim", retry_after=30.0)
                return failing_adapter
            elif provider_name == "openrouter":
                def succeeding_adapter(prompt, cfg):
                    call_log.append(("openrouter", prompt))
                    return "OpenRouter successfully synthesized verdict."
                return succeeding_adapter
            raise ValueError(f"Unexpected provider: {provider_name}")

        with patch("app.llm.client.get_adapter", side_effect=adapter_dispatch):
            result = call_llm_with_fallback("Analyze tactical SLM sovereignty")

            # Verify both providers were called for the EXACT same prompt
            assert call_log == [
                ("nvidia_nim", "Analyze tactical SLM sovereignty"),
                ("openrouter", "Analyze tactical SLM sovereignty"),
            ]
            assert result == "OpenRouter successfully synthesized verdict."
            assert get_last_serving_provider() == "openrouter"

            # Verify provider 1 was placed into cooldown with custom retry_after duration
            assert cooldown_tracker.is_cooling_down("nvidia_nim")
            # Verify provider 2 is healthy (not cooling down)
            assert not cooldown_tracker.is_cooling_down("openrouter")


# ---------------------------------------------------------------------------
# Requirement (b): All providers exhausted raises AllProvidersExhaustedError
# ---------------------------------------------------------------------------

def test_all_providers_exhausted_raises_all_providers_exhausted_error():
    """(b) When every provider in the chain fails, AllProvidersExhaustedError is raised."""
    with patch("app.llm.client.settings") as mock_settings:
        mock_settings.llm_provider_mode = "auto"
        mock_settings.provider_chain = ["nvidia_nim", "openrouter", "gemini"]
        mock_settings.llm_provider_cooldown_sec = 30
        mock_settings.llm_provider_max_retries_per_call = 4
        mock_settings.get_provider_config.side_effect = lambda p: ProviderConfig(name=p, api_key="k", model="m")

        attempted_calls = []

        def failing_adapter(provider_name):
            def _fn(prompt, cfg):
                attempted_calls.append(provider_name)
                if provider_name == "nvidia_nim":
                    raise RateLimitError("429 Too Many Requests", provider=provider_name)
                elif provider_name == "openrouter":
                    raise AuthError("401 Unauthorized API key", provider=provider_name)
                else:
                    raise ServerError("503 UNAVAILABLE: Model overloaded", provider=provider_name)
            return _fn

        with patch("app.llm.client.get_adapter", side_effect=failing_adapter):
            with pytest.raises(AllProvidersExhaustedError) as exc_info:
                call_llm_with_fallback("Run critical brief")

            assert "All LLM providers in fallback chain exhausted" in str(exc_info.value)
            # All three providers were attempted in order
            assert attempted_calls == ["nvidia_nim", "openrouter", "gemini"]
            # All three providers were placed into cooldown
            assert cooldown_tracker.is_cooling_down("nvidia_nim")
            assert cooldown_tracker.is_cooling_down("openrouter")
            assert cooldown_tracker.is_cooling_down("gemini")
            # Error carries records of all attempted errors
            assert len(exc_info.value.attempts) == 3


# ---------------------------------------------------------------------------
# Requirement (c): A provider within cooldown is skipped without being called again
# ---------------------------------------------------------------------------

def test_provider_within_cooldown_skipped_without_being_called_again():
    """(c) A provider within cooldown is skipped without its adapter being executed."""
    # Place provider 1 into active cooldown
    cooldown_tracker.set_cooldown("nvidia_nim", duration_sec=60.0)
    assert cooldown_tracker.is_cooling_down("nvidia_nim")

    with patch("app.llm.client.settings") as mock_settings:
        mock_settings.llm_provider_mode = "auto"
        mock_settings.provider_chain = ["nvidia_nim", "gemini"]
        mock_settings.llm_provider_cooldown_sec = 60
        mock_settings.llm_provider_max_retries_per_call = 4
        mock_settings.get_provider_config.side_effect = lambda p: ProviderConfig(name=p, api_key="k", model="m")

        mock_adapters_called = []

        def adapter_dispatch(provider_name):
            mock_adapters_called.append(provider_name)
            return lambda prompt, cfg: f"Response from {provider_name}"

        with patch("app.llm.client.get_adapter", side_effect=adapter_dispatch):
            result = call_llm_with_fallback("Next sequential prompt")

            # nvidia_nim was in cooldown and skipped; only gemini was called
            assert mock_adapters_called == ["gemini"]
            assert result == "Response from gemini"
            assert get_last_serving_provider() == "gemini"


def test_subsequent_calls_respect_cooldown_state():
    """Call 1 fails provider 1 -> Call 2 immediately skips provider 1 and routes to provider 2."""
    with patch("app.llm.client.settings") as mock_settings:
        mock_settings.llm_provider_mode = "auto"
        mock_settings.provider_chain = ["nvidia_nim", "openrouter"]
        mock_settings.llm_provider_cooldown_sec = 120
        mock_settings.llm_provider_max_retries_per_call = 4
        mock_settings.get_provider_config.side_effect = lambda p: ProviderConfig(name=p, api_key="k", model="m")

        call_counts = {"nvidia_nim": 0, "openrouter": 0}

        def adapter_dispatch(provider_name):
            def _fn(prompt, cfg):
                call_counts[provider_name] += 1
                if provider_name == "nvidia_nim":
                    raise RateLimitError("429 rate limit", provider=provider_name)
                return f"Success from {provider_name}"
            return _fn

        with patch("app.llm.client.get_adapter", side_effect=adapter_dispatch):
            # First call: nvidia_nim fails, openrouter succeeds
            res1 = call_llm_with_fallback("Prompt 1")
            assert res1 == "Success from openrouter"
            assert call_counts == {"nvidia_nim": 1, "openrouter": 1}

            # Second call: nvidia_nim is cooling down and MUST NOT be called again
            res2 = call_llm_with_fallback("Prompt 2")
            assert res2 == "Success from openrouter"
            assert call_counts == {"nvidia_nim": 1, "openrouter": 2}


# ---------------------------------------------------------------------------
# Requirement (d): LLM_PROVIDER_MODE=manual never invokes chain/cooldown logic
# ---------------------------------------------------------------------------

def test_manual_mode_never_invokes_chain_or_cooldown_logic():
    """(d) When LLM_PROVIDER_MODE=manual, complete() is called directly; no chain or cooldown logic."""
    with patch("app.llm.client.settings") as mock_settings:
        mock_settings.llm_provider_mode = "manual"
        mock_settings.llm_provider = "deepseek"
        mock_settings.provider_chain = ["nvidia_nim", "openrouter", "gemini"]

        # Even if a provider is marked cooling down, manual mode ignores it
        cooldown_tracker.set_cooldown("deepseek", duration_sec=60.0)

        with patch("app.llm.client.complete", return_value="Unmodified single-provider response") as mock_complete:
            with patch("app.llm.client.get_adapter") as mock_get_adapter:
                res = call_llm_with_fallback("Evaluate prompt")

                assert res == "Unmodified single-provider response"
                mock_complete.assert_called_once_with("Evaluate prompt", provider="default")
                # Fallback chain adapter lookup must NEVER be touched
                mock_get_adapter.assert_not_called()
                assert get_last_serving_provider() == "deepseek"


def test_manual_mode_exception_propagates_directly_without_failover():
    """In manual mode, if complete() raises an exception, it propagates without attempting failover."""
    with patch("app.llm.client.settings") as mock_settings:
        mock_settings.llm_provider_mode = "manual"
        mock_settings.llm_provider = "deepseek"
        mock_settings.provider_chain = ["nvidia_nim", "openrouter"]

        with patch("app.llm.client.complete", side_effect=RuntimeError("Direct single-provider error")):
            with patch("app.llm.client.get_adapter") as mock_get_adapter:
                with pytest.raises(RuntimeError, match="Direct single-provider error"):
                    call_llm_with_fallback("Evaluate prompt")

                # No fallback was attempted
                mock_get_adapter.assert_not_called()
                # Provider was not placed into cooldown because manual mode doesn't invoke cooldown logic
                assert not cooldown_tracker.is_cooling_down("openrouter")


def test_manual_mode_explicit_provider_override():
    """Manual mode with an explicit provider override (e.g. anthropic) dispatches directly."""
    with patch("app.llm.client.settings") as mock_settings:
        mock_settings.llm_provider_mode = "manual"

        with patch("app.llm.client.complete", return_value="Claude response") as mock_complete:
            with patch("app.llm.client.get_adapter") as mock_get_adapter:
                res = call_llm_with_fallback("Prompt", provider="anthropic")
                assert res == "Claude response"
                mock_complete.assert_called_once_with("Prompt", provider="anthropic")
                mock_get_adapter.assert_not_called()
                assert get_last_serving_provider() == "anthropic"


# ---------------------------------------------------------------------------
# Task 10.3.9: End-to-end fallback verification pass (nvidia_nim exhaustion -> gemini)
# ---------------------------------------------------------------------------

def test_end_to_end_fallback_nvidia_nim_exhaustion_failover_to_gemini():
    """Verify that exhausting nvidia_nim automatically fails over to gemini mid-run without breaking endpoint."""
    from fastapi.testclient import TestClient
    from app.main import app
    from app.agents.ingestion.sub_agents.context_synthesis_sub_agent import IngestionContext
    from app.agents.stack_mapping.stack_mapping_agent import StackScope
    from app.agents.stack_mapping.sub_agents.layer_identification_sub_agent import StackLayer
    from app.agents.scenario_generation.scenario_generation_agent import ScenarioSet
    from app.agents.scenario_generation.sub_agents.scenario_refinement_sub_agent import Scenario
    from app.agents.outcome_prediction.outcome_prediction_agent import OutcomeProjection, OutcomeSet
    from app.agents.outcome_prediction.sub_agents.trajectory_modeling_sub_agent import Trajectory
    from app.agents.outcome_prediction.sub_agents.risk_factor_sub_agent import RiskFactor
    from app.agents.dependency_diagnosis.dependency_diagnosis_agent import DependencyDiagnosis, DiagnosisSet
    from app.agents.dependency_diagnosis.sub_agents.lock_in_identification_sub_agent import LockInDependency
    from app.agents.dependency_diagnosis.sub_agents.failure_mode_sub_agent import FailureMode
    from app.agents.orchestrator.orchestrator_agent import OrchestratorVerdict

    client = TestClient(app)
    cooldown_tracker.reset()

    context = IngestionContext(
        entity="Indian Army", capability="SLM", options=["Build", "License"],
        context_summary="Tactical edge SLM brief.", key_facts=["Tactical edge."], sources=["https://army.in"]
    )
    scope = StackScope(
        entity="Indian Army", capability="SLM",
        layers=[
            StackLayer(name="Weights", rationale="SLM", evidence="Tactical edge."),
            StackLayer(name="Compute", rationale="SLM", evidence="Tactical edge."),
        ], links=[]
    )
    scenarios = ScenarioSet(
        entity="Indian Army", capability="SLM",
        scenarios=[
            Scenario(name="Build", option_name="Build", description="Tactical edge.", layers_addressed=["Weights"]),
            Scenario(name="License", option_name="License", description="Tactical edge.", layers_addressed=["Weights"]),
        ]
    )
    outcomes = OutcomeSet(
        entity="Indian Army", capability="SLM",
        outcomes=[
            OutcomeProjection(
                scenario_name="Build",
                trajectory=Trajectory(scenario_name="Build", summary="Tactical edge."),
                risk_factors=[RiskFactor(scenario_name="Build", factor_name="Risk", description="Desc")]
            )
        ]
    )
    diagnoses = DiagnosisSet(
        entity="Indian Army", capability="SLM",
        diagnoses=[
            DependencyDiagnosis(
                scenario_name="Build",
                dependencies=[LockInDependency(scenario_name="Build", dependency_name="Compute", lock_in_type="Hardware", description="Tactical edge.")],
                failure_modes=[FailureMode(scenario_name="Build", dependency_name="Compute", failure_mode_title="Failure", what_breaks="Tactical edge.")]
            )
        ]
    )
    verdict = OrchestratorVerdict(
        entity="Indian Army", capability="SLM", recommended_path="Build", verdict_summary="Build sovereign."
    )

    call_idx = {"count": 0}
    def mock_get_provider():
        call_idx["count"] += 1
        if call_idx["count"] == 1:
            return "nvidia_nim"
        return "gemini"

    with patch("app.agents.ingestion.ingestion_agent.run", return_value=context), \
         patch("app.agents.stack_mapping.stack_mapping_agent.run", return_value=scope), \
         patch("app.agents.scenario_generation.scenario_generation_agent.run", return_value=scenarios), \
         patch("app.agents.outcome_prediction.outcome_prediction_agent.run", return_value=outcomes), \
         patch("app.agents.dependency_diagnosis.dependency_diagnosis_agent.run", return_value=diagnoses), \
         patch("app.agents.orchestrator.orchestrator_agent.run", return_value=verdict), \
         patch("app.pipeline.graph.get_last_serving_provider", side_effect=mock_get_provider):

        payload = {
            "entity": "Indian Army signals division",
            "capability": "tactical edge speech recognition",
            "options": ["build in-house", "license open-weight"]
        }
        response = client.post("/decisions", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["stage_providers"]["ingestion"] == "nvidia_nim"
        assert data["stage_providers"]["stack_mapping"] == "gemini"
        assert data["stage_providers"]["orchestrator"] == "gemini"
        assert data["verification_passed"] is True
        assert data["verdict"]["recommended_path"] == "Build"
