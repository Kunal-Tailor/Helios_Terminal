"""
Unit tests for app.agents.ingestion.sub_agents.structured_source_sub_agent.

All network calls are mocked — no HTTP requests, no Tavily API key required.
Mocks cover:
  - httpx.get  (Hugging Face Hub REST API)
  - app.retrieval.web_search.search  (BIS, TPDi, market-share queries)

Tests cover:
  - run() returns a list of StructuredSourceResult objects
  - run() queries all four sources
  - HF Hub results are correctly mapped from the JSON response
  - Web-search-backed sources are correctly mapped from SearchResult
  - Graceful degradation: a failing source returns [] and does not abort run()
  - StructuredSourceResult fields are populated correctly
"""

from unittest.mock import MagicMock, patch

import pytest

from app.agents.ingestion.sub_agents.structured_source_sub_agent import (
    StructuredSourceResult,
    _query_bis_entity_list,
    _query_hf_hub,
    _query_market_share_reports,
    _query_tpdi,
    run,
)
from app.retrieval.web_search import SearchResult

# ---------------------------------------------------------------------------
# Shared fixtures / helpers
# ---------------------------------------------------------------------------

_MOCK_HF_MODELS = [
    {
        "modelId": "deepseek-ai/deepseek-coder",
        "pipeline_tag": "text-generation",
        "downloads": 150000,
    },
    {
        "modelId": "mistralai/Mistral-7B",
        "pipeline_tag": "text-generation",
        "downloads": 320000,
    },
]

_MOCK_SEARCH_RESULTS = [
    SearchResult(
        title="BIS Entity List Entry",
        url="https://bis.doc.gov/entities/1",
        content="Entity XYZ appears on the US BIS Entity List.",
        score=0.88,
    ),
]


def _make_httpx_response(json_data: list) -> MagicMock:
    """Return a mock httpx.Response that raises on bad status and returns json_data."""
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = json_data
    return mock_response


# ---------------------------------------------------------------------------
# run() — top-level behaviour
# ---------------------------------------------------------------------------

def test_run_returns_list_of_structured_source_results():
    """run() returns a list whose items are all StructuredSourceResult."""
    with patch("app.agents.ingestion.sub_agents.structured_source_sub_agent.httpx.get",
               return_value=_make_httpx_response(_MOCK_HF_MODELS)):
        with patch("app.agents.ingestion.sub_agents.structured_source_sub_agent.web_search",
                   return_value=_MOCK_SEARCH_RESULTS):
            results = run(entity="ACME Corp", capability="edge inference LLM")

    assert isinstance(results, list)
    assert all(isinstance(r, StructuredSourceResult) for r in results)


def test_run_queries_all_four_sources():
    """run() produces results from all four source helpers when they succeed."""
    with patch("app.agents.ingestion.sub_agents.structured_source_sub_agent.httpx.get",
               return_value=_make_httpx_response(_MOCK_HF_MODELS)):
        with patch("app.agents.ingestion.sub_agents.structured_source_sub_agent.web_search",
                   return_value=_MOCK_SEARCH_RESULTS) as mock_ws:
            results = run(entity="ACME Corp", capability="edge inference LLM")

    # web_search is called once per non-HF source (BIS + TPDi + market-share = 3 calls)
    assert mock_ws.call_count == 3
    source_names = {r.source_name for r in results}
    assert "Hugging Face Hub" in source_names


def test_run_returns_nonempty_results_when_sources_have_data():
    """run() returns results from both HF Hub and web-search-backed sources."""
    with patch("app.agents.ingestion.sub_agents.structured_source_sub_agent.httpx.get",
               return_value=_make_httpx_response(_MOCK_HF_MODELS)):
        with patch("app.agents.ingestion.sub_agents.structured_source_sub_agent.web_search",
                   return_value=_MOCK_SEARCH_RESULTS):
            results = run(entity="ACME Corp", capability="edge inference LLM")

    assert len(results) > 0


# ---------------------------------------------------------------------------
# _query_hf_hub()
# ---------------------------------------------------------------------------

def test_query_hf_hub_maps_fields_correctly():
    """_query_hf_hub() maps HF API response fields to StructuredSourceResult."""
    with patch("app.agents.ingestion.sub_agents.structured_source_sub_agent.httpx.get",
               return_value=_make_httpx_response(_MOCK_HF_MODELS)):
        results = _query_hf_hub("code generation")

    assert len(results) == 2
    first = results[0]
    assert first.source_name == "Hugging Face Hub"
    assert first.title == "deepseek-ai/deepseek-coder"
    assert "deepseek-ai/deepseek-coder" in first.url
    assert first.raw_score == 150000.0


def test_query_hf_hub_returns_empty_on_http_error():
    """_query_hf_hub() returns [] when the HF API call raises an exception."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("HTTP 503")

    with patch("app.agents.ingestion.sub_agents.structured_source_sub_agent.httpx.get",
               return_value=mock_response):
        results = _query_hf_hub("edge inference")

    assert results == []


def test_query_hf_hub_returns_empty_on_network_error():
    """_query_hf_hub() returns [] when httpx.get itself raises (e.g. timeout)."""
    with patch("app.agents.ingestion.sub_agents.structured_source_sub_agent.httpx.get",
               side_effect=Exception("Connection timeout")):
        results = _query_hf_hub("edge inference")

    assert results == []


# ---------------------------------------------------------------------------
# Web-search-backed sources (BIS / TPDi / market-share)
# ---------------------------------------------------------------------------

def test_query_bis_entity_list_maps_fields_correctly():
    """_query_bis_entity_list() wraps SearchResults as StructuredSourceResults."""
    with patch("app.agents.ingestion.sub_agents.structured_source_sub_agent.web_search",
               return_value=_MOCK_SEARCH_RESULTS):
        results = _query_bis_entity_list("ACME Corp")

    assert len(results) == 1
    assert results[0].source_name == "BIS Entity List"
    assert results[0].url == "https://bis.doc.gov/entities/1"


def test_query_bis_returns_empty_on_search_error():
    """_query_bis_entity_list() returns [] when web_search raises."""
    with patch("app.agents.ingestion.sub_agents.structured_source_sub_agent.web_search",
               side_effect=Exception("API error")):
        results = _query_bis_entity_list("ACME Corp")

    assert results == []


def test_query_tpdi_maps_source_name():
    """_query_tpdi() labels results with the correct source_name."""
    with patch("app.agents.ingestion.sub_agents.structured_source_sub_agent.web_search",
               return_value=_MOCK_SEARCH_RESULTS):
        results = _query_tpdi("ACME Corp", "edge LLM")

    assert all(r.source_name == "TPDi / Procurement Intelligence" for r in results)


def test_query_market_share_reports_maps_source_name():
    """_query_market_share_reports() labels results correctly."""
    with patch("app.agents.ingestion.sub_agents.structured_source_sub_agent.web_search",
               return_value=_MOCK_SEARCH_RESULTS):
        results = _query_market_share_reports("edge inference LLM")

    assert all(r.source_name == "Market Share Reports" for r in results)


# ---------------------------------------------------------------------------
# Graceful degradation
# ---------------------------------------------------------------------------

def test_run_continues_when_hf_hub_fails():
    """run() returns non-HF results even when the HF Hub call fails."""
    with patch("app.agents.ingestion.sub_agents.structured_source_sub_agent.httpx.get",
               side_effect=Exception("Network down")):
        with patch("app.agents.ingestion.sub_agents.structured_source_sub_agent.web_search",
                   return_value=_MOCK_SEARCH_RESULTS):
            results = run(entity="ACME Corp", capability="edge inference LLM")

    # HF Hub failed, but web-search-backed sources still returned results
    assert len(results) > 0
    assert all(r.source_name != "Hugging Face Hub" for r in results)


def test_run_returns_empty_when_all_sources_fail():
    """run() returns [] gracefully when every source raises."""
    with patch("app.agents.ingestion.sub_agents.structured_source_sub_agent.httpx.get",
               side_effect=Exception("Network down")):
        with patch("app.agents.ingestion.sub_agents.structured_source_sub_agent.web_search",
                   side_effect=Exception("Search down")):
            results = run(entity="ACME Corp", capability="edge inference LLM")

    assert results == []
