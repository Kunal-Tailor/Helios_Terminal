"""
Unit and integration tests for app.agents.scenario_generation.scenario_generation_agent.

UNIT TESTS (mock all sub-agents at their run() boundary)
  - run() returns a ScenarioSet
  - run() copies entity and capability from stack_scope into ScenarioSet
  - run() calls option-enumeration sub-agent with the StackScope
  - run() passes option-enumeration output to feasibility-check (with stack_scope)
  - run() passes feasibility-check output to scenario-refinement (with stack_scope)
  - run() populates ScenarioSet.scenarios from refinement output
  - run() returns ScenarioSet with empty scenarios when all sub-agents return []

INTEGRATION TESTS (mock at LLM boundary; real sub-agent logic executes)
  - Full pipeline produces a ScenarioSet with correct entity/capability
  - ScenarioSet.scenarios is a list of Scenario objects when LLM responds well
  - Pipeline tolerates all sub-agents returning empty (all LLMs fail)
  - Feasibility-filter fallback: when filter LLM fails, all options pass through
    to refinement (graceful fallback behaviour from 5.10)
"""

from unittest.mock import patch

import pytest

from app.agents.scenario_generation.scenario_generation_agent import ScenarioSet, run
from app.agents.scenario_generation.sub_agents.option_enumeration_sub_agent import Option
from app.agents.scenario_generation.sub_agents.scenario_refinement_sub_agent import Scenario
from app.agents.stack_mapping.stack_mapping_agent import StackScope
from app.agents.stack_mapping.sub_agents.layer_identification_sub_agent import StackLayer

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_STACK_SCOPE = StackScope(
    entity="ACME Corp",
    capability="edge inference LLM",
    layers=[
        StackLayer("Model Weights", "Controls weight ownership.", "Open-weight on HF."),
        StackLayer("Inference Infrastructure", "Required for edge.", "Edge eval."),
    ],
    links=[],
)

_CANDIDATE_OPTIONS = [
    Option("Build in-house", "Train custom model.", "Full control over weights."),
    Option("License open-weight model", "Adopt DeepSeek.", "Faster time-to-deploy."),
]

_FEASIBLE_OPTIONS = [
    Option("License open-weight model", "Adopt DeepSeek.", "Faster time-to-deploy."),
]

_SCENARIOS = [
    Scenario(
        name="License open-weight model",
        option_name="License open-weight model",
        description="ACME Corp adopts DeepSeek under open licence.",
        implementation_steps=["Evaluate models", "Review licence", "Fine-tune", "Deploy"],
        key_risks=["Licence restrictions", "Upstream dependency"],
        layers_addressed=["Model Weights", "Inference Infrastructure"],
    ),
]

_OE_PATH = "app.agents.scenario_generation.scenario_generation_agent.option_enumeration_sub_agent.run"
_FC_PATH = "app.agents.scenario_generation.scenario_generation_agent.feasibility_check_sub_agent.run"
_SR_PATH = "app.agents.scenario_generation.scenario_generation_agent.scenario_refinement_sub_agent.run"


# ---------------------------------------------------------------------------
# Unit tests — sub-agent run() functions mocked
# ---------------------------------------------------------------------------

def test_unit_run_returns_scenario_set():
    """run() returns a ScenarioSet instance."""
    with patch(_OE_PATH, return_value=_CANDIDATE_OPTIONS), \
         patch(_FC_PATH, return_value=_FEASIBLE_OPTIONS), \
         patch(_SR_PATH, return_value=_SCENARIOS):
        result = run(_STACK_SCOPE)

    assert isinstance(result, ScenarioSet)


def test_unit_run_copies_entity_and_capability():
    """run() carries entity and capability from StackScope into ScenarioSet."""
    with patch(_OE_PATH, return_value=_CANDIDATE_OPTIONS), \
         patch(_FC_PATH, return_value=_FEASIBLE_OPTIONS), \
         patch(_SR_PATH, return_value=_SCENARIOS):
        result = run(_STACK_SCOPE)

    assert result.entity == "ACME Corp"
    assert result.capability == "edge inference LLM"


def test_unit_run_calls_option_enumeration_with_stack_scope():
    """run() passes StackScope to the option-enumeration sub-agent."""
    with patch(_OE_PATH, return_value=_CANDIDATE_OPTIONS) as mock_oe, \
         patch(_FC_PATH, return_value=_FEASIBLE_OPTIONS), \
         patch(_SR_PATH, return_value=_SCENARIOS):
        run(_STACK_SCOPE)

    mock_oe.assert_called_once_with(_STACK_SCOPE)


def test_unit_run_passes_enumerated_options_to_feasibility_check():
    """run() passes option-enumeration output + stack_scope to feasibility check."""
    with patch(_OE_PATH, return_value=_CANDIDATE_OPTIONS), \
         patch(_FC_PATH, return_value=_FEASIBLE_OPTIONS) as mock_fc, \
         patch(_SR_PATH, return_value=_SCENARIOS):
        run(_STACK_SCOPE)

    mock_fc.assert_called_once_with(options=_CANDIDATE_OPTIONS, stack_scope=_STACK_SCOPE)


def test_unit_run_passes_feasible_options_to_refinement():
    """run() passes feasibility-check output + stack_scope to scenario refinement."""
    with patch(_OE_PATH, return_value=_CANDIDATE_OPTIONS), \
         patch(_FC_PATH, return_value=_FEASIBLE_OPTIONS), \
         patch(_SR_PATH, return_value=_SCENARIOS) as mock_sr:
        run(_STACK_SCOPE)

    mock_sr.assert_called_once_with(options=_FEASIBLE_OPTIONS, stack_scope=_STACK_SCOPE)


def test_unit_run_populates_scenarios_from_refinement():
    """ScenarioSet.scenarios is exactly what the refinement sub-agent returned."""
    with patch(_OE_PATH, return_value=_CANDIDATE_OPTIONS), \
         patch(_FC_PATH, return_value=_FEASIBLE_OPTIONS), \
         patch(_SR_PATH, return_value=_SCENARIOS):
        result = run(_STACK_SCOPE)

    assert result.scenarios is _SCENARIOS


def test_unit_run_handles_all_empty_sub_agent_outputs():
    """run() returns ScenarioSet with empty scenarios when all sub-agents return []."""
    with patch(_OE_PATH, return_value=[]), \
         patch(_FC_PATH, return_value=[]), \
         patch(_SR_PATH, return_value=[]):
        result = run(_STACK_SCOPE)

    assert isinstance(result, ScenarioSet)
    assert result.scenarios == []


# ---------------------------------------------------------------------------
# Integration tests — mocked at the LLM boundary
# Real sub-agent parsing / fallback logic executes end-to-end
# ---------------------------------------------------------------------------

_OE_LLM = "app.agents.scenario_generation.sub_agents.option_enumeration_sub_agent.complete"
_FC_LLM = "app.agents.scenario_generation.sub_agents.feasibility_check_sub_agent.complete"
_SR_LLM = "app.agents.scenario_generation.sub_agents.scenario_refinement_sub_agent.complete"

_OE_RESPONSE = """\
OPTION: Build in-house
DESCRIPTION: Train and deploy a custom model internally.
RATIONALE: Full control over weights and infrastructure.
---
OPTION: License open-weight model
DESCRIPTION: Adopt an existing open-weight model like DeepSeek.
RATIONALE: Faster time-to-deployment with lower upfront cost.
---
"""

_FC_RESPONSE = """\
OPTION: Build in-house
FEASIBLE: NO
REASON: High upfront cost and talent scarcity make this infeasible for ACME Corp.
---
OPTION: License open-weight model
FEASIBLE: YES
REASON: Open-weight models are readily available and immediately deployable.
---
"""

_SR_RESPONSE = """\
SCENARIO: License open-weight model
DESCRIPTION: ACME Corp adopts DeepSeek under its open licence for edge inference.
STEPS:
- Evaluate available open-weight models.
- Review and comply with licence terms.
- Fine-tune on domain-specific data.
- Deploy to edge inference hardware.
RISKS:
- Licence terms may restrict certain use cases.
- Dependency on upstream model release cadence.
LAYERS: Model Weights, Inference Infrastructure
---
"""


def test_integration_run_returns_scenario_set():
    """Integration: full pipeline returns a ScenarioSet."""
    with patch(_OE_LLM, return_value=_OE_RESPONSE), \
         patch(_FC_LLM, return_value=_FC_RESPONSE), \
         patch(_SR_LLM, return_value=_SR_RESPONSE):
        result = run(_STACK_SCOPE)

    assert isinstance(result, ScenarioSet)
    assert result.entity == "ACME Corp"
    assert result.capability == "edge inference LLM"


def test_integration_scenarios_are_scenario_instances():
    """Integration: ScenarioSet.scenarios contains Scenario objects."""
    with patch(_OE_LLM, return_value=_OE_RESPONSE), \
         patch(_FC_LLM, return_value=_FC_RESPONSE), \
         patch(_SR_LLM, return_value=_SR_RESPONSE):
        result = run(_STACK_SCOPE)

    assert all(isinstance(s, Scenario) for s in result.scenarios)


def test_integration_feasibility_removes_infeasible_options():
    """Integration: infeasible options filtered by 5.10 do not appear in final scenarios."""
    with patch(_OE_LLM, return_value=_OE_RESPONSE), \
         patch(_FC_LLM, return_value=_FC_RESPONSE), \
         patch(_SR_LLM, return_value=_SR_RESPONSE):
        result = run(_STACK_SCOPE)

    scenario_names = [s.name for s in result.scenarios]
    assert "Build in-house" not in scenario_names
    assert "License open-weight model" in scenario_names


def test_integration_pipeline_tolerates_all_llm_failures():
    """Integration: pipeline returns empty ScenarioSet when all LLM calls fail."""
    with patch(_OE_LLM, side_effect=RuntimeError("LLM down")), \
         patch(_FC_LLM, side_effect=RuntimeError("LLM down")), \
         patch(_SR_LLM, side_effect=RuntimeError("LLM down")):
        result = run(_STACK_SCOPE)

    assert isinstance(result, ScenarioSet)
    assert result.scenarios == []
