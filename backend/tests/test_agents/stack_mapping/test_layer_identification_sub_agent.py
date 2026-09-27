"""
Unit tests for app.agents.stack_mapping.sub_agents.layer_identification_sub_agent.

All LLM calls are mocked — no network access, no API key required.

Tests cover:
  - run() returns a list of StackLayer objects
  - run() returns [] when the LLM call raises
  - run() returns [] when the LLM response is unparseable
  - run() passes a non-empty prompt to the LLM
  - _parse_response() correctly parses a well-formed multi-block response
  - _parse_response() skips blocks missing the LAYER field
  - _parse_response() handles an empty string gracefully
  - _parse_response() handles a single block (no --- separator)
  - _build_prompt() includes entity, capability, options, and context summary
  - StackLayer fields are populated correctly from a parsed response
"""

from unittest.mock import patch

import pytest

from app.agents.ingestion.sub_agents.context_synthesis_sub_agent import IngestionContext
from app.agents.stack_mapping.sub_agents.layer_identification_sub_agent import (
    StackLayer,
    _build_prompt,
    _parse_response,
    run,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_CONTEXT = IngestionContext(
    entity="ACME Corp",
    capability="edge inference LLM",
    options=["build in-house", "license from vendor"],
    context_summary="ACME Corp is evaluating open-weight LLMs for edge deployment.",
    key_facts=[
        "DeepSeek models available under open licence on Hugging Face.",
        "ACME Corp has no prior AI procurement on record.",
        "Cloud inference costs are declining.",
    ],
    sources=["https://a.com", "https://hf.co/deepseek"],
)

_WELL_FORMED_RESPONSE = """\
LAYER: Model Weights
RATIONALE: The decision to license or build determines whether the entity controls its own model weights.
EVIDENCE: DeepSeek models available under open licence on Hugging Face.
---
LAYER: Inference Infrastructure
RATIONALE: Edge deployment requires dedicated inference hardware or cloud endpoints.
EVIDENCE: ACME Corp is evaluating open-weight LLMs for edge deployment.
---
LAYER: Licensing Terms
RATIONALE: Open-weight licences impose restrictions on commercial redistribution.
EVIDENCE: DeepSeek models available under open licence on Hugging Face.
---
"""

_LLM_PATH = "app.agents.stack_mapping.sub_agents.layer_identification_sub_agent.call_llm_with_fallback"


# ---------------------------------------------------------------------------
# run() — return type and basic behaviour
# ---------------------------------------------------------------------------

def test_run_returns_list_of_stack_layers():
    """run() returns a list of StackLayer instances."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE):
        result = run(_CONTEXT)

    assert isinstance(result, list)
    assert all(isinstance(layer, StackLayer) for layer in result)


def test_run_returns_correct_count():
    """run() returns one StackLayer per well-formed block."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE):
        result = run(_CONTEXT)

    assert len(result) == 3


def test_run_calls_llm_once():
    """run() makes exactly one LLM call."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE) as mock_llm:
        run(_CONTEXT)

    assert mock_llm.call_count == 1


def test_run_passes_nonempty_prompt_to_llm():
    """run() passes a non-empty string to the LLM."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE) as mock_llm:
        run(_CONTEXT)

    prompt = mock_llm.call_args[0][0]
    assert isinstance(prompt, str)
    assert len(prompt) > 0


# ---------------------------------------------------------------------------
# run() — graceful degradation
# ---------------------------------------------------------------------------

def test_run_returns_empty_list_when_llm_raises():
    """run() returns [] when the LLM call raises an exception."""
    with patch(_LLM_PATH, side_effect=RuntimeError("DEEPSEEK_API_KEY not set")):
        result = run(_CONTEXT)

    assert result == []


def test_run_returns_empty_list_when_response_unparseable():
    """run() returns [] when the LLM response contains no valid blocks."""
    with patch(_LLM_PATH, return_value="This is just a plain paragraph with no structure."):
        result = run(_CONTEXT)

    assert result == []


# ---------------------------------------------------------------------------
# _parse_response()
# ---------------------------------------------------------------------------

def test_parse_response_parses_all_blocks():
    """_parse_response() returns one StackLayer per --- separated block."""
    layers = _parse_response(_WELL_FORMED_RESPONSE)
    assert len(layers) == 3


def test_parse_response_maps_fields_correctly():
    """_parse_response() correctly maps LAYER/RATIONALE/EVIDENCE to StackLayer fields."""
    layers = _parse_response(_WELL_FORMED_RESPONSE)
    first = layers[0]
    assert first.name == "Model Weights"
    assert "license or build" in first.rationale
    assert "Hugging Face" in first.evidence


def test_parse_response_skips_blocks_missing_layer_field():
    """_parse_response() skips any block that has no LAYER: line."""
    malformed = """\
RATIONALE: Some reason with no layer name.
EVIDENCE: Some evidence.
---
LAYER: Inference Infrastructure
RATIONALE: Valid block.
EVIDENCE: Valid evidence.
---
"""
    layers = _parse_response(malformed)
    assert len(layers) == 1
    assert layers[0].name == "Inference Infrastructure"


def test_parse_response_handles_empty_string():
    """_parse_response() returns [] for an empty response."""
    assert _parse_response("") == []


def test_parse_response_handles_single_block_no_separator():
    """_parse_response() correctly parses a single block with no --- separator."""
    single = """\
LAYER: Licensing Terms
RATIONALE: Licences restrict how weights can be used commercially.
EVIDENCE: Open-weight models on Hugging Face carry usage restrictions.
"""
    layers = _parse_response(single)
    assert len(layers) == 1
    assert layers[0].name == "Licensing Terms"


# ---------------------------------------------------------------------------
# _build_prompt()
# ---------------------------------------------------------------------------

def test_build_prompt_includes_entity():
    """_build_prompt() includes the entity name."""
    prompt = _build_prompt(_CONTEXT)
    assert "ACME Corp" in prompt


def test_build_prompt_includes_capability():
    """_build_prompt() includes the capability."""
    prompt = _build_prompt(_CONTEXT)
    assert "edge inference LLM" in prompt


def test_build_prompt_includes_options():
    """_build_prompt() includes all candidate options."""
    prompt = _build_prompt(_CONTEXT)
    assert "build in-house" in prompt
    assert "license from vendor" in prompt


def test_build_prompt_includes_context_summary():
    """_build_prompt() includes the context summary text."""
    prompt = _build_prompt(_CONTEXT)
    assert _CONTEXT.context_summary in prompt


def test_build_prompt_handles_empty_options():
    """_build_prompt() handles a context with no options without raising."""
    ctx = IngestionContext(
        entity="Corp", capability="LLM", options=[],
        context_summary="", key_facts=[], sources=[],
    )
    prompt = _build_prompt(ctx)
    assert isinstance(prompt, str)
    assert len(prompt) > 0
