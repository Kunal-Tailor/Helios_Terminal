"""
Unit tests for app.llm.errors — provider error taxonomy and mapping logic.

Covers:
  - 429 / RateLimitError and retry-after parsing
  - 401 / 403 / AuthError
  - 5xx / ServerError
  - Gemini-specific 503 "UNAVAILABLE" error from production logs
  - Exception and HTTP status code mapping
"""

import httpx
import pytest

import openai
from app.llm.errors import (
    AuthError,
    LLMProviderError,
    RateLimitError,
    ServerError,
    extract_retry_after,
    map_provider_error,
)


def _make_httpx_response(status_code: int) -> httpx.Response:
    request = httpx.Request("POST", "https://api.example.com/v1/chat/completions")
    return httpx.Response(status_code=status_code, request=request)


# ---------------------------------------------------------------------------
# RateLimitError / 429 tests
# ---------------------------------------------------------------------------

def test_map_status_429():
    """Integer status 429 maps to RateLimitError."""
    err = map_provider_error(429, message="Too Many Requests", provider="openrouter")
    assert isinstance(err, RateLimitError)
    assert err.status_code == 429
    assert err.provider == "openrouter"
    assert "Too Many Requests" in err.message


def test_map_status_429_with_retry_after():
    """Retry-after delay is parsed from rate limit message."""
    err = map_provider_error(429, message="Rate limit exceeded. Please retry in 18.5s.", provider="gemini")
    assert isinstance(err, RateLimitError)
    assert err.retry_after == 18.5


def test_extract_retry_after():
    """extract_retry_after parses both 'retry in Xs' and 'retryDelay: Xs' formats."""
    assert extract_retry_after("Please retry in 12s.") == 12.0
    assert extract_retry_after("retry in 4.5s") == 4.5
    assert extract_retry_after('{"retryDelay": "30s"}') == 30.0
    assert extract_retry_after('retryDelay: 15s') == 15.0
    assert extract_retry_after("no retry delay mentioned") is None
    assert extract_retry_after("") is None


def test_map_openai_rate_limit_exception():
    """openai.RateLimitError is mapped to RateLimitError."""
    resp = _make_httpx_response(429)
    mock_exc = openai.RateLimitError(
        message="Rate limit reached for default-model",
        response=resp,
        body={"error": {"message": "Rate limit reached"}},
    )
    err = map_provider_error(mock_exc, provider="nvidia_nim")
    assert isinstance(err, RateLimitError)
    assert err.provider == "nvidia_nim"
    assert "Rate limit" in err.message


def test_map_quota_strings():
    """Messages with GenerateRequestsPerDay or limit: 20 map to RateLimitError."""
    err1 = map_provider_error(Exception("Quota exceeded: GenerateRequestsPerDay limit reached"))
    assert isinstance(err1, RateLimitError)

    err2 = map_provider_error(Exception("Resource exhausted (limit: 20 per day)"))
    assert isinstance(err2, RateLimitError)


# ---------------------------------------------------------------------------
# AuthError / 401 & 403 tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("status_code", [401, 403])
def test_map_status_auth_errors(status_code):
    """Integer status codes 401 and 403 map to AuthError."""
    err = map_provider_error(status_code, message="Unauthorized", provider="nvidia_nim")
    assert isinstance(err, AuthError)
    assert err.status_code == status_code
    assert err.provider == "nvidia_nim"


def test_map_openai_auth_exception():
    """openai.AuthenticationError maps to AuthError."""
    resp = _make_httpx_response(401)
    exc = openai.AuthenticationError(
        message="Incorrect API key provided",
        response=resp,
        body=None,
    )
    err = map_provider_error(exc, provider="openrouter")
    assert isinstance(err, AuthError)
    assert err.provider == "openrouter"
    assert "Incorrect API key" in err.message


def test_map_auth_message_strings():
    """Messages containing 'invalid api key' or 'unauthorized' map to AuthError."""
    err = map_provider_error(Exception("Invalid API key provided for provider"))
    assert isinstance(err, AuthError)


# ---------------------------------------------------------------------------
# ServerError / 5xx tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("status_code", [500, 502, 503, 504])
def test_map_status_5xx_errors(status_code):
    """5xx HTTP status codes map to ServerError."""
    err = map_provider_error(status_code, message="Upstream failure", provider="deepseek_direct")
    assert isinstance(err, ServerError)
    assert err.status_code == status_code
    assert err.provider == "deepseek_direct"


def test_map_openai_internal_server_error():
    """openai.InternalServerError maps to ServerError."""
    resp = _make_httpx_response(500)
    exc = openai.InternalServerError(
        message="The server had an error while processing your request",
        response=resp,
        body=None,
    )
    err = map_provider_error(exc, provider="nvidia_nim")
    assert isinstance(err, ServerError)
    assert err.provider == "nvidia_nim"


# ---------------------------------------------------------------------------
# Gemini-specific 503 "UNAVAILABLE" production log case
# ---------------------------------------------------------------------------

def test_gemini_503_unavailable_string_mapping():
    """Gemini-specific 503 'UNAVAILABLE' log message maps to ServerError."""
    log_text = (
        "Error code: 503 - {'error': {'code': 503, "
        "'message': 'The model is overloaded. Please try again later.', "
        "'status': 'UNAVAILABLE'}}"
    )
    err = map_provider_error(log_text, provider="gemini")
    assert isinstance(err, ServerError)
    assert err.provider == "gemini"
    assert "UNAVAILABLE" in err.message


def test_gemini_503_unavailable_exception_mapping():
    """Mocked Gemini 503 exception with status 'UNAVAILABLE' maps to ServerError."""
    class MockGeminiAPIError(Exception):
        def __init__(self):
            super().__init__(
                "503 UNAVAILABLE: The service is currently unable to handle the request."
            )
            self.status_code = 503

    exc = MockGeminiAPIError()
    err = map_provider_error(exc, provider="gemini")
    assert isinstance(err, ServerError)
    assert err.status_code == 503
    assert err.provider == "gemini"


# ---------------------------------------------------------------------------
# String representation and generic error fallback
# ---------------------------------------------------------------------------

def test_error_str_formatting():
    """Error string contains provider and status code when present."""
    err = RateLimitError("RPM exceeded", provider="gemini", status_code=429)
    assert str(err) == "[gemini] (status 429) RPM exceeded"

    err_no_provider = ServerError("Gateway down", status_code=504)
    assert str(err_no_provider) == "(status 504) Gateway down"


def test_generic_fallback_error():
    """Unknown error types map to base LLMProviderError."""
    err = map_provider_error(Exception("Something bizarre occurred"), provider="unknown")
    assert isinstance(err, LLMProviderError)
    assert not isinstance(err, (RateLimitError, AuthError, ServerError))
    assert err.provider == "unknown"
