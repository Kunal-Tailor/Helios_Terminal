"""
Unit tests for app.agents.ingestion.sub_agents.context_synthesis_sub_agent.

All LLM calls are mocked — no network access, no API key required.

Tests cover:
  - run() returns an IngestionContext
  - run() populates entity/capability/options from inputs
  - run() collects sources from both web and structured results
  - run() deduplicates sources across the two result sets
  - run() calls the LLM once with a non-empty prompt
  - run() correctly parses a well-formed LLM response
  - run() degrades gracefully when the LLM call fails
  - _parse_llm_response() handles well-formed and malformed responses
  - _collect_sources() deduplicates across both result sets
  - _build_prompt() includes entity, capability, and options
"""

from unittest.mock import patch

import pytest

from app.agents.ingestion.sub_agents.context_synthesis_sub_agent import (
    IngestionContext,
    _build_prompt,
    _collect_sources,
    _parse_llm_response,
    run,
)
from app.agents.ingestion.sub_agents.structured_source_sub_agent import (
    StructuredSourceResult,
)
from app.retrieval.web_search import SearchResult


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

def _web_result(title: str, url: str, content: str = "web content") -> SearchResult:
    return SearchResult(title=title, url=url, content=content, score=0.8)


def _struct_result(source: str, title: str, url: str, content: str = "struct content") -> StructuredSourceResult:
    return StructuredSourceResult(
        source_name=source, title=title, content=content, url=url
    )


_WELL_FORMED_LLM_RESPONSE = """\
SUMMARY:
The entity ACME Corp is evaluating edge inference LLMs. Sources indicate strong
availability of open-weight models on Hugging Face and limited vendor lock-in risk
for the build-in-house path.

KEY FACTS:
- ACME Corp has no prior AI procurement contracts on record.
- DeepSeek and Mistral models are available under open licences on Hugging Face.
- Cloud inference costs for the capability are declining quarter-on-quarter.
"""

_ENTITY = "ACME Corp"
_CAPABILITY = "edge inference LLM"
_OPTIONS = ["build in-house", "license from vendor"]

_WEB_RESULTS = [
    _web_result("Article A", "https://a.com", "Content A"),
    _web_result("Article B", "https://b.com", "Content B"),
]
_STRUCT_RESULTS = [
    _struct_result("Hugging Face Hub", "deepseek-ai/model", "https://hf.co/deepseek"),
    _struct_result("BIS Entity List", "ACME Corp", "https://bis.doc.gov/acme"),
]


# ---------------------------------------------------------------------------
# run() — return type and field population
# ---------------------------------------------------------------------------

def test_run_returns_ingestion_context():
    """run() returns an IngestionContext instance."""
    with patch("app.agents.ingestion.sub_agents.context_synthesis_sub_agent.call_llm_with_fallback",
               return_value=_WELL_FORMED_LLM_RESPONSE):
        result = run(_ENTITY, _CAPABILITY, _OPTIONS, _WEB_RESULTS, _STRUCT_RESULTS)

    assert isinstance(result, IngestionContext)


def test_run_populates_entity_capability_options():
    """run() copies entity, capability, options through to IngestionContext."""
    with patch("app.agents.ingestion.sub_agents.context_synthesis_sub_agent.call_llm_with_fallback",
               return_value=_WELL_FORMED_LLM_RESPONSE):
        result = run(_ENTITY, _CAPABILITY, _OPTIONS, _WEB_RESULTS, _STRUCT_RESULTS)

    assert result.entity == _ENTITY
    assert result.capability == _CAPABILITY
    assert result.options == _OPTIONS


def test_run_populates_context_summary():
    """run() populates context_summary from the LLM response."""
    with patch("app.agents.ingestion.sub_agents.context_synthesis_sub_agent.call_llm_with_fallback",
               return_value=_WELL_FORMED_LLM_RESPONSE):
        result = run(_ENTITY, _CAPABILITY, _OPTIONS, _WEB_RESULTS, _STRUCT_RESULTS)

    assert len(result.context_summary) > 0
    assert "ACME Corp" in result.context_summary


def test_run_populates_key_facts():
    """run() populates key_facts as a non-empty list of strings."""
    with patch("app.agents.ingestion.sub_agents.context_synthesis_sub_agent.call_llm_with_fallback",
               return_value=_WELL_FORMED_LLM_RESPONSE):
        result = run(_ENTITY, _CAPABILITY, _OPTIONS, _WEB_RESULTS, _STRUCT_RESULTS)

    assert isinstance(result.key_facts, list)
    assert len(result.key_facts) >= 3


def test_run_collects_sources_from_both_result_sets():
    """run() includes URLs from both web and structured results."""
    with patch("app.agents.ingestion.sub_agents.context_synthesis_sub_agent.call_llm_with_fallback",
               return_value=_WELL_FORMED_LLM_RESPONSE):
        result = run(_ENTITY, _CAPABILITY, _OPTIONS, _WEB_RESULTS, _STRUCT_RESULTS)

    assert "https://a.com" in result.sources
    assert "https://hf.co/deepseek" in result.sources


def test_run_deduplicates_sources():
    """run() does not repeat a URL that appears in both result sets."""
    shared_url = "https://shared.com"
    web = [_web_result("Shared", shared_url)]
    struct = [_struct_result("BIS", "Entity", shared_url)]

    with patch("app.agents.ingestion.sub_agents.context_synthesis_sub_agent.call_llm_with_fallback",
               return_value=_WELL_FORMED_LLM_RESPONSE):
        result = run(_ENTITY, _CAPABILITY, _OPTIONS, web, struct)

    assert result.sources.count(shared_url) == 1


def test_run_calls_llm_once():
    """run() makes exactly one call to the LLM."""
    with patch("app.agents.ingestion.sub_agents.context_synthesis_sub_agent.call_llm_with_fallback",
               return_value=_WELL_FORMED_LLM_RESPONSE) as mock_llm:
        run(_ENTITY, _CAPABILITY, _OPTIONS, _WEB_RESULTS, _STRUCT_RESULTS)

    assert mock_llm.call_count == 1


# ---------------------------------------------------------------------------
# run() — graceful degradation
# ---------------------------------------------------------------------------

def test_run_degrades_gracefully_when_llm_fails():
    """run() returns IngestionContext with empty summary/facts if LLM raises."""
    with patch("app.agents.ingestion.sub_agents.context_synthesis_sub_agent.call_llm_with_fallback",
               side_effect=RuntimeError("DEEPSEEK_API_KEY is not set.")):
        result = run(_ENTITY, _CAPABILITY, _OPTIONS, _WEB_RESULTS, _STRUCT_RESULTS)

    assert isinstance(result, IngestionContext)
    assert result.context_summary == ""
    assert result.key_facts == []
    # Sources are still populated from the input results
    assert len(result.sources) > 0


# ---------------------------------------------------------------------------
# _parse_llm_response()
# ---------------------------------------------------------------------------

def test_parse_llm_response_extracts_summary():
    """_parse_llm_response() returns the summary block correctly."""
    summary, _ = _parse_llm_response(_WELL_FORMED_LLM_RESPONSE)
    assert "ACME Corp" in summary
    assert "SUMMARY:" not in summary


def test_parse_llm_response_extracts_key_facts():
    """_parse_llm_response() returns each bullet as a separate string."""
    _, facts = _parse_llm_response(_WELL_FORMED_LLM_RESPONSE)
    assert len(facts) == 3
    assert all(isinstance(f, str) and len(f) > 0 for f in facts)


def test_parse_llm_response_handles_malformed_response():
    """_parse_llm_response() falls back to full text as summary if format missing."""
    malformed = "This is just a plain text response with no structure."
    summary, facts = _parse_llm_response(malformed)
    assert summary == malformed
    assert facts == []


# ---------------------------------------------------------------------------
# _collect_sources()
# ---------------------------------------------------------------------------

def test_collect_sources_returns_deduplicated_urls():
    """_collect_sources() returns each URL only once."""
    shared = "https://shared.com"
    web = [_web_result("W", shared), _web_result("W2", "https://only-web.com")]
    struct = [_struct_result("S", "T", shared), _struct_result("S2", "T2", "https://only-struct.com")]
    sources = _collect_sources(web, struct)
    assert sources.count(shared) == 1
    assert "https://only-web.com" in sources
    assert "https://only-struct.com" in sources


# ---------------------------------------------------------------------------
# _build_prompt()
# ---------------------------------------------------------------------------

def test_build_prompt_includes_entity_capability_options():
    """_build_prompt() includes all decision brief fields."""
    prompt = _build_prompt(_ENTITY, _CAPABILITY, _OPTIONS, _WEB_RESULTS, _STRUCT_RESULTS)
    assert _ENTITY in prompt
    assert _CAPABILITY in prompt
    assert "build in-house" in prompt
    assert "license from vendor" in prompt


def test_build_prompt_is_non_empty():
    """_build_prompt() returns a non-empty string."""
    prompt = _build_prompt(_ENTITY, _CAPABILITY, [], [], [])
    assert len(prompt) > 0
