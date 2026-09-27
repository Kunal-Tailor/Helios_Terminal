"""
Unit tests for app.agents.orchestrator.sub_agents.cross_path_comparison_sub_agent.

All LLM calls are mocked — no network access, no API key required.

Tests cover:
  - run() returns a CrossPathComparison object
  - run() returns empty CrossPathComparison for empty input diagnoses (no LLM call)
  - run() returns empty CrossPathComparison when the LLM call raises (graceful degradation)
  - run() returns empty CrossPathComparison when the response is unparseable
  - run() calls the LLM exactly once
  - _parse_response() parses narrative and path comparison blocks
  - _parse_response() maps PATH COMPARISON/LOCK_IN_COUNT/MAX_SEVERITY/TRADEOFFS/PATH_SUMMARY correctly
  - _parse_response() skips blocks missing PATH COMPARISON
  - _parse_response() handles an empty string
  - _build_prompt() includes scenario names, dependencies, and failure modes
"""

from unittest.mock import patch

import pytest

from app.agents.dependency_diagnosis.dependency_diagnosis_agent import DependencyDiagnosis
from app.agents.dependency_diagnosis.sub_agents.failure_mode_sub_agent import FailureMode
from app.agents.dependency_diagnosis.sub_agents.lock_in_identification_sub_agent import LockInDependency
from app.agents.dependency_diagnosis.sub_agents.severity_scoring_sub_agent import DependencySeverityScore
from app.agents.orchestrator.sub_agents.cross_path_comparison_sub_agent import (
    CrossPathComparison,
    PathComparison,
    _build_prompt,
    _parse_response,
    run,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_DIAGNOSES = [
    DependencyDiagnosis(
        scenario_name="Build custom LLM in-house",
        dependencies=[
            LockInDependency(
                scenario_name="Build custom LLM in-house",
                dependency_name="CUDA Hardware Architecture Entanglement",
                layer_name="Hardware / Compute",
                lock_in_type="Architectural Entanglement",
                description="Custom training pipeline tied to specific GPU architecture.",
            )
        ],
        failure_modes=[
            FailureMode(
                scenario_name="Build custom LLM in-house",
                dependency_name="CUDA Hardware Architecture Entanglement",
                failure_mode_title="Unmaintainable Custom CUDA Kernel Debt",
                what_breaks="Hardware migration becomes impossible.",
                trigger_condition="Next-gen GPU release.",
                time_horizon="18-24 months",
            )
        ],
        severity_scores=[
            DependencySeverityScore(
                scenario_name="Build custom LLM in-house",
                dependency_name="CUDA Hardware Architecture Entanglement",
                severity_score=8.5,
                urgency_score=7.0,
                risk_level="Critical",
                rationale="Extensive refactoring required.",
            )
        ],
    ),
    DependencyDiagnosis(
        scenario_name="License open-weight model",
        dependencies=[
            LockInDependency(
                scenario_name="License open-weight model",
                dependency_name="Upstream Weight Schema Dependency",
                layer_name="Model Weights",
                lock_in_type="Vendor Lock-in",
                description="Fine-tuning pipeline relies on upstream model architecture.",
            )
        ],
        failure_modes=[],
        severity_scores=[
            DependencySeverityScore(
                scenario_name="License open-weight model",
                dependency_name="Upstream Weight Schema Dependency",
                severity_score=4.5,
                urgency_score=3.0,
                risk_level="Low",
                rationale="Standardized model schemas.",
            )
        ],
    ),
]

_WELL_FORMED_RESPONSE = """\
OVERALL ANALYSIS:
Building custom LLM in-house offers maximum sovereign control over weights but imposes heavy architectural lock-in on specific hardware accelerators. Licensing open-weight models provides high flexibility and low upfront risk, though it creates a dependency on upstream model releases.

---
PATH COMPARISON: Build custom LLM in-house
LOCK_IN_COUNT: 1
MAX_SEVERITY: 8.5
TRADEOFFS:
- High upfront capital expenditure vs sovereign weight control
- Deep hardware entanglement vs custom kernel performance
PATH_SUMMARY: Highest technical risk path due to hardware architecture entanglement.
---
PATH COMPARISON: License open-weight model
LOCK_IN_COUNT: 1
MAX_SEVERITY: 4.5
TRADEOFFS:
- Upstream model dependence vs low initial capital outlay
PATH_SUMMARY: Lower overall risk profile with moderate operational dependency on open-source maintainers.
---
"""

_LLM_PATH = "app.agents.orchestrator.sub_agents.cross_path_comparison_sub_agent.call_llm_with_fallback"


# ---------------------------------------------------------------------------
# run() — return type and basic behaviour
# ---------------------------------------------------------------------------

def test_run_returns_cross_path_comparison():
    """run() returns a CrossPathComparison instance."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE):
        result = run(_DIAGNOSES)

    assert isinstance(result, CrossPathComparison)
    assert len(result.path_comparisons) == 2


def test_run_calls_llm_once():
    """run() makes exactly one LLM call."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE) as mock_llm:
        run(_DIAGNOSES)

    assert mock_llm.call_count == 1


# ---------------------------------------------------------------------------
# run() — graceful degradation
# ---------------------------------------------------------------------------

def test_run_returns_empty_for_empty_diagnoses():
    """run() returns empty CrossPathComparison immediately when no diagnoses are provided."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE) as mock_llm:
        result = run([])

    assert result == CrossPathComparison()
    mock_llm.assert_not_called()


def test_run_returns_empty_when_llm_raises():
    """run() returns empty CrossPathComparison when the LLM call raises an exception."""
    with patch(_LLM_PATH, side_effect=RuntimeError("LLM failure")):
        result = run(_DIAGNOSES)

    assert result == CrossPathComparison()


def test_run_returns_empty_when_response_unparseable():
    """run() returns empty CrossPathComparison when the LLM response has no valid blocks."""
    with patch(_LLM_PATH, return_value="Unstructured text with no comparison tags."):
        result = run(_DIAGNOSES)

    assert result.path_comparisons == []
    assert result.comparative_narrative == ""


# ---------------------------------------------------------------------------
# _parse_response() — field mapping
# ---------------------------------------------------------------------------

def test_parse_response_maps_narrative_and_paths_correctly():
    """_parse_response() correctly populates narrative and PathComparison fields."""
    comparison = _parse_response(_WELL_FORMED_RESPONSE, _DIAGNOSES)

    assert "Building custom LLM in-house" in comparison.comparative_narrative
    assert len(comparison.path_comparisons) == 2

    first = comparison.path_comparisons[0]
    assert first.scenario_name == "Build custom LLM in-house"
    assert first.lock_in_count == 1
    assert first.max_severity_score == 8.5
    assert len(first.key_tradeoffs) == 2
    assert "Highest technical risk path" in first.path_summary


def test_parse_response_skips_blocks_missing_path_comparison():
    """_parse_response() skips blocks missing PATH COMPARISON field."""
    malformed = """\
OVERALL ANALYSIS:
Analysis narrative.

---
LOCK_IN_COUNT: 1
MAX_SEVERITY: 8.5
TRADEOFFS:
- Tradeoff A
PATH_SUMMARY: Summary without path name.
---
PATH COMPARISON: License open-weight model
LOCK_IN_COUNT: 1
MAX_SEVERITY: 4.5
TRADEOFFS:
- Tradeoff B
PATH_SUMMARY: Valid summary.
---
"""
    comparison = _parse_response(malformed, _DIAGNOSES)
    assert len(comparison.path_comparisons) == 1
    assert comparison.path_comparisons[0].scenario_name == "License open-weight model"


def test_parse_response_returns_empty_for_empty_string():
    """_parse_response() returns empty CrossPathComparison for an empty response string."""
    res = _parse_response("", _DIAGNOSES)
    assert res.comparative_narrative == ""
    assert res.path_comparisons == []


# ---------------------------------------------------------------------------
# _build_prompt()
# ---------------------------------------------------------------------------

def test_build_prompt_includes_scenario_names_and_diagnoses():
    """_build_prompt() includes scenario names, dependencies, scores, and failure modes."""
    prompt = _build_prompt(_DIAGNOSES)
    assert "Build custom LLM in-house" in prompt
    assert "License open-weight model" in prompt
    assert "CUDA Hardware Architecture Entanglement" in prompt
    assert "Unmaintainable Custom CUDA Kernel Debt" in prompt
