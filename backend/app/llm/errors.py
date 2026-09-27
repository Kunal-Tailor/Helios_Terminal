"""
Provider error taxonomy and status-code mapping for Helios Terminal LLM integrations.

Defines standard error types:
  - LLMProviderError (base exception)
  - RateLimitError (HTTP 429, quota exceeded, daily request limits)
  - AuthError (HTTP 401/403, invalid or unauthorized API key)
  - ServerError (HTTP 5xx, including 503 UNAVAILABLE)

Provides mapper functions to classify HTTP status codes, error messages, and
provider SDK exceptions into the standard taxonomy.
"""

import re
from typing import Any, Optional


class LLMProviderError(Exception):
    """Base exception for all LLM provider errors."""

    def __init__(
        self,
        message: str = "",
        provider: Optional[str] = None,
        status_code: Optional[int] = None,
    ):
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.status_code = status_code

    def __str__(self) -> str:
        prefix = f"[{self.provider}] " if self.provider else ""
        code_str = f"(status {self.status_code}) " if self.status_code else ""
        return f"{prefix}{code_str}{self.message}".strip()


class RateLimitError(LLMProviderError):
    """Raised when an LLM provider returns 429 or quota exceeded."""

    def __init__(
        self,
        message: str = "",
        provider: Optional[str] = None,
        status_code: Optional[int] = 429,
        retry_after: Optional[float] = None,
    ):
        super().__init__(message=message, provider=provider, status_code=status_code)
        self.retry_after = retry_after


class AuthError(LLMProviderError):
    """Raised when an LLM provider returns 401 or 403 (invalid or unauthorized API key)."""

    def __init__(
        self,
        message: str = "",
        provider: Optional[str] = None,
        status_code: Optional[int] = 401,
    ):
        super().__init__(message=message, provider=provider, status_code=status_code)


class ServerError(LLMProviderError):
    """Raised when an LLM provider returns 5xx (500, 502, 503 UNAVAILABLE, 504)."""

    def __init__(
        self,
        message: str = "",
        provider: Optional[str] = None,
        status_code: Optional[int] = 500,
    ):
        super().__init__(message=message, provider=provider, status_code=status_code)


def extract_retry_after(text: str) -> Optional[float]:
    """Extract retry-after delay in seconds from an error message if present."""
    if not text:
        return None
    match = re.search(r"retry in (\d+(?:\.\d+)?)s", text, re.IGNORECASE) or re.search(
        r"retryDelay['\"]?:\s*['\"]?(\d+(?:\.\d+)?)s?", text, re.IGNORECASE
    )
    if match:
        try:
            return float(match.group(1))
        except (ValueError, IndexError):
            return None
    return None


def map_provider_error(
    target: Any,
    message: str = "",
    provider: Optional[str] = None,
) -> LLMProviderError:
    """Map an HTTP status code, string, or SDK exception to an LLMProviderError.

    Parameters
    ----------
    target:
        An int (HTTP status code), an Exception, or an error string.
    message:
        Optional message override if target is an int or empty exception.
    provider:
        Optional provider name (e.g. 'gemini', 'nvidia_nim').

    Returns
    -------
    LLMProviderError
        An instance of RateLimitError, AuthError, ServerError, or LLMProviderError.
    """
    # 1. Handle integer status code
    if isinstance(target, int):
        status_code = target
        msg = message or f"HTTP error {status_code}"
        if status_code == 429:
            retry_after = extract_retry_after(msg)
            return RateLimitError(msg, provider=provider, status_code=429, retry_after=retry_after)
        if status_code in (401, 403):
            return AuthError(msg, provider=provider, status_code=status_code)
        if 500 <= status_code < 600:
            return ServerError(msg, provider=provider, status_code=status_code)
        return LLMProviderError(msg, provider=provider, status_code=status_code)

    # 2. Extract exception attributes
    status_code: Optional[int] = None
    if hasattr(target, "status_code") and isinstance(target.status_code, int):
        status_code = target.status_code
    elif hasattr(target, "code") and isinstance(target.code, int):
        status_code = target.code

    msg = str(target) if target is not None else message
    if message and message not in msg:
        msg = f"{msg} — {message}" if msg else message

    exc_type_name = type(target).__name__ if isinstance(target, Exception) else ""
    exc_lower = msg.lower()

    retry_after = extract_retry_after(msg)

    # 3. Check for RateLimitError (429, quota limits)
    if (
        status_code == 429
        or "ratelimit" in exc_type_name.lower()
        or "rate limit" in exc_lower
        or "generaterequestsperday" in exc_lower
        or "limit: 20" in exc_lower
        or "quota exceeded" in exc_lower
        or "too many requests" in exc_lower
    ):
        return RateLimitError(
            message=msg,
            provider=provider,
            status_code=status_code or 429,
            retry_after=retry_after,
        )

    # 4. Check for AuthError (401, 403)
    if (
        status_code in (401, 403)
        or "authentication" in exc_type_name.lower()
        or "permissiondenied" in exc_type_name.lower()
        or "unauthorized" in exc_lower
        or "invalid api key" in exc_lower
        or "forbidden" in exc_lower
    ):
        return AuthError(
            message=msg,
            provider=provider,
            status_code=status_code or 401,
        )

    # 5. Check for ServerError (5xx, including Gemini 503 UNAVAILABLE)
    if (
        (status_code is not None and 500 <= status_code < 600)
        or "internalservererror" in exc_type_name.lower()
        or "serviceunavailable" in exc_type_name.lower()
        or "unavailable" in exc_lower
        or "503" in msg
        or "500 internal" in exc_lower
        or "bad gateway" in exc_lower
        or "gateway timeout" in exc_lower
    ):
        return ServerError(
            message=msg,
            provider=provider,
            status_code=status_code or 500,
        )

    # Default fallback
    return LLMProviderError(
        message=msg,
        provider=provider,
        status_code=status_code,
    )
