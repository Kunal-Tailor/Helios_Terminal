"""
Decisions API Route — Synchronous & Asynchronous decision processing endpoints.

Public API
----------
    POST /decisions
        Accepts a DecisionRequest brief (entity, capability, options),
        runs the 6-stage sequential AI sourcing pipeline synchronously,
        and returns a DecisionResponse containing the verdict and verification audit.

    POST /decisions/async
        Enqueues an asynchronous background job to process the brief and returns a JobStatusResponse.

    GET /decisions/jobs/{job_id}
        Retrieves the status and result of a background decision job.
"""

from __future__ import annotations

from datetime import datetime, timezone
import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from openai import RateLimitError

from app.api.schemas import DecisionRequest, DecisionResponse, JobStatusResponse
from app.pipeline.graph import run_pipeline

router = APIRouter(tags=["decisions"])

# In-memory background job store
JOBS: dict[str, JobStatusResponse] = {}


@router.post(
    "/decisions",
    response_model=DecisionResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate an AI sourcing decision brief (synchronous)",
    description=(
        "Submits an AI sourcing decision brief (entity, capability, candidate options), "
        "executes the 6-stage multi-agent pipeline with verification gating synchronously, and "
        "returns the comparative verdict and audit trail."
    ),
)
def create_decision(brief: DecisionRequest) -> DecisionResponse:
    """Run the 6-stage AI sourcing pipeline synchronously for *brief*."""
    try:
        pipeline_result = run_pipeline(
            entity=brief.entity,
            capability=brief.capability,
            options=brief.options,
        )
        return DecisionResponse.from_pipeline_result(pipeline_result)
    except RateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM API rate limit exceeded. Please try again in a few moments.",
        )


@router.post(
    "/decisions/async",
    response_model=JobStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit an AI sourcing decision brief for async background processing",
    description=(
        "Enqueues an asynchronous background task to execute the 6-stage pipeline. "
        "Returns a job ID and status endpoint to poll for completion."
    ),
)
def create_decision_async(
    brief: DecisionRequest,
    background_tasks: BackgroundTasks,
) -> JobStatusResponse:
    """Enqueue an asynchronous background decision processing job."""
    job_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()

    job_status = JobStatusResponse(
        job_id=job_id,
        status="queued",
        created_at=now_iso,
    )
    JOBS[job_id] = job_status

    background_tasks.add_task(_process_decision_job, job_id, brief)
    return job_status


@router.get(
    "/decisions/jobs/{job_id}",
    response_model=JobStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get background decision job status",
    description="Returns the status and result (if completed) for the given background job ID.",
)
def get_decision_job(job_id: str) -> JobStatusResponse:
    """Retrieve job status for *job_id*."""
    if job_id not in JOBS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )
    return JOBS[job_id]


# ---------------------------------------------------------------------------
# Background Worker Function
# ---------------------------------------------------------------------------

def _process_decision_job(job_id: str, brief: DecisionRequest) -> None:
    """Execute background pipeline execution for *job_id*."""
    if job_id not in JOBS:
        return

    JOBS[job_id].status = "processing"
    try:
        pipeline_result = run_pipeline(
            entity=brief.entity,
            capability=brief.capability,
            options=brief.options,
        )
        response_model = DecisionResponse.from_pipeline_result(pipeline_result)
        JOBS[job_id].result = response_model
        JOBS[job_id].status = "completed"
        JOBS[job_id].completed_at = datetime.now(timezone.utc).isoformat()
    except RateLimitError as exc:
        JOBS[job_id].status = "failed"
        JOBS[job_id].error = f"LLM API rate limit exceeded: {exc}"
        JOBS[job_id].completed_at = datetime.now(timezone.utc).isoformat()
    except Exception as exc:
        JOBS[job_id].status = "failed"
        JOBS[job_id].error = str(exc)
        JOBS[job_id].completed_at = datetime.now(timezone.utc).isoformat()
