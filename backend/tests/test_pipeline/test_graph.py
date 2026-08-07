"""
Integration tests for sequential pipeline graph with verification gating (app.pipeline.graph).
"""

from unittest.mock import MagicMock, patch

from app.agents.dependency_diagnosis.dependency_diagnosis_agent import DependencyDiagnosis, DiagnosisSet
from app.agents.dependency_diagnosis.sub_agents.failure_mode_sub_agent import FailureMode
from app.agents.dependency_diagnosis.sub_agents.lock_in_identification_sub_agent import LockInDependency
from app.agents.dependency_diagnosis.sub_agents.severity_scoring_sub_agent import DependencySeverityScore
from app.agents.ingestion.sub_agents.context_synthesis_sub_agent import IngestionContext
from app.agents.orchestrator.orchestrator_agent import OrchestratorVerdict
from app.agents.orchestrator.sub_agents.cross_path_comparison_sub_agent import CrossPathComparison, PathComparison
from app.agents.orchestrator.sub_agents.explanation_trail_sub_agent import AuditStep, ExplanationTrail
from app.agents.orchestrator.sub_agents.verdict_synthesis_sub_agent import VerdictSynthesis
from app.agents.outcome_prediction.outcome_prediction_agent import OutcomeProjection, OutcomeSet
from app.agents.outcome_prediction.sub_agents.risk_factor_sub_agent import RiskFactor
from app.agents.outcome_prediction.sub_agents.timeline_projection_sub_agent import TimelineProjection
from app.agents.outcome_prediction.sub_agents.trajectory_modeling_sub_agent import Trajectory
from app.agents.scenario_generation.scenario_generation_agent import ScenarioSet
from app.agents.scenario_generation.sub_agents.scenario_refinement_sub_agent import Scenario
from app.agents.stack_mapping.stack_mapping_agent import StackScope
from app.agents.stack_mapping.sub_agents.dependency_linkage_sub_agent import LayerLink
from app.agents.stack_mapping.sub_agents.layer_identification_sub_agent import StackLayer
from app.pipeline.graph import PipelineResult, run, run_pipeline
from app.verification.source_store import SourcedClaim, SourceStore


def test_pipeline_graph_end_to_end_success():
    """Test full sequential pipeline execution with mocked agent returns."""
    sample_context = IngestionContext(
        entity="Indian Army signals division",
        capability="small language model for edge inference",
        options=["build in-house", "license open-weight"],
        context_summary="Small language model edge inference requirements for Indian Army signals division using license open-weight model from upstream weights vendor.",
        key_facts=["Small language model edge inference requirements."],
        sources=["https://example.com/source1"],
    )

    sample_scope = StackScope(
        entity="Indian Army signals division",
        capability="small language model for edge inference",
        layers=[StackLayer(name="Model Weights", rationale="Small language model edge inference", evidence="Small language model edge inference requirements.")],
        links=[LayerLink(from_layer="Model Weights", to_layer="Inference Hardware", dependency_type="Hardware", description="Requires NPU")],
    )

    sample_scenarios = ScenarioSet(
        entity="Indian Army signals division",
        capability="small language model for edge inference",
        scenarios=[
            Scenario(
                name="License Open-Weight Model",
                option_name="license open-weight",
                description="Small language model edge inference",
                implementation_steps=["Download weights", "Quantize for NPU"],
                key_risks=["Model license restrictions"],
                layers_addressed=["Model Weights"],
            )
        ],
    )

    sample_outcomes = OutcomeSet(
        entity="Indian Army signals division",
        capability="small language model for edge inference",
        outcomes=[
            OutcomeProjection(
                scenario_name="License Open-Weight Model",
                trajectory=Trajectory(
                    scenario_name="License Open-Weight Model",
                    summary="Small language model edge inference",
                    expected_outcomes=["Low latency inference"],
                    technical_impact="Custom quantization pipeline",
                    operational_impact="In-house team maintenance",
                ),
                risk_factors=[
                    RiskFactor(
                        scenario_name="License Open-Weight Model",
                        factor_name="Upstream License Change",
                        description="Licensing policy change",
                        likelihood="Low",
                        impact_severity="High",
                        mitigation_strategy="Pin model version",
                    )
                ],
                timeline=TimelineProjection(
                    scenario_name="License Open-Weight Model",
                    short_term="Quantize model",
                    medium_term="Deploy to field",
                    long_term="Maintain fine-tunes",
                    milestones=["Lab demo"],
                ),
            )
        ],
    )

    sample_diagnoses = DiagnosisSet(
        entity="Indian Army signals division",
        capability="small language model for edge inference",
        diagnoses=[
            DependencyDiagnosis(
                scenario_name="License Open-Weight Model",
                dependencies=[
                    LockInDependency(
                        scenario_name="License Open-Weight Model",
                        dependency_name="Upstream Weights Vendor",
                        layer_name="Model Weights",
                        lock_in_type="Architectural Lock-In",
                        description="Tied to Llama architecture",
                    )
                ],
                failure_modes=[
                    FailureMode(
                        scenario_name="License Open-Weight Model",
                        dependency_name="Upstream Weights Vendor",
                        failure_mode_title="License Revocation",
                        what_breaks="Small language model edge inference",
                        trigger_condition="Terms update",
                        time_horizon="12 months",
                    )
                ],
                severity_scores=[
                    DependencySeverityScore(
                        scenario_name="License Open-Weight Model",
                        dependency_name="Upstream Weights Vendor",
                        severity_score=7.5,
                        urgency_score=6.0,
                        risk_level="Medium",
                        rationale="Manageable with open weights fallback",
                    )
                ],
            )
        ],
    )

    sample_verdict = OrchestratorVerdict(
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
            steps=[AuditStep(stage="Ingestion", claim="Small language model edge inference", evidence="Small language model edge inference requirements.")],
            sources=["https://example.com/source1"],
        ),
    )

    with patch("app.agents.ingestion.ingestion_agent.run", return_value=sample_context) as mock_ingest, \
         patch("app.agents.stack_mapping.stack_mapping_agent.run", return_value=sample_scope) as mock_stack, \
         patch("app.agents.scenario_generation.scenario_generation_agent.run", return_value=sample_scenarios) as mock_scenarios, \
         patch("app.agents.outcome_prediction.outcome_prediction_agent.run", return_value=sample_outcomes) as mock_outcomes, \
         patch("app.agents.dependency_diagnosis.dependency_diagnosis_agent.run", return_value=sample_diagnoses) as mock_diagnoses, \
         patch("app.agents.orchestrator.orchestrator_agent.run", return_value=sample_verdict) as mock_orchestrator:

        res = run_pipeline(
            entity="Indian Army signals division",
            capability="small language model for edge inference",
            options=["build in-house", "license open-weight"],
        )

        assert isinstance(res, PipelineResult)
        assert res.entity == "Indian Army signals division"
        assert res.capability == "small language model for edge inference"
        assert res.options == ["build in-house", "license open-weight"]
        assert res.ingestion_context == sample_context
        assert res.stack_scope == sample_scope
        assert res.scenario_set == sample_scenarios
        assert res.outcome_set == sample_outcomes
        assert res.diagnosis_set == sample_diagnoses
        assert res.verdict == sample_verdict
        assert res.verification_passed is True
        assert res.verification_failed_stage is None

        # Check call sequence & parameter passing
        mock_ingest.assert_called_once()
        mock_stack.assert_called_once()
        mock_scenarios.assert_called_once()
        mock_outcomes.assert_called_once()
        mock_diagnoses.assert_called_once()
        mock_orchestrator.assert_called_once()


def test_pipeline_verification_gating_halts_on_unverified_claim():
    """Verify that a bad/unverified claim at Stage 1 halts the pipeline immediately."""
    bad_context = IngestionContext(
        entity="Test Entity",
        capability="Test Cap",
        options=["option1"],
        context_summary="Standard cloud infrastructure report for edge computing.",
        key_facts=["Quantum teleportation encryption protocol active."], # Completely unmentioned in summary
        sources=["https://example.com"],
    )

    with patch("app.agents.ingestion.ingestion_agent.run", return_value=bad_context) as mock_ingest, \
         patch("app.agents.stack_mapping.stack_mapping_agent.run") as mock_stack:

        res = run_pipeline(
            entity="Test Entity",
            capability="Test Cap",
            options=["option1"],
            halt_on_verification_failure=True,
        )

        assert res.verification_passed is False
        assert res.verification_failed_stage == "ingestion"
        assert len(res.verification_results) > 0
        assert res.verification_results[0].passed is False

        # Verify downstream agent was NOT executed due to halt
        mock_stack.assert_not_called()
        assert res.stack_scope is None
        assert res.verdict is None


def test_pipeline_verification_gating_flags_without_halt_when_disabled():
    """Verify that when halt_on_verification_failure is False, pipeline continues but flags failure."""
    bad_context = IngestionContext(
        entity="Test Entity",
        capability="Test Cap",
        options=["option1"],
        context_summary="Standard cloud infrastructure report for edge computing.",
        key_facts=["Quantum teleportation encryption protocol active."],
        sources=["https://example.com"],
    )

    sample_scope = StackScope(
        entity="Test Entity",
        capability="Test Cap",
        layers=[],
        links=[],
    )

    with patch("app.agents.ingestion.ingestion_agent.run", return_value=bad_context), \
         patch("app.agents.stack_mapping.stack_mapping_agent.run", return_value=sample_scope) as mock_stack, \
         patch("app.agents.scenario_generation.scenario_generation_agent.run") as mock_scenarios, \
         patch("app.agents.outcome_prediction.outcome_prediction_agent.run"), \
         patch("app.agents.dependency_diagnosis.dependency_diagnosis_agent.run"), \
         patch("app.agents.orchestrator.orchestrator_agent.run"):

        res = run_pipeline(
            entity="Test Entity",
            capability="Test Cap",
            options=["option1"],
            halt_on_verification_failure=False,
        )

        # Flagged as failed verification, but downstream agents executed
        assert res.verification_passed is False
        mock_stack.assert_called_once()
        mock_scenarios.assert_called_once()


def test_pipeline_run_alias():
    """Verify run function alias functions identically to run_pipeline."""
    with patch("app.agents.ingestion.ingestion_agent.run") as mock_ingest, \
         patch("app.agents.stack_mapping.stack_mapping_agent.run"), \
         patch("app.agents.scenario_generation.scenario_generation_agent.run"), \
         patch("app.agents.outcome_prediction.outcome_prediction_agent.run"), \
         patch("app.agents.dependency_diagnosis.dependency_diagnosis_agent.run"), \
         patch("app.agents.orchestrator.orchestrator_agent.run"):

        res = run(entity="Test Entity", capability="Test Cap")
        assert res.entity == "Test Entity"
        assert res.capability == "Test Cap"
        assert res.options == []
        mock_ingest.assert_called_once_with(entity="Test Entity", capability="Test Cap", options=[])


def test_pipeline_handles_agent_exception_gracefully():
    """Verify that an exception in an agent halts and flags the pipeline runner."""
    with patch("app.agents.ingestion.ingestion_agent.run", side_effect=RuntimeError("Ingestion failed")):
        res = run_pipeline(entity="Fail Entity", capability="Fail Cap")
        assert res.entity == "Fail Entity"
        assert res.capability == "Fail Cap"
        assert res.ingestion_context is None
        assert res.verification_passed is False
        assert res.verification_failed_stage == "ingestion"
