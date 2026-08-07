"""
Unit and integration tests for app.agents.dependency_diagnosis.dependency_diagnosis_agent.

UNIT TESTS (mock all sub-agents at their run() boundary)
  - run() returns a DiagnosisSet
  - run() copies entity and capability from outcome_set into DiagnosisSet
  - run() calls lock-in-identification sub-agent with outcomes
  - run() passes dependencies to failure-mode and severity-scoring sub-agents
  - run() populates DependencyDiagnosis fields (dependencies, failure_modes, severity_scores)
  - run() handles empty outcome_set (returns empty DiagnosisSet without calling sub-agents)

INTEGRATION TESTS (mock at LLM boundary; real sub-agent logic executes)
  - Full pipeline produces a DiagnosisSet with correct entity/capability
  - DiagnosisSet.diagnoses contains valid DependencyDiagnosis objects
  - Pipeline tolerates all sub-agents returning empty (all LLMs fail)
"""

from unittest.mock import patch

import pytest

from app.agents.dependency_diagnosis.dependency_diagnosis_agent import DependencyDiagnosis, DiagnosisSet, run
from app.agents.dependency_diagnosis.sub_agents.failure_mode_sub_agent import FailureMode
from app.agents.dependency_diagnosis.sub_agents.lock_in_identification_sub_agent import LockInDependency
from app.agents.dependency_diagnosis.sub_agents.severity_scoring_sub_agent import DependencySeverityScore
from app.agents.outcome_prediction.outcome_prediction_agent import OutcomeProjection, OutcomeSet
from app.agents.outcome_prediction.sub_agents.trajectory_modeling_sub_agent import Trajectory

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_OUTCOME = OutcomeProjection(
    scenario_name="Build custom LLM in-house",
    trajectory=Trajectory(
        scenario_name="Build custom LLM in-house",
        summary="3-year sovereign model capability.",
    ),
)

_OUTCOME_SET = OutcomeSet(
    entity="ACME Corp",
    capability="edge inference LLM",
    outcomes=[_OUTCOME],
)

_DEPENDENCY = LockInDependency(
    scenario_name="Build custom LLM in-house",
    dependency_name="CUDA Hardware Architecture Entanglement",
    layer_name="Hardware / Compute",
    lock_in_type="Architectural Entanglement",
    description="Tightly coupled to GPU architecture.",
)

_FAILURE_MODE = FailureMode(
    scenario_name="Build custom LLM in-house",
    dependency_name="CUDA Hardware Architecture Entanglement",
    failure_mode_title="Unmaintainable Custom CUDA Kernel Debt",
    what_breaks="Hardware migration becomes impossible.",
    trigger_condition="Next-gen GPU release.",
    time_horizon="18-24 months",
)

_SEVERITY_SCORE = DependencySeverityScore(
    scenario_name="Build custom LLM in-house",
    dependency_name="CUDA Hardware Architecture Entanglement",
    severity_score=8.5,
    urgency_score=7.0,
    risk_level="Critical",
    rationale="Extensive refactoring required.",
)

_LOCK_IN_PATH = "app.agents.dependency_diagnosis.dependency_diagnosis_agent.lock_in_identification_sub_agent.run"
_FM_PATH = "app.agents.dependency_diagnosis.dependency_diagnosis_agent.failure_mode_sub_agent.run"
_SS_PATH = "app.agents.dependency_diagnosis.dependency_diagnosis_agent.severity_scoring_sub_agent.run"


# ---------------------------------------------------------------------------
# Unit tests — sub-agent run() functions mocked
# ---------------------------------------------------------------------------

def test_unit_run_returns_diagnosis_set():
    """run() returns a DiagnosisSet instance."""
    with patch(_LOCK_IN_PATH, return_value=[_DEPENDENCY]), \
         patch(_FM_PATH, return_value=[_FAILURE_MODE]), \
         patch(_SS_PATH, return_value=[_SEVERITY_SCORE]):
        result = run(_OUTCOME_SET)

    assert isinstance(result, DiagnosisSet)


def test_unit_run_copies_entity_and_capability():
    """run() carries entity and capability from OutcomeSet into DiagnosisSet."""
    with patch(_LOCK_IN_PATH, return_value=[_DEPENDENCY]), \
         patch(_FM_PATH, return_value=[_FAILURE_MODE]), \
         patch(_SS_PATH, return_value=[_SEVERITY_SCORE]):
        result = run(_OUTCOME_SET)

    assert result.entity == "ACME Corp"
    assert result.capability == "edge inference LLM"


def test_unit_run_calls_lock_in_identification_with_outcomes():
    """run() passes outcomes to lock-in identification sub-agent."""
    with patch(_LOCK_IN_PATH, return_value=[_DEPENDENCY]) as mock_li, \
         patch(_FM_PATH, return_value=[_FAILURE_MODE]), \
         patch(_SS_PATH, return_value=[_SEVERITY_SCORE]):
        run(_OUTCOME_SET)

    mock_li.assert_called_once_with([_OUTCOME])


def test_unit_run_passes_dependencies_to_failure_mode_and_severity_scoring():
    """run() passes dependencies to failure-mode and severity-scoring sub-agents."""
    with patch(_LOCK_IN_PATH, return_value=[_DEPENDENCY]), \
         patch(_FM_PATH, return_value=[_FAILURE_MODE]) as mock_fm, \
         patch(_SS_PATH, return_value=[_SEVERITY_SCORE]) as mock_ss:
        run(_OUTCOME_SET)

    mock_fm.assert_called_once_with([_DEPENDENCY], [_OUTCOME])
    mock_ss.assert_called_once_with([_DEPENDENCY], [_FAILURE_MODE])


def test_unit_run_populates_dependency_diagnosis_fields():
    """run() maps sub-agent outputs into DependencyDiagnosis fields correctly."""
    with patch(_LOCK_IN_PATH, return_value=[_DEPENDENCY]), \
         patch(_FM_PATH, return_value=[_FAILURE_MODE]), \
         patch(_SS_PATH, return_value=[_SEVERITY_SCORE]):
        result = run(_OUTCOME_SET)

    assert len(result.diagnoses) == 1
    diag = result.diagnoses[0]

    assert isinstance(diag, DependencyDiagnosis)
    assert diag.scenario_name == "Build custom LLM in-house"
    assert diag.dependencies == [_DEPENDENCY]
    assert diag.failure_modes == [_FAILURE_MODE]
    assert diag.severity_scores == [_SEVERITY_SCORE]


def test_unit_run_handles_empty_outcomes():
    """run() returns DiagnosisSet with empty diagnoses without calling sub-agents if outcome_set is empty."""
    empty_set = OutcomeSet(entity="ACME Corp", capability="LLM", outcomes=[])

    with patch(_LOCK_IN_PATH) as mock_li, \
         patch(_FM_PATH) as mock_fm, \
         patch(_SS_PATH) as mock_ss:
        result = run(empty_set)

    assert isinstance(result, DiagnosisSet)
    assert result.diagnoses == []
    mock_li.assert_not_called()
    mock_fm.assert_not_called()
    mock_ss.assert_not_called()


# ---------------------------------------------------------------------------
# Integration tests — mocked at the LLM boundary
# Real sub-agent parsing logic executes end-to-end through the parent
# ---------------------------------------------------------------------------

_LI_LLM = "app.agents.dependency_diagnosis.sub_agents.lock_in_identification_sub_agent.complete"
_FM_LLM = "app.agents.dependency_diagnosis.sub_agents.failure_mode_sub_agent.complete"
_SS_LLM = "app.agents.dependency_diagnosis.sub_agents.severity_scoring_sub_agent.complete"

_LI_RESPONSE = """\
LOCK_IN: CUDA Hardware Architecture Entanglement
SCENARIO: Build custom LLM in-house
LAYER: Hardware / Compute
TYPE: Architectural Entanglement
DESCRIPTION: Custom training pipeline tied to GPU architecture.
---
"""

_FM_RESPONSE = """\
FAILURE_MODE: Unmaintainable Custom CUDA Kernel Debt
SCENARIO: Build custom LLM in-house
DEPENDENCY: CUDA Hardware Architecture Entanglement
WHAT_BREAKS: Hardware migration becomes impossible.
TRIGGER: Next-gen GPU release.
HORIZON: 18-24 months
---
"""

_SS_RESPONSE = """\
DEPENDENCY: CUDA Hardware Architecture Entanglement
SCENARIO: Build custom LLM in-house
SEVERITY_SCORE: 8.5
URGENCY_SCORE: 7.0
RISK_LEVEL: Critical
RATIONALE: Extensive refactoring required.
---
"""


def test_integration_run_returns_diagnosis_set():
    """Integration: full pipeline returns a DiagnosisSet."""
    with patch(_LI_LLM, return_value=_LI_RESPONSE), \
         patch(_FM_LLM, return_value=_FM_RESPONSE), \
         patch(_SS_LLM, return_value=_SS_RESPONSE):
        result = run(_OUTCOME_SET)

    assert isinstance(result, DiagnosisSet)
    assert result.entity == "ACME Corp"
    assert result.capability == "edge inference LLM"


def test_integration_diagnoses_contain_valid_objects():
    """Integration: DiagnosisSet.diagnoses contains complete DependencyDiagnosis objects."""
    with patch(_LI_LLM, return_value=_LI_RESPONSE), \
         patch(_FM_LLM, return_value=_FM_RESPONSE), \
         patch(_SS_LLM, return_value=_SS_RESPONSE):
        result = run(_OUTCOME_SET)

    assert len(result.diagnoses) == 1
    diag = result.diagnoses[0]

    assert diag.scenario_name == "Build custom LLM in-house"
    assert len(diag.dependencies) == 1
    assert len(diag.failure_modes) == 1
    assert len(diag.severity_scores) == 1


def test_integration_pipeline_tolerates_all_llm_failures():
    """Integration: pipeline returns DiagnosisSet with empty sub-lists when all LLM calls fail."""
    with patch(_LI_LLM, side_effect=RuntimeError("LLM down")), \
         patch(_FM_LLM, side_effect=RuntimeError("LLM down")), \
         patch(_SS_LLM, side_effect=RuntimeError("LLM down")):
        result = run(_OUTCOME_SET)

    assert isinstance(result, DiagnosisSet)
    assert len(result.diagnoses) == 1
    assert result.diagnoses[0].dependencies == []
    assert result.diagnoses[0].failure_modes == []
    assert result.diagnoses[0].severity_scores == []
