"""
Unit tests for app.agents.orchestrator.sub_agents.explanation_trail_sub_agent.

All LLM calls are mocked — no network access, no API key required.

Tests cover:
  - run() returns an ExplanationTrail object
  - run() returns empty ExplanationTrail (preserving sources) for empty inputs (no LLM call)
  - run() returns empty ExplanationTrail when the LLM call raises (graceful degradation)
  - run() returns empty ExplanationTrail when the response is unparseable
  - run() calls the LLM exactly once
  - _parse_response() parses summary and AuditStep blocks correctly
  - _parse_response() handles an empty string
  - _build_prompt() includes verdict recommendation, diagnoses, and source URLs
"""

from unittest.mock import patch

import pytest

from app.agents.dependency_diagnosis.dependency_diagnosis_agent import DependencyDiagnosis
from app.agents.dependency_diagnosis.sub_agents.lock_in_identification_sub_agent import LockInDependency
from app.agents.orchestrator.sub_agents.explanation_trail_sub_agent import (
    AuditStep,
    ExplanationTrail,
    _build_prompt,
    _parse_response,
    run,
)
from app.agents.orchestrator.sub_agents.verdict_synthesis_sub_agent import VerdictSynthesis

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_DIAGNOSES = [
    DependencyDiagnosis(
        scenario_name="License open-weight model",
        dependencies=[
            LockInDependency(
                scenario_name="License open-weight model",
                dependency_name="Upstream Weight Schema Dependency",
                layer_name="Model Weights",
            )
        ],
    )
]

_VERDICT = VerdictSynthesis(
    recommended_path="License open-weight model",
    verdict_summary="Licensing open-weight model is recommended due to balanced risk.",
    key_recommendations=["Pin model version."],
)

_SOURCES = ["https://bis.doc.gov/entities", "https://huggingface.co/deepseek-ai"]

_WELL_FORMED_RESPONSE = """\
TRAIL SUMMARY:
The evaluation commenced with web search and Hugging Face Hub ingestion confirming model availability. Stack mapping highlighted Model Weights as critical. Licensing open-weight models was recommended over custom training due to lower hardware lock-in.

---
AUDIT STEP: Ingestion
CLAIM: Open-weight model weights are available under non-restrictive license terms.
EVIDENCE: Ingested source https://huggingface.co/deepseek-ai confirmed public availability.
---
AUDIT STEP: Verdict
CLAIM: Licensing open-weight model is the recommended procurement path.
EVIDENCE: Comparative diagnosis showed significantly lower hardware lock-in compared to custom in-house training.
---
"""

_LLM_PATH = "app.agents.orchestrator.sub_agents.explanation_trail_sub_agent.complete"


# ---------------------------------------------------------------------------
# run() — return type and basic behaviour
# ---------------------------------------------------------------------------

def test_run_returns_explanation_trail():
    """run() returns an ExplanationTrail instance."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE):
        result = run(_DIAGNOSES, _VERDICT, _SOURCES)

    assert isinstance(result, ExplanationTrail)
    assert len(result.steps) == 2
    assert result.sources == _SOURCES
    assert "The evaluation commenced" in result.summary


def test_run_calls_llm_once():
    """run() makes exactly one LLM call."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE) as mock_llm:
        run(_DIAGNOSES, _VERDICT, _SOURCES)

    assert mock_llm.call_count == 1


# ---------------------------------------------------------------------------
# run() — graceful degradation
# ---------------------------------------------------------------------------

def test_run_returns_empty_for_empty_inputs():
    """run() returns empty ExplanationTrail preserving sources when inputs are empty."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE) as mock_llm:
        result = run([], None, _SOURCES)

    assert result.summary == ""
    assert result.steps == []
    assert result.sources == _SOURCES
    mock_llm.assert_not_called()


def test_run_returns_empty_when_llm_raises():
    """run() returns empty ExplanationTrail preserving sources when LLM raises."""
    with patch(_LLM_PATH, side_effect=RuntimeError("LLM failure")):
        result = run(_DIAGNOSES, _VERDICT, _SOURCES)

    assert result.summary == ""
    assert result.steps == []
    assert result.sources == _SOURCES


def test_run_returns_empty_when_response_unparseable():
    """run() returns empty ExplanationTrail when response has no audit step blocks."""
    with patch(_LLM_PATH, return_value="Unstructured text without audit steps."):
        result = run(_DIAGNOSES, _VERDICT, _SOURCES)

    assert result.steps == []


# ---------------------------------------------------------------------------
# _parse_response() — field mapping
# ---------------------------------------------------------------------------

def test_parse_response_maps_steps_and_summary_correctly():
    """_parse_response() correctly populates summary and AuditStep objects."""
    trail = _parse_response(_WELL_FORMED_RESPONSE)

    assert "The evaluation commenced" in trail.summary
    assert len(trail.steps) == 2

    first = trail.steps[0]
    assert first.stage == "Ingestion"
    assert "Open-weight model weights" in first.claim
    assert "huggingface.co" in first.evidence


def test_parse_response_returns_empty_for_empty_string():
    """_parse_response() returns empty ExplanationTrail for an empty response string."""
    res = _parse_response("")
    assert res.summary == ""
    assert res.steps == []


# ---------------------------------------------------------------------------
# _build_prompt()
# ---------------------------------------------------------------------------

def test_build_prompt_includes_recommendation_and_sources():
    """_build_prompt() includes verdict recommendation and source URLs."""
    prompt = _build_prompt(_DIAGNOSES, _VERDICT, _SOURCES)
    assert "License open-weight model" in prompt
    assert "https://huggingface.co/deepseek-ai" in prompt
