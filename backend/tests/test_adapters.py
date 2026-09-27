"""
Unit tests for per-provider adapter functions in app.llm.adapters.

Covers:
  - call_nvidia_nim with mocked response and error handling
  - call_openrouter with mocked response and error handling
  - call_gemini with mocked response and error handling (including 503 UNAVAILABLE)
  - call_deepseek_direct with mocked response and error handling
  - ADAPTER_MAP registry and get_adapter lookup
  - Empty response / null content error raising
"""

from unittest.mock import MagicMock, patch

import httpx
import pytest

import openai
from app.core.config import ProviderConfig
from app.llm.adapters import (
    ADAPTER_MAP,
    call_deepseek_direct,
    call_gemini,
    call_nvidia_nim,
    call_openrouter,
    get_adapter,
)
from app.llm.errors import AuthError, RateLimitError, ServerError


def _make_mock_chat_completion(content: str = "Mocked LLM reply"):
    """Helper to build a mock OpenAI chat completion response."""
    mock_message = MagicMock()
    mock_message.content = content

    mock_choice = MagicMock()
    mock_choice.message = mock_message

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    return mock_response


def _make_httpx_response(status_code: int) -> httpx.Response:
    request = httpx.Request("POST", "https://api.example.com/v1/chat/completions")
    return httpx.Response(status_code=status_code, request=request)


# ---------------------------------------------------------------------------
# NVIDIA NIM Adapter Tests
# ---------------------------------------------------------------------------

def test_call_nvidia_nim_success():
    """call_nvidia_nim dispatches to OpenAI client with NIM config and returns text."""
    config = ProviderConfig(
        name="nvidia_nim",
        api_key="nvapi-test-key",
        base_url="https://integrate.api.nvidia.com/v1",
        model="deepseek-ai/deepseek-v4.1-flash",
    )
    mock_response = _make_mock_chat_completion("NIM generated analysis.")

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch("app.llm.adapters.openai.OpenAI", return_value=mock_client) as mock_cls:
        result = call_nvidia_nim("Evaluate tactical edge SLM", config)

        assert result == "NIM generated analysis."
        mock_cls.assert_called_once_with(
            api_key="nvapi-test-key",
            base_url="https://integrate.api.nvidia.com/v1",
        )
        mock_client.chat.completions.create.assert_called_once_with(
            model="deepseek-ai/deepseek-v4.1-flash",
            messages=[{"role": "user", "content": "Evaluate tactical edge SLM"}],
        )


def test_call_nvidia_nim_missing_key_raises_auth_error():
    """call_nvidia_nim raises AuthError if api_key is empty."""
    config = ProviderConfig(name="nvidia_nim", api_key="", model="deepseek-v4.1-flash")
    with pytest.raises(AuthError, match="API key for provider 'nvidia_nim' is not configured"):
        call_nvidia_nim("Hello", config)


def test_call_nvidia_nim_rate_limit_raises_rate_limit_error():
    """call_nvidia_nim maps 429 RateLimitError to app.llm.errors.RateLimitError."""
    config = ProviderConfig(name="nvidia_nim", api_key="test-key", model="model-1")
    resp = _make_httpx_response(429)
    rate_limit_exc = openai.RateLimitError(
        message="Rate limit exceeded. retry in 10s",
        response=resp,
        body=None,
    )

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = rate_limit_exc

    with patch("app.llm.adapters.openai.OpenAI", return_value=mock_client):
        with pytest.raises(RateLimitError) as exc_info:
            call_nvidia_nim("Hello", config)
        assert exc_info.value.provider == "nvidia_nim"
        assert exc_info.value.retry_after == 10.0


# ---------------------------------------------------------------------------
# OpenRouter Adapter Tests
# ---------------------------------------------------------------------------

def test_call_openrouter_success():
    """call_openrouter dispatches with OpenRouter config and returns text."""
    config = ProviderConfig(
        name="openrouter",
        api_key="sk-or-test-key",
        base_url="https://openrouter.ai/api/v1",
        model="deepseek/deepseek-chat:free",
    )
    mock_response = _make_mock_chat_completion("OpenRouter response.")

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch("app.llm.adapters.openai.OpenAI", return_value=mock_client) as mock_cls:
        result = call_openrouter("Run RAG assessment", config)
        assert result == "OpenRouter response."
        mock_cls.assert_called_once_with(
            api_key="sk-or-test-key",
            base_url="https://openrouter.ai/api/v1",
        )


def test_call_openrouter_auth_error():
    """call_openrouter maps 401 AuthenticationError to AuthError."""
    config = ProviderConfig(name="openrouter", api_key="invalid-key", model="model-1")
    resp = _make_httpx_response(401)
    auth_exc = openai.AuthenticationError(
        message="Invalid token",
        response=resp,
        body=None,
    )

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = auth_exc

    with patch("app.llm.adapters.openai.OpenAI", return_value=mock_client):
        with pytest.raises(AuthError) as exc_info:
            call_openrouter("Test", config)
        assert exc_info.value.provider == "openrouter"


# ---------------------------------------------------------------------------
# Gemini Adapter Tests
# ---------------------------------------------------------------------------

def test_call_gemini_success():
    """call_gemini dispatches with Gemini config and returns text."""
    config = ProviderConfig(
        name="gemini",
        api_key="gemini-key",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        model="gemini-3.5-flash",
    )
    mock_response = _make_mock_chat_completion("Gemini verdict text.")

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch("app.llm.adapters.openai.OpenAI", return_value=mock_client):
        result = call_gemini("Synthesize options", config)
        assert result == "Gemini verdict text."


def test_call_gemini_503_unavailable_raises_server_error():
    """call_gemini maps Gemini 503 UNAVAILABLE to ServerError."""
    config = ProviderConfig(name="gemini", api_key="gemini-key", model="gemini-3.5-flash")
    resp = _make_httpx_response(503)
    server_exc = openai.InternalServerError(
        message="503 UNAVAILABLE: The model is overloaded.",
        response=resp,
        body=None,
    )

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = server_exc

    with patch("app.llm.adapters.openai.OpenAI", return_value=mock_client):
        with pytest.raises(ServerError) as exc_info:
            call_gemini("Test", config)
        assert exc_info.value.provider == "gemini"
        assert exc_info.value.status_code == 503


# ---------------------------------------------------------------------------
# DeepSeek Direct Adapter Tests
# ---------------------------------------------------------------------------

def test_call_deepseek_direct_success():
    """call_deepseek_direct dispatches with DeepSeek Direct config and returns text."""
    config = ProviderConfig(
        name="deepseek_direct",
        api_key="ds-direct-key",
        base_url="https://api.deepseek.com/v1",
        model="deepseek-chat",
    )
    mock_response = _make_mock_chat_completion("DeepSeek Direct output.")

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch("app.llm.adapters.openai.OpenAI", return_value=mock_client):
        result = call_deepseek_direct("Map stack layers", config)
        assert result == "DeepSeek Direct output."


def test_call_deepseek_direct_server_error():
    """call_deepseek_direct maps 500 InternalServerError to ServerError."""
    config = ProviderConfig(name="deepseek_direct", api_key="ds-key", model="deepseek-chat")
    resp = _make_httpx_response(500)
    server_exc = openai.InternalServerError(
        message="Internal server error",
        response=resp,
        body=None,
    )

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = server_exc

    with patch("app.llm.adapters.openai.OpenAI", return_value=mock_client):
        with pytest.raises(ServerError) as exc_info:
            call_deepseek_direct("Test", config)
        assert exc_info.value.provider == "deepseek_direct"


# ---------------------------------------------------------------------------
# Empty Response & Malformed Response Tests
# ---------------------------------------------------------------------------

def test_empty_choices_raises_server_error():
    """Empty choices list in response raises ServerError."""
    config = ProviderConfig(name="nvidia_nim", api_key="key", model="model")
    mock_response = MagicMock()
    mock_response.choices = []

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch("app.llm.adapters.openai.OpenAI", return_value=mock_client):
        with pytest.raises(ServerError, match="choices are empty"):
            call_nvidia_nim("Prompt", config)


def test_null_content_raises_server_error():
    """Null message content raises ServerError."""
    config = ProviderConfig(name="nvidia_nim", api_key="key", model="model")
    mock_response = _make_mock_chat_completion(None)  # type: ignore

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch("app.llm.adapters.openai.OpenAI", return_value=mock_client):
        with pytest.raises(ServerError, match="content is empty"):
            call_nvidia_nim("Prompt", config)


# ---------------------------------------------------------------------------
# ADAPTER_MAP & get_adapter Tests
# ---------------------------------------------------------------------------

def test_adapter_map_and_get_adapter():
    """get_adapter retrieves correct function for each known provider."""
    assert get_adapter("nvidia_nim") is call_nvidia_nim
    assert get_adapter("openrouter") is call_openrouter
    assert get_adapter("gemini") is call_gemini
    assert get_adapter("deepseek_direct") is call_deepseek_direct
    assert get_adapter("deepseek") is call_deepseek_direct


def test_get_adapter_unknown_raises_value_error():
    """get_adapter raises ValueError for unregistered provider."""
    with pytest.raises(ValueError, match="No adapter registered for provider 'unknown'"):
        get_adapter("unknown")
