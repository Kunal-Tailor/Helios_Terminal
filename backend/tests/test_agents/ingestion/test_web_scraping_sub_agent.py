"""
Unit tests for app.agents.ingestion.sub_agents.web_scraping_sub_agent.

All calls to app.retrieval.web_search.search are mocked — no network access,
no Tavily API key required.

Tests cover:
  - run() returns a list of SearchResult objects
  - run() deduplicates results that share the same URL across queries
  - run() sorts results by score descending
  - run() works with no options supplied (two base queries only)
  - run() generates one extra query per option supplied
  - run() returns [] when search returns no results
  - _build_queries() produces the expected query strings
"""

from unittest.mock import call, patch

import pytest

from app.agents.ingestion.sub_agents.web_scraping_sub_agent import _build_queries, run
from app.retrieval.web_search import SearchResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _result(title: str, url: str, score: float) -> SearchResult:
    return SearchResult(title=title, url=url, content=f"Content for {title}", score=score)


# ---------------------------------------------------------------------------
# _build_queries
# ---------------------------------------------------------------------------

def test_build_queries_no_options():
    """_build_queries returns two base queries when options is empty."""
    queries = _build_queries("ACME Corp", "edge inference LLM", [])
    assert len(queries) == 2
    assert all("ACME Corp" in q for q in queries)
    assert all("edge inference LLM" in q for q in queries)


def test_build_queries_with_options():
    """_build_queries returns base queries plus one per option."""
    options = ["build in-house", "license from vendor"]
    queries = _build_queries("ACME Corp", "edge inference LLM", options)
    assert len(queries) == 4  # 2 base + 2 option queries
    assert any("build in-house" in q for q in queries)
    assert any("license from vendor" in q for q in queries)


# ---------------------------------------------------------------------------
# run() — return type and basic shape
# ---------------------------------------------------------------------------

def test_run_returns_list_of_search_results():
    """run() returns a list of SearchResult objects."""
    mock_results = [_result("Article A", "https://a.com", 0.9)]

    with patch("app.agents.ingestion.sub_agents.web_scraping_sub_agent.search",
               return_value=mock_results):
        results = run(entity="ACME Corp", capability="edge inference LLM")

    assert isinstance(results, list)
    assert all(isinstance(r, SearchResult) for r in results)


def test_run_no_options_calls_search_twice():
    """run() with no options issues exactly two search queries."""
    with patch("app.agents.ingestion.sub_agents.web_scraping_sub_agent.search",
               return_value=[]) as mock_search:
        run(entity="ACME Corp", capability="edge inference LLM")

    assert mock_search.call_count == 2


def test_run_with_options_calls_search_for_each_option():
    """run() issues base queries plus one per option."""
    options = ["build", "buy", "outsource"]
    with patch("app.agents.ingestion.sub_agents.web_scraping_sub_agent.search",
               return_value=[]) as mock_search:
        run(entity="ACME Corp", capability="LLM", options=options)

    assert mock_search.call_count == 2 + len(options)


# ---------------------------------------------------------------------------
# run() — deduplication
# ---------------------------------------------------------------------------

def test_run_deduplicates_by_url():
    """run() returns each URL only once even if it appears in multiple queries."""
    duplicate = _result("Shared Article", "https://shared.com", 0.8)
    unique = _result("Unique Article", "https://unique.com", 0.5)

    # Both queries return the same duplicate URL, plus a unique result on query 2.
    def side_effect(query, max_results=5):
        if "strategy" in query:
            return [duplicate, unique]
        return [duplicate]

    with patch("app.agents.ingestion.sub_agents.web_scraping_sub_agent.search",
               side_effect=side_effect):
        results = run(entity="ACME", capability="LLM")

    urls = [r.url for r in results]
    assert urls.count("https://shared.com") == 1
    assert len(results) == 2


# ---------------------------------------------------------------------------
# run() — ordering
# ---------------------------------------------------------------------------

def test_run_sorts_results_by_score_descending():
    """run() returns results ordered highest score first."""
    low = _result("Low", "https://low.com", 0.3)
    high = _result("High", "https://high.com", 0.95)
    mid = _result("Mid", "https://mid.com", 0.6)

    def side_effect(query, max_results=5):
        if "strategy" in query:
            return [mid]
        return [low, high]

    with patch("app.agents.ingestion.sub_agents.web_scraping_sub_agent.search",
               side_effect=side_effect):
        results = run(entity="ACME", capability="LLM")

    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


# ---------------------------------------------------------------------------
# run() — empty results
# ---------------------------------------------------------------------------

def test_run_returns_empty_list_when_search_returns_nothing():
    """run() returns [] when all search queries return no results."""
    with patch("app.agents.ingestion.sub_agents.web_scraping_sub_agent.search",
               return_value=[]):
        results = run(entity="Unknown Corp", capability="obscure capability")

    assert results == []
