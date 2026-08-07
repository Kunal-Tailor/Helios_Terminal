"""
Unit and integration tests for app.agents.orchestrator.orchestrator_agent.

UNIT TESTS (mock all sub-agents at their run() boundary)
  - run() returns an OrchestratorVerdict
  - run() copies entity and capability from diagnosis_set into OrchestratorVerdict
  - run() calls cross-path-comparison sub-agent with diagnoses
  - run() passes comparison and diagnoses to verdict-synthesis sub-agent
  - run() passes diagnoses, verdict, and sources to explanation-trail sub-agent
  - run() populates OrchestratorVerdict fields correctly
  - run() handles empty diagnosis_set (returns empty OrchestratorVerdict without calling sub-agents)

INTEGRATION TESTS (mock at LLM boundary; real sub-agent logic executes)
  - Full pipeline produces an OrchestratorVerdict with correct entity/capability
  - OrchestratorVerdict contains valid sub-objects (CrossPathComparison, ExplanationTrail)
  - Pipeline tolerates all sub-agents returning empty (all LLMs fail)
"""

from unittest.mock import patch

import pytest

from app.agents.dependency_diagnosis.dependency_diagnosis_agent import DependencyDiagnosis, DiagnosisSet
from app.agents.orchestrator.orchestrator_agent import OrchestratorVerdict, run
from app.agents.orchestrator.sub_agents.cross_path_comparison_sub_agent import CrossPathComparison, PathComparison
from app.agents.orchestrator.sub_agents.explanation_trail_sub_agent import AuditStep, ExplanationTrail
from app.agents.orchestrator.sub_agents.verdict_synthesis_sub_agent import VerdictSynthesis

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_DIAGNOSIS = DependencyDiagnosis(scenario_name="Build custom LLM in-house")

_DIAGNOSIS_SET = DiagnosisSet(
    entity="ACME Corp",
    capability="edge inference LLM",
    diagnoses=[_DIAGNOSIS],
)

_COMPARISON = CrossPathComparison(
    comparative_narrative="Comparative analysis narrative.",
    path_comparisons=[
        PathComparison(scenario_name="Build custom LLM in-house", lock_in_count=1, max_severity_score=8.5)
    ],
)

_VERDICT = VerdictSynthesis(
    recommended_path="License open-weight model",
    verdict_summary="License open-weight model is recommended.",
    key_recommendations=["Pin version"],
    path_stances={"License open-weight model": "Recommended"},
)

_TRAIL = ExplanationTrail(
    summary="Audit trail summary.",
    steps=[AuditStep(stage="Ingestion", claim="Weights available.", evidence="HF URL")],
    sources=["https://hf.co"],
)

_SOURCES = ["https://hf.co"]

_CPC_PATH = "app.agents.orchestrator.orchestrator_agent.cross_path_comparison_sub_agent.run"
_VS_PATH = "app.agents.orchestrator.orchestrator_agent.verdict_synthesis_sub_agent.run"
_ET_PATH = "app.agents.orchestrator.orchestrator_agent.explanation_trail_sub_agent.run"


# ---------------------------------------------------------------------------
# Unit tests — sub-agent run() functions mocked
# ---------------------------------------------------------------------------

def test_unit_run_returns_orchestrator_verdict():
    """run() returns an OrchestratorVerdict instance."""
    with patch(_CPC_PATH, return_value=_COMPARISON), \
         patch(_VS_PATH, return_value=_VERDICT), \
         patch(_ET_PATH, return_value=_TRAIL):
        result = run(_DIAGNOSIS_SET, _SOURCES)

    assert isinstance(result, OrchestratorVerdict)


def test_unit_run_copies_entity_and_capability():
    """run() carries entity and capability from DiagnosisSet into OrchestratorVerdict."""
    with patch(_CPC_PATH, return_value=_COMPARISON), \
         patch(_VS_PATH, return_value=_VERDICT), \
         patch(_ET_PATH, return_value=_TRAIL):
        result = run(_DIAGNOSIS_SET, _SOURCES)

    assert result.entity == "ACME Corp"
    assert result.capability == "edge inference LLM"


def test_unit_run_calls_cross_path_comparison_with_diagnoses():
    """run() passes diagnoses to cross-path comparison sub-agent."""
    with patch(_CPC_PATH, return_value=_COMPARISON) as mock_cpc, \
         patch(_VS_PATH, return_value=_VERDICT), \
         patch(_ET_PATH, return_value=_TRAIL):
        run(_DIAGNOSIS_SET, _SOURCES)

    mock_cpc.assert_called_once_with([_DIAGNOSIS])


def test_unit_run_passes_comparison_to_verdict_synthesis():
    """run() passes comparison, diagnoses, entity, and capability to verdict synthesis."""
    with patch(_CPC_PATH, return_value=_COMPARISON), \
         patch(_VS_PATH, return_value=_VERDICT) as mock_vs, \
         patch(_ET_PATH, return_value=_TRAIL):
        run(_DIAGNOSIS_SET, _SOURCES)

    mock_vs.assert_called_once_with(
        comparison=_COMPARISON,
        diagnoses=[_DIAGNOSIS],
        entity="ACME Corp",
        capability="edge inference LLM",
    )


def test_unit_run_passes_verdict_and_sources_to_explanation_trail():
    """run() passes diagnoses, verdict, and sources to explanation trail sub-agent."""
    with patch(_CPC_PATH, return_value=_COMPARISON), \
         patch(_VS_PATH, return_value=_VERDICT), \
         patch(_ET_PATH, return_value=_TRAIL) as mock_et:
        run(_DIAGNOSIS_SET, _SOURCES)

    mock_et.assert_called_once_with(
        diagnoses=[_DIAGNOSIS],
        verdict=_VERDICT,
        sources=_SOURCES,
    )


def test_unit_run_populates_orchestrator_verdict_fields():
    """run() maps sub-agent outputs into OrchestratorVerdict fields correctly."""
    with patch(_CPC_PATH, return_value=_COMPARISON), \
         patch(_VS_PATH, return_value=_VERDICT), \
         patch(_ET_PATH, return_value=_TRAIL):
        result = run(_DIAGNOSIS_SET, _SOURCES)

    assert result.recommended_path == "License open-weight model"
    assert result.verdict_summary == "License open-weight model is recommended."
    assert result.key_recommendations == ["Pin version"]
    assert result.path_stances == {"License open-weight model": "Recommended"}
    assert result.cross_path_comparison is _COMPARISON
    assert result.explanation_trail is _TRAIL


def test_unit_run_handles_empty_diagnoses():
    """run() returns empty OrchestratorVerdict without calling sub-agents if diagnosis_set is empty."""
    empty_set = DiagnosisSet(entity="ACME Corp", capability="LLM", diagnoses=[])

    with patch(_CPC_PATH) as mock_cpc, \
         patch(_VS_PATH) as mock_vs, \
         patch(_ET_PATH) as mock_et:
        result = run(empty_set, _SOURCES)

    assert isinstance(result, OrchestratorVerdict)
    assert result.recommended_path == ""
    mock_cpc.assert_not_called()
    mock_vs.assert_not_called()
    mock_et.assert_not_called()


# ---------------------------------------------------------------------------
# Integration tests — mocked at the LLM boundary
# Real sub-agent parsing logic executes end-to-end through the parent
# ---------------------------------------------------------------------------

_CPC_LLM = "app.agents.orchestrator.sub_agents.cross_path_comparison_sub_agent.complete"
_VS_LLM = "app.agents.orchestrator.sub_agents.verdict_synthesis_sub_agent.complete"
_ET_LLM = "app.agents.orchestrator.sub_agents.explanation_trail_sub_agent.complete"

_CPC_RESPONSE = """\
OVERALL ANALYSIS:
Analysis comparing build vs license.

---
PATH COMPARISON: Build custom LLM in-house
LOCK_IN_COUNT: 1
MAX_SEVERITY: 8.5
TRADEOFFS:
- High capex vs control
PATH_SUMMARY: Highest risk path.
---
"""

_VS_RESPONSE = """\
RECOMMENDED PATH: License open-weight model
VERDICT SUMMARY:
Licensing open-weight model is recommended.

RECOMMENDATIONS:
- Pin model version.

PATH STANCES:
- License open-weight model: Recommended
"""

_ET_RESPONSE = """\
TRAIL SUMMARY:
Audit summary narrative.

---
AUDIT STEP: Ingestion
CLAIM: Weights available.
EVIDENCE: Ingested source.
---
"""


def test_integration_run_returns_orchestrator_verdict():
    """Integration: full pipeline returns an OrchestratorVerdict."""
    with patch(_CPC_LLM, return_value=_CPC_RESPONSE), \
         patch(_VS_LLM, return_value=_VS_RESPONSE), \
         patch(_ET_LLM, return_value=_ET_RESPONSE):
        result = run(_DIAGNOSIS_SET, _SOURCES)

    assert isinstance(result, OrchestratorVerdict)
    assert result.entity == "ACME Corp"
    assert result.capability == "edge inference LLM"
    assert result.recommended_path == "License open-weight model"


def test_integration_verdict_contains_valid_sub_objects():
    """Integration: OrchestratorVerdict contains valid sub-objects."""
    with patch(_CPC_LLM, return_value=_CPC_RESPONSE), \
         patch(_VS_LLM, return_value=_VS_RESPONSE), \
         patch(_ET_LLM, return_value=_ET_RESPONSE):
        result = run(_DIAGNOSIS_SET, _SOURCES)

    assert isinstance(result.cross_path_comparison, CrossPathComparison)
    assert isinstance(result.explanation_trail, ExplanationTrail)
    assert len(result.explanation_trail.steps) == 1


def test_integration_pipeline_tolerates_all_llm_failures():
    """Integration: pipeline returns OrchestratorVerdict when all LLM calls fail."""
    with patch(_CPC_LLM, side_effect=RuntimeError("LLM down")), \
         patch(_VS_LLM, side_effect=RuntimeError("LLM down")), \
         patch(_ET_LLM, side_effect=RuntimeError("LLM down")):
        result = run(_DIAGNOSIS_SET, _SOURCES)

    assert isinstance(result, OrchestratorVerdict)
    assert result.recommended_path == ""
    assert result.cross_path_comparison == CrossPathComparison()
    assert result.explanation_trail == ExplanationTrail(sources=_SOURCES)
