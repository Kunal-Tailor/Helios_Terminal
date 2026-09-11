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

    with patch("app.agents.ingestion.ingestion_agent.run", return_value=bad_context), \
         patch("app.agents.stack_mapping.stack_mapping_agent.run", return_value=sample_scope) as mock_stack, \
         patch("app.agents.scenario_generation.scenario_generation_agent.run", return_value=sample_scenarios) as mock_scenarios, \
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

