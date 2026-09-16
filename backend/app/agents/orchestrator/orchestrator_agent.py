"""
Orchestrator Agent — parent orchestrator for the final Orchestrator stage.

Role (ARCHITECTURE.md §3.6)
    Receives the DiagnosisSet from the Dependency-Diagnosis Agent, orchestrates its
    three sub-agents in sequence, and returns one :class:`OrchestratorVerdict` object
    containing the final comparative verdict, cross-path comparisons, key recommendations,
    and source-grounded explanation trail.

Sub-agent execution order
    All three sub-agents run in sequence:

        DiagnosisSet
             │
             ▼
     Cross-Path Comparison (5.21)  → CrossPathComparison
             │
             ▼
     Verdict-Synthesis (5.22)     → VerdictSynthesis
             │
             ▼
     Explanation-Trail (5.23)     → ExplanationTrail
             │
             ▼
      OrchestratorVerdict

Public API
----------
    run(diagnosis_set: DiagnosisSet, sources: list[str] | None = None) -> OrchestratorVerdict

OrchestratorVerdict is the canonical output type of the final Orchestrator stage.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.agents.dependency_diagnosis.dependency_diagnosis_agent import DiagnosisSet
from app.agents.orchestrator.sub_agents import (
    cross_path_comparison_sub_agent,
    explanation_trail_sub_agent,
    verdict_synthesis_sub_agent,
)
from app.agents.orchestrator.sub_agents.cross_path_comparison_sub_agent import CrossPathComparison
from app.agents.orchestrator.sub_agents.explanation_trail_sub_agent import ExplanationTrail
from app.agents.orchestrator.sub_agents.verdict_synthesis_sub_agent import VerdictSynthesis


# ---------------------------------------------------------------------------
# Output type
# ---------------------------------------------------------------------------

@dataclass
class OrchestratorVerdict:
    """Final comparative verdict output produced by the Orchestrator Agent.

    Attributes
    ----------
    entity:
        The organisation making the decision (carried through for traceability).
    capability:
        The AI capability being sourced.
    recommended_path:
        Name of the primary recommended scenario path.
    verdict_summary:
        Executive summary narrative of the comparative verdict.
    key_recommendations:
        Actionable recommendations for decision makers.
    path_stances:
        Decision stance per scenario path.
    cross_path_comparison:
        Detailed side-by-side comparative analysis.
    explanation_trail:
        Source-grounded audit reasoning trail for explainability.
    """

    entity: str
    capability: str
    recommended_path: str = ""
    verdict_summary: str = ""
    key_recommendations: list[str] = field(default_factory=list)
    path_stances: dict[str, str] = field(default_factory=dict)
    cross_path_comparison: CrossPathComparison | None = None
    explanation_trail: ExplanationTrail | None = None


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(
    diagnosis_set: DiagnosisSet,
    sources: list[str] | None = None,
) -> OrchestratorVerdict:
    """Run the full Orchestrator pipeline for one decision brief.

    Parameters
    ----------
    diagnosis_set:
        The :class:`~app.agents.dependency_diagnosis.dependency_diagnosis_agent.DiagnosisSet`
        produced by the Dependency-Diagnosis Agent.
    sources:
        Optional list of source URLs accumulated during Ingestion for audit trail grounding.

    Returns
    -------
    OrchestratorVerdict
        Final comparative verdict with recommendations, comparisons, and explanation trail.
    """
    diagnoses = diagnosis_set.diagnoses
    if not diagnoses:
        return OrchestratorVerdict(
            entity=diagnosis_set.entity,
            capability=diagnosis_set.capability,
        )

    # Step 1: Compare diagnoses across paths side-by-side (5.21)
    comparison: CrossPathComparison = cross_path_comparison_sub_agent.run(diagnoses)

    # Step 2: Synthesize final comparative verdict text (5.22)
    verdict: VerdictSynthesis = verdict_synthesis_sub_agent.run(
        comparison=comparison,
        diagnoses=diagnoses,
        entity=diagnosis_set.entity,
        capability=diagnosis_set.capability,
    )

    # Step 3: Assemble source-grounded audit reasoning trail (5.23)
    trail: ExplanationTrail = explanation_trail_sub_agent.run(
        diagnoses=diagnoses,
        verdict=verdict,
        sources=sources,
    )

    return OrchestratorVerdict(
        entity=diagnosis_set.entity,
        capability=diagnosis_set.capability,
        recommended_path=verdict.recommended_path,
        verdict_summary=verdict.verdict_summary,
        key_recommendations=verdict.key_recommendations,
        path_stances=verdict.path_stances,
        cross_path_comparison=comparison,
        explanation_trail=trail,
    )
