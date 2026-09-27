"""
Unit tests for app.agents.outcome_prediction.sub_agents.risk_factor_sub_agent.

All LLM calls are mocked — no network access, no API key required.

Tests cover:
  - run() returns a list of RiskFactor objects
  - run() returns [] for empty input trajectories (no LLM call)
  - run() returns [] when the LLM call raises (graceful degradation)
  - run() returns [] when the response is unparseable
  - run() calls the LLM exactly once
  - _parse_response() parses a well-formed multi-block response
  - _parse_response() maps RISK FACTOR/SCENARIO/DESCRIPTION/LIKELIHOOD/SEVERITY/MITIGATION fields correctly
  - _parse_response() skips blocks missing RISK FACTOR or SCENARIO
  - _parse_response() returns [] for an empty string
  - _build_prompt() includes trajectory summaries and scenario details
"""

from unittest.mock import patch

import pytest

from app.agents.outcome_prediction.sub_agents.risk_factor_sub_agent import (
    RiskFactor,
    _build_prompt,
    _parse_response,
    run,
)
from app.agents.outcome_prediction.sub_agents.trajectory_modeling_sub_agent import Trajectory
from app.agents.scenario_generation.sub_agents.scenario_refinement_sub_agent import Scenario

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_TRAJECTORIES = [
    Trajectory(
        scenario_name="Build custom LLM in-house",
        summary="Over 3 years, ACME Corp establishes sovereign model capability but incurs high maintenance overhead.",
        expected_outcomes=["Full ownership of model weights.", "Higher initial capital expenditure."],
        technical_impact="High stack control but significant technical debt in training infrastructure.",
        operational_impact="Requires dedicated internal ML Ops team and hardware maintenance.",
    ),
    Trajectory(
        scenario_name="License open-weight model",
        summary="Rapid deployment with low upfront cost, relying on open-source ecosystem updates.",
        expected_outcomes=["Reduced time-to-value.", "Controlled operational expenditure."],
        technical_impact="Moderate stack control with dependence on upstream weight formats.",
        operational_impact="Lean operational footprint focused on fine-tuning.",
    ),
]

_SCENARIOS = [
    Scenario(
        name="Build custom LLM in-house",
        option_name="Build custom LLM in-house",
        description="Train and host custom weights on local GPU cluster.",
        implementation_steps=["Procure GPUs", "Train model"],
        key_risks=["High capital cost", "Talent scarcity"],
        layers_addressed=["Model Weights"],
    ),
]

_WELL_FORMED_RESPONSE = """\
RISK FACTOR: Key ML Engineering Departure
SCENARIO: Build custom LLM in-house
DESCRIPTION: Loss of lead ML engineers stalls custom architecture development and training pipeline maintenance.
LIKELIHOOD: High
SEVERITY: High
MITIGATION: Implement comprehensive code documentation and paired engineering practices.
---
RISK FACTOR: Upstream Model Licensing Term Shift
SCENARIO: License open-weight model
DESCRIPTION: Upstream maintainers alter license terms in future major releases, restricting commercial edge use.
LIKELIHOOD: Low
SEVERITY: High
MITIGATION: Pin model version and archive repository under current open license.
---
"""

_LLM_PATH = "app.agents.outcome_prediction.sub_agents.risk_factor_sub_agent.call_llm_with_fallback"


# ---------------------------------------------------------------------------
# run() — return type and basic behaviour
# ---------------------------------------------------------------------------

def test_run_returns_list_of_risk_factors():
    """run() returns a list of RiskFactor instances."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE):
        result = run(_TRAJECTORIES, _SCENARIOS)

    assert isinstance(result, list)
    assert all(isinstance(r, RiskFactor) for r in result)


def test_run_returns_correct_count():
    """run() returns one RiskFactor per parsed block."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE):
        result = run(_TRAJECTORIES, _SCENARIOS)

    assert len(result) == 2


def test_run_calls_llm_once():
    """run() makes exactly one LLM call."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE) as mock_llm:
        run(_TRAJECTORIES, _SCENARIOS)

    assert mock_llm.call_count == 1


# ---------------------------------------------------------------------------
# run() — graceful degradation
# ---------------------------------------------------------------------------

def test_run_returns_empty_for_empty_trajectories():
    """run() returns [] immediately when no trajectories are provided."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE) as mock_llm:
        result = run([])

    assert result == []
    mock_llm.assert_not_called()


def test_run_returns_empty_when_llm_raises():
    """run() returns [] when the LLM call raises an exception."""
    with patch(_LLM_PATH, side_effect=RuntimeError("LLM failure")):
        result = run(_TRAJECTORIES)

    assert result == []


def test_run_returns_empty_when_response_unparseable():
    """run() returns [] when the LLM response has no valid risk factor blocks."""
    with patch(_LLM_PATH, return_value="Unstructured text with no risk factor tags."):
        result = run(_TRAJECTORIES)

    assert result == []


# ---------------------------------------------------------------------------
# _parse_response() — field mapping
# ---------------------------------------------------------------------------

def test_parse_response_maps_fields_correctly():
    """_parse_response() correctly populates RiskFactor dataclass fields."""
    risk_factors = _parse_response(_WELL_FORMED_RESPONSE, _TRAJECTORIES)
    first = risk_factors[0]

    assert first.factor_name == "Key ML Engineering Departure"
    assert first.scenario_name == "Build custom LLM in-house"
    assert "Loss of lead ML engineers" in first.description
    assert first.likelihood == "High"
    assert first.impact_severity == "High"
    assert "documentation" in first.mitigation_strategy


def test_parse_response_skips_blocks_missing_factor_or_scenario():
    """_parse_response() skips blocks missing RISK FACTOR or SCENARIO field."""
    malformed = """\
RISK FACTOR: Missing Scenario Name
DESCRIPTION: Description without scenario name.
LIKELIHOOD: High
SEVERITY: High
MITIGATION: Mitigation text.
---
SCENARIO: License open-weight model
DESCRIPTION: Description without factor name.
LIKELIHOOD: Low
SEVERITY: High
MITIGATION: Mitigation text.
---
RISK FACTOR: Valid Risk Factor
SCENARIO: License open-weight model
DESCRIPTION: Valid description text.
LIKELIHOOD: Medium
SEVERITY: Medium
MITIGATION: Valid mitigation.
---
"""
    risk_factors = _parse_response(malformed, _TRAJECTORIES)
    assert len(risk_factors) == 1
    assert risk_factors[0].factor_name == "Valid Risk Factor"


def test_parse_response_returns_empty_for_empty_string():
    """_parse_response() returns [] for an empty response string."""
    assert _parse_response("", _TRAJECTORIES) == []


# ---------------------------------------------------------------------------
# _build_prompt()
# ---------------------------------------------------------------------------

def test_build_prompt_includes_trajectory_names_and_summaries():
    """_build_prompt() includes trajectory scenario names and summaries."""
    prompt = _build_prompt(_TRAJECTORIES, _SCENARIOS)
    assert "Build custom LLM in-house" in prompt
    assert "License open-weight model" in prompt
    assert "sovereign model capability" in prompt


def test_build_prompt_includes_scenario_known_risks():
    """_build_prompt() includes known risks from scenarios when available."""
    prompt = _build_prompt(_TRAJECTORIES, _SCENARIOS)
    assert "Talent scarcity" in prompt
