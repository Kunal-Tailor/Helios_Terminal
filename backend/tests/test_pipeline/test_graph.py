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
        layers=[
            StackLayer(name="Model Weights", rationale="Small language model edge inference", evidence="Small language model edge inference requirements."),
            StackLayer(name="Inference Hardware", rationale="Edge inference requirements", evidence="Small language model edge inference requirements."),
        ],
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
        layers=[
            StackLayer(name="Test Layer", rationale="Standard cloud infrastructure report for edge computing.", evidence="Standard cloud infrastructure report for edge computing."),
            StackLayer(name="Compute Layer", rationale="Standard cloud infrastructure report for edge computing.", evidence="Standard cloud infrastructure report for edge computing."),
        ],
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
    mock_scope = StackScope(
        entity="Test Entity",
        capability="Test Cap",
        layers=[
            StackLayer(name="L1", rationale="R1", evidence="E1"),
            StackLayer(name="L2", rationale="R2", evidence="E2"),
        ],
    )
    with patch("app.agents.ingestion.ingestion_agent.run") as mock_ingest, \
         patch("app.agents.stack_mapping.stack_mapping_agent.run", return_value=mock_scope), \
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


def test_pipeline_reports_incomplete_run_on_upstream_api_failure():
    """Simulate an upstream API failure (e.g. rate limit error) mid-pipeline and verify incomplete run reporting."""
    sample_context = IngestionContext(
        entity="Test Entity",
        capability="Test Cap",
        options=["opt1"],
        context_summary="Test context summary for edge computing.",
        key_facts=["Test context summary for edge computing."],
        sources=["https://example.com"],
    )

    sample_scope = StackScope(
        entity="Test Entity",
        capability="Test Cap",
        layers=[StackLayer(name="Compute", rationale="Test context summary for edge computing.", evidence="Test context summary for edge computing.")],
    )

    # Scenario-generation returns empty scenario set due to upstream rate-limit failure in sub-agent
    empty_scenarios = ScenarioSet(
        entity="Test Entity",
        capability="Test Cap",
        scenarios=[],
    )

    with patch("app.agents.ingestion.ingestion_agent.run", return_value=sample_context), \
         patch("app.agents.stack_mapping.stack_mapping_agent.run", return_value=sample_scope), \
         patch("app.agents.scenario_generation.scenario_generation_agent.run", return_value=empty_scenarios):

        res = run_pipeline(
            entity="Test Entity",
            capability="Test Cap",
            options=["opt1"],
        )

        assert res.verification_passed is False
        assert res.verification_failed_stage == "scenario_generation"
        assert any(
            v.passed is False and "stage did not execute" in v.reason and v.agent_stage == "scenario_generation"
            for v in res.verification_results
        )


def test_pipeline_stack_mapping_to_ingestion_fallback_fires_and_continues():
    """Integration test: on insufficient layer mapping (<=1 layer), re-invoke Ingestion scoped to gap_description,
    accumulate context, loop back to Stack-Mapping, and continue pipeline to verdict."""
    initial_context = IngestionContext(
        entity="Test Entity",
        capability="edge computing",
        options=["build", "buy"],
        context_summary="Initial context about edge computing hardware. Fact: Edge device has limited NPU memory.",
        key_facts=["Fact: Edge device has limited NPU memory."],
        sources=["https://example.com/src1"],
        raw_retrieved_content="Initial context about edge computing hardware. Fact: Edge device has limited NPU memory.",
    )

    re_ingest_context = IngestionContext(
        entity="Test Entity",
        capability="edge computing (Gap: Stack-Mapping produced only 1 surviving layer)",
        options=["build", "buy"],
        context_summary="Additional details about Model Weights and Fine-Tuning Pipeline. Fact: Model weights quantized for edge. Fact: Fine-tuning pipeline required.",
        key_facts=["Fact: Model weights quantized for edge.", "Fact: Fine-tuning pipeline required."],
        sources=["https://example.com/src2"],
        raw_retrieved_content="Additional details about Model Weights and Fine-Tuning Pipeline. Fact: Model weights quantized for edge. Fact: Fine-tuning pipeline required.",
    )

    # 1st call to stack_mapping: 1 layer -> insufficient (triggers fallback)
    thin_scope = StackScope(
        entity="Test Entity",
        capability="edge computing",
        layers=[
            StackLayer(
                name="Hardware",
                rationale="Hardware constraint",
                evidence="Fact: Edge device has limited NPU memory.",
            )
        ],
    )

    # 2nd call to stack_mapping: 2 layers -> sufficient (continues forward)
    sufficient_scope = StackScope(
        entity="Test Entity",
        capability="edge computing",
        layers=[
            StackLayer(
                name="Hardware",
                rationale="Hardware constraint",
                evidence="Fact: Edge device has limited NPU memory.",
            ),
            StackLayer(
                name="Model Weights",
                rationale="Quantized weights needed",
                evidence="Fact: Model weights quantized for edge.",
            ),
        ],
    )

    mock_scenarios = ScenarioSet(
        entity="Test Entity",
        capability="edge computing",
        scenarios=[
            Scenario(
                name="Build",
                option_name="build",
                description="Hardware and Model Weights setup",
                grounded_in="Hardware: Hardware constraint Fact: Edge device has limited NPU memory.",
            )
        ],
    )

    mock_outcomes = OutcomeSet(
        entity="Test Entity",
        capability="edge computing",
        outcomes=[
            OutcomeProjection(
                scenario_name="Build",
                trajectory=Trajectory(
                    scenario_name="Build",
                    summary="Build trajectory",
                    grounded_in="Build: Hardware and Model Weights setup",
                ),
                risk_factors=[RiskFactor(scenario_name="Build", factor_name="Risk", description="Risk desc")],
            )
        ],
    )

    mock_diagnoses = DiagnosisSet(
        entity="Test Entity",
        capability="edge computing",
        diagnoses=[
            DependencyDiagnosis(
                scenario_name="Build",
                dependencies=[LockInDependency(scenario_name="Build", dependency_name="Hardware", lock_in_type="Vendor", description="Lockin")],
                failure_modes=[FailureMode(scenario_name="Build", dependency_name="Hardware", failure_mode_title="Fail", what_breaks="Breaks", trigger_condition="Trig", time_horizon="Short", grounded_in="Build: Build trajectory")],
            )
        ],
    )

    mock_verdict = OrchestratorVerdict(
        entity="Test Entity",
        capability="edge computing",
        recommended_path="Build",
        verdict_summary="Build verdict",
        key_recommendations=["Rec 1"],
        explanation_trail=ExplanationTrail(
            summary="Trail",
            steps=[AuditStep(stage="diagnosis", claim="Build Hardware", evidence="Evidence", grounded_in="Build Hardware: Fail Breaks Trig Short")],
        ),
    )

    with patch("app.agents.ingestion.ingestion_agent.run", side_effect=[initial_context, re_ingest_context]) as mock_ingest, \
         patch("app.agents.stack_mapping.stack_mapping_agent.run", side_effect=[thin_scope, sufficient_scope]) as mock_stack, \
         patch("app.agents.scenario_generation.scenario_generation_agent.run", return_value=mock_scenarios) as mock_scenarios_run, \
         patch("app.agents.outcome_prediction.outcome_prediction_agent.run", return_value=mock_outcomes), \
         patch("app.agents.dependency_diagnosis.dependency_diagnosis_agent.run", return_value=mock_diagnoses), \
         patch("app.agents.orchestrator.orchestrator_agent.run", return_value=mock_verdict):

        res = run_pipeline(
            entity="Test Entity",
            capability="edge computing",
            options=["build", "buy"],
        )

        # 1. Pipeline succeeded all the way to verdict
        assert res.verdict is not None
        assert res.verdict.recommended_path == "Build"
        assert res.verification_passed is True

        # 2. Ingestion was called twice: initial + re-ingest scoped to gap
        assert mock_ingest.call_count == 2
        first_call = mock_ingest.call_args_list[0]
        second_call = mock_ingest.call_args_list[1]
        assert first_call.kwargs["capability"] == "edge computing"
        assert "Gap: Stack-Mapping produced only 1 surviving layer" in second_call.kwargs["capability"]

        # 3. Stack-mapping was called twice: initial thin + rerun with accumulated context
        assert mock_stack.call_count == 2

        # 4. Context was accumulated (both initial and re-ingested facts/sources present)
        assert res.ingestion_context is not None
        assert "Fact: Edge device has limited NPU memory." in res.ingestion_context.key_facts
        assert "Fact: Model weights quantized for edge." in res.ingestion_context.key_facts
        assert "https://example.com/src1" in res.ingestion_context.sources
        assert "https://example.com/src2" in res.ingestion_context.sources

        # 5. Recalibration trail recorded the loop-back
        assert len(res.recalibration_trail) == 1
        req = res.recalibration_trail[0]
        assert req.from_stage == "stack_mapping"
        assert req.to_stage == "ingestion"
        assert req.reason == "insufficient"
        assert req.iteration_count == 1
        assert "surviving layer" in req.gap_description

        # 6. Downstream stages continued and executed
        mock_scenarios_run.assert_called_once()

