"""
Unit tests for app.agents.dependency_diagnosis.sub_agents.failure_mode_sub_agent.

All LLM calls are mocked — no network access, no API key required.

Tests cover:
  - run() returns a list of FailureMode objects
  - run() returns [] for empty input dependencies (no LLM call)
  - run() returns [] when the LLM call raises (graceful degradation)
  - run() returns [] when the response is unparseable
  - run() calls the LLM exactly once
  - _parse_response() parses a well-formed multi-block response
  - _parse_response() maps FAILURE_MODE/SCENARIO/DEPENDENCY/WHAT_BREAKS/TRIGGER/HORIZON fields correctly
  - _parse_response() skips blocks missing FAILURE_MODE, SCENARIO, or DEPENDENCY
  - _parse_response() returns [] for an empty string
  - _build_prompt() includes dependency names and descriptions
"""

from unittest.mock import patch

import pytest

from app.agents.dependency_diagnosis.sub_agents.failure_mode_sub_agent import (
    FailureMode,
    _build_prompt,
    _parse_response,
    run,
)
from app.agents.dependency_diagnosis.sub_agents.lock_in_identification_sub_agent import LockInDependency

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

_WELL_FORMED_RESPONSE = """\
FAILURE_MODE: Unmaintainable Custom CUDA Kernel Debt
SCENARIO: Build custom LLM in-house
DEPENDENCY: CUDA Hardware Architecture Entanglement
WHAT_BREAKS: Hardware migration to next-gen accelerators becomes impossible without rewriting core training kernels.
TRIGGER: Next-generation GPU architecture release or hardware supply chain disruption.
HORIZON: 18-24 months
---
FAILURE_MODE: Upstream Architecture Deprecation Cascade
SCENARIO: License open-weight model
DEPENDENCY: Upstream Weight Schema Dependency
WHAT_BREAKS: Downstream fine-tuning pipeline breaks when upstream maintainer transitions to a non-backwards-compatible architecture.
TRIGGER: Upstream major version release.
HORIZON: 12-18 months
---
"""

_LLM_PATH = "app.agents.dependency_diagnosis.sub_agents.failure_mode_sub_agent.call_llm_with_fallback"


# ---------------------------------------------------------------------------
# run() — return type and basic behaviour
# ---------------------------------------------------------------------------

def test_run_returns_list_of_failure_modes():
    """run() returns a list of FailureMode instances."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE):
        result = run(_DEPENDENCIES)

    assert isinstance(result, list)
    assert all(isinstance(fm, FailureMode) for fm in result)


def test_run_returns_correct_count():
    """run() returns one FailureMode per parsed block."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE):
        result = run(_DEPENDENCIES)

    assert len(result) == 2


def test_run_calls_llm_once():
    """run() makes exactly one LLM call."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE) as mock_llm:
        run(_DEPENDENCIES)

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
    """run() returns [] when the LLM response has no valid failure mode blocks."""
    with patch(_LLM_PATH, return_value="Unstructured text with no failure mode tags."):
        result = run(_DEPENDENCIES)

    assert result == []


# ---------------------------------------------------------------------------
# _parse_response() — field mapping
# ---------------------------------------------------------------------------

def test_parse_response_maps_fields_correctly():
    """_parse_response() correctly populates FailureMode fields."""
    failure_modes = _parse_response(_WELL_FORMED_RESPONSE, _DEPENDENCIES)
    first = failure_modes[0]

    assert first.failure_mode_title == "Unmaintainable Custom CUDA Kernel Debt"
    assert first.scenario_name == "Build custom LLM in-house"
    assert first.dependency_name == "CUDA Hardware Architecture Entanglement"
    assert "Hardware migration" in first.what_breaks
    assert "Next-generation GPU" in first.trigger_condition
    assert first.time_horizon == "18-24 months"


def test_parse_response_skips_blocks_missing_required_fields():
    """_parse_response() skips blocks missing FAILURE_MODE, SCENARIO, or DEPENDENCY field."""
    malformed = """\
FAILURE_MODE: Missing Scenario and Dependency
WHAT_BREAKS: Something breaks.
---
SCENARIO: License open-weight model
DEPENDENCY: Upstream Weight Schema Dependency
WHAT_BREAKS: Missing failure mode title.
---
FAILURE_MODE: Valid Failure Mode Title
SCENARIO: License open-weight model
DEPENDENCY: Upstream Weight Schema Dependency
WHAT_BREAKS: Valid break explanation.
TRIGGER: Valid trigger condition.
HORIZON: 12 months
---
"""
    failure_modes = _parse_response(malformed, _DEPENDENCIES)
    assert len(failure_modes) == 1
    assert failure_modes[0].failure_mode_title == "Valid Failure Mode Title"


def test_parse_response_returns_empty_for_empty_string():
    """_parse_response() returns [] for an empty response string."""
    assert _parse_response("", _DEPENDENCIES) == []


# ---------------------------------------------------------------------------
# _build_prompt()
# ---------------------------------------------------------------------------

def test_build_prompt_includes_dependency_names_and_descriptions():
    """_build_prompt() includes dependency names and descriptions."""
    prompt = _build_prompt(_DEPENDENCIES, [])
    assert "CUDA Hardware Architecture Entanglement" in prompt
    assert "Upstream Weight Schema Dependency" in prompt
    assert "Custom training pipeline tied" in prompt
