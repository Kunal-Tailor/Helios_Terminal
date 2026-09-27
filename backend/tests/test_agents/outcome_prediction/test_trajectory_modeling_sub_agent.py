"""
Unit tests for app.agents.outcome_prediction.sub_agents.trajectory_modeling_sub_agent.

All LLM calls are mocked — no network access, no API key required.

Tests cover:
  - run() returns a list of Trajectory objects
  - run() returns [] for empty input scenarios (no LLM call)
  - run() returns [] when the LLM call raises (graceful degradation)
  - run() returns [] when the response is unparseable
  - run() calls the LLM exactly once
  - _parse_response() parses a well-formed multi-block response
  - _parse_response() maps TRAJECTORY/SUMMARY/EXPECTED OUTCOMES/TECHNICAL IMPACT/OPERATIONAL IMPACT fields correctly
  - _parse_response() populates expected_outcomes as a list of bullet points
  - _parse_response() skips blocks missing the TRAJECTORY field
  - _parse_response() returns [] for an empty string
  - _build_prompt() includes scenario names, descriptions, steps, and risks
"""

from unittest.mock import patch

import pytest

from app.agents.outcome_prediction.sub_agents.trajectory_modeling_sub_agent import (
    Trajectory,
    _build_prompt,
    _parse_response,
    run,
)
from app.agents.scenario_generation.sub_agents.scenario_refinement_sub_agent import Scenario

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_SCENARIOS = [
    Scenario(
        name="Build custom LLM in-house",
        option_name="Build custom LLM in-house",
        description="Train and host custom weights on local GPU cluster.",
        implementation_steps=["Procure GPUs", "Curate dataset", "Train model"],
        key_risks=["High capital cost", "Talent scarcity"],
        layers_addressed=["Model Weights", "Inference Infrastructure"],
    ),
    Scenario(
        name="License open-weight model",
        option_name="License open-weight model",
        description="Deploy DeepSeek open weights fine-tuned on local data.",
        implementation_steps=["Download weights", "Fine-tune", "Deploy API"],
        key_risks=["Licence compliance", "Upstream changes"],
        layers_addressed=["Model Weights", "Licensing Terms"],
    ),
]

_WELL_FORMED_RESPONSE = """\
TRAJECTORY: Build custom LLM in-house
SUMMARY: Over 3 years, ACME Corp establishes sovereign model capability but incurs high maintenance overhead.
EXPECTED OUTCOMES:
- Full ownership of model weights and architecture.
- Elimination of vendor API price increases.
- Higher initial capital expenditure.
TECHNICAL IMPACT: High stack control but significant technical debt in training infrastructure.
OPERATIONAL IMPACT: Requires dedicated internal ML Ops team and hardware maintenance.
---
TRAJECTORY: License open-weight model
SUMMARY: Rapid deployment with low upfront cost, relying on open-source ecosystem updates.
EXPECTED OUTCOMES:
- Reduced time-to-value within 3 months.
- Controlled operational expenditure.
TECHNICAL IMPACT: Moderate stack control with dependence on upstream weight formats.
OPERATIONAL IMPACT: Lean operational footprint focused on fine-tuning rather than base training.
---
"""

_LLM_PATH = "app.agents.outcome_prediction.sub_agents.trajectory_modeling_sub_agent.call_llm_with_fallback"


# ---------------------------------------------------------------------------
# run() — return type and basic behaviour
# ---------------------------------------------------------------------------

def test_run_returns_list_of_trajectories():
    """run() returns a list of Trajectory instances."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE):
        result = run(_SCENARIOS)

    assert isinstance(result, list)
    assert all(isinstance(t, Trajectory) for t in result)


def test_run_returns_one_trajectory_per_scenario():
    """run() returns one Trajectory per parsed block."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE):
        result = run(_SCENARIOS)

    assert len(result) == 2


def test_run_calls_llm_once():
    """run() makes exactly one LLM call."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE) as mock_llm:
        run(_SCENARIOS)

    assert mock_llm.call_count == 1


# ---------------------------------------------------------------------------
# run() — graceful degradation
# ---------------------------------------------------------------------------

def test_run_returns_empty_for_empty_scenarios():
    """run() returns [] immediately when no scenarios are provided."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE) as mock_llm:
        result = run([])

    assert result == []
    mock_llm.assert_not_called()


def test_run_returns_empty_when_llm_raises():
    """run() returns [] when the LLM call raises an exception."""
    with patch(_LLM_PATH, side_effect=RuntimeError("LLM API key error")):
        result = run(_SCENARIOS)

    assert result == []


def test_run_returns_empty_when_response_unparseable():
    """run() returns [] when the LLM response has no valid trajectory blocks."""
    with patch(_LLM_PATH, return_value="Unstructured narrative response with no headers."):
        result = run(_SCENARIOS)

    assert result == []


# ---------------------------------------------------------------------------
# _parse_response() — field mapping
# ---------------------------------------------------------------------------

def test_parse_response_maps_scenario_name():
    """_parse_response() sets Trajectory.scenario_name from TRAJECTORY field."""
    trajectories = _parse_response(_WELL_FORMED_RESPONSE, _SCENARIOS)
    assert trajectories[0].scenario_name == "Build custom LLM in-house"
    assert trajectories[1].scenario_name == "License open-weight model"


def test_parse_response_maps_summary():
    """_parse_response() sets Trajectory.summary from SUMMARY field."""
    trajectories = _parse_response(_WELL_FORMED_RESPONSE, _SCENARIOS)
    assert "ACME Corp" in trajectories[0].summary


def test_parse_response_maps_expected_outcomes_as_list():
    """_parse_response() returns Trajectory.expected_outcomes as a list of strings."""
    trajectories = _parse_response(_WELL_FORMED_RESPONSE, _SCENARIOS)
    outcomes = trajectories[0].expected_outcomes
    assert isinstance(outcomes, list)
    assert len(outcomes) >= 2
    assert "Full ownership" in outcomes[0]


def test_parse_response_maps_technical_and_operational_impact():
    """_parse_response() sets technical_impact and operational_impact."""
    trajectories = _parse_response(_WELL_FORMED_RESPONSE, _SCENARIOS)
    assert "High stack control" in trajectories[0].technical_impact
    assert "dedicated internal ML Ops team" in trajectories[0].operational_impact


def test_parse_response_skips_blocks_missing_trajectory_field():
    """_parse_response() skips any block without a TRAJECTORY: line."""
    malformed = """\
SUMMARY: Summary without a trajectory name.
EXPECTED OUTCOMES:
- Outcome 1
TECHNICAL IMPACT: Impact
OPERATIONAL IMPACT: Ops impact
---
TRAJECTORY: License open-weight model
SUMMARY: Valid block.
EXPECTED OUTCOMES:
- Outcome A
TECHNICAL IMPACT: Impact A
OPERATIONAL IMPACT: Ops A
---
"""
    trajectories = _parse_response(malformed, _SCENARIOS)
    assert len(trajectories) == 1
    assert trajectories[0].scenario_name == "License open-weight model"


def test_parse_response_returns_empty_for_empty_string():
    """_parse_response() returns [] for an empty response."""
    assert _parse_response("", _SCENARIOS) == []


# ---------------------------------------------------------------------------
# _build_prompt()
# ---------------------------------------------------------------------------

def test_build_prompt_includes_scenario_names():
    """_build_prompt() includes every scenario name."""
    prompt = _build_prompt(_SCENARIOS)
    for sc in _SCENARIOS:
        assert sc.name in prompt


def test_build_prompt_includes_steps_and_risks():
    """_build_prompt() includes scenario implementation steps and key risks."""
    prompt = _build_prompt(_SCENARIOS)
    assert "Procure GPUs" in prompt
    assert "Licence compliance" in prompt
