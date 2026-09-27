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

from openai import RateLimitError

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
from app.agents.outcome_prediction.sub_agents import timeline_projection_sub_agent
from app.agents.outcome_prediction.sub_agents.timeline_projection_sub_agent import TimelineProjection
from app.agents.scenario_generation.sub_agents import scenario_refinement_sub_agent
from app.agents.scenario_generation.sub_agents.option_enumeration_sub_agent import Option
from app.agents.stack_mapping import stack_mapping_agent
from app.agents.stack_mapping.stack_mapping_agent import StackScope
from app.verification.recalibration import (
    LoopGuard,
    RecalibrationRequest,
    accumulate_ingestion_context,
    check_sufficiency_dependency_diagnosis,
    check_sufficiency_orchestrator,
    check_sufficiency_outcome_prediction,
    check_sufficiency_scenario_generation,
    check_sufficiency_stack_mapping,
)
from app.llm.client import get_last_serving_provider
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
    recalibration_trail:
        List of :class:`~app.verification.recalibration.RecalibrationRequest` records showing backward routes.
    partial_verdict_caveats:
        Human-readable caveat strings emitted when the loop-guard cap is hit before a stage
        reaches sufficiency.  Each string identifies the stage pair that hit the cap and the
        insufficiency reason, so callers know the verdict was produced under constrained
        recalibration.  An empty list means the pipeline ran clean with no cap-hit events.
    stage_providers:
        Mapping of pipeline stage names to the LLM provider that answered each stage.
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
    recalibration_trail: list[RecalibrationRequest] = field(default_factory=list)
    partial_verdict_caveats: list[str] = field(default_factory=list)
    stage_providers: dict[str, str] = field(default_factory=dict)
    data_sovereignty_weight: str | None = None
    latency_tolerance: str | None = None


def run_pipeline(
    entity: str,
    capability: str,
    options: list[str] | None = None,
    store: SourceStore | None = None,
    halt_on_verification_failure: bool = True,
    loop_guard: LoopGuard | None = None,
    data_sovereignty_weight: str | None = None,
    latency_tolerance: str | None = None,
) -> PipelineResult:
    """Execute the 6-stage AI sourcing decision pipeline with stage verification and recalibration.

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
    loop_guard:
        Optional custom loop guard for controlling recalibration limits.
    data_sovereignty_weight:
        Optional data sovereignty priority constraint ('CRITICAL', 'STANDARD', 'LOW').
    latency_tolerance:
        Optional latency/SLA tolerance constraint ('SUB_20MS', 'BALANCED', 'BATCH').

    Returns
    -------
    PipelineResult
        Structured container holding intermediate outputs, verification results, and final verdict.
    """
    options_list = list(options) if options else []
    source_store = store if store is not None else SourceStore()
    guard = loop_guard if loop_guard is not None else LoopGuard()
    result = PipelineResult(
        entity=entity,
        capability=capability,
        options=options_list,
        source_store=source_store,
        data_sovereignty_weight=data_sovereignty_weight,
        latency_tolerance=latency_tolerance,
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
        prov_1 = get_last_serving_provider()
        if prov_1:
            result.stage_providers["ingestion"] = prov_1

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
                    provider=prov_1,
                )
            )
            logger.warning("Pipeline halted at stage 'ingestion' due to empty output.")
            return result

        if result.ingestion_context:
            context_summary = result.ingestion_context.context_summary or ""
        _register_ingestion_claims(result.ingestion_context, source_store)
        vr_1 = verify_stage(source_store, "ingestion")
        for v in vr_1:
            if not v.provider:
                v.provider = prov_1
        result.verification_results.extend(vr_1)
        if halt_on_verification_failure and any(not v.passed for v in vr_1):
            result.verification_passed = False
            result.verification_failed_stage = "ingestion"
            logger.warning("Pipeline halted at stage 'ingestion' due to verification failure.")
            return result
    except RateLimitError as exc:
        logger.error("Rate limit error executing stage 'ingestion': %s", exc, exc_info=True)
        raise
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
                provider=get_last_serving_provider(),
            )
        )
        return result

    # -----------------------------------------------------------------------
    # Stage 2: Stack Mapping (with Sufficiency Check & Ingestion Fallback)
    # -----------------------------------------------------------------------
    try:
        while True:
            result.stack_scope = stack_mapping_agent.run(
                context=result.ingestion_context,
            )
            prov_2 = get_last_serving_provider()
            if prov_2:
                result.stage_providers["stack_mapping"] = prov_2

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
                        provider=prov_2,
                    )
                )
                logger.warning("Pipeline halted at stage 'stack_mapping' due to empty output.")
                return result

            _register_stack_mapping_claims(result.stack_scope, result.ingestion_context, source_store)
            vr_2 = verify_stage(source_store, "stack_mapping")
            for v in vr_2:
                if not v.provider:
                    v.provider = prov_2
            result.verification_results.extend(vr_2)
            if halt_on_verification_failure and any(not v.passed for v in vr_2):
                result.verification_passed = False
                result.verification_failed_stage = "stack_mapping"
                logger.warning("Pipeline halted at stage 'stack_mapping' due to verification failure.")
                return result

            # Sufficiency check: Stack-Mapping -> Ingestion fallback
            suff_sm = check_sufficiency_stack_mapping(result.stack_scope)
            if not suff_sm.sufficient:
                if not guard.cap_exceeded("stack_mapping", "ingestion"):
                    iter_count = guard.record("stack_mapping", "ingestion")
                    recal_req = RecalibrationRequest(
                        from_stage="stack_mapping",
                        to_stage="ingestion",
                        reason="insufficient",
                        gap_description=suff_sm.reason,
                        iteration_count=iter_count,
                        provider=get_last_serving_provider(),
                    )
                    result.recalibration_trail.append(recal_req)
                    logger.info(
                        "Recalibration triggered from 'stack_mapping' to 'ingestion' (iteration %d): %s",
                        iter_count,
                        suff_sm.reason,
                    )
                    # Re-invoke Ingestion scoped to gap_description
                    re_ingest_ctx = ingestion_agent.run(
                        entity=entity,
                        capability=f"{capability} (Gap: {suff_sm.reason})",
                        options=options_list,
                    )
                    prov_re = get_last_serving_provider()
                    if prov_re:
                        result.stage_providers["ingestion"] = prov_re
                    result.ingestion_context = accumulate_ingestion_context(
                        result.ingestion_context,
                        re_ingest_ctx,
                    )
                    _register_ingestion_claims(re_ingest_ctx, source_store)
                    vr_re = verify_stage(source_store, "ingestion")
                    for v in vr_re:
                        if not v.provider:
                            v.provider = prov_re
                    result.verification_results.extend(vr_re)
                    if halt_on_verification_failure and any(not v.passed for v in vr_re):
                        result.verification_passed = False
                        result.verification_failed_stage = "ingestion"
                        logger.warning("Pipeline halted during recalibration re-ingestion due to verification failure.")
                        return result
                    # Loop back and re-run stack_mapping with accumulated context
                    continue
                else:
                    caveat = (
                        f"Loop-guard cap hit: stack_mapping → ingestion "
                        f"(cap={guard.max_retries}, iterations={guard.iteration_count('stack_mapping', 'ingestion')}). "
                        f"Stack-Mapping output may be insufficiently grounded; verdict produced under constrained recalibration."
                    )
                    result.partial_verdict_caveats.append(caveat)
                    logger.warning(
                        "Recalibration cap reached for stack_mapping -> ingestion (attempt %d). Continuing pipeline.",
                        guard.iteration_count("stack_mapping", "ingestion"),
                    )
            break
    except RateLimitError as exc:
        logger.error("Rate limit error executing stage 'stack_mapping': %s", exc, exc_info=True)
        raise
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
    # Stage 3: Scenario Generation (with Sufficiency Check & Dual-Target Fallback)
    # -----------------------------------------------------------------------
    try:
        while True:
            result.scenario_set = scenario_generation_agent.run(
                stack_scope=result.stack_scope,
            )
            prov_3 = get_last_serving_provider()
            if prov_3:
                result.stage_providers["scenario_generation"] = prov_3

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
                        provider=prov_3,
                    )
                )
                logger.warning("Pipeline halted at stage 'scenario_generation' due to empty output.")
                return result

            _register_scenario_generation_claims(result.scenario_set, result.stack_scope, source_store)
            vr_3 = verify_stage(source_store, "scenario_generation")
            for v in vr_3:
                if not v.provider:
                    v.provider = prov_3
            result.verification_results.extend(vr_3)
            if halt_on_verification_failure and any(not v.passed for v in vr_3):
                result.verification_passed = False
                result.verification_failed_stage = "scenario_generation"
                logger.warning("Pipeline halted at stage 'scenario_generation' due to verification failure.")
                return result

            # Sufficiency check: Scenario-Generation -> Stack-Mapping OR Ingestion fallback
            suff_sg = check_sufficiency_scenario_generation(result.scenario_set)
            if not suff_sg.sufficient:
                target_stage = _decide_scenario_fallback_target(
                    scenario_set=result.scenario_set,
                    stack_scope=result.stack_scope,
                    ingestion_context=result.ingestion_context,
                )
                if not guard.cap_exceeded("scenario_generation", target_stage):
                    iter_count = guard.record("scenario_generation", target_stage)
                    gap_desc = f"{suff_sg.reason} [Target: {target_stage}]"
                    recal_req = RecalibrationRequest(
                        from_stage="scenario_generation",
                        to_stage=target_stage,
                        reason="insufficient",
                        gap_description=gap_desc,
                        iteration_count=iter_count,
                        provider=get_last_serving_provider(),
                    )
                    result.recalibration_trail.append(recal_req)
                    logger.info(
                        "Recalibration triggered from 'scenario_generation' to '%s' (iteration %d): %s",
                        target_stage,
                        iter_count,
                        gap_desc,
                    )

                    if target_stage == "ingestion":
                        # Re-invoke Ingestion scoped to missing concrete option data
                        re_ingest_ctx = ingestion_agent.run(
                            entity=entity,
                            capability=f"{capability} (Gap: {gap_desc})",
                            options=options_list,
                        )
                        prov_re = get_last_serving_provider()
                        if prov_re:
                            result.stage_providers["ingestion"] = prov_re
                        result.ingestion_context = accumulate_ingestion_context(
                            result.ingestion_context,
                            re_ingest_ctx,
                        )
                        _register_ingestion_claims(re_ingest_ctx, source_store)
                        vr_re = verify_stage(source_store, "ingestion")
                        for v in vr_re:
                            if not v.provider:
                                v.provider = prov_re
                        result.verification_results.extend(vr_re)
                        if halt_on_verification_failure and any(not v.passed for v in vr_re):
                            result.verification_passed = False
                            result.verification_failed_stage = "ingestion"
                            logger.warning("Pipeline halted during recalibration re-ingestion due to verification failure.")
                            return result

                        # Also re-run Stack-Mapping with the newly accumulated context
                        result.stack_scope = stack_mapping_agent.run(context=result.ingestion_context)
                        prov_sm = get_last_serving_provider()
                        if prov_sm:
                            result.stage_providers["stack_mapping"] = prov_sm
                        _register_stack_mapping_claims(result.stack_scope, result.ingestion_context, source_store)
                        vr_sm = verify_stage(source_store, "stack_mapping")
                        for v in vr_sm:
                            if not v.provider:
                                v.provider = prov_sm
                        result.verification_results.extend(vr_sm)
                        if halt_on_verification_failure and any(not v.passed for v in vr_sm):
                            result.verification_passed = False
                            result.verification_failed_stage = "stack_mapping"
                            logger.warning("Pipeline halted during recalibration stack-mapping due to verification failure.")
                            return result
                    else:
                        # target_stage == "stack_mapping": re-run Stack-Mapping to broaden layer scope
                        result.stack_scope = stack_mapping_agent.run(context=result.ingestion_context)
                        prov_sm = get_last_serving_provider()
                        if prov_sm:
                            result.stage_providers["stack_mapping"] = prov_sm
                        _register_stack_mapping_claims(result.stack_scope, result.ingestion_context, source_store)
                        vr_sm = verify_stage(source_store, "stack_mapping")
                        for v in vr_sm:
                            if not v.provider:
                                v.provider = prov_sm
                        result.verification_results.extend(vr_sm)
                        if halt_on_verification_failure and any(not v.passed for v in vr_sm):
                            result.verification_passed = False
                            result.verification_failed_stage = "stack_mapping"
                            logger.warning("Pipeline halted during recalibration stack-mapping due to verification failure.")
                            return result

                    # Loop back to re-run scenario_generation
                    continue
                else:
                    caveat = (
                        f"Loop-guard cap hit: scenario_generation → {target_stage} "
                        f"(cap={guard.max_retries}, iterations={guard.iteration_count('scenario_generation', target_stage)}). "
                        f"Scenario-Generation output may be insufficient; verdict produced under constrained recalibration."
                    )
                    result.partial_verdict_caveats.append(caveat)
                    logger.warning(
                        "Recalibration cap reached for scenario_generation -> %s (attempt %d). Continuing pipeline.",
                        target_stage,
                        guard.iteration_count("scenario_generation", target_stage),
                    )
            break
    except RateLimitError as exc:
        logger.error("Rate limit error executing stage 'scenario_generation': %s", exc, exc_info=True)
        raise
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
    # Stage 4: Outcome Prediction (with Sufficiency Check & Scenario Refinement Fallback)
    # -----------------------------------------------------------------------
    try:
        while True:
            result.outcome_set = outcome_prediction_agent.run(
                scenario_set=result.scenario_set,
            )
            prov_4 = get_last_serving_provider()
            if prov_4:
                result.stage_providers["outcome_prediction"] = prov_4

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
                        provider=prov_4,
                    )
                )
                logger.warning("Pipeline halted at stage 'outcome_prediction' due to empty output.")
                return result

            _register_outcome_prediction_claims(result.outcome_set, result.scenario_set, source_store)
            vr_4 = verify_stage(source_store, "outcome_prediction")
            for v in vr_4:
                if not v.provider:
                    v.provider = prov_4
            result.verification_results.extend(vr_4)
            if halt_on_verification_failure and any(not v.passed for v in vr_4):
                result.verification_passed = False
                result.verification_failed_stage = "outcome_prediction"
                logger.warning("Pipeline halted at stage 'outcome_prediction' due to verification failure.")
                return result

            # Sufficiency check: Outcome-Prediction -> Scenario-Generation fallback
            suff_op = check_sufficiency_outcome_prediction(result.outcome_set)
            if not suff_op.sufficient:
                if not guard.cap_exceeded("outcome_prediction", "scenario_generation"):
                    iter_count = guard.record("outcome_prediction", "scenario_generation")
                    gap_desc = (
                        f"{suff_op.reason} [Invoking scenario_refinement_sub_agent to sharpen scenario specifications]"
                    )
                    recal_req = RecalibrationRequest(
                        from_stage="outcome_prediction",
                        to_stage="scenario_generation",
                        reason="insufficient",
                        gap_description=gap_desc,
                        iteration_count=iter_count,
                        provider=get_last_serving_provider(),
                    )
                    result.recalibration_trail.append(recal_req)
                    logger.info(
                        "Recalibration triggered from 'outcome_prediction' to 'scenario_generation' (iteration %d): %s",
                        iter_count,
                        gap_desc,
                    )

                    # Targeted refinement: invoke scenario_refinement_sub_agent instead of blind re-run
                    candidate_options = [
                        Option(
                            name=sc.name,
                            description=sc.description,
                            rationale=getattr(sc, "rationale", ""),
                            grounded_in=sc.grounded_in,
                        )
                        for sc in (result.scenario_set.scenarios if result.scenario_set else [])
                    ]
                    stack_scope_for_refine = result.stack_scope or StackScope(entity=entity, capability=capability)
                    refined_scenarios = scenario_refinement_sub_agent.run(
                        options=candidate_options,
                        stack_scope=stack_scope_for_refine,
                    )
                    prov_ref = get_last_serving_provider()
                    if prov_ref:
                        result.stage_providers["scenario_generation"] = prov_ref
                    if refined_scenarios:
                        result.scenario_set = ScenarioSet(
                            entity=entity,
                            capability=capability,
                            scenarios=refined_scenarios,
                        )
                    _register_scenario_generation_claims(result.scenario_set, result.stack_scope, source_store)
                    vr_sg = verify_stage(source_store, "scenario_generation")
                    for v in vr_sg:
                        if not v.provider:
                            v.provider = prov_ref
                    result.verification_results.extend(vr_sg)
                    if halt_on_verification_failure and any(not v.passed for v in vr_sg):
                        result.verification_passed = False
                        result.verification_failed_stage = "scenario_generation"
                        logger.warning("Pipeline halted during recalibration scenario refinement due to verification failure.")
                        return result

                    # Loop back to re-run outcome_prediction with the refined scenario set
                    continue
                else:
                    caveat = (
                        f"Loop-guard cap hit: outcome_prediction → scenario_generation "
                        f"(cap={guard.max_retries}, iterations={guard.iteration_count('outcome_prediction', 'scenario_generation')}). "
                        f"Outcome-Prediction output may lack sufficient trajectory/risk data; verdict produced under constrained recalibration."
                    )
                    result.partial_verdict_caveats.append(caveat)
                    logger.warning(
                        "Recalibration cap reached for outcome_prediction -> scenario_generation (attempt %d). Continuing pipeline.",
                        guard.iteration_count("outcome_prediction", "scenario_generation"),
                    )
            break
    except RateLimitError as exc:
        logger.error("Rate limit error executing stage 'outcome_prediction': %s", exc, exc_info=True)
        raise
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
                provider=get_last_serving_provider(),
            )
        )
        return result

    # -----------------------------------------------------------------------
    # Stage 5: Dependency Diagnosis
    # -----------------------------------------------------------------------
    while True:
        try:
            result.diagnosis_set = dependency_diagnosis_agent.run(
                outcome_set=result.outcome_set,
            )
            prov_5 = get_last_serving_provider()
            if prov_5:
                result.stage_providers["dependency_diagnosis"] = prov_5

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
                        provider=prov_5,
                    )
                )
                logger.warning("Pipeline halted at stage 'dependency_diagnosis' due to empty output.")
                return result

            _register_dependency_diagnosis_claims(result.diagnosis_set, result.outcome_set, source_store)
            vr_5 = verify_stage(source_store, "dependency_diagnosis")
            for v in vr_5:
                if not v.provider:
                    v.provider = prov_5
            result.verification_results.extend(vr_5)
            if halt_on_verification_failure and any(not v.passed for v in vr_5):
                result.verification_passed = False
                result.verification_failed_stage = "dependency_diagnosis"
                logger.warning("Pipeline halted at stage 'dependency_diagnosis' due to verification failure.")
                return result
        except RateLimitError as exc:
            logger.error("Rate limit error executing stage 'dependency_diagnosis': %s", exc, exc_info=True)
            raise
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
                    provider=get_last_serving_provider(),
                )
            )
            return result

        # ------------------------------------------------------------------
        # Sufficiency check: at least one diagnosis must have dependencies
        # ------------------------------------------------------------------
        suf_5 = check_sufficiency_dependency_diagnosis(result.diagnosis_set)
        if suf_5.sufficient:
            break

        if guard.cap_exceeded("dependency_diagnosis", "outcome_prediction"):
            caveat = (
                f"Loop-guard cap hit: dependency_diagnosis → outcome_prediction "
                f"(cap={guard.max_retries}, iterations={guard.iteration_count('dependency_diagnosis', 'outcome_prediction')}). "
                f"Dependency-Diagnosis output may be generic or lack specific lock-ins; verdict produced under constrained recalibration."
            )
            result.partial_verdict_caveats.append(caveat)
            logger.warning(
                "LoopGuard cap exceeded for dependency_diagnosis → outcome_prediction; "
                "proceeding with last diagnosis output."
            )
            break

        guard.record("dependency_diagnosis", "outcome_prediction")
        iter_count = guard.iteration_count("dependency_diagnosis", "outcome_prediction")
        gap = (
            f"Dependency-Diagnosis produced generic/non-specific lock-in output "
            f"({suf_5.reason}). Invoking timeline_projection_sub_agent to enrich "
            f"OutcomeProjection timelines and re-running Dependency-Diagnosis. "
            f"[Iteration {iter_count}]"
        )
        result.recalibration_trail.append(
            RecalibrationRequest(
                from_stage="dependency_diagnosis",
                to_stage="outcome_prediction",
                reason="insufficient",
                gap_description=gap,
                iteration_count=iter_count,
                provider=get_last_serving_provider(),
            )
        )
        logger.info(
            "Stage 5 recalibration (%d): %s", iter_count, gap
        )

        # Invoke timeline_projection_sub_agent on current trajectories + scenarios
        trajectories = [
            proj.trajectory
            for proj in result.outcome_set.outcomes
            if proj.trajectory is not None
        ]
        scenarios = result.scenario_set.scenarios if result.scenario_set else []
        timeline_projections: list[TimelineProjection] = timeline_projection_sub_agent.run(
            trajectories=trajectories,
            scenarios=scenarios,
        )
        prov_tp = get_last_serving_provider()
        if prov_tp:
            result.stage_providers["outcome_prediction"] = prov_tp

        # Attach returned TimelineProjection objects to matching OutcomeProjection entries
        timeline_map = {tp.scenario_name: tp for tp in timeline_projections}
        for proj in result.outcome_set.outcomes:
            if proj.trajectory is not None and proj.trajectory.scenario_name in timeline_map:
                proj.timeline = timeline_map[proj.trajectory.scenario_name]

        # Re-register outcome-prediction claims with enriched timelines before re-diagnosis
        _register_outcome_prediction_claims(result.outcome_set, result.scenario_set, source_store)

        # Loop back to re-run Dependency-Diagnosis with enriched OutcomeSet
        continue


    # -----------------------------------------------------------------------
    # Stage 6: Orchestrator
    # -----------------------------------------------------------------------
    while True:
        try:
            sources = result.ingestion_context.sources if result.ingestion_context else None
            result.verdict = orchestrator_agent.run(
                diagnosis_set=result.diagnosis_set,
                sources=sources,
            )
            prov_6 = get_last_serving_provider()
            if prov_6:
                result.stage_providers["orchestrator"] = prov_6

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
                        provider=prov_6,
                    )
                )
                logger.warning("Pipeline halted at stage 'orchestrator' due to empty output.")
                return result

            _register_orchestrator_claims(result.verdict, result.diagnosis_set, source_store)
            vr_6 = verify_stage(source_store, "orchestrator")
            for v in vr_6:
                if not v.provider:
                    v.provider = prov_6
            result.verification_results.extend(vr_6)
            if halt_on_verification_failure and any(not v.passed for v in vr_6):
                result.verification_passed = False
                result.verification_failed_stage = "orchestrator"
                logger.warning("Pipeline halted at stage 'orchestrator' due to verification failure.")
                return result
        except RateLimitError as exc:
            logger.error("Rate limit error executing stage 'orchestrator': %s", exc, exc_info=True)
            raise
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
                    provider=get_last_serving_provider(),
                )
            )
            return result

        # ------------------------------------------------------------------
        # Asymmetric completeness check: path-scoped Dependency-Diagnosis
        # fallback for paths with no identified lock-ins while others have them
        # ------------------------------------------------------------------
        deficient_paths = _find_deficient_paths(result.verdict)
        if not deficient_paths:
            break

        if guard.cap_exceeded("orchestrator", "dependency_diagnosis"):
            caveat = (
                f"Loop-guard cap hit: orchestrator → dependency_diagnosis "
                f"(cap={guard.max_retries}, iterations={guard.iteration_count('orchestrator', 'dependency_diagnosis')}). "
                f"Orchestrator cross-path comparison relies on asymmetric lock-in data; verdict produced under constrained recalibration."
            )
            result.partial_verdict_caveats.append(caveat)
            logger.warning(
                "LoopGuard cap exceeded for orchestrator → dependency_diagnosis; "
                "proceeding with last verdict."
            )
            break

        guard.record("orchestrator", "dependency_diagnosis")
        iter_count = guard.iteration_count("orchestrator", "dependency_diagnosis")
        gap = (
            f"cross_path_comparison_sub_agent found asymmetric completeness: "
            f"path(s) {deficient_paths!r} have no identified lock-ins while other paths do. "
            f"Re-running Dependency-Diagnosis scoped to deficient path(s) only. "
            f"[Iteration {iter_count}]"
        )
        result.recalibration_trail.append(
            RecalibrationRequest(
                from_stage="orchestrator",
                to_stage="dependency_diagnosis",
                reason="insufficient",
                gap_description=gap,
                iteration_count=iter_count,
                provider=get_last_serving_provider(),
            )
        )
        logger.info("Stage 6 recalibration (%d): %s", iter_count, gap)

        # Build a scoped OutcomeSet containing only the deficient paths' OutcomeProjections
        deficient_set = set(p.lower() for p in deficient_paths)
        scoped_outcomes = [
            proj
            for proj in (result.outcome_set.outcomes if result.outcome_set else [])
            if proj.scenario_name.lower() in deficient_set
        ]
        scoped_outcome_set = OutcomeSet(
            entity=result.entity,
            capability=result.capability,
            outcomes=scoped_outcomes,
        )

        # Re-run Dependency-Diagnosis for only the deficient paths
        new_diag_set = dependency_diagnosis_agent.run(outcome_set=scoped_outcome_set)
        prov_nd = get_last_serving_provider()
        if prov_nd:
            result.stage_providers["dependency_diagnosis"] = prov_nd

        # Merge: replace deficient path diagnoses in result.diagnosis_set; keep the rest untouched
        new_diag_map = {d.scenario_name.lower(): d for d in new_diag_set.diagnoses}
        merged_diagnoses = [
            new_diag_map.get(d.scenario_name.lower(), d)
            for d in result.diagnosis_set.diagnoses
        ]
        # Also add any new diagnoses for paths that had no prior entry
        existing_names = {d.scenario_name.lower() for d in result.diagnosis_set.diagnoses}
        for name_lower, diag in new_diag_map.items():
            if name_lower not in existing_names:
                merged_diagnoses.append(diag)

        result.diagnosis_set = DiagnosisSet(
            entity=result.diagnosis_set.entity,
            capability=result.diagnosis_set.capability,
            diagnoses=merged_diagnoses,
        )

        # Re-register dependency-diagnosis claims with the enriched DiagnosisSet
        _register_dependency_diagnosis_claims(result.diagnosis_set, result.outcome_set, source_store)

        # Loop back to re-run Orchestrator with enriched DiagnosisSet
        continue

    if any(not v.passed for v in result.verification_results):
        result.verification_passed = False

    return result


run = run_pipeline


# ---------------------------------------------------------------------------
# Recalibration routing decision helpers
# ---------------------------------------------------------------------------

def _decide_scenario_fallback_target(
    scenario_set: ScenarioSet | None,
    stack_scope: StackScope | None,
    ingestion_context: IngestionContext | None,
) -> str:
    """Decide whether Scenario-Generation should fall back to Stack-Mapping or Ingestion.

    Routing policy (ARCHITECTURE.md §3.8, §6):
      - If Stack-Mapping layer scope is narrow (<= 2 layers), route to "stack_mapping"
        to broaden the architectural layer coverage.
      - If Stack-Mapping already has sufficient layers (> 2 layers) but Scenario-Generation
        could not produce viable concrete options (e.g. missing concrete vendor/solution data),
        route to "ingestion" to gather concrete market/vendor evidence.
      - If Ingestion has no options or no structured source content, route to "ingestion".

    Returns
    -------
    str
        "stack_mapping" or "ingestion"
    """
    layer_count = len(stack_scope.layers) if stack_scope and stack_scope.layers else 0
    if layer_count <= 2:
        return "stack_mapping"
    return "ingestion"


def _find_deficient_paths(verdict: OrchestratorVerdict | None) -> list[str]:
    """Return path names that show asymmetric completeness in the cross-path comparison.

    A path is considered "deficient" if its ``PathComparison.lock_in_count == 0``
    (no identified lock-ins) while **at least one other** path has a non-zero
    ``lock_in_count``.  This indicates the Orchestrator received incomplete
    Dependency-Diagnosis data for that path and its cross-path comparison is
    therefore skewed.

    Parameters
    ----------
    verdict:
        The :class:`~app.agents.orchestrator.orchestrator_agent.OrchestratorVerdict`
        returned by the Orchestrator.

    Returns
    -------
    list[str]
        Names of deficient paths, or an empty list if all paths have comparable
        completeness or if no cross-path comparison data is available.
    """
    if not verdict or not verdict.cross_path_comparison:
        return []
    path_comparisons = verdict.cross_path_comparison.path_comparisons
    if len(path_comparisons) < 2:
        # Cannot determine asymmetry with a single path
        return []
    any_with_lockins = any(pc.lock_in_count > 0 for pc in path_comparisons)
    if not any_with_lockins:
        # All paths have no lock-ins — symmetrically empty, not asymmetric
        return []
    return [pc.scenario_name for pc in path_comparisons if pc.lock_in_count == 0]


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
