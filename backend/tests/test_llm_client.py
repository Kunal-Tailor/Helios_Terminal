"""
Unit tests for app.llm.client.

All LLM API calls are mocked — no network access, no API key required.
Tests cover:
  - complete() dispatches to DeepSeek by default (primary provider)
  - complete() dispatches to Anthropic when provider="anthropic"
  - complete() dispatches to OpenAI when provider="openai"
  - complete() raises ValueError for an unknown provider
  - RuntimeError is raised when the required API key is missing
"""

from unittest.mock import MagicMock, patch

import pytest

from app.llm.client import complete


# ---------------------------------------------------------------------------
# DeepSeek (default provider)
# ---------------------------------------------------------------------------

def test_complete_deepseek_returns_text():
    """complete() with default provider calls DeepSeek and returns reply text."""
    mock_text = "This is a mocked DeepSeek response."

    mock_message = MagicMock()
    mock_message.content = mock_text

    mock_choice = MagicMock()
    mock_choice.message = mock_message

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client_instance = MagicMock()
    mock_client_instance.chat.completions.create.return_value = mock_response

    with patch("app.llm.client.openai.OpenAI", return_value=mock_client_instance):
        with patch("app.llm.client.settings") as mock_settings:
            mock_settings.deepseek_api_key = "test-deepseek-key"
            mock_settings.deepseek_base_url = "https://api.deepseek.com/v1"
            mock_settings.default_model = "deepseek-chat"
            result = complete("Hello from test")  # default provider = "deepseek"

    assert result == mock_text


def test_complete_deepseek_raises_when_key_missing():
    """complete() raises RuntimeError when DEEPSEEK_API_KEY is not set."""
    with patch("app.llm.client.settings") as mock_settings:
        mock_settings.deepseek_api_key = ""
        with pytest.raises(RuntimeError, match="DEEPSEEK_API_KEY"):
            complete("Hello")


# ---------------------------------------------------------------------------
# Anthropic (explicit provider)
# ---------------------------------------------------------------------------

def test_complete_anthropic_returns_text():
    """complete(provider='anthropic') calls Anthropic and returns reply text."""
    mock_text = "This is a mocked Anthropic response."

    mock_content_block = MagicMock()
    mock_content_block.text = mock_text

    mock_message = MagicMock()
    mock_message.content = [mock_content_block]

    mock_client_instance = MagicMock()
    mock_client_instance.messages.create.return_value = mock_message

    with patch("app.llm.client.anthropic.Anthropic", return_value=mock_client_instance):
        with patch("app.llm.client.settings") as mock_settings:
            mock_settings.anthropic_api_key = "test-anthropic-key"
            mock_settings.default_model = "deepseek-chat"
            result = complete("Hello from test", provider="anthropic")

    assert result == mock_text


def test_complete_anthropic_raises_when_key_missing():
    """complete(provider='anthropic') raises RuntimeError when key is not set."""
    with patch("app.llm.client.settings") as mock_settings:
        mock_settings.anthropic_api_key = ""
        with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
            complete("Hello", provider="anthropic")


# ---------------------------------------------------------------------------
# OpenAI (explicit provider)
# ---------------------------------------------------------------------------

def test_complete_openai_returns_text():
    """complete(provider='openai') calls OpenAI and returns reply text."""
    mock_text = "This is a mocked OpenAI response."

    mock_message = MagicMock()
    mock_message.content = mock_text

    mock_choice = MagicMock()
    mock_choice.message = mock_message

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client_instance = MagicMock()
    mock_client_instance.chat.completions.create.return_value = mock_response

    with patch("app.llm.client.openai.OpenAI", return_value=mock_client_instance):
        with patch("app.llm.client.settings") as mock_settings:
            mock_settings.openai_api_key = "test-openai-key"
            mock_settings.default_model = "deepseek-chat"
            result = complete("Hello from test", provider="openai")

    assert result == mock_text


def test_complete_openai_raises_when_key_missing():
    """complete(provider='openai') raises RuntimeError when key is not set."""
    with patch("app.llm.client.settings") as mock_settings:
        mock_settings.openai_api_key = ""
        with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
            complete("Hello", provider="openai")


# ---------------------------------------------------------------------------
# Unknown provider
# ---------------------------------------------------------------------------

def test_complete_raises_for_unknown_provider():
    """complete() raises ValueError for an unrecognised provider name."""
    with pytest.raises(ValueError, match="Unknown provider"):
        complete("Hello", provider="some_unknown_llm")
