"""
Pipeline Graph — Sequential multi-agent pipeline execution.

Role (ARCHITECTURE.md §2)
    Wires together all six parent agents in sequence to execute an end-to-end
    AI sourcing decision evaluation:

        User Decision Brief (entity, capability, options)
                            │
                            ▼
                    1. Ingestion Agent
                            │
                            ▼
                   2. Stack-Mapping Agent
                            │
                            ▼
                3. Scenario-Generation Agent
                            │
                            ▼
                 4. Outcome-Prediction Agent
                            │
                            ▼
                5. Dependency-Diagnosis Agent
                            │
                            ▼
                   6. Orchestrator Agent
                            │
                            ▼
                      PipelineResult (with final OrchestratorVerdict)

Public API
----------
    run_pipeline(entity, capability, options=None) -> PipelineResult
    run(entity, capability, options=None) -> PipelineResult
"""

from __future__ import annotations

from dataclasses import dataclass, field
import logging

from app.agents.dependency_diagnosis import dependency_diagnosis_agent
from app.agents.dependency_diagnosis.dependency_diagnosis_agent import DiagnosisSet
from app.agents.ingestion import ingestion_agent
from app.agents.ingestion.sub_agents.context_synthesis_sub_agent import IngestionContext
from app.agents.orchestrator import orchestrator_agent
from app.agents.orchestrator.orchestrator_agent import OrchestratorVerdict
from app.agents.outcome_prediction import outcome_prediction_agent
from app.agents.outcome_prediction.outcome_prediction_agent import OutcomeSet
from app.agents.scenario_generation import scenario_generation_agent
from app.agents.scenario_generation.scenario_generation_agent import ScenarioSet
from app.agents.stack_mapping import stack_mapping_agent
from app.agents.stack_mapping.stack_mapping_agent import StackScope

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """End-to-end execution result containing intermediate outputs and final verdict.

    Attributes
    ----------
    entity:
        Organization or unit making the decision.
    capability:
        AI capability being evaluated.
    options:
        Candidate sourcing options provided by the user.
    ingestion_context:
        Output from Stage 1: Ingestion Agent.
    stack_scope:
        Output from Stage 2: Stack-Mapping Agent.
    scenario_set:
        Output from Stage 3: Scenario-Generation Agent.
    outcome_set:
        Output from Stage 4: Outcome-Prediction Agent.
    diagnosis_set:
        Output from Stage 5: Dependency-Diagnosis Agent.
    verdict:
        Output from Stage 6: Orchestrator Agent.
    """

    entity: str
    capability: str
    options: list[str] = field(default_factory=list)
    ingestion_context: IngestionContext | None = None
    stack_scope: StackScope | None = None
    scenario_set: ScenarioSet | None = None
    outcome_set: OutcomeSet | None = None
    diagnosis_set: DiagnosisSet | None = None
    verdict: OrchestratorVerdict | None = None


def run_pipeline(
    entity: str,
    capability: str,
    options: list[str] | None = None,
) -> PipelineResult:
    """Execute the sequential 6-stage AI sourcing decision pipeline.

    Parameters
    ----------
    entity:
        The organization making the sourcing decision (e.g. "Indian Army signals division").
    capability:
        The AI capability being sourced (e.g. "small language model for edge inference").
    options:
        Optional candidate sourcing options (e.g. ["build in-house", "license open-weight"]).

    Returns
    -------
    PipelineResult
        Structured container holding intermediate outputs for all 6 stages and final verdict.
    """
    options_list = list(options) if options else []
    result = PipelineResult(entity=entity, capability=capability, options=options_list)

    try:
        # Stage 1: Ingestion
        result.ingestion_context = ingestion_agent.run(
            entity=entity,
            capability=capability,
            options=options_list,
        )

        # Stage 2: Stack Mapping
        result.stack_scope = stack_mapping_agent.run(
            context=result.ingestion_context,
        )

        # Stage 3: Scenario Generation
        result.scenario_set = scenario_generation_agent.run(
            stack_scope=result.stack_scope,
        )

        # Stage 4: Outcome Prediction
        result.outcome_set = outcome_prediction_agent.run(
            scenario_set=result.scenario_set,
        )

        # Stage 5: Dependency Diagnosis
        result.diagnosis_set = dependency_diagnosis_agent.run(
            outcome_set=result.outcome_set,
        )

        # Stage 6: Orchestrator
        sources = result.ingestion_context.sources if result.ingestion_context else None
        result.verdict = orchestrator_agent.run(
            diagnosis_set=result.diagnosis_set,
            sources=sources,
        )

    except Exception as exc:
        logger.error("Error executing pipeline graph: %s", exc, exc_info=True)

    return result


run = run_pipeline
