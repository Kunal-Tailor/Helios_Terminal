"""
Unit tests for app.agents.dependency_diagnosis.sub_agents.lock_in_identification_sub_agent.

All LLM calls are mocked — no network access, no API key required.

Tests cover:
  - run() returns a list of LockInDependency objects
  - run() returns [] for empty input outcomes (no LLM call)
  - run() returns [] when the LLM call raises (graceful degradation)
  - run() returns [] when the response is unparseable
  - run() calls the LLM exactly once
  - _parse_response() parses a well-formed multi-block response
  - _parse_response() maps LOCK_IN/SCENARIO/LAYER/TYPE/DESCRIPTION fields correctly
  - _parse_response() skips blocks missing LOCK_IN or SCENARIO
  - _parse_response() returns [] for an empty string
  - _build_prompt() includes outcome summaries and risk factors
"""

from unittest.mock import patch

import pytest

from app.agents.dependency_diagnosis.sub_agents.lock_in_identification_sub_agent import (
    LockInDependency,
    _build_prompt,
    _parse_response,
    run,
)
from app.agents.outcome_prediction.outcome_prediction_agent import OutcomeProjection
from app.agents.outcome_prediction.sub_agents.risk_factor_sub_agent import RiskFactor
from app.agents.outcome_prediction.sub_agents.trajectory_modeling_sub_agent import Trajectory

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_TRAJECTORY = Trajectory(
    scenario_name="Build custom LLM in-house",
    summary="3-year sovereign model capability with custom hardware.",
    expected_outcomes=["Full weight ownership"],
    technical_impact="High stack control but training hardware lock-in.",
    operational_impact="ML Ops team needed.",
)

_RISK_FACTOR = RiskFactor(
    scenario_name="Build custom LLM in-house",
    factor_name="Hardware Supply Chain Delay",
    description="GPU availability bottlenecks scaling.",
)

_OUTCOMES = [
    OutcomeProjection(
        scenario_name="Build custom LLM in-house",
        trajectory=_TRAJECTORY,
        risk_factors=[_RISK_FACTOR],
    ),
    OutcomeProjection(
        scenario_name="License open-weight model",
        trajectory=Trajectory(
            scenario_name="License open-weight model",
            summary="Rapid deployment using DeepSeek weights.",
        ),
    ),
]

_WELL_FORMED_RESPONSE = """\
LOCK_IN: CUDA Hardware Architecture Entanglement
SCENARIO: Build custom LLM in-house
LAYER: Hardware / Compute
TYPE: Architectural Entanglement
DESCRIPTION: Custom kernels and training pipelines are tightly coupled to specific GPU accelerator architectures.
---
LOCK_IN: Upstream Weight Schema Dependency
SCENARIO: License open-weight model
LAYER: Model Weights
TYPE: Vendor Lock-in
DESCRIPTION: Downstream fine-tuning depends entirely on the upstream maintainer's model architecture format.
---
"""

_LLM_PATH = "app.agents.dependency_diagnosis.sub_agents.lock_in_identification_sub_agent.complete"


# ---------------------------------------------------------------------------
# run() — return type and basic behaviour
# ---------------------------------------------------------------------------

def test_run_returns_list_of_lock_in_dependencies():
    """run() returns a list of LockInDependency instances."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE):
        result = run(_OUTCOMES)

    assert isinstance(result, list)
    assert all(isinstance(dep, LockInDependency) for dep in result)


def test_run_returns_correct_count():
    """run() returns one LockInDependency per parsed block."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE):
        result = run(_OUTCOMES)

    assert len(result) == 2


def test_run_calls_llm_once():
    """run() makes exactly one LLM call."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE) as mock_llm:
        run(_OUTCOMES)

    assert mock_llm.call_count == 1


# ---------------------------------------------------------------------------
# run() — graceful degradation
# ---------------------------------------------------------------------------

def test_run_returns_empty_for_empty_outcomes():
    """run() returns [] immediately when no outcomes are provided."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE) as mock_llm:
        result = run([])

    assert result == []
    mock_llm.assert_not_called()


def test_run_synthesizes_fallback_when_llm_raises():
    """run() synthesizes fallback lock-ins when the LLM call raises."""
    with patch(_LLM_PATH, side_effect=RuntimeError("LLM error")):
        result = run(_OUTCOMES)

    assert len(result) >= 1
    assert all(isinstance(dep, LockInDependency) for dep in result)
    assert {dep.scenario_name for dep in result} <= {o.scenario_name for o in _OUTCOMES}


def test_run_synthesizes_fallback_when_response_unparseable():
    """run() synthesizes fallback lock-ins when the LLM response is unparseable."""
    with patch(_LLM_PATH, return_value="Unstructured text with no lock-in fields."):
        result = run(_OUTCOMES)

    assert len(result) >= 1
    assert all(isinstance(dep, LockInDependency) for dep in result)


# ---------------------------------------------------------------------------
# _parse_response() — field mapping
# ---------------------------------------------------------------------------

def test_parse_response_maps_fields_correctly():
    """_parse_response() correctly populates LockInDependency fields."""
    dependencies = _parse_response(_WELL_FORMED_RESPONSE, _OUTCOMES)
    first = dependencies[0]

    assert first.dependency_name == "CUDA Hardware Architecture Entanglement"
    assert first.scenario_name == "Build custom LLM in-house"
    assert first.layer_name == "Hardware / Compute"
    assert first.lock_in_type == "Architectural Entanglement"
    assert "tightly coupled" in first.description


def test_parse_response_skips_blocks_missing_lock_in_or_scenario():
    """_parse_response() skips blocks missing LOCK_IN or SCENARIO field."""
    malformed = """\
LOCK_IN: Missing Scenario Name
LAYER: Hardware
TYPE: Vendor Lock-in
DESCRIPTION: Description without scenario name.
---
SCENARIO: License open-weight model
LAYER: Model Weights
TYPE: Vendor Lock-in
DESCRIPTION: Description without dependency name.
---
LOCK_IN: Valid Lock-in Name
SCENARIO: License open-weight model
LAYER: Model Weights
TYPE: Vendor Lock-in
DESCRIPTION: Valid description text.
---
"""
    dependencies = _parse_response(malformed, _OUTCOMES)
    assert len(dependencies) == 1
    assert dependencies[0].dependency_name == "Valid Lock-in Name"


def test_parse_response_returns_empty_for_empty_string():
    """_parse_response() returns [] for an empty response string."""
    assert _parse_response("", _OUTCOMES) == []


# ---------------------------------------------------------------------------
# _build_prompt()
# ---------------------------------------------------------------------------

def test_build_prompt_includes_outcome_scenario_names_and_summaries():
    """_build_prompt() includes scenario names and trajectory summaries."""
    prompt = _build_prompt(_OUTCOMES)
    assert "Build custom LLM in-house" in prompt
    assert "License open-weight model" in prompt
    assert "3-year sovereign model capability" in prompt


def test_build_prompt_includes_risk_factors():
    """_build_prompt() includes risk factors when available."""
    prompt = _build_prompt(_OUTCOMES)
    assert "Hardware Supply Chain Delay" in prompt
