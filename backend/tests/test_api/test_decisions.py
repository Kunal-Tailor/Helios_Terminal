"""
Integration tests for POST /decisions and async decision processing API endpoints (app.api.routes.decisions).
"""

from unittest.mock import patch
from fastapi.testclient import TestClient

from app.agents.dependency_diagnosis.dependency_diagnosis_agent import DependencyDiagnosis, DiagnosisSet
from app.agents.dependency_diagnosis.sub_agents.failure_mode_sub_agent import FailureMode
from app.agents.dependency_diagnosis.sub_agents.lock_in_identification_sub_agent import LockInDependency
from app.agents.ingestion.sub_agents.context_synthesis_sub_agent import IngestionContext
from app.agents.orchestrator.orchestrator_agent import OrchestratorVerdict
from app.agents.orchestrator.sub_agents.cross_path_comparison_sub_agent import CrossPathComparison, PathComparison
from app.agents.orchestrator.sub_agents.explanation_trail_sub_agent import AuditStep, ExplanationTrail
from app.agents.outcome_prediction.outcome_prediction_agent import OutcomeProjection, OutcomeSet
from app.agents.outcome_prediction.sub_agents.risk_factor_sub_agent import RiskFactor
from app.agents.outcome_prediction.sub_agents.trajectory_modeling_sub_agent import Trajectory
from app.agents.scenario_generation.scenario_generation_agent import ScenarioSet
from app.agents.scenario_generation.sub_agents.scenario_refinement_sub_agent import Scenario
from app.agents.stack_mapping.stack_mapping_agent import StackScope
from app.agents.stack_mapping.sub_agents.layer_identification_sub_agent import StackLayer
from app.main import app
from app.pipeline.graph import PipelineResult
from app.verification.recalibration import RecalibrationRequest

client = TestClient(app)


def test_post_decisions_endpoint_success():
    """Test POST /decisions returns 200 OK with valid verdict payload."""
    mock_verdict = OrchestratorVerdict(
        entity="Indian Army signals division",
        capability="small language model for edge inference",
        recommended_path="License Open-Weight Model",
        verdict_summary="License open-weight model is recommended due to tactical offline autonomy.",
        key_recommendations=["Pin weights hash", "Build in-house fine-tuning toolchain"],
        path_stances={"License Open-Weight Model": "Recommended"},
        cross_path_comparison=CrossPathComparison(
            comparative_narrative="Open weights offers better autonomy than proprietary API.",
            path_comparisons=[
                PathComparison(
                    scenario_name="License Open-Weight Model",
                    lock_in_count=1,
                    max_severity_score=7.5,
                    key_tradeoffs=["Upstream dependency vs autonomy"],
                    path_summary="Solid option.",
                )
            ],
        ),
        explanation_trail=ExplanationTrail(
            summary="Reasoning trail based on tactical requirements.",
            steps=[AuditStep(stage="Ingestion", claim="Offline requirement", evidence="Brief")],
            sources=["https://example.com/source1"],
        ),
    )

    mock_result = PipelineResult(
        entity="Indian Army signals division",
        capability="small language model for edge inference",
        options=["build in-house", "license open-weight"],
        verdict=mock_verdict,
        verification_passed=True,
    )

    payload = {
        "entity": "Indian Army signals division",
        "capability": "small language model for edge inference",
        "options": ["build in-house", "license open-weight"],
    }

    with patch("app.api.routes.decisions.run_pipeline", return_value=mock_result) as mock_run:
        response = client.post("/decisions", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["entity"] == "Indian Army signals division"
        assert data["capability"] == "small language model for edge inference"
        assert data["options"] == ["build in-house", "license open-weight"]
        assert data["verification_passed"] is True
        assert data["verdict"] is not None
        assert data["verdict"]["recommended_path"] == "License Open-Weight Model"
        assert data["verdict"]["verdict_summary"] == "License open-weight model is recommended due to tactical offline autonomy."
        assert "recalibration_trail" in data
        assert data["recalibration_trail"] == []

        mock_run.assert_called_once_with(
            entity="Indian Army signals division",
            capability="small language model for edge inference",
            options=["build in-house", "license open-weight"],
        )


def test_post_decisions_endpoint_surfaces_recalibration_trail():
    """Test POST /decisions surfaces recalibration_trail with backward stage routing metadata."""
    mock_verdict = OrchestratorVerdict(
        entity="Indian Army signals division",
        capability="small language model for edge inference",
        recommended_path="License Open-Weight Model",
        verdict_summary="License open-weight model recommended.",
    )

    mock_recal = RecalibrationRequest(
        from_stage="stack_mapping",
        to_stage="ingestion",
        reason="insufficient",
        gap_description="Only 1 surviving layer; need additional grounding facts.",
        iteration_count=1,
    )

    mock_result = PipelineResult(
        entity="Indian Army signals division",
        capability="small language model for edge inference",
        options=["build in-house", "license open-weight"],
        verdict=mock_verdict,
        verification_passed=True,
        recalibration_trail=[mock_recal],
        partial_verdict_caveats=["Constrained recalibration on stack_mapping -> ingestion."],
    )

    payload = {
        "entity": "Indian Army signals division",
        "capability": "small language model for edge inference",
        "options": ["build in-house", "license open-weight"],
    }

    with patch("app.api.routes.decisions.run_pipeline", return_value=mock_result):
        response = client.post("/decisions", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "recalibration_trail" in data
        assert len(data["recalibration_trail"]) == 1
        item = data["recalibration_trail"][0]
        assert item["from_stage"] == "stack_mapping"
        assert item["to_stage"] == "ingestion"
        assert item["reason"] == "insufficient"
        assert item["gap_description"] == "Only 1 surviving layer; need additional grounding facts."
        assert item["iteration_count"] == 1

        assert "partial_verdict_caveats" in data
        assert len(data["partial_verdict_caveats"]) == 1


def test_post_decisions_endpoint_validation_error():
    """Test POST /decisions returns 422 Unprocessable Entity when required fields are missing."""
    invalid_payload = {
        "entity": "Indian Army signals division",
        # Missing required capability field
    }

    response = client.post("/decisions", json=invalid_payload)
    assert response.status_code == 422
    errors = response.json()
    assert "detail" in errors


def test_post_decisions_endpoint_full_pipeline_flow():
    """Test POST /decisions endpoint flowing through the pipeline with mocked agent calls."""
    sample_context = IngestionContext(
        entity="ACME Corp",
        capability="Speech Recognition",
        options=["build", "buy"],
        context_summary="Speech Recognition requirements for ACME Corp model layer.",
        key_facts=["Speech Recognition requirements."],
        sources=["https://example.com"],
    )

    sample_scope = StackScope(
        entity="ACME Corp",
        capability="Speech Recognition",
        layers=[
            StackLayer(name="Model", rationale="Speech Recognition requirements", evidence="Speech Recognition requirements for ACME Corp model layer."),
            StackLayer(name="Audio Infra", rationale="Speech Recognition requirements", evidence="Speech Recognition requirements for ACME Corp model layer."),
        ],
        links=[],
    )

    sample_scenarios = ScenarioSet(
        entity="ACME Corp",
        capability="Speech Recognition",
        scenarios=[
            Scenario(name="Build", option_name="build", description="Speech Recognition requirements"),
            Scenario(name="Buy", option_name="buy", description="Speech Recognition requirements"),
        ],
    )

    sample_outcomes = OutcomeSet(
        entity="ACME Corp",
        capability="Speech Recognition",
        outcomes=[
            OutcomeProjection(
                scenario_name="Build",
                trajectory=Trajectory(
                    scenario_name="Build",
                    summary="Speech Recognition requirements",
                ),
                risk_factors=[
                    RiskFactor(scenario_name="Build", factor_name="Risk", description="Desc")
                ],
            )
        ],
    )

    sample_diagnoses = DiagnosisSet(
        entity="ACME Corp",
        capability="Speech Recognition",
        diagnoses=[
            DependencyDiagnosis(
                scenario_name="Build",
                dependencies=[
                    LockInDependency(
                        scenario_name="Build",
                        dependency_name="Vendor",
                        lock_in_type="Vendor",
                        description="Speech Recognition vendor lock-in",
                    )
                ],
                failure_modes=[
                    FailureMode(
                        scenario_name="Build",
                        dependency_name="Vendor",
                        failure_mode_title="Title",
                        what_breaks="Speech Recognition requirements",
                    )
                ],
            )
        ],
    )

    sample_verdict = OrchestratorVerdict(
        entity="ACME Corp",
        capability="Speech Recognition",
        recommended_path="Build",
        verdict_summary="Recommended to build.",
    )

    payload = {
        "entity": "ACME Corp",
        "capability": "Speech Recognition",
        "options": ["build", "buy"],
    }

    with patch("app.agents.ingestion.ingestion_agent.run", return_value=sample_context), \
         patch("app.agents.stack_mapping.stack_mapping_agent.run", return_value=sample_scope), \
         patch("app.agents.scenario_generation.scenario_generation_agent.run", return_value=sample_scenarios), \
         patch("app.agents.outcome_prediction.outcome_prediction_agent.run", return_value=sample_outcomes), \
         patch("app.agents.dependency_diagnosis.dependency_diagnosis_agent.run", return_value=sample_diagnoses), \
         patch("app.agents.orchestrator.orchestrator_agent.run", return_value=sample_verdict):

        response = client.post("/decisions", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["entity"] == "ACME Corp"
        assert data["capability"] == "Speech Recognition"
        assert data["verdict"]["recommended_path"] == "Build"
        assert "recalibration_trail" in data
        assert data["recalibration_trail"] == []


def test_post_decisions_async_and_get_job_status():
    """Test POST /decisions/async enqueues job and GET /decisions/jobs/{job_id} retrieves status."""
    payload = {
        "entity": "Indian Army signals division",
        "capability": "small language model for edge inference",
        "options": ["build in-house"],
    }

    mock_verdict = OrchestratorVerdict(
        entity="Indian Army signals division",
        capability="small language model for edge inference",
        recommended_path="Build",
        verdict_summary="Summary",
    )
    mock_result = PipelineResult(
        entity="Indian Army signals division",
        capability="small language model for edge inference",
        options=["build in-house"],
        verdict=mock_verdict,
    )

    with patch("app.api.routes.decisions.run_pipeline", return_value=mock_result):
        # 1. Enqueue job
        res_post = client.post("/decisions/async", json=payload)
        assert res_post.status_code == 202
        job_data = res_post.json()
        assert "job_id" in job_data
        assert job_data["status"] in ["queued", "processing", "completed"]
        job_id = job_data["job_id"]

        # 2. Get status
        res_get = client.get(f"/decisions/jobs/{job_id}")
        assert res_get.status_code == 200
        get_data = res_get.json()
        assert get_data["job_id"] == job_id
        assert get_data["status"] in ["queued", "processing", "completed"]


def test_get_decision_job_not_found():
    """Test GET /decisions/jobs/{job_id} returns 404 for unknown job_id."""
    res = client.get("/decisions/jobs/invalid-job-id-12345")
    assert res.status_code == 404
    assert "detail" in res.json()
