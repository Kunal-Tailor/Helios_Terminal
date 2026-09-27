"""
Unit tests for app.agents.scenario_generation.sub_agents.scenario_refinement_sub_agent.

All LLM calls are mocked — no network access, no API key required.

Tests cover:
  - run() returns a list of Scenario objects
  - run() returns [] for empty input options (no LLM call)
  - run() returns [] when the LLM call raises (graceful degradation)
  - run() returns [] when the response is unparseable
  - run() calls the LLM exactly once
  - _parse_response() parses a well-formed multi-block response
  - _parse_response() maps SCENARIO/DESCRIPTION/STEPS/RISKS/LAYERS fields correctly
  - _parse_response() populates implementation_steps as a list
  - _parse_response() populates key_risks as a list
  - _parse_response() populates layers_addressed as a list from comma-separated text
  - _parse_response() skips blocks missing the SCENARIO field
  - _parse_response() returns [] for empty string
  - _build_prompt() includes entity, capability, and all option names
  - Scenario.option_name matches the originating Option name
"""

from unittest.mock import patch

import pytest

from app.agents.scenario_generation.sub_agents.option_enumeration_sub_agent import Option
from app.agents.scenario_generation.sub_agents.scenario_refinement_sub_agent import (
    Scenario,
    _build_prompt,
    _parse_response,
    run,
)
from app.agents.stack_mapping.stack_mapping_agent import StackScope
from app.agents.stack_mapping.sub_agents.dependency_linkage_sub_agent import LayerLink
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
    links=[
        LayerLink("Model Weights", "Inference Infrastructure", "depends on",
                  "Weights format must suit inference hardware."),
    ],
)

_OPTIONS = [
    Option(
        name="Build in-house",
        description="Train and deploy a custom model internally.",
        rationale="Gives full control over weights and infrastructure.",
    ),
    Option(
        name="License open-weight model",
        description="Adopt an existing open-weight model like DeepSeek.",
        rationale="Faster time-to-deployment with lower upfront cost.",
    ),
]

_WELL_FORMED_RESPONSE = """\
SCENARIO: Build in-house
DESCRIPTION: ACME Corp builds and trains a custom edge LLM from scratch using
internal compute resources, retaining full control over model weights.
STEPS:
- Assemble an ML engineering team with LLM expertise.
- Acquire or lease GPU compute infrastructure for training.
- Collect and curate domain-specific training data.
- Train, evaluate, and iterate on the model.
- Deploy to edge inference hardware.
RISKS:
- High upfront cost and long time-to-production.
- Talent scarcity for specialised LLM engineering roles.
LAYERS: Model Weights, Inference Infrastructure
---
SCENARIO: License open-weight model
DESCRIPTION: ACME Corp adopts an existing open-weight LLM (e.g. DeepSeek)
under its open licence, fine-tuning it for edge deployment.
STEPS:
- Evaluate available open-weight models for capability fit.
- Review and comply with licence terms for internal deployment.
- Fine-tune the model on domain-specific data.
- Deploy to edge inference hardware.
RISKS:
- Licence terms may restrict certain use cases.
- Dependency on upstream model maintainer's update cadence.
LAYERS: Model Weights, Inference Infrastructure
---
"""

_LLM_PATH = "app.agents.scenario_generation.sub_agents.scenario_refinement_sub_agent.call_llm_with_fallback"


# ---------------------------------------------------------------------------
# run() — return type and basic behaviour
# ---------------------------------------------------------------------------

def test_run_returns_list_of_scenarios():
    """run() returns a list of Scenario instances."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE):
        result = run(_OPTIONS, _STACK_SCOPE)

    assert isinstance(result, list)
    assert all(isinstance(s, Scenario) for s in result)


def test_run_returns_one_scenario_per_option():
    """run() returns one Scenario per well-formed block in the LLM response."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE):
        result = run(_OPTIONS, _STACK_SCOPE)

    assert len(result) == 2


def test_run_calls_llm_once():
    """run() makes exactly one LLM call."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE) as mock_llm:
        run(_OPTIONS, _STACK_SCOPE)

    assert mock_llm.call_count == 1


def test_run_scenario_option_name_matches_source():
    """Scenario.option_name matches the name of the originating Option."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE):
        result = run(_OPTIONS, _STACK_SCOPE)

    assert result[0].option_name == "Build in-house"
    assert result[1].option_name == "License open-weight model"


# ---------------------------------------------------------------------------
# run() — graceful degradation
# ---------------------------------------------------------------------------

def test_run_returns_empty_for_empty_options():
    """run() returns [] immediately when no options are provided."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE) as mock_llm:
        result = run([], _STACK_SCOPE)

    assert result == []
    mock_llm.assert_not_called()


def test_run_returns_empty_when_llm_raises():
    """run() returns [] when the LLM call raises an exception."""
    with patch(_LLM_PATH, side_effect=RuntimeError("DEEPSEEK_API_KEY not set")):
        result = run(_OPTIONS, _STACK_SCOPE)

    assert result == []


def test_run_returns_empty_when_response_unparseable():
    """run() returns [] when the LLM response has no valid scenario blocks."""
    with patch(_LLM_PATH, return_value="I cannot refine these options at this time."):
        result = run(_OPTIONS, _STACK_SCOPE)

    assert result == []


# ---------------------------------------------------------------------------
# _parse_response() — field mapping
# ---------------------------------------------------------------------------

def test_parse_response_maps_description():
    """_parse_response() sets Scenario.description from DESCRIPTION field."""
    scenarios = _parse_response(_WELL_FORMED_RESPONSE, _OPTIONS)
    assert "ACME Corp" in scenarios[0].description
    assert len(scenarios[0].description) > 0


def test_parse_response_maps_implementation_steps_as_list():
    """_parse_response() returns Scenario.implementation_steps as a list."""
    scenarios = _parse_response(_WELL_FORMED_RESPONSE, _OPTIONS)
    assert isinstance(scenarios[0].implementation_steps, list)
    assert len(scenarios[0].implementation_steps) >= 3


def test_parse_response_maps_key_risks_as_list():
    """_parse_response() returns Scenario.key_risks as a list."""
    scenarios = _parse_response(_WELL_FORMED_RESPONSE, _OPTIONS)
    assert isinstance(scenarios[0].key_risks, list)
    assert len(scenarios[0].key_risks) >= 2


def test_parse_response_maps_layers_addressed_from_csv():
    """_parse_response() splits LAYERS comma-separated text into a list."""
    scenarios = _parse_response(_WELL_FORMED_RESPONSE, _OPTIONS)
    layers = scenarios[0].layers_addressed
    assert isinstance(layers, list)
    assert "Model Weights" in layers
    assert "Inference Infrastructure" in layers


def test_parse_response_skips_blocks_missing_scenario_field():
    """_parse_response() skips any block without a SCENARIO: line."""
    malformed = """\
DESCRIPTION: A description with no scenario name.
STEPS:
- Step 1
RISKS:
- Risk 1
LAYERS: Model Weights
---
SCENARIO: License open-weight model
DESCRIPTION: Valid block.
STEPS:
- Step A
- Step B
- Step C
RISKS:
- Risk X
- Risk Y
LAYERS: Model Weights
---
"""
    scenarios = _parse_response(malformed, _OPTIONS)
    assert len(scenarios) == 1
    assert scenarios[0].name == "License open-weight model"


def test_parse_response_returns_empty_for_empty_string():
    """_parse_response() returns [] for an empty response."""
    assert _parse_response("", _OPTIONS) == []


# ---------------------------------------------------------------------------
# _build_prompt()
# ---------------------------------------------------------------------------

def test_build_prompt_includes_entity_and_capability():
    """_build_prompt() includes the entity and capability."""
    prompt = _build_prompt(_OPTIONS, _STACK_SCOPE)
    assert "ACME Corp" in prompt
    assert "edge inference LLM" in prompt


def test_build_prompt_includes_all_option_names():
    """_build_prompt() includes every option name."""
    prompt = _build_prompt(_OPTIONS, _STACK_SCOPE)
    for opt in _OPTIONS:
        assert opt.name in prompt


def test_build_prompt_includes_stack_layer_names():
    """_build_prompt() includes the stack layer names from the StackScope."""
    prompt = _build_prompt(_OPTIONS, _STACK_SCOPE)
    for layer in _STACK_SCOPE.layers:
        assert layer.name in prompt
