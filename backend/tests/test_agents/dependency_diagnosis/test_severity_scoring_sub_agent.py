"""
Unit tests for app.agents.dependency_diagnosis.sub_agents.severity_scoring_sub_agent.

All LLM calls are mocked — no network access, no API key required.

Tests cover:
  - run() returns a list of DependencySeverityScore objects
  - run() returns [] for empty input dependencies (no LLM call)
  - run() returns [] when the LLM call raises (graceful degradation)
  - run() returns [] when the response is unparseable
  - run() calls the LLM exactly once
  - _parse_response() parses a well-formed multi-block response
  - _parse_response() maps DEPENDENCY/SCENARIO/SEVERITY_SCORE/URGENCY_SCORE/RISK_LEVEL/RATIONALE correctly
  - _parse_response() skips blocks missing DEPENDENCY or SCENARIO
  - _parse_response() returns [] for an empty string
  - _build_prompt() includes dependency names and associated failure mode details
"""

from unittest.mock import patch

import pytest

from app.agents.dependency_diagnosis.sub_agents.failure_mode_sub_agent import FailureMode
from app.agents.dependency_diagnosis.sub_agents.lock_in_identification_sub_agent import LockInDependency
from app.agents.dependency_diagnosis.sub_agents.severity_scoring_sub_agent import (
    DependencySeverityScore,
    _build_prompt,
    _parse_response,
    run,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_DEPENDENCIES = [
    LockInDependency(
        scenario_name="Build custom LLM in-house",
        dependency_name="CUDA Hardware Architecture Entanglement",
        layer_name="Hardware / Compute",
        lock_in_type="Architectural Entanglement",
        description="Custom training pipeline tied to specific GPU architecture.",
    ),
    LockInDependency(
        scenario_name="License open-weight model",
        dependency_name="Upstream Weight Schema Dependency",
        layer_name="Model Weights",
        lock_in_type="Vendor Lock-in",
        description="Fine-tuning pipeline relies on upstream model architecture.",
    ),
]

_FAILURE_MODES = [
    FailureMode(
        scenario_name="Build custom LLM in-house",
        dependency_name="CUDA Hardware Architecture Entanglement",
        failure_mode_title="Unmaintainable Custom CUDA Kernel Debt",
        what_breaks="Hardware migration becomes impossible.",
        trigger_condition="Next-gen GPU release.",
        time_horizon="18-24 months",
    ),
]

_WELL_FORMED_RESPONSE = """\
DEPENDENCY: CUDA Hardware Architecture Entanglement
SCENARIO: Build custom LLM in-house
SEVERITY_SCORE: 8.5
URGENCY_SCORE: 7.0
RISK_LEVEL: Critical
RATIONALE: Hardware entanglement requires extensive engineering refactoring if accelerator vendors change.
---
DEPENDENCY: Upstream Weight Schema Dependency
SCENARIO: License open-weight model
SEVERITY_SCORE: 4.5
URGENCY_SCORE: 3.0
RISK_LEVEL: Low
RATIONALE: Open-weight schemas are standardized across open-source inference backends.
---
"""

_LLM_PATH = "app.agents.dependency_diagnosis.sub_agents.severity_scoring_sub_agent.complete"


# ---------------------------------------------------------------------------
# run() — return type and basic behaviour
# ---------------------------------------------------------------------------

def test_run_returns_list_of_severity_scores():
    """run() returns a list of DependencySeverityScore instances."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE):
        result = run(_DEPENDENCIES, _FAILURE_MODES)

    assert isinstance(result, list)
    assert all(isinstance(score, DependencySeverityScore) for score in result)


def test_run_returns_correct_count():
    """run() returns one DependencySeverityScore per parsed block."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE):
        result = run(_DEPENDENCIES, _FAILURE_MODES)

    assert len(result) == 2


def test_run_calls_llm_once():
    """run() makes exactly one LLM call."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE) as mock_llm:
        run(_DEPENDENCIES, _FAILURE_MODES)

    assert mock_llm.call_count == 1


# ---------------------------------------------------------------------------
# run() — graceful degradation
# ---------------------------------------------------------------------------

def test_run_returns_empty_for_empty_dependencies():
    """run() returns [] immediately when no dependencies are provided."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE) as mock_llm:
        result = run([])

    assert result == []
    mock_llm.assert_not_called()


def test_run_returns_empty_when_llm_raises():
    """run() returns [] when the LLM call raises an exception."""
    with patch(_LLM_PATH, side_effect=RuntimeError("LLM failure")):
        result = run(_DEPENDENCIES)

    assert result == []


def test_run_returns_empty_when_response_unparseable():
    """run() returns [] when the LLM response has no valid severity blocks."""
    with patch(_LLM_PATH, return_value="Unstructured text with no severity tags."):
        result = run(_DEPENDENCIES)

    assert result == []


# ---------------------------------------------------------------------------
# _parse_response() — field mapping
# ---------------------------------------------------------------------------

def test_parse_response_maps_fields_correctly():
    """_parse_response() correctly populates DependencySeverityScore fields."""
    scores = _parse_response(_WELL_FORMED_RESPONSE, _DEPENDENCIES)
    first = scores[0]

    assert first.dependency_name == "CUDA Hardware Architecture Entanglement"
    assert first.scenario_name == "Build custom LLM in-house"
    assert first.severity_score == 8.5
    assert first.urgency_score == 7.0
    assert first.risk_level == "Critical"
    assert "Hardware entanglement" in first.rationale


def test_parse_response_skips_blocks_missing_required_fields():
    """_parse_response() skips blocks missing DEPENDENCY or SCENARIO field."""
    malformed = """\
DEPENDENCY: Missing Scenario Name
SEVERITY_SCORE: 8.0
URGENCY_SCORE: 6.0
RISK_LEVEL: High
RATIONALE: Description without scenario name.
---
SCENARIO: License open-weight model
SEVERITY_SCORE: 5.0
URGENCY_SCORE: 5.0
RISK_LEVEL: Medium
RATIONALE: Description without dependency name.
---
DEPENDENCY: Valid Dependency Name
SCENARIO: License open-weight model
SEVERITY_SCORE: 3.5
URGENCY_SCORE: 4.0
RISK_LEVEL: Low
RATIONALE: Valid rationale text.
---
"""
    scores = _parse_response(malformed, _DEPENDENCIES)
    assert len(scores) == 1
    assert scores[0].dependency_name == "Valid Dependency Name"
    assert scores[0].severity_score == 3.5


def test_parse_response_returns_empty_for_empty_string():
    """_parse_response() returns [] for an empty response string."""
    assert _parse_response("", _DEPENDENCIES) == []


# ---------------------------------------------------------------------------
# _build_prompt()
# ---------------------------------------------------------------------------

def test_build_prompt_includes_dependency_names_and_failure_modes():
    """_build_prompt() includes dependency names and associated failure mode titles."""
    prompt = _build_prompt(_DEPENDENCIES, _FAILURE_MODES)
    assert "CUDA Hardware Architecture Entanglement" in prompt
    assert "Upstream Weight Schema Dependency" in prompt
    assert "Unmaintainable Custom CUDA Kernel Debt" in prompt
