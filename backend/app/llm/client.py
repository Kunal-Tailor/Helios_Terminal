"""
LLM client wrapper — thin layer over Anthropic (Claude) and OpenAI (GPT) APIs.

Public API
----------
    complete(prompt: str, provider: str = "anthropic") -> str

Reads API keys from app.core.config.settings.
Raises RuntimeError if the required key is not set.
No retry logic, streaming, or token management here — those belong in the agents.
"""

import anthropic
import openai

from app.core.config import settings

# Default models — one per provider.
# These are the cost-effective options suitable for agent reasoning tasks.
_ANTHROPIC_MODEL = "claude-3-5-haiku-latest"
_OPENAI_MODEL = "gpt-4o-mini"


def complete(prompt: str, provider: str = "anthropic") -> str:
    """Send *prompt* to the chosen LLM provider and return the response text.

    Parameters
    ----------
    prompt:
        The user-turn text to send.
    provider:
        ``"anthropic"`` (default) or ``"openai"``.

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
    if provider == "anthropic":
        return _call_anthropic(prompt)
    if provider == "openai":
        return _call_openai(prompt)
    raise ValueError(
        f"Unknown provider '{provider}'. Choose 'anthropic' or 'openai'."
    )


# ---------------------------------------------------------------------------
# Private helpers — one per provider
# ---------------------------------------------------------------------------

def _call_anthropic(prompt: str) -> str:
    if not settings.anthropic_api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. "
            "Add it to your .env file or environment before running agents."
        )
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    message = client.messages.create(
        model=_ANTHROPIC_MODEL,
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
        model=_OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
