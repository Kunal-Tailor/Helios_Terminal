"""
Unit and integration tests for app.agents.outcome_prediction.outcome_prediction_agent.

UNIT TESTS (mock all sub-agents at their run() boundary)
  - run() returns an OutcomeSet
  - run() copies entity and capability from scenario_set into OutcomeSet
  - run() calls trajectory-modeling sub-agent with scenarios
  - run() passes trajectories and scenarios to risk-factor and timeline-projection sub-agents
  - run() populates OutcomeProjection fields (trajectory, risk_factors, timeline)
  - run() handles empty scenario_set (returns empty OutcomeSet without calling sub-agents)

INTEGRATION TESTS (mock at LLM boundary; real sub-agent logic executes)
  - Full pipeline produces an OutcomeSet with correct entity/capability
  - OutcomeSet.outcomes contains valid OutcomeProjection objects
  - Pipeline tolerates all sub-agents returning empty (all LLMs fail)
"""

from unittest.mock import patch

import pytest

from app.agents.outcome_prediction.outcome_prediction_agent import OutcomeProjection, OutcomeSet, run
from app.agents.outcome_prediction.sub_agents.risk_factor_sub_agent import RiskFactor
from app.agents.outcome_prediction.sub_agents.timeline_projection_sub_agent import TimelineProjection
from app.agents.outcome_prediction.sub_agents.trajectory_modeling_sub_agent import Trajectory
from app.agents.scenario_generation.scenario_generation_agent import ScenarioSet
from app.agents.scenario_generation.sub_agents.scenario_refinement_sub_agent import Scenario

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_SCENARIO = Scenario(
    name="Build custom LLM in-house",
    option_name="Build custom LLM in-house",
    description="Train and host custom weights on local GPU cluster.",
    implementation_steps=["Procure GPUs", "Train model"],
    key_risks=["High capital cost"],
    layers_addressed=["Model Weights"],
)

_SCENARIO_SET = ScenarioSet(
    entity="ACME Corp",
    capability="edge inference LLM",
    scenarios=[_SCENARIO],
)

_TRAJECTORY = Trajectory(
    scenario_name="Build custom LLM in-house",
    summary="3-year sovereign model capability.",
    expected_outcomes=["Full weight ownership"],
    technical_impact="High stack control.",
    operational_impact="ML Ops team needed.",
)

_RISK_FACTOR = RiskFactor(
    scenario_name="Build custom LLM in-house",
    factor_name="ML Engineer Departure",
    description="Loss of key talent.",
    likelihood="High",
    impact_severity="High",
    mitigation_strategy="Paired engineering.",
)

_TIMELINE = TimelineProjection(
    scenario_name="Build custom LLM in-house",
    short_term="GPU procurement.",
    medium_term="Pilot deployment.",
    long_term="Production operations.",
    milestones=["Month 3: Cluster ready"],
)

_TM_PATH = "app.agents.outcome_prediction.outcome_prediction_agent.trajectory_modeling_sub_agent.run"
_RF_PATH = "app.agents.outcome_prediction.outcome_prediction_agent.risk_factor_sub_agent.run"
_TP_PATH = "app.agents.outcome_prediction.outcome_prediction_agent.timeline_projection_sub_agent.run"


# ---------------------------------------------------------------------------
# Unit tests — sub-agent run() functions mocked
# ---------------------------------------------------------------------------

def test_unit_run_returns_outcome_set():
    """run() returns an OutcomeSet instance."""
    with patch(_TM_PATH, return_value=[_TRAJECTORY]), \
         patch(_RF_PATH, return_value=[_RISK_FACTOR]), \
         patch(_TP_PATH, return_value=[_TIMELINE]):
        result = run(_SCENARIO_SET)

    assert isinstance(result, OutcomeSet)


def test_unit_run_copies_entity_and_capability():
    """run() carries entity and capability from ScenarioSet into OutcomeSet."""
    with patch(_TM_PATH, return_value=[_TRAJECTORY]), \
         patch(_RF_PATH, return_value=[_RISK_FACTOR]), \
         patch(_TP_PATH, return_value=[_TIMELINE]):
        result = run(_SCENARIO_SET)

    assert result.entity == "ACME Corp"
    assert result.capability == "edge inference LLM"


def test_unit_run_calls_trajectory_modeling_with_scenarios():
    """run() passes scenarios to trajectory-modeling sub-agent."""
    with patch(_TM_PATH, return_value=[_TRAJECTORY]) as mock_tm, \
         patch(_RF_PATH, return_value=[_RISK_FACTOR]), \
         patch(_TP_PATH, return_value=[_TIMELINE]):
        run(_SCENARIO_SET)

    mock_tm.assert_called_once_with([_SCENARIO])


def test_unit_run_passes_trajectories_and_scenarios_to_sub_agents():
    """run() passes trajectories and scenarios to risk-factor and timeline-projection sub-agents."""
    with patch(_TM_PATH, return_value=[_TRAJECTORY]), \
         patch(_RF_PATH, return_value=[_RISK_FACTOR]) as mock_rf, \
         patch(_TP_PATH, return_value=[_TIMELINE]) as mock_tp:
        run(_SCENARIO_SET)

    mock_rf.assert_called_once_with([_TRAJECTORY], [_SCENARIO])
    mock_tp.assert_called_once_with([_TRAJECTORY], [_SCENARIO])


def test_unit_run_populates_outcome_projection_fields():
    """run() maps sub-agent outputs into OutcomeProjection fields correctly."""
    with patch(_TM_PATH, return_value=[_TRAJECTORY]), \
         patch(_RF_PATH, return_value=[_RISK_FACTOR]), \
         patch(_TP_PATH, return_value=[_TIMELINE]):
        result = run(_SCENARIO_SET)

    assert len(result.outcomes) == 1
    outcome = result.outcomes[0]

    assert isinstance(outcome, OutcomeProjection)
    assert outcome.scenario_name == "Build custom LLM in-house"
    assert outcome.trajectory is _TRAJECTORY
    assert outcome.risk_factors == [_RISK_FACTOR]
    assert outcome.timeline is _TIMELINE


def test_unit_run_handles_empty_scenarios():
    """run() returns OutcomeSet with empty outcomes without calling sub-agents if scenario_set is empty."""
    empty_set = ScenarioSet(entity="ACME Corp", capability="LLM", scenarios=[])

    with patch(_TM_PATH) as mock_tm, \
         patch(_RF_PATH) as mock_rf, \
         patch(_TP_PATH) as mock_tp:
        result = run(empty_set)

    assert isinstance(result, OutcomeSet)
    assert result.outcomes == []
    mock_tm.assert_not_called()
    mock_rf.assert_not_called()
    mock_tp.assert_not_called()


def test_unit_run_handles_empty_trajectories():
    """run() returns empty outcomes if trajectory-modeling returns empty list."""
    with patch(_TM_PATH, return_value=[]), \
         patch(_RF_PATH) as mock_rf, \
         patch(_TP_PATH) as mock_tp:
        result = run(_SCENARIO_SET)

    assert isinstance(result, OutcomeSet)
    assert result.outcomes == []
    mock_rf.assert_not_called()
    mock_tp.assert_not_called()


# ---------------------------------------------------------------------------
# Integration tests — mocked at the LLM boundary
# Real sub-agent parsing logic executes end-to-end through the parent
# ---------------------------------------------------------------------------

_TM_LLM = "app.agents.outcome_prediction.sub_agents.trajectory_modeling_sub_agent.call_llm_with_fallback"
_RF_LLM = "app.agents.outcome_prediction.sub_agents.risk_factor_sub_agent.call_llm_with_fallback"
_TP_LLM = "app.agents.outcome_prediction.sub_agents.timeline_projection_sub_agent.call_llm_with_fallback"

_TM_RESPONSE = """\
TRAJECTORY: Build custom LLM in-house
SUMMARY: Over 3 years, ACME Corp establishes sovereign model capability.
EXPECTED OUTCOMES:
- Full ownership of model weights.
- Higher initial capital expenditure.
TECHNICAL IMPACT: High stack control.
OPERATIONAL IMPACT: Requires dedicated internal ML Ops team.
---
"""

_RF_RESPONSE = """\
RISK FACTOR: Key ML Engineering Departure
SCENARIO: Build custom LLM in-house
DESCRIPTION: Loss of lead ML engineers stalls custom development.
LIKELIHOOD: High
SEVERITY: High
MITIGATION: Paired engineering.
---
"""

_TP_RESPONSE = """\
SCENARIO: Build custom LLM in-house
SHORT_TERM: Months 0-6: GPU procurement.
MEDIUM_TERM: Months 6-18: Pilot deployment.
LONG_TERM: Months 18+: Production operations.
MILESTONES:
- Month 3: Cluster ready.
---
"""


def test_integration_run_returns_outcome_set():
    """Integration: full pipeline returns an OutcomeSet."""
    with patch(_TM_LLM, return_value=_TM_RESPONSE), \
         patch(_RF_LLM, return_value=_RF_RESPONSE), \
         patch(_TP_LLM, return_value=_TP_RESPONSE):
        result = run(_SCENARIO_SET)

    assert isinstance(result, OutcomeSet)
    assert result.entity == "ACME Corp"
    assert result.capability == "edge inference LLM"


def test_integration_outcomes_contain_valid_projections():
    """Integration: OutcomeSet.outcomes contains complete OutcomeProjection objects."""
    with patch(_TM_LLM, return_value=_TM_RESPONSE), \
         patch(_RF_LLM, return_value=_RF_RESPONSE), \
         patch(_TP_LLM, return_value=_TP_RESPONSE):
        result = run(_SCENARIO_SET)

    assert len(result.outcomes) == 1
    outcome = result.outcomes[0]

    assert outcome.scenario_name == "Build custom LLM in-house"
    assert outcome.trajectory is not None
    assert len(outcome.risk_factors) == 1
    assert outcome.timeline is not None


def test_integration_pipeline_tolerates_all_llm_failures():
    """Integration: pipeline returns empty OutcomeSet when all LLM calls fail."""
    with patch(_TM_LLM, side_effect=RuntimeError("LLM down")), \
         patch(_RF_LLM, side_effect=RuntimeError("LLM down")), \
         patch(_TP_LLM, side_effect=RuntimeError("LLM down")):
        result = run(_SCENARIO_SET)

    assert isinstance(result, OutcomeSet)
    assert result.outcomes == []
