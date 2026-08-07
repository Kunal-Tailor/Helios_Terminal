"""
Decision API Schemas — Pydantic models for decision brief request, verdict response, and async jobs.

Public API
----------
    DecisionRequest
        Pydantic input schema for POST /decisions request body.
    DecisionResponse
        Pydantic response schema returning pipeline verdict and verification metadata.
    OrchestratorVerdictSchema
        Nested response schema for OrchestratorVerdict data.
    JobStatusResponse
        Response schema for async background decision processing jobs.
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field

from app.agents.orchestrator.orchestrator_agent import OrchestratorVerdict
from app.pipeline.graph import PipelineResult


class DecisionRequest(BaseModel):
    """Input payload for submitting an AI sourcing decision brief."""

    entity: str = Field(
        ...,
        min_length=1,
        description="The organisation or unit making the AI sourcing decision.",
        json_schema_extra={"example": "Indian Army signals division"},
    )
    capability: str = Field(
        ...,
        min_length=1,
        description="The AI capability being sourced.",
        json_schema_extra={"example": "small language model for edge inference"},
    )
    options: list[str] = Field(
        default_factory=list,
        description="Optional list of candidate sourcing options.",
        json_schema_extra={"example": ["build in-house", "license open-weight"]},
    )


class AuditStepSchema(BaseModel):
    """Audit step record in explanation trail."""

    stage: str
    claim: str
    evidence: str


class ExplanationTrailSchema(BaseModel):
    """Audit reasoning trail supporting the final verdict."""

    summary: str = ""
    steps: list[AuditStepSchema] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)


class PathComparisonSchema(BaseModel):
    """Side-by-side comparative metric for a single scenario path."""

    scenario_name: str
    lock_in_count: int = 0
    max_severity_score: float = 0.0
    key_tradeoffs: list[str] = Field(default_factory=list)
    path_summary: str = ""


class CrossPathComparisonSchema(BaseModel):
    """Cross-path comparative analysis breakdown."""

    comparative_narrative: str = ""
    path_comparisons: list[PathComparisonSchema] = Field(default_factory=list)


class VerificationResultSchema(BaseModel):
    """Verification result record per claim."""

    passed: bool
    confidence: float
    reason: str
    claim: str
    agent_stage: str


class OrchestratorVerdictSchema(BaseModel):
    """Verdict response schema produced by the Orchestrator stage."""

    entity: str
    capability: str
    recommended_path: str = ""
    verdict_summary: str = ""
    key_recommendations: list[str] = Field(default_factory=list)
    path_stances: dict[str, str] = Field(default_factory=dict)
    cross_path_comparison: Optional[CrossPathComparisonSchema] = None
    explanation_trail: Optional[ExplanationTrailSchema] = None

    @classmethod
    def from_dataclass(cls, verdict: OrchestratorVerdict) -> OrchestratorVerdictSchema:
        """Construct schema from OrchestratorVerdict dataclass."""
        cpc = None
        if verdict.cross_path_comparison:
            path_comps = [
                PathComparisonSchema(
                    scenario_name=pc.scenario_name,
                    lock_in_count=pc.lock_in_count,
                    max_severity_score=pc.max_severity_score,
                    key_tradeoffs=list(pc.key_tradeoffs),
                    path_summary=pc.path_summary,
                )
                for pc in verdict.cross_path_comparison.path_comparisons
            ]
            cpc = CrossPathComparisonSchema(
                comparative_narrative=verdict.cross_path_comparison.comparative_narrative,
                path_comparisons=path_comps,
            )

        et = None
        if verdict.explanation_trail:
            steps = [
                AuditStepSchema(stage=s.stage, claim=s.claim, evidence=s.evidence)
                for s in verdict.explanation_trail.steps
            ]
            et = ExplanationTrailSchema(
                summary=verdict.explanation_trail.summary,
                steps=steps,
                sources=list(verdict.explanation_trail.sources),
            )

        return cls(
            entity=verdict.entity,
            capability=verdict.capability,
            recommended_path=verdict.recommended_path,
            verdict_summary=verdict.verdict_summary,
            key_recommendations=list(verdict.key_recommendations),
            path_stances=dict(verdict.path_stances),
            cross_path_comparison=cpc,
            explanation_trail=et,
        )


class DecisionResponse(BaseModel):
    """Full decision pipeline response payload returned to the client."""

    entity: str
    capability: str
    options: list[str] = Field(default_factory=list)
    verdict: Optional[OrchestratorVerdictSchema] = None
    verification_passed: bool = True
    verification_failed_stage: Optional[str] = None
    verification_results: list[VerificationResultSchema] = Field(default_factory=list)

    @classmethod
    def from_pipeline_result(cls, res: PipelineResult) -> DecisionResponse:
        """Construct response model from PipelineResult dataclass."""
        verdict_schema = (
            OrchestratorVerdictSchema.from_dataclass(res.verdict)
            if res.verdict
            else None
        )
        ver_results = [
            VerificationResultSchema(
                passed=vr.passed,
                confidence=vr.confidence,
                reason=vr.reason,
                claim=vr.claim,
                agent_stage=vr.agent_stage,
            )
            for vr in res.verification_results
        ]

        return cls(
            entity=res.entity,
            capability=res.capability,
            options=list(res.options),
            verdict=verdict_schema,
            verification_passed=res.verification_passed,
            verification_failed_stage=res.verification_failed_stage,
            verification_results=ver_results,
        )


class JobStatusResponse(BaseModel):
    """Async background decision processing job status payload."""

    job_id: str = Field(..., description="Unique background job UUID")
    status: str = Field(..., description="Execution status: queued, processing, completed, failed")
    created_at: str = Field(..., description="ISO 8601 timestamp when job was enqueued")
    completed_at: Optional[str] = Field(None, description="ISO 8601 timestamp when job finished")
    result: Optional[DecisionResponse] = Field(None, description="Decision verdict response if completed")
    error: Optional[str] = Field(None, description="Error details if execution failed")
