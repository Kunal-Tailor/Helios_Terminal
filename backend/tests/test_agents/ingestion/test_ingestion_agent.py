"""
Unit and integration tests for app.agents.ingestion.ingestion_agent.

UNIT TESTS (mock all sub-agents at their run() boundary)
  - run() returns IngestionContext
  - run() passes entity/capability/options correctly to each sub-agent
  - run() calls web-scraping and structured-source sub-agents (both called)
  - run() passes their combined outputs to context-synthesis sub-agent
  - run() works when options=None (defaults to [])
  - run() works when options=[] (empty list)

INTEGRATION TESTS (mock at lowest layer: web_search, httpx, LLM client)
  - Full pipeline produces IngestionContext with correct fields
  - Full pipeline tolerates all retrieval returning empty results
  - Full pipeline degrades gracefully when LLM call fails
"""

from unittest.mock import MagicMock, patch

import pytest

from app.agents.ingestion.ingestion_agent import run
from app.agents.ingestion.sub_agents.context_synthesis_sub_agent import IngestionContext
from app.agents.ingestion.sub_agents.structured_source_sub_agent import StructuredSourceResult
from app.retrieval.web_search import SearchResult


# ---------------------------------------------------------------------------
# Shared mock data
# ---------------------------------------------------------------------------

_ENTITY = "ACME Corp"
_CAPABILITY = "edge inference LLM"
_OPTIONS = ["build in-house", "license from vendor"]

_MOCK_WEB_RESULTS = [
    SearchResult(title="Article", url="https://a.com", content="content", score=0.9),
]
_MOCK_STRUCT_RESULTS = [
    StructuredSourceResult(
        source_name="Hugging Face Hub",
        title="deepseek-ai/model",
        content="Downloads: 100k",
        url="https://hf.co/deepseek",
    ),
]
_MOCK_CONTEXT = IngestionContext(
    entity=_ENTITY,
    capability=_CAPABILITY,
    options=_OPTIONS,
    context_summary="Synthesised context.",
    key_facts=["Fact 1", "Fact 2"],
    sources=["https://a.com", "https://hf.co/deepseek"],
)

_WELL_FORMED_LLM_RESPONSE = """\
SUMMARY:
ACME Corp is evaluating edge inference LLMs. Open-weight models are available.

KEY FACTS:
- DeepSeek models available on Hugging Face under open licence.
- ACME Corp has no prior AI procurement on record.
- Cloud inference costs declining quarter-on-quarter.
"""


# ---------------------------------------------------------------------------
# Unit tests — sub-agent run() functions are mocked
# ---------------------------------------------------------------------------

_WEB_MOCK_PATH = "app.agents.ingestion.ingestion_agent.web_scraping_sub_agent.run"
_STRUCT_MOCK_PATH = "app.agents.ingestion.ingestion_agent.structured_source_sub_agent.run"
_SYNTH_MOCK_PATH = "app.agents.ingestion.ingestion_agent.context_synthesis_sub_agent.run"


def test_unit_run_returns_ingestion_context():
    """run() returns an IngestionContext instance."""
    with patch(_WEB_MOCK_PATH, return_value=_MOCK_WEB_RESULTS), \
         patch(_STRUCT_MOCK_PATH, return_value=_MOCK_STRUCT_RESULTS), \
         patch(_SYNTH_MOCK_PATH, return_value=_MOCK_CONTEXT):
        result = run(_ENTITY, _CAPABILITY, _OPTIONS)

    assert isinstance(result, IngestionContext)


def test_unit_run_calls_web_scraping_sub_agent():
    """run() calls the web-scraping sub-agent with entity, capability, options."""
    with patch(_WEB_MOCK_PATH, return_value=_MOCK_WEB_RESULTS) as mock_web, \
         patch(_STRUCT_MOCK_PATH, return_value=_MOCK_STRUCT_RESULTS), \
         patch(_SYNTH_MOCK_PATH, return_value=_MOCK_CONTEXT):
        run(_ENTITY, _CAPABILITY, _OPTIONS)

    mock_web.assert_called_once_with(
        entity=_ENTITY, capability=_CAPABILITY, options=_OPTIONS
    )


def test_unit_run_calls_structured_source_sub_agent():
    """run() calls the structured-source sub-agent with entity and capability."""
    with patch(_WEB_MOCK_PATH, return_value=_MOCK_WEB_RESULTS), \
         patch(_STRUCT_MOCK_PATH, return_value=_MOCK_STRUCT_RESULTS) as mock_struct, \
         patch(_SYNTH_MOCK_PATH, return_value=_MOCK_CONTEXT):
        run(_ENTITY, _CAPABILITY, _OPTIONS)

    mock_struct.assert_called_once_with(entity=_ENTITY, capability=_CAPABILITY)


def test_unit_run_passes_merged_results_to_synthesis():
    """run() passes the combined web + structured results to context synthesis."""
    with patch(_WEB_MOCK_PATH, return_value=_MOCK_WEB_RESULTS), \
         patch(_STRUCT_MOCK_PATH, return_value=_MOCK_STRUCT_RESULTS), \
         patch(_SYNTH_MOCK_PATH, return_value=_MOCK_CONTEXT) as mock_synth:
        run(_ENTITY, _CAPABILITY, _OPTIONS)

    mock_synth.assert_called_once_with(
        entity=_ENTITY,
        capability=_CAPABILITY,
        options=_OPTIONS,
        web_results=_MOCK_WEB_RESULTS,
        structured_results=_MOCK_STRUCT_RESULTS,
    )


def test_unit_run_options_none_defaults_to_empty_list():
    """run() with options=None passes [] to sub-agents."""
    with patch(_WEB_MOCK_PATH, return_value=[]) as mock_web, \
         patch(_STRUCT_MOCK_PATH, return_value=[]), \
         patch(_SYNTH_MOCK_PATH, return_value=_MOCK_CONTEXT):
        run(_ENTITY, _CAPABILITY, options=None)

    mock_web.assert_called_once_with(
        entity=_ENTITY, capability=_CAPABILITY, options=[]
    )


def test_unit_run_returns_synthesis_output_directly():
    """run() returns exactly what the context-synthesis sub-agent returns."""
    with patch(_WEB_MOCK_PATH, return_value=_MOCK_WEB_RESULTS), \
         patch(_STRUCT_MOCK_PATH, return_value=_MOCK_STRUCT_RESULTS), \
         patch(_SYNTH_MOCK_PATH, return_value=_MOCK_CONTEXT):
        result = run(_ENTITY, _CAPABILITY, _OPTIONS)

    assert result is _MOCK_CONTEXT


# ---------------------------------------------------------------------------
# Integration tests — mocked at the lowest layer (web_search, httpx, LLM)
# Real sub-agent logic executes end-to-end through the parent
# ---------------------------------------------------------------------------

_SEARCH_MOCK = "app.agents.ingestion.sub_agents.web_scraping_sub_agent.search"
_HF_MOCK = "app.agents.ingestion.sub_agents.structured_source_sub_agent.httpx.get"
_WS_MOCK = "app.agents.ingestion.sub_agents.structured_source_sub_agent.web_search"
_LLM_MOCK = "app.agents.ingestion.sub_agents.context_synthesis_sub_agent.complete"

_MOCK_SEARCH_RESULTS = [
    SearchResult(
        title="Inference article",
        url="https://inference.com",
        content="Edge inference for LLMs is growing.",
        score=0.88,
    ),
]

def _hf_response():
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    mock.json.return_value = [
        {"modelId": "deepseek-ai/model", "pipeline_tag": "text-generation", "downloads": 50000}
    ]
    return mock


def test_integration_full_pipeline_returns_ingestion_context():
    """Integration: full pipeline (all real sub-agent logic) returns IngestionContext."""
    with patch(_SEARCH_MOCK, return_value=_MOCK_SEARCH_RESULTS), \
         patch(_HF_MOCK, return_value=_hf_response()), \
         patch(_WS_MOCK, return_value=_MOCK_SEARCH_RESULTS), \
         patch(_LLM_MOCK, return_value=_WELL_FORMED_LLM_RESPONSE):
        result = run(_ENTITY, _CAPABILITY, _OPTIONS)

    assert isinstance(result, IngestionContext)
    assert result.entity == _ENTITY
    assert result.capability == _CAPABILITY


def test_integration_context_has_sources_from_retrieval():
    """Integration: IngestionContext sources include URLs from web and HF results."""
    with patch(_SEARCH_MOCK, return_value=_MOCK_SEARCH_RESULTS), \
         patch(_HF_MOCK, return_value=_hf_response()), \
         patch(_WS_MOCK, return_value=_MOCK_SEARCH_RESULTS), \
         patch(_LLM_MOCK, return_value=_WELL_FORMED_LLM_RESPONSE):
        result = run(_ENTITY, _CAPABILITY, _OPTIONS)

    assert len(result.sources) > 0


def test_integration_pipeline_tolerates_empty_retrieval():
    """Integration: pipeline completes even when all retrieval returns nothing."""
    with patch(_SEARCH_MOCK, return_value=[]), \
         patch(_HF_MOCK, side_effect=Exception("Network error")), \
         patch(_WS_MOCK, return_value=[]), \
         patch(_LLM_MOCK, return_value=_WELL_FORMED_LLM_RESPONSE):
        result = run(_ENTITY, _CAPABILITY, _OPTIONS)

    assert isinstance(result, IngestionContext)
    assert result.sources == []


def test_integration_pipeline_degrades_when_llm_fails():
    """Integration: pipeline returns IngestionContext with empty summary if LLM fails."""
    with patch(_SEARCH_MOCK, return_value=_MOCK_SEARCH_RESULTS), \
         patch(_HF_MOCK, return_value=_hf_response()), \
         patch(_WS_MOCK, return_value=_MOCK_SEARCH_RESULTS), \
         patch(_LLM_MOCK, side_effect=RuntimeError("DEEPSEEK_API_KEY not set")):
        result = run(_ENTITY, _CAPABILITY, _OPTIONS)

    assert isinstance(result, IngestionContext)
    assert result.context_summary == ""
    assert result.key_facts == []
    # Sources still populated from retrieval
    assert len(result.sources) > 0
