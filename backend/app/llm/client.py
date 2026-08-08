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

import anthropic
import openai

from app.core.config import settings

logger = logging.getLogger(__name__)



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
    if provider in ("default", "deepseek", "openrouter"):
        return _call_llm(prompt)
    if provider == "anthropic":
        return _call_anthropic(prompt)
    if provider == "openai":
        return _call_openai(prompt)
    raise ValueError(
        f"Unknown provider '{provider}'. Choose 'default', 'deepseek', 'openrouter', 'anthropic', or 'openai'."
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

    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=settings.default_model,  # DEFAULT_MODEL env var
                messages=[{"role": "user", "content": prompt}],
            )
            break
        except (openai.RateLimitError, openai.APIError) as exc:
            if attempt == max_retries - 1:
                raise
            sleep_time = 4 * (attempt + 1)
            logger.warning(
                "LLM API call rate limited (attempt %d/%d), sleeping %ds: %s",
                attempt + 1,
                max_retries,
                sleep_time,
                exc,
            )
            time.sleep(sleep_time)
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
