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

import anthropic
import openai

from app.core.config import settings


def complete(prompt: str, provider: str = "deepseek") -> str:
    """Send *prompt* to the chosen LLM provider and return the response text.

    Parameters
    ----------
    prompt:
        The user-turn text to send.
    provider:
        ``"deepseek"`` (default — DeepSeek V4 Flash via OpenAI-compatible API),
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
    if provider == "deepseek":
        return _call_deepseek(prompt)
    if provider == "anthropic":
        return _call_anthropic(prompt)
    if provider == "openai":
        return _call_openai(prompt)
    raise ValueError(
        f"Unknown provider '{provider}'. Choose 'deepseek', 'anthropic', or 'openai'."
    )


# ---------------------------------------------------------------------------
# Private helpers — one per provider
# ---------------------------------------------------------------------------

def _call_deepseek(prompt: str) -> str:
    """Call DeepSeek V4 Flash via its OpenAI-compatible API."""
    if not settings.deepseek_api_key:
        raise RuntimeError(
            "DEEPSEEK_API_KEY is not set. "
            "Add it to your .env file or environment before running agents."
        )
    client = openai.OpenAI(
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
    )
    response = client.chat.completions.create(
        model=settings.default_model,  # DEFAULT_MODEL env var, default "deepseek-chat"
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


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
