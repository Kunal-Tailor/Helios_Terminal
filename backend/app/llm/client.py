"""
LLM client wrapper — thin layer over DeepSeek (primary), Anthropic, and OpenAI APIs.

Public API
----------
    complete(prompt: str, provider: str = "deepseek") -> str

The active model is controlled by settings.default_model (env var DEFAULT_MODEL).
Reads API keys from app.core.config.settings.
Raises RuntimeError if the required key is not set.
No retry logic, streaming, or token management here — those belong in the agents.
"""

import logging
import re
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

import anthropic
import openai

from app.core.config import settings
from app.llm.adapters import get_adapter
from app.llm.errors import (
    AllProvidersExhaustedError,
    AuthError,
    RateLimitError,
    ServerError,
    map_provider_error,
)

logger = logging.getLogger(__name__)


class CooldownTracker:
    """In-memory thread-safe tracker for LLM provider cooldown timestamps."""

    def __init__(self):
        self._cooldowns: Dict[str, float] = {}
        self._lock = threading.Lock()

    def is_cooling_down(self, provider: str, now: Optional[float] = None) -> bool:
        """Check if provider is currently cooling down."""
        curr = time.time() if now is None else now
        with self._lock:
            until = self._cooldowns.get(provider.strip().lower(), 0.0)
            return curr < until

    def set_cooldown(self, provider: str, duration_sec: float, now: Optional[float] = None) -> None:
        """Place provider into cooldown for duration_sec seconds."""
        curr = time.time() if now is None else now
        with self._lock:
            self._cooldowns[provider.strip().lower()] = curr + max(0.0, float(duration_sec))

    def get_remaining_cooldown(self, provider: str, now: Optional[float] = None) -> float:
        """Return remaining cooldown seconds for provider (0.0 if not cooling down)."""
        curr = time.time() if now is None else now
        with self._lock:
            until = self._cooldowns.get(provider.strip().lower(), 0.0)
            return max(0.0, until - curr)

    def reset(self, provider: Optional[str] = None) -> None:
        """Clear cooldown for a single provider or all providers."""
        with self._lock:
            if provider is not None:
                self._cooldowns.pop(provider.strip().lower(), None)
            else:
                self._cooldowns.clear()


# Shared in-memory cooldown tracker instance
cooldown_tracker = CooldownTracker()

_last_serving_provider: Optional[str] = None


def get_last_serving_provider() -> Optional[str]:
    """Return the name of the provider that answered the most recent LLM call."""
    return _last_serving_provider


def call_llm_with_fallback(prompt: str, provider: str = "default") -> str:
    """Execute LLM call with multi-provider fallback and cooldown management.

    Behavior
    --------
    - If LLM_PROVIDER_MODE is 'manual' (or a specific provider like 'anthropic' or
      'openai' is requested), delegates directly to the single-provider complete()
      function with zero fallback logic invoked.
    - If LLM_PROVIDER_MODE is 'auto', iterates LLM_PROVIDER_CHAIN in priority order.
      Providers currently cooling down are skipped. On RateLimitError, AuthError,
      or ServerError, the failing provider is placed into cooldown and the NEXT
      provider in the chain is attempted for the SAME call.
    - Returns text on the first successful provider reply.
    - Raises AllProvidersExhaustedError if all candidate providers fail or are
      in cooldown.
    """
    global _last_serving_provider
    mode = (getattr(settings, "llm_provider_mode", "manual") or "manual").strip().lower()

    # Manual mode or specific provider requested -> call single provider directly
    if mode == "manual" or provider not in ("default", "auto"):
        active_provider = settings.llm_provider if provider == "default" else provider
        result = complete(prompt, provider=provider)
        _last_serving_provider = active_provider
        return result

    # Auto mode -> iterate provider chain
    chain = getattr(settings, "provider_chain", None)
    if not chain:
        result = complete(prompt, provider=provider)
        _last_serving_provider = settings.llm_provider
        return result

    cooldown_sec = float(getattr(settings, "llm_provider_cooldown_sec", 60))
    max_retries = int(getattr(settings, "llm_provider_max_retries_per_call", len(chain)))
    attempts: List[Tuple[str, Any]] = []

    for idx, provider_name in enumerate(chain):
        if idx >= max_retries:
            logger.warning(
                "Reached max provider retries per call (%d). Stopping fallback chain.",
                max_retries,
            )
            break

        if cooldown_tracker.is_cooling_down(provider_name):
            remaining = cooldown_tracker.get_remaining_cooldown(provider_name)
            logger.debug(
                "Provider '%s' is in cooldown (%.1fs remaining), skipping.",
                provider_name,
                remaining,
            )
            attempts.append((provider_name, f"cooldown_active_{remaining:.1f}s"))
            continue

        try:
            adapter = get_adapter(provider_name)
            config = settings.get_provider_config(provider_name)
            result = adapter(prompt, config)
            _last_serving_provider = provider_name
            logger.info("LLM call succeeded via provider '%s'", provider_name)
            return result
        except (RateLimitError, AuthError, ServerError) as exc:
            duration = (
                exc.retry_after
                if (isinstance(exc, RateLimitError) and exc.retry_after and exc.retry_after > 0)
                else cooldown_sec
            )
            cooldown_tracker.set_cooldown(provider_name, duration)
            logger.warning(
                "Provider '%s' failed with %s: %s. Cooldown set for %.1fs. Failing over to next provider.",
                provider_name,
                type(exc).__name__,
                exc,
                duration,
            )
            attempts.append((provider_name, exc))
        except Exception as exc:
            mapped_exc = map_provider_error(exc, provider=provider_name)
            duration = (
                mapped_exc.retry_after
                if (isinstance(mapped_exc, RateLimitError) and mapped_exc.retry_after and mapped_exc.retry_after > 0)
                else cooldown_sec
            )
            cooldown_tracker.set_cooldown(provider_name, duration)
            logger.warning(
                "Provider '%s' failed with unexpected %s: %s. Cooldown set for %.1fs. Failing over.",
                provider_name,
                type(exc).__name__,
                exc,
                duration,
            )
            attempts.append((provider_name, mapped_exc))

    raise AllProvidersExhaustedError(
        f"All LLM providers in fallback chain exhausted: {attempts}",
        attempts=attempts,
    )




def complete(prompt: str, provider: str = "default") -> str:
    """Send *prompt* to the chosen LLM provider and return the response text.

    Parameters
    ----------
    prompt:
        The user-turn text to send.
    provider:
        ``"default"``, ``"deepseek"``, ``"openrouter"`` (uses settings.llm_provider),
        ``"anthropic"``, or ``"openai"``.

    The model used is ``settings.default_model`` (env var ``DEFAULT_MODEL``).
    Override it per-call by setting a different model in the environment.

    Returns
    -------
    str
        The model's reply as a plain string.

    Raises
    ------
    ValueError
        If *provider* is not a known value.
    RuntimeError
        If the API key for the requested provider is not configured.
    """
    if provider in ("default", "deepseek", "openrouter", "gemini"):
        return _call_llm(prompt)
    if provider == "anthropic":
        return _call_anthropic(prompt)
    if provider == "openai":
        return _call_openai(prompt)
    raise ValueError(
        f"Unknown provider '{provider}'. Choose 'default', 'deepseek', 'openrouter', 'gemini', 'anthropic', or 'openai'."
    )


# ---------------------------------------------------------------------------
# Private helpers — one per provider
# ---------------------------------------------------------------------------

def _call_llm(prompt: str) -> str:
    """Call OpenAI-compatible LLM API (DeepSeek, OpenRouter, etc.)."""
    api_key = settings.llm_api_key
    base_url = settings.llm_base_url
    logger.debug(
        "LLM API Call [%s]: model='%s', key_is_set=%s, base_url='%s'",
        settings.llm_provider,
        settings.default_model,
        bool(api_key),
        base_url,
    )
    if not api_key:
        raise RuntimeError(
            f"LLM API key for provider '{settings.llm_provider}' is not set. "
            "Add OPENROUTER_API_KEY or DEEPSEEK_API_KEY to your .env file or environment."
        )
    client = openai.OpenAI(
        api_key=api_key,
        base_url=base_url,
    )
    import time

    models_to_try = [settings.default_model]
    if (settings.llm_provider or "").lower() == "gemini":
        for fallback in ("gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.5-flash"):
            if fallback not in models_to_try:
                models_to_try.append(fallback)

    max_retries = 5
    response = None
    last_exc = None
    chosen_model = settings.default_model

    for current_model in models_to_try:
        chosen_model = current_model
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=current_model,
                    messages=[{"role": "user", "content": prompt}],
                )
                break
            except (openai.RateLimitError, openai.APIError) as exc:
                exc_str = str(exc)
                if "GenerateRequestsPerDay" in exc_str or "limit: 20" in exc_str:
                    logger.warning(
                        "Model '%s' hit daily quota. Failing over to next sibling model.",
                        current_model,
                    )
                    last_exc = exc
                    break
                if attempt == max_retries - 1:
                    last_exc = exc
                    break
                sleep_time = float(4 * (attempt + 1))
                delay_match = re.search(r"retry in (\d+(?:\.\d+)?)s", exc_str, re.IGNORECASE) or re.search(r"retryDelay['\"]?:\s*['\"]?(\d+)s", exc_str, re.IGNORECASE)
                if delay_match:
                    try:
                        parsed_delay = float(delay_match.group(1)) + 1.5
                        sleep_time = max(sleep_time, min(parsed_delay, 60.0))
                    except (ValueError, IndexError):
                        pass
                logger.warning(
                    "LLM API call rate limited (model='%s', attempt %d/%d), sleeping %ds: %s",
                    current_model,
                    attempt + 1,
                    max_retries,
                    int(sleep_time),
                    exc,
                )
                time.sleep(sleep_time)
        if response is not None:
            break

    if response is None:
        if last_exc:
            raise last_exc
        raise RuntimeError(f"All candidate models failed for prompt: {models_to_try}")
    if response is None or getattr(response, "choices", None) is None or len(response.choices) == 0:
        logger.error(
            "LLM API response or choices is empty/None for model='%s'. Raw response object: %r",
            settings.default_model,
            response,
        )
        raise RuntimeError(f"LLM API response or choices is empty/None: {response!r}")

    choice = response.choices[0]
    if choice is None or getattr(choice, "message", None) is None or getattr(choice.message, "content", None) is None:
        logger.error(
            "LLM API response choice or message content is empty/None for model='%s'. Raw response object: %r",
            settings.default_model,
            response,
        )
        raise RuntimeError(f"LLM API response choice or message content is empty/None: {response!r}")

    return choice.message.content


def _call_anthropic(prompt: str) -> str:
    if not settings.anthropic_api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. "
            "Add it to your .env file or environment before running agents."
        )
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    message = client.messages.create(
        model=settings.default_model,  # DEFAULT_MODEL env var
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def _call_openai(prompt: str) -> str:
    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. "
            "Add it to your .env file or environment before running agents."
        )
    client = openai.OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.default_model,  # DEFAULT_MODEL env var
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
