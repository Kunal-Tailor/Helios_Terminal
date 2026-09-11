"""
Unit tests for app.verification.recalibration — sufficiency-check functions (Phase 7.5.2).

For each of the six pipeline stages this module covers:
  check_sufficiency_ingestion
  check_sufficiency_stack_mapping
  check_sufficiency_scenario_generation
  check_sufficiency_outcome_prediction
  check_sufficiency_dependency_diagnosis
  check_sufficiency_orchestrator

Each stage has:
  - A known-sufficient case (passes the threshold)
  - A known-insufficient case (fails the threshold)
  - Boundary / edge cases where relevant

The tests use lightweight dataclass stubs that mirror the real agent output
types without importing the agent modules (which need live LLM clients).
This keeps tests fast, isolated, and free of network/IO dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from app.verification.recalibration import (
    SufficiencyResult,
    check_sufficiency_dependency_diagnosis,
    check_sufficiency_ingestion,
    check_sufficiency_orchestrator,
    check_sufficiency_outcome_prediction,
    check_sufficiency_scenario_generation,
    check_sufficiency_stack_mapping,
)


# ---------------------------------------------------------------------------
# Minimal stubs — mirror only the fields the check functions inspect.
# Using real dataclasses so isinstance checks still pass for any future
# structural validation.
# ---------------------------------------------------------------------------

@dataclass
class _StackLayer:
    name: str


@dataclass
class _StackScope:
    layers: list[_StackLayer] = field(default_factory=list)


@dataclass
class _Scenario:
    name: str


@dataclass
class _ScenarioSet:
    scenarios: list[_Scenario] = field(default_factory=list)


@dataclass
class _RiskFactor:
    description: str


@dataclass
class _Trajectory:
    scenario_name: str


@dataclass
class _OutcomeProjection:
    scenario_name: str
    trajectory: _Trajectory | None = None
    risk_factors: list[_RiskFactor] = field(default_factory=list)


@dataclass
class _OutcomeSet:
    outcomes: list[_OutcomeProjection] = field(default_factory=list)


@dataclass
class _LockInDependency:
    dependency_name: str


@dataclass
class _DependencyDiagnosis:
    scenario_name: str
    dependencies: list[_LockInDependency] = field(default_factory=list)


@dataclass
class _DiagnosisSet:
    diagnoses: list[_DependencyDiagnosis] = field(default_factory=list)


@dataclass
class _OrchestratorVerdict:
    verdict_summary: str = ""
    key_recommendations: list[str] = field(default_factory=list)


@dataclass
class _IngestionContext:
    context_summary: str = ""
    key_facts: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _layers(n: int) -> list[_StackLayer]:
    return [_StackLayer(name=f"Layer {i}") for i in range(n)]


def _scenarios(n: int) -> list[_Scenario]:
    return [_Scenario(name=f"Scenario {i}") for i in range(n)]


# ---------------------------------------------------------------------------
# SufficiencyResult — dataclass sanity
# ---------------------------------------------------------------------------

class TestSufficiencyResultDataclass:
    def test_fields_are_stored(self):
        r = SufficiencyResult(sufficient=True, stage="ingestion", reason="ok", detail="x")
        assert r.sufficient is True
        assert r.stage == "ingestion"
        assert r.reason == "ok"
        assert r.detail == "x"

    def test_detail_defaults_to_empty_string(self):
        r = SufficiencyResult(sufficient=False, stage="stack_mapping", reason="not enough")
        assert r.detail == ""


# ---------------------------------------------------------------------------
# check_sufficiency_ingestion
# ---------------------------------------------------------------------------

class TestCheckSufficiencyIngestion:
    def test_sufficient_with_summary_and_facts(self):
        ctx = _IngestionContext(
            context_summary="DeepSeek has published model weights on Hugging Face.",
            key_facts=["DeepSeek licensed weights under a non-commercial licence."],
        )
        result = check_sufficiency_ingestion(ctx)  # type: ignore[arg-type]
        assert result.sufficient is True
        assert result.stage == "ingestion"
        assert "1 key fact" in result.reason

    def test_sufficient_with_multiple_facts(self):
        ctx = _IngestionContext(
            context_summary="Some summary.",
            key_facts=["Fact A", "Fact B", "Fact C"],
        )
        result = check_sufficiency_ingestion(ctx)  # type: ignore[arg-type]
        assert result.sufficient is True
        assert "3 key fact" in result.reason

    def test_insufficient_empty_summary(self):
        ctx = _IngestionContext(
            context_summary="",
            key_facts=["Fact A"],
        )
        result = check_sufficiency_ingestion(ctx)  # type: ignore[arg-type]
        assert result.sufficient is False
        assert "context_summary is empty" in result.reason
        assert result.stage == "ingestion"

    def test_insufficient_no_facts(self):
        ctx = _IngestionContext(
            context_summary="Some summary.",
            key_facts=[],
        )
        result = check_sufficiency_ingestion(ctx)  # type: ignore[arg-type]
        assert result.sufficient is False
        assert "key fact" in result.reason

    def test_insufficient_empty_summary_and_no_facts(self):
        ctx = _IngestionContext(context_summary="", key_facts=[])
        result = check_sufficiency_ingestion(ctx)  # type: ignore[arg-type]
        assert result.sufficient is False
        assert "context_summary is empty" in result.reason

    def test_insufficient_whitespace_only_summary(self):
        ctx = _IngestionContext(context_summary="   ", key_facts=["Fact A"])
        result = check_sufficiency_ingestion(ctx)  # type: ignore[arg-type]
        assert result.sufficient is False
        assert "context_summary is empty" in result.reason

    def test_reason_is_non_empty_string_in_all_cases(self):
        for ctx in [
            _IngestionContext(context_summary="S", key_facts=["F"]),
            _IngestionContext(context_summary="", key_facts=[]),
        ]:
            result = check_sufficiency_ingestion(ctx)  # type: ignore[arg-type]
            assert isinstance(result.reason, str)
            assert len(result.reason) > 0


# ---------------------------------------------------------------------------
# check_sufficiency_stack_mapping
# ---------------------------------------------------------------------------

class TestCheckSufficiencyStackMapping:
    def test_sufficient_two_layers(self):
        scope = _StackScope(layers=_layers(2))
        result = check_sufficiency_stack_mapping(scope)  # type: ignore[arg-type]
        assert result.sufficient is True
        assert result.stage == "stack_mapping"
        assert "2" in result.reason

    def test_sufficient_many_layers(self):
        scope = _StackScope(layers=_layers(5))
        result = check_sufficiency_stack_mapping(scope)  # type: ignore[arg-type]
        assert result.sufficient is True

    def test_insufficient_zero_layers(self):
        scope = _StackScope(layers=[])
        result = check_sufficiency_stack_mapping(scope)  # type: ignore[arg-type]
        assert result.sufficient is False
        assert result.stage == "stack_mapping"
        assert "0" in result.reason or "only 0" in result.reason.lower()

    def test_insufficient_one_layer(self):
        """One layer is below the threshold of 2 — must be flagged."""
        scope = _StackScope(layers=_layers(1))
        result = check_sufficiency_stack_mapping(scope)  # type: ignore[arg-type]
        assert result.sufficient is False
        assert "1" in result.reason

    def test_detail_contains_layer_count(self):
        scope = _StackScope(layers=_layers(3))
        result = check_sufficiency_stack_mapping(scope)  # type: ignore[arg-type]
        assert result.detail == "3"

    def test_detail_zero_layers(self):
        scope = _StackScope(layers=[])
        result = check_sufficiency_stack_mapping(scope)  # type: ignore[arg-type]
        assert result.detail == "0"


# ---------------------------------------------------------------------------
# check_sufficiency_scenario_generation
# ---------------------------------------------------------------------------

class TestCheckSufficiencyScenarioGeneration:
    def test_sufficient_two_scenarios(self):
        ss = _ScenarioSet(scenarios=_scenarios(2))
        result = check_sufficiency_scenario_generation(ss)  # type: ignore[arg-type]
        assert result.sufficient is True
        assert result.stage == "scenario_generation"

    def test_sufficient_many_scenarios(self):
        ss = _ScenarioSet(scenarios=_scenarios(4))
        result = check_sufficiency_scenario_generation(ss)  # type: ignore[arg-type]
        assert result.sufficient is True

    def test_insufficient_zero_scenarios(self):
        ss = _ScenarioSet(scenarios=[])
        result = check_sufficiency_scenario_generation(ss)  # type: ignore[arg-type]
        assert result.sufficient is False
        assert result.stage == "scenario_generation"

    def test_insufficient_one_scenario(self):
        """One scenario is below the threshold of 2."""
        ss = _ScenarioSet(scenarios=_scenarios(1))
        result = check_sufficiency_scenario_generation(ss)  # type: ignore[arg-type]
        assert result.sufficient is False
        assert "1" in result.reason

    def test_boundary_exactly_two(self):
        """Exactly 2 scenarios is the minimum sufficient value."""
        ss = _ScenarioSet(scenarios=_scenarios(2))
        assert check_sufficiency_scenario_generation(ss).sufficient is True  # type: ignore[arg-type]

    def test_detail_contains_scenario_count(self):
        ss = _ScenarioSet(scenarios=_scenarios(3))
        result = check_sufficiency_scenario_generation(ss)  # type: ignore[arg-type]
        assert result.detail == "3"


# ---------------------------------------------------------------------------
# check_sufficiency_outcome_prediction
# ---------------------------------------------------------------------------

class TestCheckSufficiencyOutcomePrediction:
    def _make_outcome_set(
        self,
        *,
        n_with_trajectory: int = 1,
        n_without_trajectory: int = 0,
        risk_per_projection: int = 1,
    ) -> _OutcomeSet:
        outcomes = []
        for i in range(n_with_trajectory):
            outcomes.append(
                _OutcomeProjection(
                    scenario_name=f"scenario_{i}",
                    trajectory=_Trajectory(scenario_name=f"scenario_{i}"),
                    risk_factors=[_RiskFactor(description=f"risk_{j}") for j in range(risk_per_projection)],
                )
            )
        for i in range(n_without_trajectory):
            outcomes.append(
                _OutcomeProjection(
                    scenario_name=f"no_traj_{i}",
                    trajectory=None,
                    risk_factors=[],
                )
            )
        return _OutcomeSet(outcomes=outcomes)

    def test_sufficient_one_trajectory_one_risk(self):
        outcome_set = self._make_outcome_set(n_with_trajectory=1, risk_per_projection=1)
        result = check_sufficiency_outcome_prediction(outcome_set)  # type: ignore[arg-type]
        assert result.sufficient is True
        assert result.stage == "outcome_prediction"

    def test_sufficient_multiple_projections(self):
        outcome_set = self._make_outcome_set(n_with_trajectory=2, risk_per_projection=2)
        result = check_sufficiency_outcome_prediction(outcome_set)  # type: ignore[arg-type]
        assert result.sufficient is True

    def test_insufficient_no_trajectories(self):
        outcome_set = self._make_outcome_set(n_with_trajectory=0, n_without_trajectory=2, risk_per_projection=0)
        result = check_sufficiency_outcome_prediction(outcome_set)  # type: ignore[arg-type]
        assert result.sufficient is False
        assert "trajectory" in result.reason

    def test_insufficient_no_risk_factors(self):
        outcome_set = self._make_outcome_set(n_with_trajectory=1, risk_per_projection=0)
        result = check_sufficiency_outcome_prediction(outcome_set)  # type: ignore[arg-type]
        assert result.sufficient is False
        assert "risk factor" in result.reason

    def test_insufficient_empty_outcome_set(self):
        outcome_set = _OutcomeSet(outcomes=[])
        result = check_sufficiency_outcome_prediction(outcome_set)  # type: ignore[arg-type]
        assert result.sufficient is False

    def test_detail_format(self):
        outcome_set = self._make_outcome_set(n_with_trajectory=2, risk_per_projection=3)
        result = check_sufficiency_outcome_prediction(outcome_set)  # type: ignore[arg-type]
        assert "trajectories=2" in result.detail
        assert "risk_factors=6" in result.detail


# ---------------------------------------------------------------------------
# check_sufficiency_dependency_diagnosis
# ---------------------------------------------------------------------------

class TestCheckSufficiencyDependencyDiagnosis:
    def test_sufficient_one_diagnosis_with_deps(self):
        ds = _DiagnosisSet(diagnoses=[
            _DependencyDiagnosis(
                scenario_name="build",
                dependencies=[_LockInDependency(dependency_name="GPU vendor")],
            )
        ])
        result = check_sufficiency_dependency_diagnosis(ds)  # type: ignore[arg-type]
        assert result.sufficient is True
        assert result.stage == "dependency_diagnosis"

    def test_sufficient_multiple_diagnoses(self):
        ds = _DiagnosisSet(diagnoses=[
            _DependencyDiagnosis(
                scenario_name="build",
                dependencies=[_LockInDependency(dependency_name="GPU vendor")],
            ),
            _DependencyDiagnosis(
                scenario_name="license",
                dependencies=[_LockInDependency(dependency_name="Model licence")],
            ),
        ])
        result = check_sufficiency_dependency_diagnosis(ds)  # type: ignore[arg-type]
        assert result.sufficient is True

    def test_insufficient_all_diagnoses_empty(self):
        ds = _DiagnosisSet(diagnoses=[
            _DependencyDiagnosis(scenario_name="build", dependencies=[]),
            _DependencyDiagnosis(scenario_name="license", dependencies=[]),
        ])
        result = check_sufficiency_dependency_diagnosis(ds)  # type: ignore[arg-type]
        assert result.sufficient is False
        assert result.stage == "dependency_diagnosis"

    def test_insufficient_empty_diagnosis_set(self):
        ds = _DiagnosisSet(diagnoses=[])
        result = check_sufficiency_dependency_diagnosis(ds)  # type: ignore[arg-type]
        assert result.sufficient is False

    def test_mixed_some_empty_some_with_deps(self):
        """One empty diagnosis + one with deps: threshold of 1 is met."""
        ds = _DiagnosisSet(diagnoses=[
            _DependencyDiagnosis(scenario_name="build", dependencies=[]),
            _DependencyDiagnosis(
                scenario_name="license",
                dependencies=[_LockInDependency(dependency_name="Model licence")],
            ),
        ])
        result = check_sufficiency_dependency_diagnosis(ds)  # type: ignore[arg-type]
        assert result.sufficient is True

    def test_detail_counts_diagnoses_with_deps(self):
        ds = _DiagnosisSet(diagnoses=[
            _DependencyDiagnosis(
                scenario_name="build",
                dependencies=[_LockInDependency("GPU")],
            ),
            _DependencyDiagnosis(scenario_name="license", dependencies=[]),
        ])
        result = check_sufficiency_dependency_diagnosis(ds)  # type: ignore[arg-type]
        assert result.detail == "1"


# ---------------------------------------------------------------------------
# check_sufficiency_orchestrator
# ---------------------------------------------------------------------------

class TestCheckSufficiencyOrchestrator:
    def test_sufficient_summary_and_one_recommendation(self):
        v = _OrchestratorVerdict(
            verdict_summary="Recommend the build-in-house path due to lower lock-in.",
            key_recommendations=["Negotiate an escape clause."],
        )
        result = check_sufficiency_orchestrator(v)  # type: ignore[arg-type]
        assert result.sufficient is True
        assert result.stage == "orchestrator"

    def test_sufficient_multiple_recommendations(self):
        v = _OrchestratorVerdict(
            verdict_summary="Full verdict text.",
            key_recommendations=["Rec A", "Rec B", "Rec C"],
        )
        result = check_sufficiency_orchestrator(v)  # type: ignore[arg-type]
        assert result.sufficient is True

    def test_insufficient_empty_summary(self):
        v = _OrchestratorVerdict(
            verdict_summary="",
            key_recommendations=["Rec A"],
        )
        result = check_sufficiency_orchestrator(v)  # type: ignore[arg-type]
        assert result.sufficient is False
        assert "verdict_summary is empty" in result.reason

    def test_insufficient_whitespace_only_summary(self):
        v = _OrchestratorVerdict(
            verdict_summary="   ",
            key_recommendations=["Rec A"],
        )
        result = check_sufficiency_orchestrator(v)  # type: ignore[arg-type]
        assert result.sufficient is False
        assert "verdict_summary is empty" in result.reason

    def test_insufficient_no_recommendations(self):
        v = _OrchestratorVerdict(
            verdict_summary="Full verdict text.",
            key_recommendations=[],
        )
        result = check_sufficiency_orchestrator(v)  # type: ignore[arg-type]
        assert result.sufficient is False
        assert "recommendation" in result.reason

    def test_insufficient_empty_summary_and_no_recommendations(self):
        v = _OrchestratorVerdict(verdict_summary="", key_recommendations=[])
        result = check_sufficiency_orchestrator(v)  # type: ignore[arg-type]
        assert result.sufficient is False

    def test_detail_reports_has_summary_and_count(self):
        v = _OrchestratorVerdict(
            verdict_summary="Summary.",
            key_recommendations=["R1", "R2"],
        )
        result = check_sufficiency_orchestrator(v)  # type: ignore[arg-type]
        assert "has_summary=True" in result.detail
        assert "recommendations=2" in result.detail
