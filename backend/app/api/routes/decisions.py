"""
Decisions API Route — POST /decisions endpoint.

Public API
----------
    POST /decisions
        Accepts a DecisionRequest brief (entity, capability, options),
        runs the 6-stage sequential AI sourcing pipeline,
        and returns a DecisionResponse containing the verdict and verification audit.
"""

from __future__ import annotations

from fastapi import APIRouter, status

from app.api.schemas import DecisionRequest, DecisionResponse
from app.pipeline.graph import run_pipeline

router = APIRouter(tags=["decisions"])


@router.post(
    "/decisions",
    response_model=DecisionResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate an AI sourcing decision brief",
    description=(
        "Submits an AI sourcing decision brief (entity, capability, candidate options), "
        "executes the 6-stage multi-agent pipeline with verification gating, and "
        "returns the comparative verdict and audit trail."
    ),
)
def create_decision(brief: DecisionRequest) -> DecisionResponse:
    """Run the 6-stage AI sourcing pipeline synchronously for *brief*."""
    pipeline_result = run_pipeline(
        entity=brief.entity,
        capability=brief.capability,
        options=brief.options,
    )
    return DecisionResponse.from_pipeline_result(pipeline_result)
