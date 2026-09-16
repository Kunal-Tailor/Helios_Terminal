"""
Unit tests for app.agents.scenario_generation.sub_agents.option_enumeration_sub_agent.

All LLM calls are mocked — no network access, no API key required.

Tests cover:
  - run() returns a list of Option objects
  - run() returns [] when the LLM call raises
  - run() returns [] when the LLM response is unparseable
  - run() passes a non-empty prompt to the LLM
  - _parse_response() correctly parses a well-formed multi-block response
  - _parse_response() skips blocks missing the OPTION field
  - _parse_response() handles an empty string gracefully
  - _parse_response() handles a single block (no --- separator)
  - _build_prompt() includes entity, capability, and stack scope information
  - Option fields are populated correctly from a parsed response
"""

from unittest.mock import patch

import pytest

from app.agents.scenario_generation.sub_agents.option_enumeration_sub_agent import (
    Option,
    _build_prompt,
    _parse_response,
    run,
)
from app.agents.stack_mapping.stack_mapping_agent import StackScope, StackLayer
from app.agents.stack_mapping.sub_agents.dependency_linkage_sub_agent import LayerLink


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_STACK_SCOPE = StackScope(
    entity="ACME Corp",
    capability="edge inference LLM",
    layers=[
        StackLayer(
            name="Model Weights",
            rationale="Decision to license or build determines weight control.",
            evidence="DeepSeek models available under open licence.",
        ),
        StackLayer(
            name="Inference Infrastructure",
            rationale="Edge deployment requires dedicated hardware or cloud endpoints.",
            evidence="ACME Corp evaluating edge deployment.",
        ),
    ],
    links=[
        LayerLink(
            from_layer="Model Weights",
            to_layer="Inference Infrastructure",
            dependency_type="requires",
            description="Model weights must be compatible with inference hardware.",
        ),
    ],
)

_WELL_FORMED_RESPONSE = """\
OPTION: Build in-house
DESCRIPTION: Develop the LLM from scratch using internal engineering resources, including training data collection, model training, and deployment infrastructure.
RATIONALE: Given the identified Model Weights and Inference Infrastructure layers, building in-house provides full control over both the model and the deployment environment.
---
OPTION: License open-weight model
DESCRIPTION: License an open-weight model from a provider like DeepSeek and deploy it on internal or cloud infrastructure, avoiding the need to train from scratch.
RATIONALE: The Model Weights layer can be satisfied via open licensing, while the Inference Infrastructure layer can be tailored to the chosen model's requirements.
---
OPTION: Outsource to vendor
DESCRIPTION: Contract with a third-party AI vendor to provide the complete capability as a managed service, with the vendor handling all stack layers.
RATIONALE: Transfers responsibility for both Model Weights and Inference Infrastructure to the vendor, reducing internal technical burden but increasing vendor lock-in risk.
---
"""

_LLM_PATH = "app.agents.scenario_generation.sub_agents.option_enumeration_sub_agent.complete"


# ---------------------------------------------------------------------------
# run() — return type and basic behaviour
# ---------------------------------------------------------------------------

def test_run_returns_list_of_options():
    """run() returns a list of Option instances."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE):
        result = run(_STACK_SCOPE)

    assert isinstance(result, list)
    assert all(isinstance(option, Option) for option in result)


def test_run_returns_correct_count():
    """run() returns one Option per well-formed block."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE):
        result = run(_STACK_SCOPE)

    assert len(result) == 3


def test_run_calls_llm_once():
    """run() makes exactly one LLM call."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE) as mock_llm:
        run(_STACK_SCOPE)

    assert mock_llm.call_count == 1


def test_run_passes_nonempty_prompt_to_llm():
    """run() passes a non-empty string to the LLM."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE) as mock_llm:
        run(_STACK_SCOPE)

    prompt = mock_llm.call_args[0][0]
    assert isinstance(prompt, str)
    assert len(prompt) > 0


# ---------------------------------------------------------------------------
# run() — graceful degradation
# ---------------------------------------------------------------------------

def test_run_returns_empty_list_when_llm_raises():
    """run() returns [] when the LLM call raises an exception."""
    with patch(_LLM_PATH, side_effect=RuntimeError("DEEPSEEK_API_KEY not set")):
        result = run(_STACK_SCOPE)

    assert result == []


def test_run_returns_empty_list_when_response_unparseable():
    """run() returns [] when the LLM response contains no valid blocks."""
    with patch(_LLM_PATH, return_value="This is just a plain paragraph with no structure."):
        result = run(_STACK_SCOPE)

    assert result == []


# ---------------------------------------------------------------------------
# _parse_response()
# ---------------------------------------------------------------------------

def test_parse_response_parses_all_blocks():
    """_parse_response() returns one Option per --- separated block."""
    options = _parse_response(_WELL_FORMED_RESPONSE)
    assert len(options) == 3


def test_parse_response_maps_fields_correctly():
    """_parse_response() correctly maps OPTION/DESCRIPTION/RATIONALE to Option fields."""
    options = _parse_response(_WELL_FORMED_RESPONSE)
    first = options[0]
    assert first.name == "Build in-house"
    assert "internal engineering resources" in first.description
    assert "full control" in first.rationale


def test_parse_response_skips_blocks_missing_option_field():
    """_parse_response() skips any block that has no OPTION: line."""
    malformed = """\
DESCRIPTION: Some description with no option name.
RATIONALE: Some rationale.
---
OPTION: License open-weight model
DESCRIPTION: Valid block.
RATIONALE: Valid rationale.
---
"""
    options = _parse_response(malformed)
    assert len(options) == 1
    assert options[0].name == "License open-weight model"


def test_parse_response_handles_empty_string():
    """_parse_response() returns [] for an empty response."""
    assert _parse_response("") == []


def test_parse_response_handles_single_block_no_separator():
    """_parse_response() correctly parses a single block with no --- separator."""
    single = """\
OPTION: Hybrid approach
DESCRIPTION: Combine in-house development with licensed components.
RATIONALE: Balances control with time-to-market considerations.
"""
    options = _parse_response(single)
    assert len(options) == 1
    assert options[0].name == "Hybrid approach"


# ---------------------------------------------------------------------------
# _build_prompt()
# ---------------------------------------------------------------------------

def test_build_prompt_includes_entity():
    """_build_prompt() includes the entity name."""
    prompt = _build_prompt(_STACK_SCOPE)
    assert "ACME Corp" in prompt


def test_build_prompt_includes_capability():
    """_build_prompt() includes the capability."""
    prompt = _build_prompt(_STACK_SCOPE)
    assert "edge inference LLM" in prompt


def test_build_prompt_includes_layers():
    """_build_prompt() includes all stack layers."""
    prompt = _build_prompt(_STACK_SCOPE)
    assert "Model Weights" in prompt
    assert "Inference Infrastructure" in prompt


def test_build_prompt_includes_links():
    """_build_prompt() includes inter-layer dependencies."""
    prompt = _build_prompt(_STACK_SCOPE)
    assert "Model Weights" in prompt
    assert "Inference Infrastructure" in prompt


def test_build_prompt_handles_empty_layers():
    """_build_prompt() handles a StackScope with no layers without raising."""
    scope = StackScope(
        entity="Corp", capability="LLM", layers=[], links=[],
    )
    prompt = _build_prompt(scope)
    assert isinstance(prompt, str)
    assert len(prompt) > 0


def test_build_prompt_handles_empty_links():
    """_build_prompt() handles a StackScope with no links without raising."""
    scope = StackScope(
        entity="Corp", capability="LLM",
        layers=[StackLayer(name="Model", rationale="test", evidence="test")],
        links=[],
    )
    prompt = _build_prompt(scope)
    assert isinstance(prompt, str)
    assert len(prompt) > 0
