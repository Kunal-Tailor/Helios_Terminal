"""
Unit tests for multi-provider configuration parsing in app.core.config.

Covers:
  - Valid LLM_PROVIDER_CHAIN strings and sequences
  - Malformed LLM_PROVIDER_CHAIN strings (empty, whitespace, unknown providers)
  - Validation error handling in Settings model
  - Building per-provider ProviderConfig objects for each of the four providers
  - Handling of provider fallbacks and unknown provider lookups
"""

import pytest
from pydantic import ValidationError

from app.core.config import (
    KNOWN_PROVIDERS,
    ProviderConfig,
    Settings,
    parse_provider_chain,
)


# ---------------------------------------------------------------------------
# parse_provider_chain unit tests (valid values)
# ---------------------------------------------------------------------------

def test_parse_provider_chain_default_full():
    """Parsing standard 4-provider comma-separated string succeeds."""
    raw = "nvidia_nim,openrouter,gemini,deepseek_direct"
    result = parse_provider_chain(raw)
    assert result == ["nvidia_nim", "openrouter", "gemini", "deepseek_direct"]


def test_parse_provider_chain_single_provider():
    """A single valid provider returns a single-element list."""
    assert parse_provider_chain("gemini") == ["gemini"]
    assert parse_provider_chain("nvidia_nim") == ["nvidia_nim"]


def test_parse_provider_chain_whitespace_and_casing():
    """Leading/trailing whitespace and uppercase characters are normalized."""
    raw = "  NVIDIA_NIM  ,  OpenRouter ,  GEMINI  "
    result = parse_provider_chain(raw)
    assert result == ["nvidia_nim", "openrouter", "gemini"]


def test_parse_provider_chain_from_list():
    """Passing a sequence of provider names is supported and normalized."""
    result = parse_provider_chain(["nvidia_nim", " GEMINI "])
    assert result == ["nvidia_nim", "gemini"]


# ---------------------------------------------------------------------------
# parse_provider_chain unit tests (malformed values)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "malformed_chain",
    [
        "",
        "   ",
        ",,,",
        "  ,  ,  ",
    ],
)
def test_parse_provider_chain_empty_fails(malformed_chain):
    """Empty or whitespace-only chains raise ValueError."""
    with pytest.raises(ValueError, match="cannot be empty"):
        parse_provider_chain(malformed_chain)


def test_parse_provider_chain_unknown_provider():
    """Unknown provider name raises ValueError listing the invalid item."""
    with pytest.raises(ValueError, match="Unknown provider\\(s\\) in LLM_PROVIDER_CHAIN: claude"):
        parse_provider_chain("claude")


def test_parse_provider_chain_mixed_valid_and_unknown():
    """Chain containing both valid and invalid provider names raises ValueError."""
    with pytest.raises(ValueError, match="Unknown provider\\(s\\) in LLM_PROVIDER_CHAIN: gpt4_turbo"):
        parse_provider_chain("nvidia_nim,gpt4_turbo,gemini")


def test_parse_provider_chain_invalid_type():
    """Passing a non-string/non-list type raises ValueError."""
    with pytest.raises(ValueError, match="Invalid provider chain type"):
        parse_provider_chain(12345)  # type: ignore


# ---------------------------------------------------------------------------
# Settings model validation with LLM_PROVIDER_CHAIN
# ---------------------------------------------------------------------------

def test_settings_valid_provider_chain():
    """Settings initialized with valid chain normalizes correctly via provider_chain property."""
    s = Settings(llm_provider_chain="nvidia_nim,gemini")
    assert s.provider_chain == ["nvidia_nim", "gemini"]


def test_settings_malformed_provider_chain_raises():
    """Settings initialized with malformed chain raises ValidationError."""
    with pytest.raises(ValidationError):
        Settings(llm_provider_chain="invalid_provider")

    with pytest.raises(ValidationError):
        Settings(llm_provider_chain="")


# ---------------------------------------------------------------------------
# Per-provider config object tests
# ---------------------------------------------------------------------------

def test_per_provider_config_objects():
    """Settings builds ProviderConfig objects for each of the four providers."""
    s = Settings(
        nvidia_nim_api_key="nim-key-123",
        nvidia_nim_base_url="https://integrate.api.nvidia.com/v1",
        nvidia_nim_model="deepseek-ai/deepseek-v4.1-flash",
        openrouter_api_key="or-key-456",
        openrouter_base_url="https://openrouter.ai/api/v1",
        openrouter_model="deepseek/deepseek-chat:free",
        gemini_api_key="gem-key-789",
        gemini_base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        gemini_model="gemini-3.5-flash",
        deepseek_direct_api_key="ds-direct-key-000",
        deepseek_direct_base_url="https://api.deepseek.com/v1",
        deepseek_direct_model="deepseek-chat",
    )

    nim_cfg = s.get_provider_config("nvidia_nim")
    assert isinstance(nim_cfg, ProviderConfig)
    assert nim_cfg.name == "nvidia_nim"
    assert nim_cfg.api_key == "nim-key-123"
    assert nim_cfg.base_url == "https://integrate.api.nvidia.com/v1"
    assert nim_cfg.model == "deepseek-ai/deepseek-v4.1-flash"

    or_cfg = s.get_provider_config("openrouter")
    assert or_cfg.name == "openrouter"
    assert or_cfg.api_key == "or-key-456"
    assert or_cfg.model == "deepseek/deepseek-chat:free"

    gem_cfg = s.get_provider_config("gemini")
    assert gem_cfg.name == "gemini"
    assert gem_cfg.api_key == "gem-key-789"
    assert gem_cfg.model == "gemini-3.5-flash"

    ds_cfg = s.get_provider_config("deepseek_direct")
    assert ds_cfg.name == "deepseek_direct"
    assert ds_cfg.api_key == "ds-direct-key-000"
    assert ds_cfg.model == "deepseek-chat"

    # Verify providers dictionary contains all 4 known providers
    all_providers = s.providers
    assert set(all_providers.keys()) == set(KNOWN_PROVIDERS)
    assert all_providers["nvidia_nim"] == nim_cfg
    assert all_providers["openrouter"] == or_cfg
    assert all_providers["gemini"] == gem_cfg
    assert all_providers["deepseek_direct"] == ds_cfg


def test_deepseek_legacy_key_fallback():
    """deepseek_direct falls back to legacy deepseek_api_key when direct key is empty."""
    s = Settings(
        deepseek_direct_api_key="",
        deepseek_api_key="legacy-deepseek-key",
    )
    cfg = s.get_provider_config("deepseek_direct")
    assert cfg.api_key == "legacy-deepseek-key"

    # Also works with alias 'deepseek'
    cfg_alias = s.get_provider_config("deepseek")
    assert cfg_alias.api_key == "legacy-deepseek-key"


def test_get_provider_config_unknown_raises():
    """Looking up an unknown provider name raises ValueError."""
    s = Settings()
    with pytest.raises(ValueError, match="Unknown provider 'unsupported_provider'"):
        s.get_provider_config("unsupported_provider")
