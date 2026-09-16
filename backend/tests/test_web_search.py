"""
Unit tests for app.retrieval.web_search.

All Tavily API calls are mocked — no network access, no API key required.
Tests cover:
  - search() returns a list of SearchResult dataclasses
  - SearchResult fields are correctly mapped from the raw Tavily response
  - max_results is capped at 10 regardless of the caller's argument
  - RuntimeError is raised when TAVILY_API_KEY is not set
"""

from unittest.mock import MagicMock, patch

import pytest

from app.retrieval.web_search import SearchResult, search

# ---------------------------------------------------------------------------
# Shared fixture: a minimal Tavily-style raw response
# ---------------------------------------------------------------------------

_RAW_RESPONSE = {
    "results": [
        {
            "title": "Example Title",
            "url": "https://example.com/article",
            "content": "This is a snippet about the topic.",
            "score": 0.92,
        },
        {
            "title": "Another Result",
            "url": "https://other.com/page",
            "content": "Another snippet here.",
            "score": 0.75,
        },
    ]
}


def _make_mock_client(raw_response: dict) -> MagicMock:
    """Return a mock TavilyClient whose .search() returns raw_response."""
    mock_instance = MagicMock()
    mock_instance.search.return_value = raw_response
    return mock_instance


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

def test_search_returns_list_of_search_results():
    """search() returns a list of SearchResult instances."""
    mock_client = _make_mock_client(_RAW_RESPONSE)
    with patch("app.retrieval.web_search.TavilyClient", return_value=mock_client):
        with patch("app.retrieval.web_search.settings") as mock_settings:
            mock_settings.tavily_api_key = "test-key"
            results = search("AI sourcing options")

    assert isinstance(results, list)
    assert all(isinstance(r, SearchResult) for r in results)


def test_search_maps_fields_correctly():
    """SearchResult fields are correctly mapped from the raw Tavily response."""
    mock_client = _make_mock_client(_RAW_RESPONSE)
    with patch("app.retrieval.web_search.TavilyClient", return_value=mock_client):
        with patch("app.retrieval.web_search.settings") as mock_settings:
            mock_settings.tavily_api_key = "test-key"
            results = search("test query")

    first = results[0]
    assert first.title == "Example Title"
    assert first.url == "https://example.com/article"
    assert first.content == "This is a snippet about the topic."
    assert first.score == pytest.approx(0.92)


def test_search_returns_correct_count():
    """search() returns as many results as the raw response contains."""
    mock_client = _make_mock_client(_RAW_RESPONSE)
    with patch("app.retrieval.web_search.TavilyClient", return_value=mock_client):
        with patch("app.retrieval.web_search.settings") as mock_settings:
            mock_settings.tavily_api_key = "test-key"
            results = search("test query")

    assert len(results) == 2


# ---------------------------------------------------------------------------
# max_results cap test
# ---------------------------------------------------------------------------

def test_search_caps_max_results_at_10():
    """search() never passes more than 10 to the Tavily client."""
    mock_client = _make_mock_client({"results": []})
    with patch("app.retrieval.web_search.TavilyClient", return_value=mock_client):
        with patch("app.retrieval.web_search.settings") as mock_settings:
            mock_settings.tavily_api_key = "test-key"
            search("test query", max_results=999)

    # The actual call to TavilyClient.search must have max_results <= 10
    call_kwargs = mock_client.search.call_args.kwargs
    assert call_kwargs["max_results"] <= 10


# ---------------------------------------------------------------------------
# Missing API key test
# ---------------------------------------------------------------------------

def test_search_raises_when_key_missing():
    """search() raises RuntimeError when TAVILY_API_KEY is not set."""
    with patch("app.retrieval.web_search.settings") as mock_settings:
        mock_settings.tavily_api_key = ""
        with pytest.raises(RuntimeError, match="TAVILY_API_KEY"):
            search("test query")
