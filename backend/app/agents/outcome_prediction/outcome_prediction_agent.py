"""
Outcome-Prediction Agent — parent orchestrator for the Outcome-Prediction stage.

Role (ARCHITECTURE.md §3.4)
    Receives the ScenarioSet from the Scenario-Generation Agent, orchestrates its
    three sub-agents, and returns one :class:`OutcomeSet` object containing
    projected trajectories, risk factors, and timeline projections for each scenario.

Sub-agent execution order
    Step 1 (Sequential): Trajectory-Modeling Sub-Agent (5.13)
        Projects forward paths for each scenario -> list[Trajectory]

    Step 2 (Parallel via ThreadPoolExecutor):
        - Risk-Factor Sub-Agent (5.14) -> list[RiskFactor]
        - Timeline-Projection Sub-Agent (5.15) -> list[TimelineProjection]
        (Both depend on 5.13 output but are independent of each other)

Public API
----------
    run(scenario_set: ScenarioSet) -> OutcomeSet

OutcomeSet is the canonical output type of the Outcome-Prediction stage and is
defined here so the Dependency-Diagnosis Agent can import it from one place.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

from app.agents.outcome_prediction.sub_agents import (
    risk_factor_sub_agent,
    timeline_projection_sub_agent,
    trajectory_modeling_sub_agent,
)
from app.agents.outcome_prediction.sub_agents.risk_factor_sub_agent import RiskFactor
from app.agents.outcome_prediction.sub_agents.timeline_projection_sub_agent import TimelineProjection
from app.agents.outcome_prediction.sub_agents.trajectory_modeling_sub_agent import Trajectory
from app.agents.scenario_generation.scenario_generation_agent import ScenarioSet


# ---------------------------------------------------------------------------
# Output types
# ---------------------------------------------------------------------------

@dataclass
class OutcomeProjection:
    """Complete outcome projection for a single scenario.

    Attributes
    ----------
    scenario_name:
        Name of the scenario.
    trajectory:
        Projected forward path trajectory.
    risk_factors:
        Key risk factors that could alter or derail this trajectory.
    timeline:
        Time-horizon breakdown and key chronological milestones.
    """

    scenario_name: str
    trajectory: Trajectory | None = None
    risk_factors: list[RiskFactor] = field(default_factory=list)
    timeline: TimelineProjection | None = None


@dataclass
class OutcomeSet:
    """The outcome-prediction output for one decision brief.

    Attributes
    ----------
    entity:
        The organisation making the decision (carried through for traceability).
    capability:
        The AI capability being sourced.
    outcomes:
        List of complete :class:`OutcomeProjection` objects, one per scenario.
    """

    entity: str
    capability: str
    outcomes: list[OutcomeProjection] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(scenario_set: ScenarioSet) -> OutcomeSet:
    """Run the full Outcome-Prediction pipeline for one decision brief.

    Parameters
    ----------
    scenario_set:
        The :class:`~app.agents.scenario_generation.scenario_generation_agent.ScenarioSet`
        produced by the Scenario-Generation Agent.

    Returns
    -------
    OutcomeSet
        Projected outcomes for each scenario, ready for the Dependency-Diagnosis Agent.
    """
    scenarios = scenario_set.scenarios
    if not scenarios:
        return OutcomeSet(
            entity=scenario_set.entity,
            capability=scenario_set.capability,
            outcomes=[],
        )

    # Step 1: Sequential call to Trajectory-Modeling Sub-Agent (5.13)
    trajectories: list[Trajectory] = trajectory_modeling_sub_agent.run(scenarios)

    if not trajectories:
        return OutcomeSet(
            entity=scenario_set.entity,
            capability=scenario_set.capability,
            outcomes=[],
        )

    # Step 2: Parallel execution of Risk-Factor (5.14) and Timeline-Projection (5.15)
    risk_factors: list[RiskFactor] = []
    timelines: list[TimelineProjection] = []

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_risks = executor.submit(risk_factor_sub_agent.run, trajectories, scenarios)
        future_timelines = executor.submit(timeline_projection_sub_agent.run, trajectories, scenarios)

        risk_factors = future_risks.result()
        timelines = future_timelines.result()

    # Step 3: Bundle sub-agent outputs by scenario name into OutcomeProjection objects
    risk_map: dict[str, list[RiskFactor]] = {}
    for rf in risk_factors:
        risk_map.setdefault(rf.scenario_name.lower(), []).append(rf)

    timeline_map: dict[str, TimelineProjection] = {
        tl.scenario_name.lower(): tl for tl in timelines
    }

    outcomes: list[OutcomeProjection] = []
    for tr in trajectories:
        key = tr.scenario_name.lower()
        rfs = risk_map.get(key, [])
        tl = timeline_map.get(key)

        outcomes.append(
            OutcomeProjection(
                scenario_name=tr.scenario_name,
                trajectory=tr,
                risk_factors=rfs,
                timeline=tl,
            )
        )

    return OutcomeSet(
        entity=scenario_set.entity,
        capability=scenario_set.capability,
        outcomes=outcomes,
    )
