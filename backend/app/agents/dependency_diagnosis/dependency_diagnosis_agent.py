"""
Dependency-Diagnosis Agent — parent orchestrator for the Dependency-Diagnosis stage.

Role (ARCHITECTURE.md §3.5)
    Receives the OutcomeSet from the Outcome-Prediction Agent, orchestrates its
    three sub-agents in sequence, and returns one :class:`DiagnosisSet` object containing
    lock-in dependencies, failure modes, and severity scores for each scenario path.

Sub-agent execution order
    All three sub-agents run in sequence — each builds upon previous outputs:

        OutcomeSet
            │
            ▼
    Lock-in Identification (5.17)   → list[LockInDependency]
            │
            ▼
    Failure-Mode (5.18)             → list[FailureMode]
            │
            ▼
    Severity-Scoring (5.19)         → list[DependencySeverityScore]
            │
            ▼
        DiagnosisSet

Public API
----------
    run(outcome_set: OutcomeSet) -> DiagnosisSet

DiagnosisSet is the canonical output type of the Dependency-Diagnosis stage and is
defined here so the Orchestrator Agent can import it from one place.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.agents.dependency_diagnosis.sub_agents import (
    failure_mode_sub_agent,
    lock_in_identification_sub_agent,
    severity_scoring_sub_agent,
)
from app.agents.dependency_diagnosis.sub_agents.failure_mode_sub_agent import FailureMode
from app.agents.dependency_diagnosis.sub_agents.lock_in_identification_sub_agent import LockInDependency
from app.agents.dependency_diagnosis.sub_agents.severity_scoring_sub_agent import DependencySeverityScore
from app.agents.outcome_prediction.outcome_prediction_agent import OutcomeSet


# ---------------------------------------------------------------------------
# Output types
# ---------------------------------------------------------------------------

@dataclass
class DependencyDiagnosis:
    """Complete dependency diagnosis for a single scenario path.

    Attributes
    ----------
    scenario_name:
        Name of the scenario path.
    dependencies:
        Identified lock-in points and dependencies.
    failure_modes:
        Projected failure modes if dependencies go unmanaged.
    severity_scores:
        Quantitative severity and urgency scores for the dependencies.
    """

    scenario_name: str
    dependencies: list[LockInDependency] = field(default_factory=list)
    failure_modes: list[FailureMode] = field(default_factory=list)
    severity_scores: list[DependencySeverityScore] = field(default_factory=list)


@dataclass
class DiagnosisSet:
    """The dependency-diagnosis output for one decision brief.

    Attributes
    ----------
    entity:
        The organisation making the decision (carried through for traceability).
    capability:
        The AI capability being sourced.
    diagnoses:
        List of :class:`DependencyDiagnosis` objects, one per scenario path.
    """

    entity: str
    capability: str
    diagnoses: list[DependencyDiagnosis] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(outcome_set: OutcomeSet) -> DiagnosisSet:
    """Run the full Dependency-Diagnosis pipeline for one decision brief.

    Parameters
    ----------
    outcome_set:
        The :class:`~app.agents.outcome_prediction.outcome_prediction_agent.OutcomeSet`
        produced by the Outcome-Prediction Agent.

    Returns
    -------
    DiagnosisSet
        Dependency diagnoses for each scenario path, ready for the Orchestrator Agent.
    """
    outcomes = outcome_set.outcomes
    if not outcomes:
        return DiagnosisSet(
            entity=outcome_set.entity,
            capability=outcome_set.capability,
            diagnoses=[],
        )

    # Step 1: Identify lock-ins and dependencies (5.17)
    dependencies: list[LockInDependency] = lock_in_identification_sub_agent.run(outcomes)

    # Step 2: Diagnose failure modes for identified dependencies (5.18)
    failure_modes: list[FailureMode] = failure_mode_sub_agent.run(dependencies, outcomes)

    # Step 3: Score severity and urgency for dependencies (5.19)
    severity_scores: list[DependencySeverityScore] = severity_scoring_sub_agent.run(
        dependencies, failure_modes
    )

    # Step 4: Group sub-agent outputs by scenario name into DependencyDiagnosis objects
    dep_map: dict[str, list[LockInDependency]] = {}
    for dep in dependencies:
        dep_map.setdefault(dep.scenario_name.lower(), []).append(dep)

    fm_map: dict[str, list[FailureMode]] = {}
    for fm in failure_modes:
        fm_map.setdefault(fm.scenario_name.lower(), []).append(fm)

    score_map: dict[str, list[DependencySeverityScore]] = {}
    for score in severity_scores:
        score_map.setdefault(score.scenario_name.lower(), []).append(score)

    diagnoses: list[DependencyDiagnosis] = []
    for out in outcomes:
        key = out.scenario_name.lower()
        deps = dep_map.get(key, [])
        fms = fm_map.get(key, [])
        scores = score_map.get(key, [])

        diagnoses.append(
            DependencyDiagnosis(
                scenario_name=out.scenario_name,
                dependencies=deps,
                failure_modes=fms,
                severity_scores=scores,
            )
        )

    return DiagnosisSet(
        entity=outcome_set.entity,
        capability=outcome_set.capability,
        diagnoses=diagnoses,
    )
