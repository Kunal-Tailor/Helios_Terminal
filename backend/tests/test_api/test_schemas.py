"""
Unit tests for API Pydantic schemas (app.api.schemas.decision).
"""

import pytest
from pydantic import ValidationError

from app.agents.orchestrator.orchestrator_agent import OrchestratorVerdict
from app.agents.orchestrator.sub_agents.cross_path_comparison_sub_agent import CrossPathComparison, PathComparison
from app.agents.orchestrator.sub_agents.explanation_trail_sub_agent import AuditStep, ExplanationTrail
from app.api.schemas import (
    DecisionRequest,
    DecisionResponse,
    OrchestratorVerdictSchema,
    RecalibrationRequestSchema,
    RecalibrationTrailItemSchema,
)
from app.pipeline.graph import PipelineResult
from app.verification.recalibration import RecalibrationRequest
from app.verification.verifier import VerificationResult


def test_decision_request_valid():
    """Verify valid DecisionRequest creation and dict serialization."""
    req = DecisionRequest(
        entity="Indian Army signals division",
        capability="small language model for edge inference",
        options=["build in-house", "license open-weight"],
    )
    assert req.entity == "Indian Army signals division"
    assert req.capability == "small language model for edge inference"
    assert req.options == ["build in-house", "license open-weight"]

    data = req.model_dump()
    assert data["entity"] == "Indian Army signals division"
    assert data["options"] == ["build in-house", "license open-weight"]


def test_decision_request_validation_error():
    """Verify validation error when entity or capability is empty."""
    with pytest.raises(ValidationError):
        DecisionRequest(entity="", capability="edge inference")

    with pytest.raises(ValidationError):
        DecisionRequest(entity="Army", capability="")


def test_orchestrator_verdict_schema_from_dataclass():
    """Verify conversion from OrchestratorVerdict dataclass to OrchestratorVerdictSchema."""
    verdict = OrchestratorVerdict(
        entity="ACME Corp",
        capability="Speech Recognition",
        recommended_path="License Open-Weight Model",
        verdict_summary="License open weights model for edge offline autonomy.",
        key_recommendations=["Recommendation 1", "Recommendation 2"],
        path_stances={"License Open-Weight Model": "Recommended"},
        cross_path_comparison=CrossPathComparison(
            comparative_narrative="Open weights outperforms proprietary APIs for offline edge.",
            path_comparisons=[
                PathComparison(
                    scenario_name="License Open-Weight Model",
                    lock_in_count=1,
                    max_severity_score=6.5,
                    key_tradeoffs=["Upstream dependency vs autonomy"],
                    path_summary="Solid choice.",
                )
            ],
        ),
        explanation_trail=ExplanationTrail(
            summary="Reasoning trail summary.",
            steps=[AuditStep(stage="Ingestion", claim="Offline requirement", evidence="Brief text")],
            sources=["https://example.com/source"],
        ),
    )

    schema = OrchestratorVerdictSchema.from_dataclass(verdict)
    assert schema.entity == "ACME Corp"
    assert schema.recommended_path == "License Open-Weight Model"
    assert len(schema.key_recommendations) == 2
    assert schema.cross_path_comparison is not None
    assert schema.cross_path_comparison.comparative_narrative == "Open weights outperforms proprietary APIs for offline edge."
    assert len(schema.cross_path_comparison.path_comparisons) == 1
    assert schema.explanation_trail is not None
    assert len(schema.explanation_trail.steps) == 1
    assert schema.explanation_trail.steps[0].stage == "Ingestion"


def test_decision_response_from_pipeline_result():
    """Verify conversion from PipelineResult dataclass to DecisionResponse Pydantic model."""
    verdict = OrchestratorVerdict(
        entity="ACME Corp",
        capability="Speech Recognition",
        recommended_path="License Open-Weight Model",
        verdict_summary="Executive summary text.",
    )
    vr = VerificationResult(
        passed=True,
        confidence=0.9,
        reason="90% keywords matched",
        claim="Offline requirement",
        agent_stage="ingestion",
    )
    res = PipelineResult(
        entity="ACME Corp",
        capability="Speech Recognition",
        options=["build", "buy"],
        verdict=verdict,
        verification_passed=True,
        verification_failed_stage=None,
        verification_results=[vr],
    )

    resp = DecisionResponse.from_pipeline_result(res)
    assert resp.entity == "ACME Corp"
    assert resp.capability == "Speech Recognition"
    assert resp.options == ["build", "buy"]
    assert resp.verdict is not None
    assert resp.verdict.recommended_path == "License Open-Weight Model"
    assert resp.verification_passed is True
    assert len(resp.verification_results) == 1
    assert resp.verification_results[0].passed is True
    assert resp.verification_results[0].agent_stage == "ingestion"
    assert resp.recalibration_trail == []
    assert resp.partial_verdict_caveats == []


def test_recalibration_request_schema_from_dataclass_and_dict():
    """Verify RecalibrationRequestSchema construction from dataclass and dict."""
    req_dc = RecalibrationRequest(
        from_stage="stack_mapping",
        to_stage="ingestion",
        reason="insufficient",
        gap_description="Only 1 surviving layer; need additional grounding facts.",
        iteration_count=1,
    )
    schema = RecalibrationRequestSchema.from_dataclass(req_dc)
    assert schema.from_stage == "stack_mapping"
    assert schema.to_stage == "ingestion"
    assert schema.reason == "insufficient"
    assert schema.gap_description == "Only 1 surviving layer; need additional grounding facts."
    assert schema.iteration_count == 1

    dump = schema.model_dump()
    assert dump["from_stage"] == "stack_mapping"
    assert dump["iteration_count"] == 1

    # Also test from_dataclass with dict input
    schema2 = RecalibrationTrailItemSchema.from_dataclass(dump)
    assert schema2.from_stage == "stack_mapping"
    assert schema2.iteration_count == 1


def test_decision_response_with_recalibration_trail():
    """Verify DecisionResponse serialization with non-empty recalibration_trail."""
    verdict = OrchestratorVerdict(
        entity="ACME Corp",
        capability="Speech Recognition",
        recommended_path="Build",
        verdict_summary="Build path recommended.",
    )
    req1 = RecalibrationRequest(
        from_stage="stack_mapping",
        to_stage="ingestion",
        reason="insufficient",
        gap_description="Insufficient layer mapping.",
        iteration_count=1,
    )
    req2 = RecalibrationRequest(
        from_stage="scenario_generation",
        to_stage="stack_mapping",
        reason="insufficient",
        gap_description="Fewer than 2 scenarios generated.",
        iteration_count=1,
    )
    res = PipelineResult(
        entity="ACME Corp",
        capability="Speech Recognition",
        options=["build", "buy"],
        verdict=verdict,
        verification_passed=True,
        recalibration_trail=[req1, req2],
        partial_verdict_caveats=["Caveat: retry cap hit on stage pair."],
    )

    resp = DecisionResponse.from_pipeline_result(res)
    assert len(resp.recalibration_trail) == 2
    assert resp.recalibration_trail[0].from_stage == "stack_mapping"
    assert resp.recalibration_trail[0].to_stage == "ingestion"
    assert resp.recalibration_trail[1].from_stage == "scenario_generation"
    assert resp.recalibration_trail[1].to_stage == "stack_mapping"
    assert len(resp.partial_verdict_caveats) == 1

    dump = resp.model_dump()
    assert len(dump["recalibration_trail"]) == 2
    assert dump["recalibration_trail"][0]["from_stage"] == "stack_mapping"
    assert dump["recalibration_trail"][1]["to_stage"] == "stack_mapping"
    assert dump["partial_verdict_caveats"] == ["Caveat: retry cap hit on stage pair."]
