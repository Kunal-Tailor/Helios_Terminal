"""
Unit tests for app.agents.orchestrator.sub_agents.verdict_synthesis_sub_agent.

All LLM calls are mocked — no network access, no API key required.

Tests cover:
  - run() returns a VerdictSynthesis object
  - run() returns empty VerdictSynthesis for empty input (no LLM call)
  - run() returns empty VerdictSynthesis when the LLM call raises (graceful degradation)
  - run() returns empty VerdictSynthesis when the response is unparseable
  - run() calls the LLM exactly once
  - _parse_response() parses recommended path, summary, recommendations, and stances
  - _parse_response() handles an empty string
  - _build_prompt() includes entity, capability, narrative, and path comparisons
"""

from unittest.mock import patch

import pytest

from app.agents.dependency_diagnosis.dependency_diagnosis_agent import DependencyDiagnosis
from app.agents.orchestrator.sub_agents.cross_path_comparison_sub_agent import (
    CrossPathComparison,
    PathComparison,
)
from app.agents.orchestrator.sub_agents.verdict_synthesis_sub_agent import (
    VerdictSynthesis,
    _build_prompt,
    _parse_response,
    run,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_COMPARISON = CrossPathComparison(
    comparative_narrative="Building custom LLM offers maximum control but high lock-in. Licensing open-weight models provides optimal balance.",
    path_comparisons=[
        PathComparison(
            scenario_name="Build custom LLM in-house",
            lock_in_count=1,
            max_severity_score=8.5,
            key_tradeoffs=["High capex vs sovereign control"],
            path_summary="Highest technical risk.",
        ),
        PathComparison(
            scenario_name="License open-weight model",
            lock_in_count=1,
            max_severity_score=4.5,
            key_tradeoffs=["Upstream reliance vs low capex"],
            path_summary="Optimal risk profile.",
        ),
    ],
)

_DIAGNOSES = [
    DependencyDiagnosis(scenario_name="Build custom LLM in-house"),
    DependencyDiagnosis(scenario_name="License open-weight model"),
]

_WELL_FORMED_RESPONSE = """\
RECOMMENDED PATH: License open-weight model
VERDICT SUMMARY:
ACME Corp should proceed with licensing an open-weight model (e.g. DeepSeek) as its primary sourcing path. This path minimizes initial capital expenditure and hardware lock-in while preserving fine-tuning control.

RECOMMENDATIONS:
- Establish strict model weight version pinning.
- Conduct quarterly open-source license audits.
- Maintain a secondary cloud fallback endpoint.

PATH STANCES:
- Build custom LLM in-house: High Risk - avoid due to custom hardware entanglement
- License open-weight model: Recommended - best balance of control and cost efficiency
"""

_LLM_PATH = "app.agents.orchestrator.sub_agents.verdict_synthesis_sub_agent.complete"


# ---------------------------------------------------------------------------
# run() — return type and basic behaviour
# ---------------------------------------------------------------------------

def test_run_returns_verdict_synthesis():
    """run() returns a VerdictSynthesis instance."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE):
        result = run(_COMPARISON, _DIAGNOSES, "ACME Corp", "edge LLM")

    assert isinstance(result, VerdictSynthesis)
    assert result.recommended_path == "License open-weight model"
    assert len(result.key_recommendations) == 3
    assert len(result.path_stances) == 2


def test_run_calls_llm_once():
    """run() makes exactly one LLM call."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE) as mock_llm:
        run(_COMPARISON, _DIAGNOSES, "ACME Corp", "edge LLM")

    assert mock_llm.call_count == 1


# ---------------------------------------------------------------------------
# run() — graceful degradation
# ---------------------------------------------------------------------------

def test_run_returns_empty_for_empty_inputs():
    """run() returns empty VerdictSynthesis immediately when inputs are empty."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE) as mock_llm:
        result = run(CrossPathComparison(), [], "", "")

    assert result == VerdictSynthesis()
    mock_llm.assert_not_called()


def test_run_returns_empty_when_llm_raises():
    """run() returns empty VerdictSynthesis when the LLM call raises an exception."""
    with patch(_LLM_PATH, side_effect=RuntimeError("LLM failure")):
        result = run(_COMPARISON, _DIAGNOSES)

    assert result == VerdictSynthesis()


def test_run_returns_empty_when_response_unparseable():
    """run() returns empty VerdictSynthesis when the LLM response has no valid fields."""
    with patch(_LLM_PATH, return_value="Plain text response without headers."):
        result = run(_COMPARISON, _DIAGNOSES)

    assert result.recommended_path == ""
    assert result.key_recommendations == []


# ---------------------------------------------------------------------------
# _parse_response() — field mapping
# ---------------------------------------------------------------------------

def test_parse_response_maps_all_fields_correctly():
    """_parse_response() correctly populates VerdictSynthesis dataclass fields."""
    verdict = _parse_response(_WELL_FORMED_RESPONSE)

    assert verdict.recommended_path == "License open-weight model"
    assert "ACME Corp should proceed" in verdict.verdict_summary
    assert "Establish strict model weight version pinning." in verdict.key_recommendations
    assert "License open-weight model" in verdict.path_stances
    assert "Recommended" in verdict.path_stances["License open-weight model"]


def test_parse_response_returns_empty_for_empty_string():
    """_parse_response() returns empty VerdictSynthesis for an empty response string."""
    res = _parse_response("")
    assert res.recommended_path == ""
    assert res.verdict_summary == ""
    assert res.key_recommendations == []
    assert res.path_stances == {}


# ---------------------------------------------------------------------------
# _build_prompt()
# ---------------------------------------------------------------------------

def test_build_prompt_includes_entity_narrative_and_tradeoffs():
    """_build_prompt() includes entity, capability, narrative, and tradeoffs."""
    prompt = _build_prompt(_COMPARISON, _DIAGNOSES, "ACME Corp", "edge LLM")
    assert "ACME Corp" in prompt
    assert "edge LLM" in prompt
    assert "Building custom LLM offers maximum control" in prompt
    assert "High capex vs sovereign control" in prompt
