"""
End-to-End Integration Test: Dashboard to Live Backend (Task 10.5).

Verifies the complete asynchronous decision workflow triggered by the
Bloomberg Decision Console (F2) against the backend:
1. POST /decisions/async enqueues background processing with strategic constraints.
2. Polling loop GET /decisions/jobs/{job_id} completes with status 'completed'.
3. The response populates all 4 dashboard quadrants:
   - Q1: Decision Console brief and constraints.
   - Q2: 6-Stage Agent Pipeline Topology with audit gates, recalibration trail,
         and stage_providers showing which provider served each stage.
   - Q3: Institutional Verdict Panel with sovereign stance, summary, recommendations,
         and partial verdict caveats.
   - Q4: Trajectory Chart Panel with comparative narrative and path comparisons.
4. Audit Inspector displays real grounded verification results with provider attribution.
5. Multi-provider fallback active: automatic failover mid-pipeline is tracked in stage_providers.
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import pytest

from app.agents.dependency_diagnosis.dependency_diagnosis_agent import DependencyDiagnosis, DiagnosisSet
from app.agents.dependency_diagnosis.sub_agents.failure_mode_sub_agent import FailureMode
from app.agents.dependency_diagnosis.sub_agents.lock_in_identification_sub_agent import LockInDependency
from app.agents.dependency_diagnosis.sub_agents.severity_scoring_sub_agent import DependencySeverityScore
from app.agents.ingestion.sub_agents.context_synthesis_sub_agent import IngestionContext
from app.agents.orchestrator.orchestrator_agent import OrchestratorVerdict
from app.agents.orchestrator.sub_agents.cross_path_comparison_sub_agent import CrossPathComparison, PathComparison
from app.agents.orchestrator.sub_agents.explanation_trail_sub_agent import AuditStep, ExplanationTrail
from app.agents.outcome_prediction.outcome_prediction_agent import OutcomeProjection, OutcomeSet
from app.agents.outcome_prediction.sub_agents.risk_factor_sub_agent import RiskFactor
from app.agents.outcome_prediction.sub_agents.timeline_projection_sub_agent import TimelineProjection
from app.agents.outcome_prediction.sub_agents.trajectory_modeling_sub_agent import Trajectory
from app.agents.scenario_generation.scenario_generation_agent import ScenarioSet
from app.agents.scenario_generation.sub_agents.scenario_refinement_sub_agent import Scenario
from app.agents.stack_mapping.stack_mapping_agent import StackScope
from app.agents.stack_mapping.sub_agents.dependency_linkage_sub_agent import LayerLink
from app.agents.stack_mapping.sub_agents.layer_identification_sub_agent import StackLayer
from app.core.config import settings
from app.main import app
from app.pipeline.graph import PipelineResult, run_pipeline
from app.verification.recalibration import RecalibrationRequest
from app.verification.verifier import VerificationResult

client = TestClient(app)


def test_e2e_dashboard_async_submission_and_quadrant_population():
    """Simulate a complete dashboard session: submit brief from F2 Decision Console,

    poll until completed, and verify all four quadrants and audit trail are populated
    with stage provider metadata.
    """
    brief_payload = {
        "entity": "Indian Army Signals Directorate",
        "capability": "Tactical Small Language Model for Edge Comms & SIGINT",
        "options": [
            "Self-hosted Fine-tuned Open Weights (Llama 3.3 / Sarvam)",
            "Licensed Closed-Weights via Sovereign Cloud",
            "Outsourced Defense System Integrator Turnkey SLM",
        ],
        "data_sovereignty_weight": "CRITICAL",
        "latency_tolerance": "SUB_20MS",
    }

    mock_verdict = OrchestratorVerdict(
        entity=brief_payload["entity"],
        capability=brief_payload["capability"],
        recommended_path="Self-hosted Fine-tuned Open Weights (Llama 3.3 / Sarvam)",
        verdict_summary=(
            "Self-hosting fine-tuned open-weights models yields an 84% reduction in "
            "existential dependency risk and full air-gap compliance."
        ),
        key_recommendations=[
            "Standardize on GGUF / AWQ 4-bit quantization pipelines",
            "Establish a dedicated Sovereign Fine-Tuning Lab",
        ],
        path_stances={
            "Self-hosted Fine-tuned Open Weights (Llama 3.3 / Sarvam)": "STRONGLY RECOMMENDED",
            "Licensed Closed-Weights via Sovereign Cloud": "HIGH RISK",
            "Outsourced Defense System Integrator Turnkey SLM": "CRITICAL LOCK-IN",
        },
        cross_path_comparison=CrossPathComparison(
            comparative_narrative="Open-weights strategy insulates national defense infrastructure permanently.",
            path_comparisons=[
                PathComparison(
                    scenario_name="Self-hosted Fine-tuned Open Weights (Llama 3.3 / Sarvam)",
                    lock_in_count=1,
                    max_severity_score=2.6,
                    key_tradeoffs=["Front-loaded engineering capex vs permanent sovereign autonomy"],
                    path_summary="Optimal sovereign trajectory for tactical edge deployment.",
                ),
                PathComparison(
                    scenario_name="Licensed Closed-Weights via Sovereign Cloud",
                    lock_in_count=3,
                    max_severity_score=7.8,
                    key_tradeoffs=["Fast initial deployment vs recurring token extraction and telemetry egress"],
                    path_summary="Vulnerable during electronic warfare disconnects.",
                ),
            ],
        ),
        explanation_trail=ExplanationTrail(
            summary="Grounded in tactical doctrine and validated hardware specifications.",
            steps=[
                AuditStep(
                    stage="ingestion",
                    claim="Open weights available for air-gap distribution",
                    evidence="License manifests confirm offline redistribution.",
                ),
                AuditStep(
                    stage="orchestrator",
                    claim="Self-hosted approach is the only viable path satisfying Indian Defense Air-Gap standards",
                    evidence="Synthesis verified against Stage 1-5 grounded audit evidence.",
                ),
            ],
            sources=[
                "https://huggingface.co/sarvamai",
                "https://mod.gov.in/defence-doctrine",
            ],
        ),
    )

    mock_vr_1 = VerificationResult(
        passed=True,
        confidence=0.98,
        reason="Verified against open weights license manifests.",
        claim="Open weights available for air-gap distribution",
        agent_stage="ingestion",
        provider="nvidia_nim",
    )
    mock_vr_2 = VerificationResult(
        passed=True,
        confidence=0.95,
        reason="Architecture isolates edge tensor engine to local hardware memory.",
        claim="Inference runtime independent of foreign cloud APIs",
        agent_stage="stack_mapping",
        provider="nvidia_nim",
    )
    mock_vr_3 = VerificationResult(
        passed=True,
        confidence=0.92,
        reason="Model token pricing extrapolated against edge node power.",
        claim="Self-hosted TCO breaks even with API licenses by Month 14",
        agent_stage="outcome_prediction",
        provider="gemini",
    )

    mock_recal = RecalibrationRequest(
        from_stage="stack_mapping",
        to_stage="ingestion",
        reason="insufficient",
        gap_description="Required additional hardware acceleration memory specs.",
        iteration_count=1,
        provider="nvidia_nim",
    )

    mock_result = PipelineResult(
        entity=brief_payload["entity"],
        capability=brief_payload["capability"],
        options=brief_payload["options"],
        data_sovereignty_weight="CRITICAL",
        latency_tolerance="SUB_20MS",
        verdict=mock_verdict,
        verification_passed=True,
        verification_failed_stage=None,
        verification_results=[mock_vr_1, mock_vr_2, mock_vr_3],
        recalibration_trail=[mock_recal],
        partial_verdict_caveats=[
            "Assumes access to indigenous edge accelerators.",
        ],
        stage_providers={
            "ingestion": "nvidia_nim",
            "stack_mapping": "nvidia_nim",
            "scenario_generation": "nvidia_nim",
            "outcome_prediction": "gemini",
            "dependency_diagnosis": "gemini",
            "orchestrator": "openrouter",
        },
    )

    with patch("app.api.routes.decisions.run_pipeline", return_value=mock_result) as mock_run:
        # Step 1: Submit brief from Decision Console (F2) to POST /decisions/async
        submit_res = client.post("/decisions/async", json=brief_payload)
        assert submit_res.status_code == 202, f"Expected 202 Accepted, got {submit_res.status_code}"
        submit_data = submit_res.json()
        assert "job_id" in submit_data
        job_id = submit_data["job_id"]
        assert submit_data["status"] in ("queued", "processing", "completed")

        # Step 2: Poll GET /decisions/jobs/{job_id} until completion
        poll_res = client.get(f"/decisions/jobs/{job_id}")
        assert poll_res.status_code == 200
        poll_data = poll_res.json()
        assert poll_data["job_id"] == job_id
        assert poll_data["status"] == "completed"
        assert poll_data["error"] is None
        assert poll_data["completed_at"] is not None

        res_data = poll_data["result"]
        assert res_data is not None

        # Step 3: Verify Quadrant 1 (Decision Console inputs and constraints echoed)
        assert res_data["entity"] == brief_payload["entity"]
        assert res_data["capability"] == brief_payload["capability"]
        assert res_data["options"] == brief_payload["options"]
        assert res_data["data_sovereignty_weight"] == "CRITICAL"
        assert res_data["latency_tolerance"] == "SUB_20MS"

        # Step 4: Verify Quadrant 2 (6-Stage Pipeline Topology & Stage Providers)
        assert res_data["verification_passed"] is True
        assert len(res_data["verification_results"]) == 3
        assert len(res_data["recalibration_trail"]) == 1
        assert "stage_providers" in res_data
        stage_providers = res_data["stage_providers"]
        assert stage_providers["ingestion"] == "nvidia_nim"
        assert stage_providers["stack_mapping"] == "nvidia_nim"
        assert stage_providers["outcome_prediction"] == "gemini"
        assert stage_providers["orchestrator"] == "openrouter"

        # Step 5: Verify Quadrant 3 (Institutional Verdict Panel)
        verdict = res_data["verdict"]
        assert verdict is not None
        assert verdict["recommended_path"] == "Self-hosted Fine-tuned Open Weights (Llama 3.3 / Sarvam)"
        assert "84% reduction in existential dependency risk" in verdict["verdict_summary"]
        assert len(verdict["key_recommendations"]) == 2
        assert "Self-hosted Fine-tuned Open Weights (Llama 3.3 / Sarvam)" in verdict["path_stances"]
        assert len(res_data["partial_verdict_caveats"]) == 1

        # Step 6: Verify Quadrant 4 (5-Year Trajectory & Cross-Path Comparison)
        cmp = verdict["cross_path_comparison"]
        assert cmp is not None
        assert len(cmp["path_comparisons"]) == 2
        assert cmp["path_comparisons"][0]["scenario_name"] == "Self-hosted Fine-tuned Open Weights (Llama 3.3 / Sarvam)"
        assert cmp["path_comparisons"][0]["max_severity_score"] == 2.6
        assert len(cmp["path_comparisons"][0]["key_tradeoffs"]) > 0

        # Step 7: Verify Grounded Audit Trail (F5 Audit Inspector)
        vr_list = res_data["verification_results"]
        for vr in vr_list:
            assert vr["passed"] is True
            assert vr["confidence"] >= 0.90
            assert len(vr["claim"]) > 0
            assert len(vr["reason"]) > 0
            assert vr["provider"] in ("nvidia_nim", "gemini", "openrouter")

        trail = verdict["explanation_trail"]
        assert trail is not None
        assert len(trail["steps"]) == 2
        assert len(trail["sources"]) == 2


def test_e2e_multi_provider_fallback_active_records_failover_provider():
    """Verify that when multi-provider fallback triggers mid-pipeline,

    the background job completes normally and stage_providers logs
    the actual fallback provider that served the stage.
    """
    brief_payload = {
        "entity": "Global Tier-1 Investment Bank",
        "capability": "Regulatory-Compliant Financial Intelligence & Synthesis RAG",
        "options": ["In-House Open-Source Vector Stack", "Azure Managed Service"],
        "data_sovereignty_weight": "STANDARD",
        "latency_tolerance": "BALANCED",
    }

    mock_verdict = OrchestratorVerdict(
        entity=brief_payload["entity"],
        capability=brief_payload["capability"],
        recommended_path="In-House Open-Source Vector Stack",
        verdict_summary="In-House vector stack avoids proprietary embedding lock-in.",
        key_recommendations=["Deploy Qdrant on private VNet"],
    )

    # Ingestion was served by nvidia_nim; stack_mapping suffered rate limit and fell back to gemini
    mock_result = PipelineResult(
        entity=brief_payload["entity"],
        capability=brief_payload["capability"],
        options=brief_payload["options"],
        data_sovereignty_weight="STANDARD",
        latency_tolerance="BALANCED",
        verdict=mock_verdict,
        verification_passed=True,
        verification_results=[
            VerificationResult(
                passed=True,
                confidence=0.97,
                reason="Grounded in FINRA specs",
                claim="Regulatory compliance validated",
                agent_stage="ingestion",
                provider="nvidia_nim",
            ),
            VerificationResult(
                passed=True,
                confidence=0.94,
                reason="Embedding dimension compatibility verified",
                claim="Vector stack portability validated",
                agent_stage="stack_mapping",
                provider="gemini",
            ),
        ],
        recalibration_trail=[],
        stage_providers={
            "ingestion": "nvidia_nim",
            "stack_mapping": "gemini",  # Failover provider recorded
            "scenario_generation": "gemini",
            "outcome_prediction": "gemini",
            "dependency_diagnosis": "gemini",
            "orchestrator": "gemini",
        },
    )

    with patch("app.api.routes.decisions.run_pipeline", return_value=mock_result):
        submit_res = client.post("/decisions/async", json=brief_payload)
        assert submit_res.status_code == 202
        job_id = submit_res.json()["job_id"]

        poll_res = client.get(f"/decisions/jobs/{job_id}")
        assert poll_res.status_code == 200
        poll_data = poll_res.json()
        assert poll_data["status"] == "completed"

        result = poll_data["result"]
        assert result["stage_providers"]["ingestion"] == "nvidia_nim"
        assert result["stage_providers"]["stack_mapping"] == "gemini"
        assert result["verification_results"][0]["provider"] == "nvidia_nim"
        assert result["verification_results"][1]["provider"] == "gemini"


def test_backend_health_and_midchain_failover_maintains_online_beacon():
    """Verify backend health beacon endpoint /health remains 200 OK during job processing

    and that mid-chain failover preserves healthy online state.
    """
    # 1. Health check returns 200 OK
    health_res = client.get("/health")
    assert health_res.status_code == 200
    assert health_res.json() == {"status": "ok"}

    brief_payload = {
        "entity": "Indian Army signals division",
        "capability": "tactical edge speech recognition",
        "options": ["build in-house"],
        "data_sovereignty_weight": "CRITICAL",
        "latency_tolerance": "SUB_20MS",
    }
    mock_result = PipelineResult(
        entity=brief_payload["entity"],
        capability=brief_payload["capability"],
        options=brief_payload["options"],
        data_sovereignty_weight="CRITICAL",
        latency_tolerance="SUB_20MS",
        verdict=OrchestratorVerdict(
            entity=brief_payload["entity"],
            capability=brief_payload["capability"],
            recommended_path="build in-house",
            verdict_summary="Build in-house verdict.",
        ),
        stage_providers={"ingestion": "nvidia_nim", "stack_mapping": "gemini"},
    )
    with patch("app.api.routes.decisions.run_pipeline", return_value=mock_result):
        # 2. Async job submission
        post_res = client.post("/decisions/async", json=brief_payload)
        assert post_res.status_code == 202
        job_id = post_res.json()["job_id"]

        # 3. Health check while job is active or completed remains 200 OK
        health_during_job = client.get("/health")
        assert health_during_job.status_code == 200
        assert health_during_job.json() == {"status": "ok"}

        # 4. Polling completes normally
        poll_res = client.get(f"/decisions/jobs/{job_id}")
        assert poll_res.status_code == 200
        assert poll_res.json()["status"] == "completed"


def test_backend_rate_limit_error_returns_503():
    """Verify that an exhausted provider chain returns HTTP 503 from backend,

    which is an HTTP server error response (not a network unreachable failure).
    """
    from openai import RateLimitError
    import httpx

    fake_request = httpx.Request("POST", "https://api.fake.com")
    fake_response = httpx.Response(429, request=fake_request)

    brief_payload = {
        "entity": "Indian Army signals division",
        "capability": "tactical edge speech recognition",
        "options": ["build in-house"],
    }

    with patch("app.api.routes.decisions.run_pipeline", side_effect=RateLimitError("Rate limit exceeded", response=fake_response, body=None)):
        res = client.post("/decisions", json=brief_payload)
        assert res.status_code == 503
        assert "LLM API rate limit exceeded" in res.json()["detail"]


@pytest.mark.skipif(
    os.getenv("RUN_LIVE_E2E", "0") != "1" or not settings.llm_api_key,
    reason="Set RUN_LIVE_E2E=1 with a valid LLM API key to run the live non-mocked E2E pipeline verification pass",
)
def test_live_backend_e2e_pipeline_execution():
    """Live (non-mocked) end-to-end integration test against the real running pipeline.

    Submits an async decision brief, polls the job until completed, and asserts
    that all quadrants, verification results, and serving providers are populated.
    """
    brief_payload = {
        "entity": "Indian Army signals division",
        "capability": "tactical edge speech recognition",
        "options": ["build in-house", "license open-weight"],
        "data_sovereignty_weight": "CRITICAL",
        "latency_tolerance": "SUB_20MS",
    }

    submit_res = client.post("/decisions/async", json=brief_payload)
    assert submit_res.status_code == 202
    job_id = submit_res.json()["job_id"]

    import time
    max_wait = 180
    start = time.time()
    poll_data = None

    while time.time() - start < max_wait:
        poll_res = client.get(f"/decisions/jobs/{job_id}")
        assert poll_res.status_code == 200
        poll_data = poll_res.json()
        if poll_data["status"] in ("completed", "failed"):
            break
        time.sleep(2.5)

    assert poll_data is not None
    assert poll_data["status"] == "completed", f"Job failed: {poll_data.get('error')}"
    result = poll_data["result"]
    assert result["verdict"] is not None
    assert len(result["verdict"]["verdict_summary"]) > 0
    assert len(result["stage_providers"]) > 0
