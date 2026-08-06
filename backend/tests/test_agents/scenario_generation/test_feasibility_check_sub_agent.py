"""
Unit tests for app.agents.scenario_generation.sub_agents.feasibility_check_sub_agent.

All LLM calls are mocked — no network access, no API key required.

Tests cover:
  - run() returns a list of Option objects
  - run() returns only feasible options from the input list
  - run() preserves original order of feasible options
  - run() returns original list when LLM call raises (graceful degradation)
  - run() returns original list when response is unparseable (graceful degradation)
  - run() returns [] when input options is empty
  - run() passes a non-empty prompt to the LLM
  - _parse_response() correctly parses a well-formed multi-block response
  - _parse_response() skips blocks with unknown option names
  - _parse_response() handles YES/NO case insensitivity
  - _parse_response() handles an empty string gracefully
  - _parse_response() handles a single block (no --- separator)
  - _build_prompt() includes entity, capability, and options
  - _build_prompt() includes stack scope information
  - FeasibilityResult fields are populated correctly from a parsed response
"""

from unittest.mock import patch

import pytest

from app.agents.scenario_generation.sub_agents.feasibility_check_sub_agent import (
    FeasibilityResult,
    _build_prompt,
    _parse_response,
    run,
)
from app.agents.scenario_generation.sub_agents.option_enumeration_sub_agent import Option
from app.agents.stack_mapping.stack_mapping_agent import StackScope, StackLayer
from app.agents.stack_mapping.sub_agents.dependency_linkage_sub_agent import LayerLink


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_OPTIONS = [
    Option(
        name="Build in-house",
        description="Develop the LLM from scratch using internal resources.",
        rationale="Full control over model and deployment environment.",
    ),
    Option(
        name="License open-weight model",
        description="License an open-weight model and deploy on internal infrastructure.",
        rationale="Satisfies Model Weights layer via open licensing.",
    ),
    Option(
        name="Outsource to vendor",
        description="Contract with a third-party AI vendor for managed service.",
        rationale="Transfers responsibility to vendor.",
    ),
]

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
FEASIBLE: NO
REASON: ACME Corp lacks the internal AI talent and compute resources for full model development.
---
OPTION: License open-weight model
FEASIBLE: YES
REASON: Open-weight models are readily available and compatible with ACME Corp's existing infrastructure.
---
OPTION: Outsource to vendor
FEASIBLE: YES
REASON: Multiple vendors offer managed AI services that meet ACME Corp's edge deployment requirements.
---
"""

_LLM_PATH = "app.agents.scenario_generation.sub_agents.feasibility_check_sub_agent.complete"


# ---------------------------------------------------------------------------
# run() — return type and basic behaviour
# ---------------------------------------------------------------------------

def test_run_returns_list_of_options():
    """run() returns a list of Option instances."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE):
        result = run(_OPTIONS, _STACK_SCOPE)

    assert isinstance(result, list)
    assert all(isinstance(opt, Option) for opt in result)


def test_run_returns_only_feasible_options():
    """run() returns only options marked as feasible (YES)."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE):
        result = run(_OPTIONS, _STACK_SCOPE)

    assert len(result) == 2
    assert all(opt.name in ["License open-weight model", "Outsource to vendor"] for opt in result)


def test_run_preserves_original_order():
    """run() preserves the original order of feasible options."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE):
        result = run(_OPTIONS, _STACK_SCOPE)

    assert result[0].name == "License open-weight model"
    assert result[1].name == "Outsource to vendor"


def test_run_calls_llm_once():
    """run() makes exactly one LLM call."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE) as mock_llm:
        run(_OPTIONS, _STACK_SCOPE)

    assert mock_llm.call_count == 1


def test_run_passes_nonempty_prompt_to_llm():
    """run() passes a non-empty string to the LLM."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE) as mock_llm:
        run(_OPTIONS, _STACK_SCOPE)

    prompt = mock_llm.call_args[0][0]
    assert isinstance(prompt, str)
    assert len(prompt) > 0


# ---------------------------------------------------------------------------
# run() — graceful degradation
# ---------------------------------------------------------------------------

def test_run_returns_original_list_when_llm_raises():
    """run() returns the original options list when the LLM call raises an exception."""
    with patch(_LLM_PATH, side_effect=RuntimeError("DEEPSEEK_API_KEY not set")):
        result = run(_OPTIONS, _STACK_SCOPE)

    assert result == _OPTIONS


def test_run_returns_original_list_when_response_unparseable():
    """run() returns the original options list when the LLM response contains no valid blocks."""
    with patch(_LLM_PATH, return_value="This is just a plain paragraph with no structure."):
        result = run(_OPTIONS, _STACK_SCOPE)

    assert result == _OPTIONS


def test_run_returns_empty_list_when_input_options_empty():
    """run() returns [] when the input options list is empty."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE):
        result = run([], _STACK_SCOPE)

    assert result == []


# ---------------------------------------------------------------------------
# _parse_response()
# ---------------------------------------------------------------------------

def test_parse_response_parses_all_blocks():
    """_parse_response() returns one FeasibilityResult per --- separated block."""
    results = _parse_response(_WELL_FORMED_RESPONSE, _OPTIONS)
    assert len(results) == 3


def test_parse_response_maps_fields_correctly():
    """_parse_response() correctly maps OPTION/FEASIBLE/REASON to FeasibilityResult fields."""
    results = _parse_response(_WELL_FORMED_RESPONSE, _OPTIONS)
    first = results[0]
    assert first.option.name == "Build in-house"
    assert first.is_feasible is False
    assert "internal AI talent" in first.reason


def test_parse_response_handles_yes_case_insensitive():
    """_parse_response() treats 'yes', 'YES', 'Yes' as feasible."""
    response_lower = """\
OPTION: Build in-house
FEASIBLE: yes
REASON: Test reason.
---
"""
    results = _parse_response(response_lower, _OPTIONS)
    assert len(results) == 1
    assert results[0].is_feasible is True


def test_parse_response_handles_no_case_insensitive():
    """_parse_response() treats 'no', 'NO', 'No' as not feasible."""
    response_lower = """\
OPTION: Build in-house
FEASIBLE: no
REASON: Test reason.
---
"""
    results = _parse_response(response_lower, _OPTIONS)
    assert len(results) == 1
    assert results[0].is_feasible is False


def test_parse_response_skips_unknown_option_names():
    """_parse_response() skips blocks that reference option names not in the input list."""
    response_with_unknown = """\
OPTION: Unknown Option
FEASIBLE: YES
REASON: This option is not in the input list.
---
OPTION: Build in-house
FEASIBLE: NO
REASON: Valid option.
---
"""
    results = _parse_response(response_with_unknown, _OPTIONS)
    assert len(results) == 1
    assert results[0].option.name == "Build in-house"


def test_parse_response_handles_empty_string():
    """_parse_response() returns [] for an empty response."""
    assert _parse_response("", _OPTIONS) == []


def test_parse_response_handles_single_block_no_separator():
    """_parse_response() correctly parses a single block with no --- separator."""
    single = """\
OPTION: License open-weight model
FEASIBLE: YES
REASON: Open-weight models are readily available.
"""
    results = _parse_response(single, _OPTIONS)
    assert len(results) == 1
    assert results[0].option.name == "License open-weight model"
    assert results[0].is_feasible is True


# ---------------------------------------------------------------------------
# _build_prompt()
# ---------------------------------------------------------------------------

def test_build_prompt_includes_entity():
    """_build_prompt() includes the entity name."""
    prompt = _build_prompt(_OPTIONS, _STACK_SCOPE)
    assert "ACME Corp" in prompt


def test_build_prompt_includes_capability():
    """_build_prompt() includes the capability."""
    prompt = _build_prompt(_OPTIONS, _STACK_SCOPE)
    assert "edge inference LLM" in prompt


def test_build_prompt_includes_all_options():
    """_build_prompt() includes all candidate options."""
    prompt = _build_prompt(_OPTIONS, _STACK_SCOPE)
    assert "Build in-house" in prompt
    assert "License open-weight model" in prompt
    assert "Outsource to vendor" in prompt


def test_build_prompt_includes_layers():
    """_build_prompt() includes all stack layers."""
    prompt = _build_prompt(_OPTIONS, _STACK_SCOPE)
    assert "Model Weights" in prompt
    assert "Inference Infrastructure" in prompt


def test_build_prompt_handles_empty_options():
    """_build_prompt() handles an empty options list without raising."""
    prompt = _build_prompt([], _STACK_SCOPE)
    assert isinstance(prompt, str)
    assert len(prompt) > 0


def test_build_prompt_handles_empty_layers():
    """_build_prompt() handles a StackScope with no layers without raising."""
    scope = StackScope(
        entity="Corp", capability="LLM", layers=[], links=[],
    )
    prompt = _build_prompt(_OPTIONS, scope)
    assert isinstance(prompt, str)
    assert len(prompt) > 0
