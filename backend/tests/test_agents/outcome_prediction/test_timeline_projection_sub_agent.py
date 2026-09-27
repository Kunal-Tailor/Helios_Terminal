"""
Unit tests for app.agents.outcome_prediction.sub_agents.timeline_projection_sub_agent.

All LLM calls are mocked — no network access, no API key required.

Tests cover:
  - run() returns a list of TimelineProjection objects
  - run() returns [] for empty input trajectories (no LLM call)
  - run() returns [] when the LLM call raises (graceful degradation)
  - run() returns [] when the response is unparseable
  - run() calls the LLM exactly once
  - _parse_response() parses a well-formed multi-block response
  - _parse_response() maps SCENARIO/SHORT_TERM/MEDIUM_TERM/LONG_TERM/MILESTONES fields correctly
  - _parse_response() skips blocks missing the SCENARIO field
  - _parse_response() returns [] for an empty string
  - _build_prompt() includes trajectory summaries and scenario implementation steps
"""

from unittest.mock import patch

import pytest

from app.agents.outcome_prediction.sub_agents.timeline_projection_sub_agent import (
    TimelineProjection,
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
        technical_impact="High stack control but significant technical debt.",
        operational_impact="Requires dedicated internal ML Ops team.",
    ),
    Trajectory(
        scenario_name="License open-weight model",
        summary="Rapid deployment with low upfront cost, relying on open-source ecosystem updates.",
        expected_outcomes=["Reduced time-to-value.", "Controlled operational expenditure."],
        technical_impact="Moderate stack control.",
        operational_impact="Lean operational footprint.",
    ),
]

_SCENARIOS = [
    Scenario(
        name="Build custom LLM in-house",
        option_name="Build custom LLM in-house",
        description="Train and host custom weights on local GPU cluster.",
        implementation_steps=["Procure GPUs", "Train model"],
        key_risks=["High capital cost"],
        layers_addressed=["Model Weights"],
    ),
]

_WELL_FORMED_RESPONSE = """\
SCENARIO: Build custom LLM in-house
SHORT_TERM: Months 0-6: GPU cluster procurement, data curation, and initial baseline model training.
MEDIUM_TERM: Months 6-18: Internal pilot deployment, model fine-tuning, and ML Ops process integration.
LONG_TERM: Months 18+: Full production operations, custom model updates, and ongoing hardware maintenance.
MILESTONES:
- Month 3: GPU cluster operational and baseline training started.
- Month 6: Initial 7B parameter model pilot evaluation complete.
- Month 12: Enterprise-wide deployment and data governance sign-off.
- Month 24: Model retrained on updated domain datasets.
---
SCENARIO: License open-weight model
SHORT_TERM: Months 0-6: Open weights evaluation, license compliance check, and rapid edge deployment.
MEDIUM_TERM: Months 6-18: Fine-tuning pipeline optimization and operational monitoring.
LONG_TERM: Months 18+: Upstream open-source model upgrade and long-term cost optimization.
MILESTONES:
- Month 1: Open weight model selected and local test environment provisioned.
- Month 3: Fine-tuned edge model deployed to pilot users.
- Month 12: Full production deployment across all edge nodes.
---
"""

_LLM_PATH = "app.agents.outcome_prediction.sub_agents.timeline_projection_sub_agent.call_llm_with_fallback"


# ---------------------------------------------------------------------------
# run() — return type and basic behaviour
# ---------------------------------------------------------------------------

def test_run_returns_list_of_timeline_projections():
    """run() returns a list of TimelineProjection instances."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE):
        result = run(_TRAJECTORIES, _SCENARIOS)

    assert isinstance(result, list)
    assert all(isinstance(p, TimelineProjection) for p in result)


def test_run_returns_correct_count():
    """run() returns one TimelineProjection per parsed block."""
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
    """run() returns [] when the LLM response has no valid timeline blocks."""
    with patch(_LLM_PATH, return_value="Unstructured text response with no scenario headers."):
        result = run(_TRAJECTORIES)

    assert result == []


# ---------------------------------------------------------------------------
# _parse_response() — field mapping
# ---------------------------------------------------------------------------

def test_parse_response_maps_fields_correctly():
    """_parse_response() correctly populates TimelineProjection dataclass fields."""
    projections = _parse_response(_WELL_FORMED_RESPONSE, _TRAJECTORIES)
    first = projections[0]

    assert first.scenario_name == "Build custom LLM in-house"
    assert "GPU cluster procurement" in first.short_term
    assert "Internal pilot deployment" in first.medium_term
    assert "Full production operations" in first.long_term
    assert len(first.milestones) == 4
    assert "GPU cluster operational" in first.milestones[0]


def test_parse_response_skips_blocks_missing_scenario_field():
    """_parse_response() skips blocks missing the SCENARIO field."""
    malformed = """\
SHORT_TERM: Short term text without scenario name.
MEDIUM_TERM: Medium term text.
LONG_TERM: Long term text.
MILESTONES:
- Milestone 1
---
SCENARIO: License open-weight model
SHORT_TERM: Valid short term.
MEDIUM_TERM: Valid medium term.
LONG_TERM: Valid long term.
MILESTONES:
- Valid milestone A
- Valid milestone B
---
"""
    projections = _parse_response(malformed, _TRAJECTORIES)
    assert len(projections) == 1
    assert projections[0].scenario_name == "License open-weight model"


def test_parse_response_returns_empty_for_empty_string():
    """_parse_response() returns [] for an empty response string."""
    assert _parse_response("", _TRAJECTORIES) == []


# ---------------------------------------------------------------------------
# _build_prompt()
# ---------------------------------------------------------------------------

def test_build_prompt_includes_trajectory_summaries():
    """_build_prompt() includes trajectory scenario names and summaries."""
    prompt = _build_prompt(_TRAJECTORIES, _SCENARIOS)
    assert "Build custom LLM in-house" in prompt
    assert "License open-weight model" in prompt
    assert "sovereign model capability" in prompt


def test_build_prompt_includes_scenario_implementation_steps():
    """_build_prompt() includes implementation steps from scenarios when available."""
    prompt = _build_prompt(_TRAJECTORIES, _SCENARIOS)
    assert "Procure GPUs" in prompt
