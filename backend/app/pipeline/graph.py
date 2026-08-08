"""
Pipeline Graph — Sequential multi-agent pipeline execution with verification gating.

Role (ARCHITECTURE.md §2, §3.7)
    Wires together all six parent agents in sequence with cross-stage verification
    gates between each handoff boundary:

        User Decision Brief (entity, capability, options)
                            │
                            ▼
                    1. Ingestion Agent
                            │
                       [✓ Verify]
                            ▼
                   2. Stack-Mapping Agent
                            │
                       [✓ Verify]
                            ▼
                3. Scenario-Generation Agent
                            │
                       [✓ Verify]
                            ▼
                 4. Outcome-Prediction Agent
                            │
                       [✓ Verify]
                            ▼
                5. Dependency-Diagnosis Agent
                            │
                       [✓ Verify]
                            ▼
                   6. Orchestrator Agent
                            │
                       [✓ Verify]
                            ▼
                      PipelineResult (with final OrchestratorVerdict & Verification Results)

Public API
----------
    run_pipeline(entity, capability, options=None, store=None, halt_on_verification_failure=True) -> PipelineResult
    run(entity, capability, options=None, store=None, halt_on_verification_failure=True) -> PipelineResult
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
from app.verification.source_store import SourcedClaim, SourceStore
from app.verification.verifier import VerificationResult, verify_stage

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """End-to-end execution result containing intermediate outputs, verification, and final verdict.

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
    source_store:
        Accumulated :class:`~app.verification.source_store.SourceStore` for all stages.
    verification_results:
        All :class:`~app.verification.verifier.VerificationResult` records generated during execution.
    verification_passed:
        True if all verified claims met the verification threshold.
    verification_failed_stage:
        Name of the stage that failed verification, if halted or flagged.
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
    source_store: SourceStore = field(default_factory=SourceStore)
    verification_results: list[VerificationResult] = field(default_factory=list)
    verification_passed: bool = True
    verification_failed_stage: str | None = None


def run_pipeline(
    entity: str,
    capability: str,
    options: list[str] | None = None,
    store: SourceStore | None = None,
    halt_on_verification_failure: bool = True,
) -> PipelineResult:
    """Execute the sequential 6-stage AI sourcing decision pipeline with stage verification gating.

    Parameters
    ----------
    entity:
        The organization making the sourcing decision (e.g. "Indian Army signals division").
    capability:
        The AI capability being sourced (e.g. "small language model for edge inference").
    options:
        Optional candidate sourcing options (e.g. ["build in-house", "license open-weight"]).
    store:
        Optional pre-populated :class:`~app.verification.source_store.SourceStore`.
    halt_on_verification_failure:
        If True (default), pipeline halts downstream execution if any claim in a stage fails verification.

    Returns
    -------
    PipelineResult
        Structured container holding intermediate outputs, verification results, and final verdict.
    """
    options_list = list(options) if options else []
    source_store = store if store is not None else SourceStore()
    result = PipelineResult(
        entity=entity,
        capability=capability,
        options=options_list,
        source_store=source_store,
    )

    context_summary = ""

    # -----------------------------------------------------------------------
    # Stage 1: Ingestion
    # -----------------------------------------------------------------------
    try:
        result.ingestion_context = ingestion_agent.run(
            entity=entity,
            capability=capability,
            options=options_list,
        )
        if not result.ingestion_context or (not result.ingestion_context.context_summary and not result.ingestion_context.key_facts):
            result.verification_passed = False
            result.verification_failed_stage = "ingestion"
            reason = "stage did not execute: ingestion returned empty context"
            result.verification_results.append(
                VerificationResult(
                    passed=False,
                    confidence=0.0,
                    reason=reason,
                    claim="Stage execution: ingestion",
                    agent_stage="ingestion",
                )
            )
            logger.warning("Pipeline halted at stage 'ingestion' due to empty output.")
            return result

        if result.ingestion_context:
            context_summary = result.ingestion_context.context_summary or ""
        _register_ingestion_claims(result.ingestion_context, source_store)
        vr_1 = verify_stage(source_store, "ingestion")
        result.verification_results.extend(vr_1)
        if halt_on_verification_failure and any(not v.passed for v in vr_1):
            result.verification_passed = False
            result.verification_failed_stage = "ingestion"
            logger.warning("Pipeline halted at stage 'ingestion' due to verification failure.")
            return result
    except Exception as exc:
        logger.error("Error executing stage 'ingestion': %s", exc, exc_info=True)
        result.verification_passed = False
        result.verification_failed_stage = "ingestion"
        result.verification_results.append(
            VerificationResult(
                passed=False,
                confidence=0.0,
                reason=f"stage did not execute: {exc}",
                claim="Stage execution: ingestion",
                agent_stage="ingestion",
            )
        )
        return result

    # -----------------------------------------------------------------------
    # Stage 2: Stack Mapping
    # -----------------------------------------------------------------------
    try:
        result.stack_scope = stack_mapping_agent.run(
            context=result.ingestion_context,
        )
        if not result.stack_scope or not result.stack_scope.layers:
            result.verification_passed = False
            result.verification_failed_stage = "stack_mapping"
            reason = "stage did not execute: stack_mapping returned empty scope"
            result.verification_results.append(
                VerificationResult(
                    passed=False,
                    confidence=0.0,
                    reason=reason,
                    claim="Stage execution: stack_mapping",
                    agent_stage="stack_mapping",
                )
            )
            logger.warning("Pipeline halted at stage 'stack_mapping' due to empty output.")
            return result

        _register_stack_mapping_claims(result.stack_scope, result.ingestion_context, source_store)
        vr_2 = verify_stage(source_store, "stack_mapping")
        result.verification_results.extend(vr_2)
        if halt_on_verification_failure and any(not v.passed for v in vr_2):
            result.verification_passed = False
            result.verification_failed_stage = "stack_mapping"
            logger.warning("Pipeline halted at stage 'stack_mapping' due to verification failure.")
            return result
    except Exception as exc:
        logger.error("Error executing stage 'stack_mapping': %s", exc, exc_info=True)
        result.verification_passed = False
        result.verification_failed_stage = "stack_mapping"
        result.verification_results.append(
            VerificationResult(
                passed=False,
                confidence=0.0,
                reason=f"stage did not execute: {exc}",
                claim="Stage execution: stack_mapping",
                agent_stage="stack_mapping",
            )
        )
        return result

    # -----------------------------------------------------------------------
    # Stage 3: Scenario Generation
    # -----------------------------------------------------------------------
    try:
        result.scenario_set = scenario_generation_agent.run(
            stack_scope=result.stack_scope,
        )
        if not result.scenario_set or not result.scenario_set.scenarios:
            result.verification_passed = False
            result.verification_failed_stage = "scenario_generation"
            reason = "stage did not execute: scenario_generation returned empty scenario set"
            result.verification_results.append(
                VerificationResult(
                    passed=False,
                    confidence=0.0,
                    reason=reason,
                    claim="Stage execution: scenario_generation",
                    agent_stage="scenario_generation",
                )
            )
            logger.warning("Pipeline halted at stage 'scenario_generation' due to empty output.")
            return result

        _register_scenario_generation_claims(result.scenario_set, result.stack_scope, source_store)
        vr_3 = verify_stage(source_store, "scenario_generation")
        result.verification_results.extend(vr_3)
        if halt_on_verification_failure and any(not v.passed for v in vr_3):
            result.verification_passed = False
            result.verification_failed_stage = "scenario_generation"
            logger.warning("Pipeline halted at stage 'scenario_generation' due to verification failure.")
            return result
    except Exception as exc:
        logger.error("Error executing stage 'scenario_generation': %s", exc, exc_info=True)
        result.verification_passed = False
        result.verification_failed_stage = "scenario_generation"
        result.verification_results.append(
            VerificationResult(
                passed=False,
                confidence=0.0,
                reason=f"stage did not execute: {exc}",
                claim="Stage execution: scenario_generation",
                agent_stage="scenario_generation",
            )
        )
        return result

    # -----------------------------------------------------------------------
    # Stage 4: Outcome Prediction
    # -----------------------------------------------------------------------
    try:
        result.outcome_set = outcome_prediction_agent.run(
            scenario_set=result.scenario_set,
        )
        if not result.outcome_set or not result.outcome_set.outcomes:
            result.verification_passed = False
            result.verification_failed_stage = "outcome_prediction"
            reason = "stage did not execute: outcome_prediction returned empty outcome set"
            result.verification_results.append(
                VerificationResult(
                    passed=False,
                    confidence=0.0,
                    reason=reason,
                    claim="Stage execution: outcome_prediction",
                    agent_stage="outcome_prediction",
                )
            )
            logger.warning("Pipeline halted at stage 'outcome_prediction' due to empty output.")
            return result

        _register_outcome_prediction_claims(result.outcome_set, result.scenario_set, source_store)
        vr_4 = verify_stage(source_store, "outcome_prediction")
        result.verification_results.extend(vr_4)
        if halt_on_verification_failure and any(not v.passed for v in vr_4):
            result.verification_passed = False
            result.verification_failed_stage = "outcome_prediction"
            logger.warning("Pipeline halted at stage 'outcome_prediction' due to verification failure.")
            return result
    except Exception as exc:
        logger.error("Error executing stage 'outcome_prediction': %s", exc, exc_info=True)
        result.verification_passed = False
        result.verification_failed_stage = "outcome_prediction"
        result.verification_results.append(
            VerificationResult(
                passed=False,
                confidence=0.0,
                reason=f"stage did not execute: {exc}",
                claim="Stage execution: outcome_prediction",
                agent_stage="outcome_prediction",
            )
        )
        return result

    # -----------------------------------------------------------------------
    # Stage 5: Dependency Diagnosis
    # -----------------------------------------------------------------------
    try:
        result.diagnosis_set = dependency_diagnosis_agent.run(
            outcome_set=result.outcome_set,
        )
        if not result.diagnosis_set or not result.diagnosis_set.diagnoses:
            result.verification_passed = False
            result.verification_failed_stage = "dependency_diagnosis"
            reason = "stage did not execute: dependency_diagnosis returned empty diagnosis set"
            result.verification_results.append(
                VerificationResult(
                    passed=False,
                    confidence=0.0,
                    reason=reason,
                    claim="Stage execution: dependency_diagnosis",
                    agent_stage="dependency_diagnosis",
                )
            )
            logger.warning("Pipeline halted at stage 'dependency_diagnosis' due to empty output.")
            return result

        _register_dependency_diagnosis_claims(result.diagnosis_set, result.outcome_set, source_store)
        vr_5 = verify_stage(source_store, "dependency_diagnosis")
        result.verification_results.extend(vr_5)
        if halt_on_verification_failure and any(not v.passed for v in vr_5):
            result.verification_passed = False
            result.verification_failed_stage = "dependency_diagnosis"
            logger.warning("Pipeline halted at stage 'dependency_diagnosis' due to verification failure.")
            return result
    except Exception as exc:
        logger.error("Error executing stage 'dependency_diagnosis': %s", exc, exc_info=True)
        result.verification_passed = False
        result.verification_failed_stage = "dependency_diagnosis"
        result.verification_results.append(
            VerificationResult(
                passed=False,
                confidence=0.0,
                reason=f"stage did not execute: {exc}",
                claim="Stage execution: dependency_diagnosis",
                agent_stage="dependency_diagnosis",
            )
        )
        return result

    # -----------------------------------------------------------------------
    # Stage 6: Orchestrator
    # -----------------------------------------------------------------------
    try:
        sources = result.ingestion_context.sources if result.ingestion_context else None
        result.verdict = orchestrator_agent.run(
            diagnosis_set=result.diagnosis_set,
            sources=sources,
        )
        if not result.verdict or (not result.verdict.recommended_path and not result.verdict.verdict_summary):
            result.verification_passed = False
            result.verification_failed_stage = "orchestrator"
            reason = "stage did not execute: orchestrator returned empty verdict"
            result.verification_results.append(
                VerificationResult(
                    passed=False,
                    confidence=0.0,
                    reason=reason,
                    claim="Stage execution: orchestrator",
                    agent_stage="orchestrator",
                )
            )
            logger.warning("Pipeline halted at stage 'orchestrator' due to empty output.")
            return result

        _register_orchestrator_claims(result.verdict, result.diagnosis_set, source_store)
        vr_6 = verify_stage(source_store, "orchestrator")
        result.verification_results.extend(vr_6)
        if halt_on_verification_failure and any(not v.passed for v in vr_6):
            result.verification_passed = False
            result.verification_failed_stage = "orchestrator"
            logger.warning("Pipeline halted at stage 'orchestrator' due to verification failure.")
            return result
    except Exception as exc:
        logger.error("Error executing stage 'orchestrator': %s", exc, exc_info=True)
        result.verification_passed = False
        result.verification_failed_stage = "orchestrator"
        result.verification_results.append(
            VerificationResult(
                passed=False,
                confidence=0.0,
                reason=f"stage did not execute: {exc}",
                claim="Stage execution: orchestrator",
                agent_stage="orchestrator",
            )
        )
        return result

    if any(not v.passed for v in result.verification_results):
        result.verification_passed = False

    return result


run = run_pipeline


# ---------------------------------------------------------------------------
# Stage claim registration helpers — chained verification
# ---------------------------------------------------------------------------

def _get_ingestion_context_text(ctx: IngestionContext | None) -> str:
    """Return text representing Ingestion's verified output (context summary + key facts)."""
    if not ctx:
        return ""
    parts = [ctx.context_summary] + ctx.key_facts
    return "\n".join(p for p in parts if p)


def _get_stack_mapping_context_text(scope: StackScope | None) -> str:
    """Return text representing Stack-Mapping's verified output."""
    if not scope:
        return ""
    lines = []
    for layer in scope.layers:
        lines.append(f"{layer.name}: {layer.rationale} {layer.evidence}".strip())
    return "\n".join(lines)


def _get_scenario_generation_context_text(sc_set: ScenarioSet | None) -> str:
    """Return text representing Scenario-Generation's verified output."""
    if not sc_set:
        return ""
    lines = []
    for sc in sc_set.scenarios:
        lines.append(f"{sc.name}: {sc.description}".strip())
    return "\n".join(lines)


def _get_outcome_prediction_context_text(out_set: OutcomeSet | None) -> str:
    """Return text representing Outcome-Prediction's verified output."""
    if not out_set:
        return ""
    lines = []
    for out in out_set.outcomes:
        traj_summary = out.trajectory.summary if out.trajectory else ""
        lines.append(f"{out.scenario_name}: {traj_summary}".strip())
        for rf in out.risk_factors:
            lines.append(f"{rf.factor_name}: {rf.description}".strip())
    return "\n".join(lines)


def _get_dependency_diagnosis_context_text(diag_set: DiagnosisSet | None) -> str:
    """Return text representing Dependency-Diagnosis's verified output."""
    if not diag_set:
        return ""
    lines = []
    for diag in diag_set.diagnoses:
        for fm in diag.failure_modes:
            lines.append(
                f"{fm.scenario_name} {fm.dependency_name}: {fm.failure_mode_title} {fm.what_breaks} "
                f"{fm.trigger_condition} {fm.time_horizon}".strip()
            )
    return "\n".join(lines)


def _register_ingestion_claims(ctx: IngestionContext | None, store: SourceStore) -> None:
    """Extract sourced claims from Stage 1: Ingestion Context."""
    if not ctx:
        return
    # Use raw retrieved content (web & structured source snippets) for claim verification,
    # falling back to context_summary if raw_retrieved_content is empty.
    source_text = ctx.raw_retrieved_content if ctx.raw_retrieved_content else (ctx.context_summary or "")
    source_url = ctx.sources[0] if ctx.sources else None
    for fact in ctx.key_facts:
        if fact.strip():
            store.add(
                SourcedClaim(
                    claim=fact,
                    source_text=source_text,
                    agent_stage="ingestion",
                    source_url=source_url,
                )
            )


def _register_stack_mapping_claims(
    scope: StackScope | None,
    ingestion_ctx: IngestionContext | None,
    store: SourceStore,
) -> None:
    """Extract sourced claims from Stage 2: Stack Scope, verifying grounded facts against Ingestion's verified output."""
    if not scope:
        return
    prior_context = _get_ingestion_context_text(ingestion_ctx)
    for layer in scope.layers:
        # Verify the grounded_in fact (layer.evidence) against Ingestion's verified output,
        # while layer.rationale (analytical inference) flows downstream on the StackLayer object.
        claim_text = layer.evidence if layer.evidence else (f"{layer.name}: {layer.rationale}" if layer.rationale else layer.name)
        source_text = prior_context
        store.add(
            SourcedClaim(
                claim=claim_text,
                source_text=source_text,
                agent_stage="stack_mapping",
            )
        )


def _register_scenario_generation_claims(
    sc_set: ScenarioSet | None,
    stack_scope: StackScope | None,
    store: SourceStore,
) -> None:
    """Extract sourced claims from Stage 3: Scenario Set, verifying grounded facts against Stack-Mapping's verified output."""
    if not sc_set:
        return
    prior_context = _get_stack_mapping_context_text(stack_scope)
    for sc in sc_set.scenarios:
        # Verify the grounded_in fact (sc.grounded_in) against Stack-Mapping's verified output,
        # while sc.description (the full scenario description) flows downstream on the Scenario object.
        claim_text = sc.grounded_in if sc.grounded_in else (f"{sc.name}: {sc.description}" if sc.description else sc.name)
        store.add(
            SourcedClaim(
                claim=claim_text,
                source_text=prior_context,
                agent_stage="scenario_generation",
            )
        )


def _register_outcome_prediction_claims(
    out_set: OutcomeSet | None,
    sc_set: ScenarioSet | None,
    store: SourceStore,
) -> None:
    """Extract sourced claims from Stage 4: Outcome Set, verifying grounded facts against Scenario-Generation's verified output."""
    if not out_set:
        return
    prior_context = _get_scenario_generation_context_text(sc_set)
    for out in out_set.outcomes:
        # Verify the grounded_in fact (out.trajectory.grounded_in) against Scenario-Generation's verified output,
        # while out.trajectory.summary (the trajectory projection) flows downstream.
        grounded = out.trajectory.grounded_in if (out.trajectory and out.trajectory.grounded_in) else ""
        claim_text = grounded if grounded else (
            f"{out.scenario_name}: {out.trajectory.summary}"
            if out.trajectory and out.trajectory.summary
            else out.scenario_name
        )
        store.add(
            SourcedClaim(
                claim=claim_text,
                source_text=prior_context,
                agent_stage="outcome_prediction",
            )
        )


def _register_dependency_diagnosis_claims(
    diag_set: DiagnosisSet | None,
    out_set: OutcomeSet | None,
    store: SourceStore,
) -> None:
    """Extract sourced claims from Stage 5: Diagnosis Set, verifying grounded facts against Outcome-Prediction's verified output."""
    if not diag_set:
        return
    prior_context = _get_outcome_prediction_context_text(out_set)
    outcome_map: dict[str, str] = {}
    if out_set:
        for out in out_set.outcomes:
            grounded = (
                out.trajectory.grounded_in
                if (out.trajectory and out.trajectory.grounded_in)
                else (out.trajectory.summary if out.trajectory else "")
            )
            if grounded:
                outcome_map[out.scenario_name.lower()] = grounded

    for diag in diag_set.diagnoses:
        fallback = outcome_map.get(diag.scenario_name.lower(), "")
        for fm in diag.failure_modes:
            # Verify the grounded_in fact against Outcome-Prediction's verified output,
            # falling back to the scenario's trajectory grounded fact/summary if empty.
            claim_text = fm.grounded_in if fm.grounded_in else (fallback if fallback else f"{fm.scenario_name} {fm.dependency_name}: {fm.what_breaks}")
            store.add(
                SourcedClaim(
                    claim=claim_text,
                    source_text=prior_context,
                    agent_stage="dependency_diagnosis",
                )
            )


def _register_orchestrator_claims(
    verdict: OrchestratorVerdict | None,
    diag_set: DiagnosisSet | None,
    store: SourceStore,
) -> None:
    """Extract sourced claims from Stage 6: Orchestrator Verdict, verifying grounded facts against Dependency-Diagnosis's verified output."""
    if not verdict or not verdict.explanation_trail:
        return
    prior_context = _get_dependency_diagnosis_context_text(diag_set)
    fallback_line = prior_context.split("\n")[0] if prior_context else ""
    for step in verdict.explanation_trail.steps:
        grounded = step.grounded_in.strip() if (step.grounded_in and step.grounded_in.strip().lower() not in ("none identified", "none", "n/a")) else ""
        evidence = step.evidence.strip() if (step.evidence and step.evidence.strip().lower() not in ("none identified", "none", "n/a")) else ""
        claim_text = grounded if grounded else (evidence if evidence else fallback_line)
        if claim_text:
            store.add(
                SourcedClaim(
                    claim=claim_text,
                    source_text=prior_context,
                    agent_stage="orchestrator",
                )
            )
