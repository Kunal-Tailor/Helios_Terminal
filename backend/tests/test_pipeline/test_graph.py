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
            ),
            Scenario(
                name="Build In-House",
                option_name="build in-house",
                description="Small language model edge inference",
                implementation_steps=["Procure GPUs", "Train base model"],
                key_risks=["Long timeline"],
                layers_addressed=["Inference Hardware"],
            ),
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

    sample_scenarios = ScenarioSet(
        entity="Test Entity",
        capability="Test Cap",
        scenarios=[
            Scenario(name="S1", option_name="o1", description="desc1"),
            Scenario(name="S2", option_name="o2", description="desc2"),
        ],
    )

    sample_outcomes = OutcomeSet(
        entity="Test Entity",
        capability="Test Cap",
        outcomes=[
            OutcomeProjection(
                scenario_name="S1",
                trajectory=Trajectory(scenario_name="S1", summary="sum"),
                risk_factors=[RiskFactor(scenario_name="S1", factor_name="f", description="d")],
            )
        ],
    )

    sample_diagnoses = DiagnosisSet(
        entity="Test Entity",
        capability="Test Cap",
        diagnoses=[
            DependencyDiagnosis(
                scenario_name="S1",
                dependencies=[LockInDependency(scenario_name="S1", dependency_name="Dep1", lock_in_type="Vendor", description="A vendor dep")],
            )
        ],
    )

    with patch("app.agents.ingestion.ingestion_agent.run", return_value=bad_context), \
         patch("app.agents.stack_mapping.stack_mapping_agent.run", return_value=sample_scope) as mock_stack, \
         patch("app.agents.scenario_generation.scenario_generation_agent.run", return_value=sample_scenarios) as mock_scenarios, \
         patch("app.agents.outcome_prediction.outcome_prediction_agent.run", return_value=sample_outcomes), \
         patch("app.agents.dependency_diagnosis.dependency_diagnosis_agent.run", return_value=sample_diagnoses), \
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
    mock_scenarios = ScenarioSet(
        entity="Test Entity",
        capability="Test Cap",
        scenarios=[
            Scenario(name="S1", option_name="o1", description="d1"),
            Scenario(name="S2", option_name="o2", description="d2"),
        ],
    )
    mock_outcomes = OutcomeSet(
        entity="Test Entity",
        capability="Test Cap",
        outcomes=[
            OutcomeProjection(
                scenario_name="S1",
                trajectory=Trajectory(scenario_name="S1", summary="traj"),
                risk_factors=[RiskFactor(scenario_name="S1", factor_name="f", description="d")],
            )
        ],
    )
    mock_diagnoses = DiagnosisSet(
        entity="Test Entity",
        capability="Test Cap",
        diagnoses=[
            DependencyDiagnosis(
                scenario_name="S1",
                dependencies=[LockInDependency(scenario_name="S1", dependency_name="D1", lock_in_type="Vendor", description="dep")],
            )
        ],
    )
    with patch("app.agents.ingestion.ingestion_agent.run") as mock_ingest, \
         patch("app.agents.stack_mapping.stack_mapping_agent.run", return_value=mock_scope), \
         patch("app.agents.scenario_generation.scenario_generation_agent.run", return_value=mock_scenarios), \
         patch("app.agents.outcome_prediction.outcome_prediction_agent.run", return_value=mock_outcomes), \
         patch("app.agents.dependency_diagnosis.dependency_diagnosis_agent.run", return_value=mock_diagnoses), \
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
            ),
            Scenario(
                name="Buy",
                option_name="buy",
                description="Pre-quantized edge model purchase",
                grounded_in="Model Weights: Quantized weights needed Fact: Model weights quantized for edge.",
            ),
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


def test_pipeline_scenario_generation_fallback_to_stack_mapping_branch():
    """Integration test (Branch 1): on insufficient scenarios when stack scope is narrow (<= 2 layers),
    Scenario-Generation routes backward to Stack-Mapping to broaden layer scope, loops back, and continues."""
    context = IngestionContext(
        entity="Gov Agency",
        capability="secure LLM",
        options=["open-weights", "commercial"],
        context_summary="Gov Agency secure LLM deployment. Fact: Local infrastructure has GPU cluster. Fact: Data privacy rules strict.",
        key_facts=["Fact: Local infrastructure has GPU cluster.", "Fact: Data privacy rules strict."],
        sources=["https://example.com/sec1"],
        raw_retrieved_content="Gov Agency secure LLM deployment. Fact: Local infrastructure has GPU cluster. Fact: Data privacy rules strict.",
    )

    # Initial narrow stack scope (2 layers <= 2 -> routes to stack_mapping)
    initial_scope = StackScope(
        entity="Gov Agency",
        capability="secure LLM",
        layers=[
            StackLayer(name="Model Weights", rationale="Weights", evidence="Fact: Local infrastructure has GPU cluster."),
            StackLayer(name="Data Governance", rationale="Rules", evidence="Fact: Data privacy rules strict."),
        ],
    )

    # Broadened stack scope after recalibration re-run
    broadened_scope = StackScope(
        entity="Gov Agency",
        capability="secure LLM",
        layers=[
            StackLayer(name="Model Weights", rationale="Weights", evidence="Fact: Local infrastructure has GPU cluster."),
            StackLayer(name="Data Governance", rationale="Rules", evidence="Fact: Data privacy rules strict."),
            StackLayer(name="Inference Infrastructure", rationale="Cluster", evidence="Fact: Local infrastructure has GPU cluster."),
        ],
    )

    # 1st call to scenario_generation: 1 scenario -> insufficient (< 2 scenarios)
    thin_scenarios = ScenarioSet(
        entity="Gov Agency",
        capability="secure LLM",
        scenarios=[
            Scenario(
                name="Open-Weights",
                option_name="open-weights",
                description="Local deployment on cluster",
                grounded_in="Model Weights: Weights Fact: Local infrastructure has GPU cluster.",
            )
        ],
    )

    # 2nd call to scenario_generation: 2 scenarios -> sufficient
    sufficient_scenarios = ScenarioSet(
        entity="Gov Agency",
        capability="secure LLM",
        scenarios=[
            Scenario(
                name="Open-Weights",
                option_name="open-weights",
                description="Local deployment on cluster",
                grounded_in="Model Weights: Weights Fact: Local infrastructure has GPU cluster.",
            ),
            Scenario(
                name="Commercial API",
                option_name="commercial",
                description="Encrypted VPC commercial gateway",
                grounded_in="Data Governance: Rules Fact: Data privacy rules strict.",
            ),
        ],
    )

    mock_outcomes = OutcomeSet(
        entity="Gov Agency",
        capability="secure LLM",
        outcomes=[
            OutcomeProjection(
                scenario_name="Open-Weights",
                trajectory=Trajectory(scenario_name="Open-Weights", summary="Local traj", grounded_in="Open-Weights: Local deployment on cluster"),
                risk_factors=[RiskFactor(scenario_name="Open-Weights", factor_name="Risk1", description="Desc1")],
            ),
            OutcomeProjection(
                scenario_name="Commercial API",
                trajectory=Trajectory(scenario_name="Commercial API", summary="VPC traj", grounded_in="Commercial API: Encrypted VPC commercial gateway"),
                risk_factors=[RiskFactor(scenario_name="Commercial API", factor_name="Risk2", description="Desc2")],
            ),
        ],
    )

    mock_diagnoses = DiagnosisSet(
        entity="Gov Agency",
        capability="secure LLM",
        diagnoses=[
            DependencyDiagnosis(
                scenario_name="Open-Weights",
                dependencies=[LockInDependency(scenario_name="Open-Weights", dependency_name="Hardware", lock_in_type="Compute", description="GPU")],
                failure_modes=[FailureMode(scenario_name="Open-Weights", dependency_name="Hardware", failure_mode_title="Fail1", what_breaks="GPU breaks", trigger_condition="Trig1", time_horizon="Short", grounded_in="Open-Weights: Local traj")],
            )
        ],
    )

    mock_verdict = OrchestratorVerdict(
        entity="Gov Agency",
        capability="secure LLM",
        recommended_path="Open-Weights",
        verdict_summary="Verdict summary for secure LLM",
        key_recommendations=["Deploy open weights"],
        explanation_trail=ExplanationTrail(
            summary="Trail",
            steps=[AuditStep(stage="diagnosis", claim="Open-Weights Hardware", evidence="Evidence", grounded_in="Open-Weights Hardware: Fail1 GPU breaks Trig1 Short")],
        ),
    )

    with patch("app.agents.ingestion.ingestion_agent.run", return_value=context) as mock_ingest, \
         patch("app.agents.stack_mapping.stack_mapping_agent.run", side_effect=[initial_scope, broadened_scope]) as mock_stack, \
         patch("app.agents.scenario_generation.scenario_generation_agent.run", side_effect=[thin_scenarios, sufficient_scenarios]) as mock_scenarios, \
         patch("app.agents.outcome_prediction.outcome_prediction_agent.run", return_value=mock_outcomes), \
         patch("app.agents.dependency_diagnosis.dependency_diagnosis_agent.run", return_value=mock_diagnoses), \
         patch("app.agents.orchestrator.orchestrator_agent.run", return_value=mock_verdict):

        res = run_pipeline(
            entity="Gov Agency",
            capability="secure LLM",
            options=["open-weights", "commercial"],
        )

        assert res.verdict is not None
        assert res.verdict.recommended_path == "Open-Weights"
        assert res.verification_passed is True

        # Ingestion was only called once initially (did NOT fall back to Ingestion)
        assert mock_ingest.call_count == 1

        # Stack-mapping was called twice (initial + recalibration re-run to broaden scope)
        assert mock_stack.call_count == 2

        # Scenario-generation was called twice (initial thin + re-run with broadened scope)
        assert mock_scenarios.call_count == 2

        # Recalibration trail verifies target was "stack_mapping"
        assert len(res.recalibration_trail) == 1
        req = res.recalibration_trail[0]
        assert req.from_stage == "scenario_generation"
        assert req.to_stage == "stack_mapping"
        assert req.reason == "insufficient"
        assert req.iteration_count == 1
        assert "[Target: stack_mapping]" in req.gap_description


def test_pipeline_scenario_generation_fallback_to_ingestion_branch():
    """Integration test (Branch 2): on insufficient scenarios when stack scope is already broad (> 2 layers),
    Scenario-Generation routes backward to Ingestion to retrieve concrete options/vendor data, loops back, and continues."""
    context = IngestionContext(
        entity="FinTech Corp",
        capability="fraud detection",
        options=["vendor A", "vendor B"],
        context_summary="FinTech Corp fraud detection. Fact: Low latency transaction stream. Fact: ISO compliance mandated. Fact: Model weights hosted in cloud.",
        key_facts=["Fact: Low latency transaction stream.", "Fact: ISO compliance mandated.", "Fact: Model weights hosted in cloud."],
        sources=["https://example.com/fin1"],
        raw_retrieved_content="FinTech Corp fraud detection. Fact: Low latency transaction stream. Fact: ISO compliance mandated. Fact: Model weights hosted in cloud.",
    )

    re_ingest_context = IngestionContext(
        entity="FinTech Corp",
        capability="fraud detection (Gap: missing concrete vendor data)",
        options=["vendor A", "vendor B"],
        context_summary="Targeted vendor data for Vendor A and Vendor B. Fact: Vendor A supports on-prem. Fact: Vendor B cloud API.",
        key_facts=["Fact: Vendor A supports on-prem.", "Fact: Vendor B cloud API."],
        sources=["https://example.com/fin2"],
        raw_retrieved_content="Targeted vendor data for Vendor A and Vendor B. Fact: Vendor A supports on-prem. Fact: Vendor B cloud API.",
    )

    # Broad initial stack scope (3 layers > 2 -> routes to ingestion)
    broad_scope = StackScope(
        entity="FinTech Corp",
        capability="fraud detection",
        layers=[
            StackLayer(name="Inference Infra", rationale="Stream", evidence="Fact: Low latency transaction stream."),
            StackLayer(name="Compliance Layer", rationale="ISO", evidence="Fact: ISO compliance mandated."),
            StackLayer(name="Model Weights", rationale="Cloud", evidence="Fact: Model weights hosted in cloud."),
        ],
    )

    # 1st call to scenario_generation: 1 scenario -> insufficient (< 2 scenarios)
    thin_scenarios = ScenarioSet(
        entity="FinTech Corp",
        capability="fraud detection",
        scenarios=[
            Scenario(
                name="Generic Option",
                option_name="generic",
                description="Generic fraud pipeline",
                grounded_in="Inference Infra: Stream Fact: Low latency transaction stream.",
            )
        ],
    )

    # 2nd call to scenario_generation after re-ingestion: 2 concrete scenarios
    sufficient_scenarios = ScenarioSet(
        entity="FinTech Corp",
        capability="fraud detection",
        scenarios=[
            Scenario(
                name="Vendor A Appliance",
                option_name="vendor A",
                description="On-prem appliance deployment",
                grounded_in="Inference Infra: Stream Fact: Low latency transaction stream.",
            ),
            Scenario(
                name="Vendor B Cloud",
                option_name="vendor B",
                description="Cloud API deployment",
                grounded_in="Model Weights: Cloud Fact: Model weights hosted in cloud.",
            ),
        ],
    )

    mock_outcomes = OutcomeSet(
        entity="FinTech Corp",
        capability="fraud detection",
        outcomes=[
            OutcomeProjection(
                scenario_name="Vendor A Appliance",
                trajectory=Trajectory(scenario_name="Vendor A Appliance", summary="Appliance traj", grounded_in="Vendor A Appliance: On-prem appliance deployment"),
                risk_factors=[RiskFactor(scenario_name="Vendor A Appliance", factor_name="Risk1", description="Desc1")],
            ),
            OutcomeProjection(
                scenario_name="Vendor B Cloud",
                trajectory=Trajectory(scenario_name="Vendor B Cloud", summary="Cloud traj", grounded_in="Vendor B Cloud: Cloud API deployment"),
                risk_factors=[RiskFactor(scenario_name="Vendor B Cloud", factor_name="Risk2", description="Desc2")],
            ),
        ],
    )

    mock_diagnoses = DiagnosisSet(
        entity="FinTech Corp",
        capability="fraud detection",
        diagnoses=[
            DependencyDiagnosis(
                scenario_name="Vendor A Appliance",
                dependencies=[LockInDependency(scenario_name="Vendor A Appliance", dependency_name="Appliance Vendor", lock_in_type="Vendor", description="Hardware")],
                failure_modes=[FailureMode(scenario_name="Vendor A Appliance", dependency_name="Appliance Vendor", failure_mode_title="Break1", what_breaks="Appliance breaks", trigger_condition="Trig", time_horizon="Medium", grounded_in="Vendor A Appliance: Appliance traj")],
            )
        ],
    )

    mock_verdict = OrchestratorVerdict(
        entity="FinTech Corp",
        capability="fraud detection",
        recommended_path="Vendor A Appliance",
        verdict_summary="Verdict summary for fraud detection",
        key_recommendations=["Deploy Vendor A"],
        explanation_trail=ExplanationTrail(
            summary="Trail",
            steps=[AuditStep(stage="diagnosis", claim="Vendor A Appliance Appliance Vendor", evidence="Evidence", grounded_in="Vendor A Appliance Appliance Vendor: Break1 Appliance breaks Trig Medium")],
        ),
    )

    with patch("app.agents.ingestion.ingestion_agent.run", side_effect=[context, re_ingest_context]) as mock_ingest, \
         patch("app.agents.stack_mapping.stack_mapping_agent.run", return_value=broad_scope) as mock_stack, \
         patch("app.agents.scenario_generation.scenario_generation_agent.run", side_effect=[thin_scenarios, sufficient_scenarios]) as mock_scenarios, \
         patch("app.agents.outcome_prediction.outcome_prediction_agent.run", return_value=mock_outcomes), \
         patch("app.agents.dependency_diagnosis.dependency_diagnosis_agent.run", return_value=mock_diagnoses), \
         patch("app.agents.orchestrator.orchestrator_agent.run", return_value=mock_verdict):

        res = run_pipeline(
            entity="FinTech Corp",
            capability="fraud detection",
            options=["vendor A", "vendor B"],
        )

        assert res.verdict is not None
        assert res.verdict.recommended_path == "Vendor A Appliance"
        assert res.verification_passed is True

        # Ingestion was called twice (initial + scoped re-ingestion)
        assert mock_ingest.call_count == 2
        second_call = mock_ingest.call_args_list[1]
        assert "[Target: ingestion]" in second_call.kwargs["capability"]

        # Stack-mapping was called twice (initial + re-run with accumulated context)
        assert mock_stack.call_count == 2

        # Scenario-generation was called twice (initial thin + re-run with re-ingested context)
        assert mock_scenarios.call_count == 2

        # Context accumulated the new facts and sources
        assert res.ingestion_context is not None
        assert "Fact: Vendor A supports on-prem." in res.ingestion_context.key_facts
        assert "https://example.com/fin2" in res.ingestion_context.sources

        # Recalibration trail verifies target was "ingestion"
        assert len(res.recalibration_trail) == 1
        req = res.recalibration_trail[0]
        assert req.from_stage == "scenario_generation"
        assert req.to_stage == "ingestion"
        assert req.reason == "insufficient"
        assert req.iteration_count == 1
        assert "[Target: ingestion]" in req.gap_description


def test_pipeline_outcome_prediction_fallback_invokes_scenario_refinement():
    """Integration test: on insufficient outcome predictions (e.g. 0 trajectories or no risk factors),
    Outcome-Prediction routes backward to Scenario-Generation, invoking scenario_refinement_sub_agent
    to sharpen specifications rather than a blind re-run, loops back, and continues."""
    context = IngestionContext(
        entity="Auto OEM",
        capability="autonomous driving perception",
        options=["lidar-fusion", "camera-only"],
        context_summary="Auto OEM perception. Fact: Automotive safety integrity ASIL-D. Fact: High resolution sensor data.",
        key_facts=["Fact: Automotive safety integrity ASIL-D.", "Fact: High resolution sensor data."],
        sources=["https://example.com/auto1"],
        raw_retrieved_content="Auto OEM perception. Fact: Automotive safety integrity ASIL-D. Fact: High resolution sensor data.",
    )

    scope = StackScope(
        entity="Auto OEM",
        capability="autonomous driving perception",
        layers=[
            StackLayer(name="Sensor Layer", rationale="Sensors", evidence="Fact: High resolution sensor data."),
            StackLayer(name="Safety Gateway", rationale="ASIL-D", evidence="Fact: Automotive safety integrity ASIL-D."),
        ],
    )

    # Scenarios before refinement
    raw_scenarios = ScenarioSet(
        entity="Auto OEM",
        capability="autonomous driving perception",
        scenarios=[
            Scenario(
                name="Lidar Fusion",
                option_name="lidar-fusion",
                description="Raw lidar fusion setup",
                grounded_in="Sensor Layer: Sensors Fact: High resolution sensor data.",
            ),
            Scenario(
                name="Camera Only",
                option_name="camera-only",
                description="Vision model pipeline",
                grounded_in="Safety Gateway: ASIL-D Fact: Automotive safety integrity ASIL-D.",
            ),
        ],
    )

    # Refined scenarios returned by scenario_refinement_sub_agent
    refined_scenarios_list = [
        Scenario(
            name="Lidar Fusion Refined",
            option_name="lidar-fusion",
            description="Sharpened multi-sensor lidar perception pipeline with redundant ASIL-D processors",
            implementation_steps=["Procure automotive grade solid-state lidar", "Deploy sensor fusion node"],
            key_risks=["Sensor calibration drift in harsh weather"],
            layers_addressed=["Sensor Layer", "Safety Gateway"],
            grounded_in="Sensor Layer: Sensors Fact: High resolution sensor data.",
        ),
        Scenario(
            name="Camera Only Refined",
            option_name="camera-only",
            description="Sharpened end-to-end vision network with temporal feature extraction",
            implementation_steps=["Train spatial-temporal transformer", "Integrate optical flow"],
            key_risks=["Edge-case perception failure in occlusion"],
            layers_addressed=["Sensor Layer"],
            grounded_in="Safety Gateway: ASIL-D Fact: Automotive safety integrity ASIL-D.",
        ),
    ]

    # 1st call to outcome_prediction: outcomes have no trajectory/risk -> insufficient
    thin_outcomes = OutcomeSet(
        entity="Auto OEM",
        capability="autonomous driving perception",
        outcomes=[
            OutcomeProjection(
                scenario_name="Lidar Fusion",
                trajectory=None,  # No trajectory
                risk_factors=[],  # No risk factors
            )
        ],
    )

    # 2nd call to outcome_prediction: sufficient projections with trajectory and risk factors
    sufficient_outcomes = OutcomeSet(
        entity="Auto OEM",
        capability="autonomous driving perception",
        outcomes=[
            OutcomeProjection(
                scenario_name="Lidar Fusion Refined",
                trajectory=Trajectory(
                    scenario_name="Lidar Fusion Refined",
                    summary="High accuracy all-weather perception trajectory",
                    grounded_in="Lidar Fusion Refined: Sharpened multi-sensor lidar perception pipeline with redundant ASIL-D processors",
                ),
                risk_factors=[
                    RiskFactor(
                        scenario_name="Lidar Fusion Refined",
                        factor_name="Calibration drift",
                        description="Drift in winter conditions",
                    )
                ],
            ),
            OutcomeProjection(
                scenario_name="Camera Only Refined",
                trajectory=Trajectory(
                    scenario_name="Camera Only Refined",
                    summary="Lower cost vision trajectory",
                    grounded_in="Camera Only Refined: Sharpened end-to-end vision network with temporal feature extraction",
                ),
                risk_factors=[
                    RiskFactor(
                        scenario_name="Camera Only Refined",
                        factor_name="Occlusion risk",
                        description="Adverse lighting failure",
                    )
                ],
            ),
        ],
    )

    mock_diagnoses = DiagnosisSet(
        entity="Auto OEM",
        capability="autonomous driving perception",
        diagnoses=[
            DependencyDiagnosis(
                scenario_name="Lidar Fusion Refined",
                dependencies=[LockInDependency(scenario_name="Lidar Fusion Refined", dependency_name="Lidar Supplier", lock_in_type="Vendor", description="Proprietary transceiver")],
                failure_modes=[FailureMode(scenario_name="Lidar Fusion Refined", dependency_name="Lidar Supplier", failure_mode_title="Supply disruption", what_breaks="Lidar assembly", trigger_condition="Shortage", time_horizon="Medium", grounded_in="Lidar Fusion Refined: High accuracy all-weather perception trajectory")],
            )
        ],
    )

    mock_verdict = OrchestratorVerdict(
        entity="Auto OEM",
        capability="autonomous driving perception",
        recommended_path="Lidar Fusion Refined",
        verdict_summary="Lidar fusion path recommended for safety integrity.",
        key_recommendations=["Lock in multi-year lidar supply"],
        explanation_trail=ExplanationTrail(
            summary="Trail",
            steps=[AuditStep(stage="diagnosis", claim="Lidar Fusion Refined Lidar Supplier", evidence="Evidence", grounded_in="Lidar Fusion Refined Lidar Supplier: Supply disruption Lidar assembly Shortage Medium")],
        ),
    )

    with patch("app.agents.ingestion.ingestion_agent.run", return_value=context), \
         patch("app.agents.stack_mapping.stack_mapping_agent.run", return_value=scope), \
         patch("app.agents.scenario_generation.scenario_generation_agent.run", return_value=raw_scenarios) as mock_scenario_agent_run, \
         patch("app.agents.scenario_generation.sub_agents.scenario_refinement_sub_agent.run", return_value=refined_scenarios_list) as mock_refinement_run, \
         patch("app.agents.outcome_prediction.outcome_prediction_agent.run", side_effect=[thin_outcomes, sufficient_outcomes]) as mock_outcome_agent_run, \
         patch("app.agents.dependency_diagnosis.dependency_diagnosis_agent.run", return_value=mock_diagnoses), \
         patch("app.agents.orchestrator.orchestrator_agent.run", return_value=mock_verdict):

        res = run_pipeline(
            entity="Auto OEM",
            capability="autonomous driving perception",
            options=["lidar-fusion", "camera-only"],
        )

        assert res.verdict is not None
        assert res.verdict.recommended_path == "Lidar Fusion Refined"
        assert res.verification_passed is True

        # Scenario-generation agent was only called once initially (did NOT do a blind agent re-run)
        assert mock_scenario_agent_run.call_count == 1

        # Instead, scenario_refinement_sub_agent was directly invoked to sharpen the scenario options
        assert mock_refinement_run.call_count == 1
        options_arg = mock_refinement_run.call_args.kwargs["options"]
        assert len(options_arg) == 2
        assert options_arg[0].name == "Lidar Fusion"
        assert options_arg[1].name == "Camera Only"

        # Outcome-prediction was called twice (initial thin + re-run with refined scenarios)
        assert mock_outcome_agent_run.call_count == 2
        second_call_scenarios = mock_outcome_agent_run.call_args_list[1].kwargs["scenario_set"].scenarios
        assert second_call_scenarios[0].name == "Lidar Fusion Refined"
        assert second_call_scenarios[1].name == "Camera Only Refined"

        # Recalibration trail recorded the loop-back
        assert len(res.recalibration_trail) == 1
        req = res.recalibration_trail[0]
        assert req.from_stage == "outcome_prediction"
        assert req.to_stage == "scenario_generation"
        assert req.reason == "insufficient"
        assert req.iteration_count == 1
        assert "scenario_refinement_sub_agent" in req.gap_description


def test_pipeline_dependency_diagnosis_fallback_invokes_timeline_projection():
    """Integration test (7.5.8): on generic/non-specific Dependency-Diagnosis output (all diagnoses
    have empty dependencies), invoke timeline_projection_sub_agent to enrich OutcomeProjection
    timelines, then re-run Dependency-Diagnosis until it produces concrete lock-in dependencies."""
    context = IngestionContext(
        entity="Defense Agency",
        capability="satellite imagery AI",
        options=["on-prem GPU cluster", "cloud API"],
        context_summary=(
            "Defense Agency satellite imagery AI. "
            "Fact: Real-time imagery inference at 1fps. "
            "Fact: Data sovereignty mandated."
        ),
        key_facts=[
            "Fact: Real-time imagery inference at 1fps.",
            "Fact: Data sovereignty mandated.",
        ],
        sources=["https://example.com/def1"],
        raw_retrieved_content=(
            "Defense Agency satellite imagery AI. "
            "Fact: Real-time imagery inference at 1fps. "
            "Fact: Data sovereignty mandated."
        ),
    )

    scope = StackScope(
        entity="Defense Agency",
        capability="satellite imagery AI",
        layers=[
            StackLayer(name="Inference Layer", rationale="GPU cluster", evidence="Fact: Real-time imagery inference at 1fps."),
            StackLayer(name="Data Sovereignty Layer", rationale="On-prem data store", evidence="Fact: Data sovereignty mandated."),
            StackLayer(name="Model Weights Layer", rationale="Foundation model weights", evidence="Fact: Real-time imagery inference at 1fps."),
        ],
    )

    raw_scenarios = ScenarioSet(
        entity="Defense Agency",
        capability="satellite imagery AI",
        scenarios=[
            Scenario(
                name="On-Prem GPU",
                option_name="on-prem GPU cluster",
                description="Local GPU cluster inference",
                grounded_in="Inference Layer: GPU cluster Fact: Real-time imagery inference at 1fps.",
            ),
            Scenario(
                name="Cloud API",
                option_name="cloud API",
                description="Cloud inference via secure API",
                grounded_in="Data Sovereignty Layer: On-prem data store Fact: Data sovereignty mandated.",
            ),
        ],
    )

    sufficient_outcomes = OutcomeSet(
        entity="Defense Agency",
        capability="satellite imagery AI",
        outcomes=[
            OutcomeProjection(
                scenario_name="On-Prem GPU",
                trajectory=Trajectory(
                    scenario_name="On-Prem GPU",
                    summary="Local inference trajectory with GPU cluster procurement",
                    grounded_in="On-Prem GPU: Local GPU cluster inference",
                ),
                risk_factors=[
                    RiskFactor(
                        scenario_name="On-Prem GPU",
                        factor_name="Hardware Lock-In",
                        description="Dependency on specific GPU vendor",
                    )
                ],
            ),
            OutcomeProjection(
                scenario_name="Cloud API",
                trajectory=Trajectory(
                    scenario_name="Cloud API",
                    summary="Cloud API trajectory with sovereignty controls",
                    grounded_in="Cloud API: Cloud inference via secure API",
                ),
                risk_factors=[
                    RiskFactor(
                        scenario_name="Cloud API",
                        factor_name="Vendor Dependency",
                        description="Reliance on cloud provider uptime",
                    )
                ],
            ),
        ],
    )

    # Timeline projections returned by timeline_projection_sub_agent
    mock_timeline_projections = [
        TimelineProjection(
            scenario_name="On-Prem GPU",
            short_term="Hardware procurement and rack installation",
            medium_term="GPU cluster integration and model deployment",
            long_term="Steady-state GPU cluster operations with model versioning",
            milestones=["Vendor RFP issued", "Cluster delivered", "Model deployed at 1fps"],
        ),
        TimelineProjection(
            scenario_name="Cloud API",
            short_term="API contract and onboarding",
            medium_term="Sovereign data pipeline integration",
            long_term="Full operational cloud inference with audit trail",
            milestones=["Contract signed", "Pilot inference running", "Sovereignty audit passed"],
        ),
    ]

    # 1st call to dependency_diagnosis: all diagnoses have empty dependencies -> insufficient
    thin_diagnoses = DiagnosisSet(
        entity="Defense Agency",
        capability="satellite imagery AI",
        diagnoses=[
            DependencyDiagnosis(
                scenario_name="On-Prem GPU",
                dependencies=[],  # Empty -> triggers fallback
                failure_modes=[],
            ),
            DependencyDiagnosis(
                scenario_name="Cloud API",
                dependencies=[],  # Empty -> triggers fallback
                failure_modes=[],
            ),
        ],
    )

    # 2nd call to dependency_diagnosis: concrete lock-in dependencies -> sufficient
    sufficient_diagnoses = DiagnosisSet(
        entity="Defense Agency",
        capability="satellite imagery AI",
        diagnoses=[
            DependencyDiagnosis(
                scenario_name="On-Prem GPU",
                dependencies=[
                    LockInDependency(
                        scenario_name="On-Prem GPU",
                        dependency_name="GPU Vendor",
                        lock_in_type="Hardware Vendor Lock-In",
                        description="Proprietary GPU drivers and toolchain",
                    )
                ],
                failure_modes=[
                    FailureMode(
                        scenario_name="On-Prem GPU",
                        dependency_name="GPU Vendor",
                        failure_mode_title="Driver Discontinuation",
                        what_breaks="Inference pipeline",
                        trigger_condition="Vendor EOL",
                        time_horizon="3 years",
                        grounded_in="On-Prem GPU: Local inference trajectory with GPU cluster procurement",
                    )
                ],
                severity_scores=[
                    DependencySeverityScore(
                        scenario_name="On-Prem GPU",
                        dependency_name="GPU Vendor",
                        severity_score=8.0,
                        urgency_score=6.5,
                        risk_level="High",
                        rationale="Critical hardware dependency with limited alternatives",
                    )
                ],
            )
        ],
    )

    mock_verdict = OrchestratorVerdict(
        entity="Defense Agency",
        capability="satellite imagery AI",
        recommended_path="On-Prem GPU",
        verdict_summary="On-Prem GPU cluster recommended for data sovereignty and real-time inference.",
        key_recommendations=["Negotiate multi-vendor GPU procurement", "Maintain open-source driver fallback"],
        explanation_trail=ExplanationTrail(
            summary="Trail",
            steps=[
                AuditStep(
                    stage="diagnosis",
                    claim="On-Prem GPU GPU Vendor",
                    evidence="Driver Discontinuation",
                    grounded_in="On-Prem GPU GPU Vendor: Driver Discontinuation Inference pipeline Vendor EOL 3 years",
                )
            ],
        ),
    )

    with patch("app.agents.ingestion.ingestion_agent.run", return_value=context), \
         patch("app.agents.stack_mapping.stack_mapping_agent.run", return_value=scope), \
         patch("app.agents.scenario_generation.scenario_generation_agent.run", return_value=raw_scenarios), \
         patch("app.agents.outcome_prediction.outcome_prediction_agent.run", return_value=sufficient_outcomes), \
         patch(
             "app.agents.outcome_prediction.sub_agents.timeline_projection_sub_agent.run",
             return_value=mock_timeline_projections,
         ) as mock_timeline_run, \
         patch(
             "app.agents.dependency_diagnosis.dependency_diagnosis_agent.run",
             side_effect=[thin_diagnoses, sufficient_diagnoses],
         ) as mock_diag_run, \
         patch("app.agents.orchestrator.orchestrator_agent.run", return_value=mock_verdict):

        res = run_pipeline(
            entity="Defense Agency",
            capability="satellite imagery AI",
            options=["on-prem GPU cluster", "cloud API"],
        )

        # Pipeline ran all the way to verdict
        assert res.verdict is not None
        assert res.verdict.recommended_path == "On-Prem GPU"
        assert res.verification_passed is True

        # dependency_diagnosis_agent was called twice: initial thin + re-run after timeline enrichment
        assert mock_diag_run.call_count == 2

        # timeline_projection_sub_agent was invoked exactly once during the fallback
        assert mock_timeline_run.call_count == 1

        # timeline_projection_sub_agent received the current trajectories and scenarios
        traj_arg = mock_timeline_run.call_args.kwargs["trajectories"]
        scenario_arg = mock_timeline_run.call_args.kwargs["scenarios"]
        assert len(traj_arg) == 2
        assert traj_arg[0].scenario_name == "On-Prem GPU"
        assert traj_arg[1].scenario_name == "Cloud API"
        assert len(scenario_arg) == 2

        # Recalibration trail recorded the dependency_diagnosis -> outcome_prediction loop-back
        assert len(res.recalibration_trail) == 1
        req = res.recalibration_trail[0]
        assert req.from_stage == "dependency_diagnosis"
        assert req.to_stage == "outcome_prediction"
        assert req.reason == "insufficient"
        assert req.iteration_count == 1
        assert "timeline_projection_sub_agent" in req.gap_description

        # The final diagnosis set is the sufficient one (with concrete dependencies)
        assert res.diagnosis_set is not None
        assert len(res.diagnosis_set.diagnoses) == 1
        assert len(res.diagnosis_set.diagnoses[0].dependencies) == 1
        assert res.diagnosis_set.diagnoses[0].dependencies[0].dependency_name == "GPU Vendor"


def test_pipeline_orchestrator_fallback_path_scoped_dependency_diagnosis():
    """Integration test (7.5.9): when cross_path_comparison_sub_agent finds asymmetric completeness
    (one path has lock_in_count=0 while another has lock_in_count>0), re-run Dependency-Diagnosis
    scoped to only the deficient path, merge results, re-run Orchestrator, and confirm the
    non-deficient path's diagnosis was NOT re-run (i.e. remains untouched from Stage 5)."""
    context = IngestionContext(
        entity="Retail Corp",
        capability="demand forecasting AI",
        options=["cloud SaaS", "open-source on-prem"],
        context_summary=(
            "Retail Corp demand forecasting AI. "
            "Fact: Seasonal peak load requires elastic compute. "
            "Fact: Data residency within EU mandated."
        ),
        key_facts=[
            "Fact: Seasonal peak load requires elastic compute.",
            "Fact: Data residency within EU mandated.",
        ],
        sources=["https://example.com/retail1"],
        raw_retrieved_content=(
            "Retail Corp demand forecasting AI. "
            "Fact: Seasonal peak load requires elastic compute. "
            "Fact: Data residency within EU mandated."
        ),
    )

    scope = StackScope(
        entity="Retail Corp",
        capability="demand forecasting AI",
        layers=[
            StackLayer(name="Compute Layer", rationale="Elastic compute for peak load", evidence="Fact: Seasonal peak load requires elastic compute."),
            StackLayer(name="Data Sovereignty Layer", rationale="EU data residency", evidence="Fact: Data residency within EU mandated."),
            StackLayer(name="ML Model Layer", rationale="Forecasting model weights", evidence="Fact: Seasonal peak load requires elastic compute."),
        ],
    )

    raw_scenarios = ScenarioSet(
        entity="Retail Corp",
        capability="demand forecasting AI",
        scenarios=[
            Scenario(
                name="Cloud SaaS",
                option_name="cloud SaaS",
                description="Managed cloud SaaS forecasting with EU data-residency controls",
                grounded_in="Data Sovereignty Layer: EU data residency Fact: Data residency within EU mandated.",
            ),
            Scenario(
                name="Open-Source On-Prem",
                option_name="open-source on-prem",
                description="Self-hosted open-source forecasting on own GPU cluster",
                grounded_in="Compute Layer: Elastic compute for peak load Fact: Seasonal peak load requires elastic compute.",
            ),
        ],
    )

    mock_outcomes = OutcomeSet(
        entity="Retail Corp",
        capability="demand forecasting AI",
        outcomes=[
            OutcomeProjection(
                scenario_name="Cloud SaaS",
                trajectory=Trajectory(
                    scenario_name="Cloud SaaS",
                    summary="Cloud SaaS trajectory with vendor-managed EU residency controls",
                    grounded_in="Cloud SaaS: Managed cloud SaaS forecasting with EU data-residency controls",
                ),
                risk_factors=[RiskFactor(scenario_name="Cloud SaaS", factor_name="Vendor Lock-In", description="Dependence on SaaS provider APIs")],
            ),
            OutcomeProjection(
                scenario_name="Open-Source On-Prem",
                trajectory=Trajectory(
                    scenario_name="Open-Source On-Prem",
                    summary="Self-hosted trajectory with full infrastructure ownership",
                    grounded_in="Open-Source On-Prem: Self-hosted open-source forecasting on own GPU cluster",
                ),
                risk_factors=[RiskFactor(scenario_name="Open-Source On-Prem", factor_name="Ops Burden", description="High operational overhead")],
            ),
        ],
    )

    # Stage 5 (initial full run): Cloud SaaS has good diagnosis; Open-Source has empty deps (deficient)
    initial_diagnoses = DiagnosisSet(
        entity="Retail Corp",
        capability="demand forecasting AI",
        diagnoses=[
            DependencyDiagnosis(
                scenario_name="Cloud SaaS",
                dependencies=[
                    LockInDependency(
                        scenario_name="Cloud SaaS",
                        dependency_name="SaaS Provider",
                        lock_in_type="Vendor Lock-In",
                        description="Proprietary SaaS APIs with no open standard",
                    )
                ],
                failure_modes=[
                    FailureMode(
                        scenario_name="Cloud SaaS",
                        dependency_name="SaaS Provider",
                        failure_mode_title="Provider Exit",
                        what_breaks="Forecasting pipeline",
                        trigger_condition="SaaS vendor shutdown",
                        time_horizon="2 years",
                        grounded_in="Cloud SaaS: Cloud SaaS trajectory with vendor-managed EU residency controls",
                    )
                ],
                severity_scores=[
                    DependencySeverityScore(
                        scenario_name="Cloud SaaS",
                        dependency_name="SaaS Provider",
                        severity_score=7.0,
                        urgency_score=5.5,
                        risk_level="Medium",
                        rationale="Mitigable with data export contracts",
                    )
                ],
            ),
            DependencyDiagnosis(
                scenario_name="Open-Source On-Prem",
                dependencies=[],  # No dependencies found initially -> deficient
                failure_modes=[],
            ),
        ],
    )

    # Path-scoped re-run result for deficient path "Open-Source On-Prem"
    enriched_open_source_diag = DiagnosisSet(
        entity="Retail Corp",
        capability="demand forecasting AI",
        diagnoses=[
            DependencyDiagnosis(
                scenario_name="Open-Source On-Prem",
                dependencies=[
                    LockInDependency(
                        scenario_name="Open-Source On-Prem",
                        dependency_name="GPU Hardware",
                        lock_in_type="Hardware Lock-In",
                        description="Tied to specific GPU vendor for ML acceleration",
                    )
                ],
                failure_modes=[
                    FailureMode(
                        scenario_name="Open-Source On-Prem",
                        dependency_name="GPU Hardware",
                        failure_mode_title="Hardware EOL",
                        what_breaks="Model training and inference",
                        trigger_condition="GPU vendor discontinues line",
                        time_horizon="3 years",
                        grounded_in="Open-Source On-Prem: Self-hosted trajectory with full infrastructure ownership",
                    )
                ],
            ),
        ],
    )

    # 1st Orchestrator call: asymmetric comparison — Cloud SaaS has lock_in_count=1, Open-Source has 0
    asymmetric_verdict = OrchestratorVerdict(
        entity="Retail Corp",
        capability="demand forecasting AI",
        recommended_path="Cloud SaaS",
        verdict_summary="Asymmetric analysis: Cloud SaaS fully diagnosed; Open-Source path underdiagnosed.",
        key_recommendations=["Negotiate SaaS exit clause"],
        cross_path_comparison=CrossPathComparison(
            comparative_narrative="Cloud SaaS has concrete lock-in data; Open-Source path has none — asymmetric.",
            path_comparisons=[
                PathComparison(
                    scenario_name="Cloud SaaS",
                    lock_in_count=1,
                    max_severity_score=7.0,
                    key_tradeoffs=["Vendor API lock-in vs managed operations"],
                    path_summary="Well-diagnosed with medium-risk SaaS dependency.",
                ),
                PathComparison(
                    scenario_name="Open-Source On-Prem",
                    lock_in_count=0,  # Deficient: no lock-ins identified yet
                    max_severity_score=0.0,
                    key_tradeoffs=[],
                    path_summary="Under-diagnosed — no lock-in data available for comparison.",
                ),
            ],
        ),
        explanation_trail=ExplanationTrail(
            summary="Asymmetric analysis — Open-Source path requires further diagnosis.",
            steps=[
                AuditStep(
                    stage="diagnosis",
                    claim="Cloud SaaS SaaS Provider",
                    evidence="Provider Exit",
                    grounded_in="Cloud SaaS SaaS Provider: Provider Exit Forecasting pipeline SaaS vendor shutdown 2 years",
                )
            ],
        ),
    )

    # 2nd Orchestrator call: balanced comparison — both paths now have lock-in data
    balanced_verdict = OrchestratorVerdict(
        entity="Retail Corp",
        capability="demand forecasting AI",
        recommended_path="Cloud SaaS",
        verdict_summary="Cloud SaaS recommended for managed EU compliance with acceptable lock-in risk.",
        key_recommendations=["Negotiate SaaS exit clause", "Maintain open-source fallback plan"],
        cross_path_comparison=CrossPathComparison(
            comparative_narrative="Both paths now fully diagnosed. Cloud SaaS offers managed compliance; Open-Source has hardware lock-in.",
            path_comparisons=[
                PathComparison(
                    scenario_name="Cloud SaaS",
                    lock_in_count=1,
                    max_severity_score=7.0,
                    key_tradeoffs=["Vendor API lock-in vs managed operations"],
                    path_summary="Medium-risk with mitigable SaaS dependency.",
                ),
                PathComparison(
                    scenario_name="Open-Source On-Prem",
                    lock_in_count=1,
                    max_severity_score=6.5,
                    key_tradeoffs=["Hardware lock-in vs full operational control"],
                    path_summary="Hardware lock-in is manageable with multi-vendor procurement.",
                ),
            ],
        ),
        explanation_trail=ExplanationTrail(
            summary="Balanced cross-path analysis complete.",
            steps=[
                AuditStep(
                    stage="diagnosis",
                    claim="Cloud SaaS SaaS Provider",
                    evidence="Provider Exit",
                    grounded_in="Cloud SaaS SaaS Provider: Provider Exit Forecasting pipeline SaaS vendor shutdown 2 years",
                ),
                AuditStep(
                    stage="diagnosis",
                    claim="Open-Source On-Prem GPU Hardware",
                    evidence="Hardware EOL",
                    grounded_in="Open-Source On-Prem GPU Hardware: Hardware EOL Model training and inference GPU vendor discontinues line 3 years",
                ),
            ],
        ),
    )

    with patch("app.agents.ingestion.ingestion_agent.run", return_value=context), \
         patch("app.agents.stack_mapping.stack_mapping_agent.run", return_value=scope), \
         patch("app.agents.scenario_generation.scenario_generation_agent.run", return_value=raw_scenarios), \
         patch("app.agents.outcome_prediction.outcome_prediction_agent.run", return_value=mock_outcomes), \
         patch(
             "app.agents.dependency_diagnosis.dependency_diagnosis_agent.run",
             side_effect=[initial_diagnoses, enriched_open_source_diag],
         ) as mock_diag_run, \
         patch(
             "app.agents.orchestrator.orchestrator_agent.run",
             side_effect=[asymmetric_verdict, balanced_verdict],
         ) as mock_orchestrator_run:

        res = run_pipeline(
            entity="Retail Corp",
            capability="demand forecasting AI",
            options=["cloud SaaS", "open-source on-prem"],
        )

        # Pipeline completed all the way to a final verdict
        assert res.verdict is not None
        assert res.verdict.recommended_path == "Cloud SaaS"
        assert res.verification_passed is True

        # dependency_diagnosis_agent was called twice:
        # 1st = full Stage 5 run (both paths), 2nd = path-scoped run for "Open-Source On-Prem" only
        assert mock_diag_run.call_count == 2

        # Verify the 2nd dependency_diagnosis call received only the deficient path's outcomes
        second_diag_call_outcome_set = mock_diag_run.call_args_list[1].kwargs["outcome_set"]
        assert len(second_diag_call_outcome_set.outcomes) == 1
        assert second_diag_call_outcome_set.outcomes[0].scenario_name == "Open-Source On-Prem"

        # Orchestrator was called twice: 1st with asymmetric data, 2nd after enrichment
        assert mock_orchestrator_run.call_count == 2

        # Verify the 2nd Orchestrator call received the enriched DiagnosisSet (both paths diagnosed)
        second_orch_call_diag_set = mock_orchestrator_run.call_args_list[1].kwargs["diagnosis_set"]
        diag_names = {d.scenario_name for d in second_orch_call_diag_set.diagnoses}
        assert "Cloud SaaS" in diag_names
        assert "Open-Source On-Prem" in diag_names

        # Cloud SaaS diagnosis was NOT re-run — confirm it kept its original dependencies
        cloud_saas_diag = next(d for d in second_orch_call_diag_set.diagnoses if d.scenario_name == "Cloud SaaS")
        assert len(cloud_saas_diag.dependencies) == 1
        assert cloud_saas_diag.dependencies[0].dependency_name == "SaaS Provider"

        # Open-Source On-Prem diagnosis was enriched by the scoped re-run
        open_source_diag = next(d for d in second_orch_call_diag_set.diagnoses if d.scenario_name == "Open-Source On-Prem")
        assert len(open_source_diag.dependencies) == 1
        assert open_source_diag.dependencies[0].dependency_name == "GPU Hardware"

        # Recalibration trail recorded the orchestrator -> dependency_diagnosis loop-back
        assert len(res.recalibration_trail) == 1
        req = res.recalibration_trail[0]
        assert req.from_stage == "orchestrator"
        assert req.to_stage == "dependency_diagnosis"
        assert req.reason == "insufficient"
        assert req.iteration_count == 1
        assert "cross_path_comparison_sub_agent" in req.gap_description
        assert "Open-Source On-Prem" in req.gap_description


def test_pipeline_partial_verdict_terminal_state_on_loop_guard_exceeded():
    """Integration test (7.5.10): when the loop-guard cap is hit before a stage becomes sufficient,
    the pipeline appends a caveat to `partial_verdict_caveats` and proceeds rather than looping indefinitely.
    Asserts a caveat-flagged (not null) verdict is returned."""
    
    # We will mock stack_mapping to ALWAYS return a 1-layer scope (which is insufficient).
    # With LoopGuard max_retries=1, it will try to fallback once, and on the next iteration
    # it will hit the cap and proceed anyway.
    
    context = IngestionContext(
        entity="Corp", capability="AI", options=["A"],
        context_summary="Fact: Something.", key_facts=["Fact: Something."],
        sources=["http://x.com"], raw_retrieved_content="Fact: Something."
    )
    
    # Always insufficient (< 2 layers)
    thin_scope = StackScope(
        entity="Corp", capability="AI",
        layers=[StackLayer(name="Layer", rationale="R", evidence="Fact: Something.")]
    )
    
    # Valid output for remaining stages so the pipeline completes
    scenarios = ScenarioSet(
        entity="Corp", capability="AI",
        scenarios=[
            Scenario(name="A", option_name="A", description="A", grounded_in="Layer: R Fact: Something."),
            Scenario(name="B", option_name="B", description="B", grounded_in="Layer: R Fact: Something.")
        ]
    )
    outcomes = OutcomeSet(
        entity="Corp", capability="AI",
        outcomes=[
            OutcomeProjection(
                scenario_name="A",
                trajectory=Trajectory(scenario_name="A", summary="A", grounded_in="A: A"),
                risk_factors=[RiskFactor(scenario_name="A", factor_name="R1", description="D1")]
            ),
            OutcomeProjection(
                scenario_name="B",
                trajectory=Trajectory(scenario_name="B", summary="B", grounded_in="B: B"),
                risk_factors=[RiskFactor(scenario_name="B", factor_name="R2", description="D2")]
            )
        ]
    )
    diagnoses = DiagnosisSet(
        entity="Corp", capability="AI",
        diagnoses=[
            DependencyDiagnosis(
                scenario_name="A",
                dependencies=[LockInDependency(scenario_name="A", dependency_name="D", lock_in_type="T", description="D")],
                failure_modes=[], severity_scores=[]
            ),
            DependencyDiagnosis(
                scenario_name="B",
                dependencies=[LockInDependency(scenario_name="B", dependency_name="D", lock_in_type="T", description="D")],
                failure_modes=[], severity_scores=[]
            )
        ]
    )
    verdict = OrchestratorVerdict(
        entity="Corp", capability="AI", recommended_path="A", verdict_summary="V", key_recommendations=["K"],
        cross_path_comparison=CrossPathComparison(
            comparative_narrative="N",
            path_comparisons=[
                PathComparison(scenario_name="A", lock_in_count=1, max_severity_score=0.0, key_tradeoffs=[], path_summary="S"),
                PathComparison(scenario_name="B", lock_in_count=1, max_severity_score=0.0, key_tradeoffs=[], path_summary="S")
            ]
        ),
        explanation_trail=None
    )

    with patch("app.agents.ingestion.ingestion_agent.run", return_value=context), \
         patch("app.agents.stack_mapping.stack_mapping_agent.run", return_value=thin_scope), \
         patch("app.agents.scenario_generation.scenario_generation_agent.run", return_value=scenarios), \
         patch("app.agents.outcome_prediction.outcome_prediction_agent.run", return_value=outcomes), \
         patch("app.agents.dependency_diagnosis.dependency_diagnosis_agent.run", return_value=diagnoses), \
         patch("app.agents.orchestrator.orchestrator_agent.run", return_value=verdict):

        from app.verification.recalibration import LoopGuard
        # Custom loop guard allowing only 1 retry
        guard = LoopGuard(max_retries=1)
        
        res = run_pipeline(
            entity="Corp",
            capability="AI",
            options=["A", "B"],
            loop_guard=guard
        )
        
        # Pipeline didn't crash and produced a verdict
        assert res.verdict is not None
        
        # Recalibration trail has the 1 attempted loop-back
        assert len(res.recalibration_trail) == 1
        assert res.recalibration_trail[0].from_stage == "stack_mapping"
        assert res.recalibration_trail[0].to_stage == "ingestion"
        
        # The pipeline hit the cap on the next try and flagged it
        assert len(res.partial_verdict_caveats) == 1
        caveat = res.partial_verdict_caveats[0]
        assert "stack_mapping → ingestion" in caveat
        assert "cap=1" in caveat
        assert "constrained recalibration" in caveat
