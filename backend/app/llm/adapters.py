"""
Per-provider adapter functions for Helios Terminal LLM fallback chain.

Provides typed adapters taking (prompt, config) and returning response text:
  - call_nvidia_nim
  - call_openrouter
  - call_gemini
  - call_deepseek_direct

All adapters call OpenAI-compatible APIs and raise normalized exception types
from app.llm.errors (RateLimitError, AuthError, ServerError).
"""

import logging
from typing import Any, Callable, Dict, Optional

import openai

from app.core.config import ProviderConfig
from app.llm.errors import (
    AuthError,
    LLMProviderError,
    ServerError,
    map_provider_error,
)

logger = logging.getLogger(__name__)


def _extract_config(config: Any, default_name: str) -> tuple[str, str, str, str]:
    """Extract (name, api_key, base_url, model) from ProviderConfig or dict."""
    if isinstance(config, dict):
        name = config.get("name", default_name)
        api_key = (config.get("api_key") or "").strip()
        base_url = (config.get("base_url") or "").strip()
        model = (config.get("model") or "").strip()
    else:
        name = getattr(config, "name", default_name)
        api_key = (getattr(config, "api_key", "") or "").strip()
        base_url = (getattr(config, "base_url", "") or "").strip()
        model = (getattr(config, "model", "") or "").strip()
    return name, api_key, base_url, model


def _call_openai_compatible_provider(prompt: str, config: Any, default_name: str) -> str:
    """Core call function for OpenAI-compatible LLM endpoints.

    Parameters
    ----------
    prompt:
        User prompt text.
    config:
        ProviderConfig or dict containing api_key, base_url, model, name.
    default_name:
        Fallback provider name if not set on config.

    Returns
    -------
    str
        Response content string.

    Raises
    ------
    AuthError
        If api_key is missing or invalid.
    RateLimitError
        If 429 or quota limit is reached.
    ServerError
        If 5xx or server/response issue occurs.
    """
    name, api_key, base_url, model = _extract_config(config, default_name)

    if not api_key:
        raise AuthError(
            f"API key for provider '{name}' is not configured.",
            provider=name,
            status_code=401,
        )

    client = openai.OpenAI(
        api_key=api_key,
        base_url=base_url or None,
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
    except LLMProviderError:
        raise
    except Exception as exc:
        raise map_provider_error(exc, provider=name) from exc

    if not response or not getattr(response, "choices", None) or len(response.choices) == 0:
        raise ServerError(
            f"Response choices are empty from provider '{name}'.",
            provider=name,
            status_code=500,
        )

    choice = response.choices[0]
    if not choice or not getattr(choice, "message", None) or choice.message.content is None:
        raise ServerError(
            f"Response message content is empty from provider '{name}'.",
            provider=name,
            status_code=500,
        )

    return choice.message.content


def call_nvidia_nim(prompt: str, config: Any) -> str:
    """Execute LLM call using NVIDIA NIM endpoint."""
    return _call_openai_compatible_provider(prompt, config, default_name="nvidia_nim")


def call_openrouter(prompt: str, config: Any) -> str:
    """Execute LLM call using OpenRouter endpoint."""
    return _call_openai_compatible_provider(prompt, config, default_name="openrouter")


def call_gemini(prompt: str, config: Any) -> str:
    """Execute LLM call using Google Gemini endpoint (OpenAI-compatible)."""
    return _call_openai_compatible_provider(prompt, config, default_name="gemini")


def call_deepseek_direct(prompt: str, config: Any) -> str:
    """Execute LLM call using DeepSeek Direct endpoint."""
    return _call_openai_compatible_provider(prompt, config, default_name="deepseek_direct")


ADAPTER_MAP: Dict[str, Callable[[str, Any], str]] = {
    "nvidia_nim": call_nvidia_nim,
    "openrouter": call_openrouter,
    "gemini": call_gemini,
    "deepseek_direct": call_deepseek_direct,
    # Alias for backward compatibility
    "deepseek": call_deepseek_direct,
}


def get_adapter(provider_name: str) -> Callable[[str, Any], str]:
    """Retrieve adapter function by provider name.

    Raises
    ------
    ValueError
        If provider_name has no registered adapter.
    """
    key = (provider_name or "").strip().lower()
    if key not in ADAPTER_MAP:
        raise ValueError(
            f"No adapter registered for provider '{provider_name}'. "
            f"Available adapters: {', '.join(k for k in ADAPTER_MAP if k != 'deepseek')}"
        )
    return ADAPTER_MAP[key]
