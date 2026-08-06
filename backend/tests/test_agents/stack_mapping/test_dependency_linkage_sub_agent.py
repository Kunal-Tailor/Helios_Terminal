"""
Unit tests for app.agents.stack_mapping.sub_agents.dependency_linkage_sub_agent.

All LLM calls are mocked — no network access, no API key required.

Tests cover:
  - run() returns a list of LayerLink objects
  - run() returns [] for fewer than two input layers (no links possible)
  - run() does NOT call the LLM when fewer than two layers provided
  - run() returns [] when the LLM responds with NO DEPENDENCIES
  - run() returns [] when the LLM call raises (graceful degradation)
  - run() returns [] when the response is unparseable
  - _parse_response() parses a well-formed multi-block response correctly
  - _parse_response() maps FROM/TO/TYPE/DESCRIPTION to LayerLink fields
  - _parse_response() skips blocks missing FROM or TO
  - _parse_response() returns [] for an empty string
  - _parse_response() handles "NO DEPENDENCIES" response (case-insensitive)
  - _build_prompt() includes entity, capability, and all layer names
  - LayerLink fields are populated correctly
"""

from unittest.mock import patch

import pytest

from app.agents.ingestion.sub_agents.context_synthesis_sub_agent import IngestionContext
from app.agents.stack_mapping.sub_agents.dependency_linkage_sub_agent import (
    LayerLink,
    _build_prompt,
    _parse_response,
    run,
)
from app.agents.stack_mapping.sub_agents.layer_identification_sub_agent import StackLayer

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_CONTEXT = IngestionContext(
    entity="ACME Corp",
    capability="edge inference LLM",
    options=["build in-house", "license from vendor"],
    context_summary="ACME Corp is evaluating open-weight LLMs for edge deployment.",
    key_facts=["DeepSeek models available under open licence."],
    sources=["https://hf.co"],
)

_LAYERS = [
    StackLayer(
        name="Model Weights",
        rationale="Determines if entity controls its own weights.",
        evidence="Open-weight models on Hugging Face.",
    ),
    StackLayer(
        name="Licensing Terms",
        rationale="Open-weight licences restrict redistribution.",
        evidence="DeepSeek available under open licence.",
    ),
    StackLayer(
        name="Inference Infrastructure",
        rationale="Edge deployment requires dedicated hardware.",
        evidence="Evaluating edge deployment options.",
    ),
]

_SINGLE_LAYER = [_LAYERS[0]]

_WELL_FORMED_RESPONSE = """\
FROM: Model Weights
TO: Licensing Terms
TYPE: constrained by
DESCRIPTION: Using open-weight models requires compliance with their licence terms.
---
FROM: Inference Infrastructure
TO: Model Weights
TYPE: depends on
DESCRIPTION: The edge inference infrastructure must be compatible with the chosen model weights format.
---
"""

_LLM_PATH = "app.agents.stack_mapping.sub_agents.dependency_linkage_sub_agent.complete"


# ---------------------------------------------------------------------------
# run() — return type and basic behaviour
# ---------------------------------------------------------------------------

def test_run_returns_list_of_layer_links():
    """run() returns a list of LayerLink instances."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE):
        result = run(_LAYERS, _CONTEXT)

    assert isinstance(result, list)
    assert all(isinstance(link, LayerLink) for link in result)


def test_run_returns_correct_count():
    """run() returns one LayerLink per well-formed block."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE):
        result = run(_LAYERS, _CONTEXT)

    assert len(result) == 2


def test_run_calls_llm_once():
    """run() makes exactly one LLM call."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE) as mock_llm:
        run(_LAYERS, _CONTEXT)

    assert mock_llm.call_count == 1


# ---------------------------------------------------------------------------
# run() — short-circuit for fewer than two layers
# ---------------------------------------------------------------------------

def test_run_returns_empty_for_single_layer():
    """run() returns [] immediately when only one layer is provided."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE) as mock_llm:
        result = run(_SINGLE_LAYER, _CONTEXT)

    assert result == []
    mock_llm.assert_not_called()


def test_run_returns_empty_for_zero_layers():
    """run() returns [] immediately when no layers are provided."""
    with patch(_LLM_PATH, return_value=_WELL_FORMED_RESPONSE) as mock_llm:
        result = run([], _CONTEXT)

    assert result == []
    mock_llm.assert_not_called()


# ---------------------------------------------------------------------------
# run() — graceful degradation
# ---------------------------------------------------------------------------

def test_run_returns_empty_when_llm_raises():
    """run() returns [] when the LLM call raises an exception."""
    with patch(_LLM_PATH, side_effect=RuntimeError("DEEPSEEK_API_KEY not set")):
        result = run(_LAYERS, _CONTEXT)

    assert result == []


def test_run_returns_empty_when_response_unparseable():
    """run() returns [] when the LLM returns an unparseable response."""
    with patch(_LLM_PATH, return_value="I cannot identify any dependencies here."):
        result = run(_LAYERS, _CONTEXT)

    assert result == []


def test_run_returns_empty_for_no_dependencies_response():
    """run() returns [] when the LLM explicitly signals NO DEPENDENCIES."""
    with patch(_LLM_PATH, return_value="NO DEPENDENCIES"):
        result = run(_LAYERS, _CONTEXT)

    assert result == []


# ---------------------------------------------------------------------------
# _parse_response()
# ---------------------------------------------------------------------------

def test_parse_response_parses_all_blocks():
    """_parse_response() returns one LayerLink per --- separated block."""
    links = _parse_response(_WELL_FORMED_RESPONSE)
    assert len(links) == 2


def test_parse_response_maps_fields_correctly():
    """_parse_response() maps FROM/TO/TYPE/DESCRIPTION to LayerLink fields."""
    links = _parse_response(_WELL_FORMED_RESPONSE)
    first = links[0]
    assert first.from_layer == "Model Weights"
    assert first.to_layer == "Licensing Terms"
    assert first.dependency_type == "constrained by"
    assert "licence" in first.description


def test_parse_response_skips_blocks_missing_from_or_to():
    """_parse_response() skips blocks that lack a FROM or TO field."""
    partial = """\
TO: Licensing Terms
TYPE: constrained by
DESCRIPTION: Missing FROM field — should be skipped.
---
FROM: Model Weights
TO: Licensing Terms
TYPE: constrained by
DESCRIPTION: Valid block.
---
"""
    links = _parse_response(partial)
    assert len(links) == 1
    assert links[0].from_layer == "Model Weights"


def test_parse_response_returns_empty_for_empty_string():
    """_parse_response() returns [] for an empty response."""
    assert _parse_response("") == []


def test_parse_response_handles_no_dependencies_uppercase():
    """_parse_response() returns [] for 'NO DEPENDENCIES' response."""
    assert _parse_response("NO DEPENDENCIES") == []


def test_parse_response_handles_no_dependencies_mixed_case():
    """_parse_response() returns [] for 'No Dependencies' (case-insensitive)."""
    assert _parse_response("No Dependencies found between these layers.") == []


def test_parse_response_handles_single_block_no_separator():
    """_parse_response() parses a single block with no --- separator."""
    single = """\
FROM: Model Weights
TO: Licensing Terms
TYPE: constrained by
DESCRIPTION: Open-weight models are subject to licence terms.
"""
    links = _parse_response(single)
    assert len(links) == 1
    assert links[0].from_layer == "Model Weights"


# ---------------------------------------------------------------------------
# _build_prompt()
# ---------------------------------------------------------------------------

def test_build_prompt_includes_entity_and_capability():
    """_build_prompt() contains the entity and capability."""
    prompt = _build_prompt(_LAYERS, _CONTEXT)
    assert "ACME Corp" in prompt
    assert "edge inference LLM" in prompt


def test_build_prompt_includes_all_layer_names():
    """_build_prompt() lists every surviving layer name."""
    prompt = _build_prompt(_LAYERS, _CONTEXT)
    for layer in _LAYERS:
        assert layer.name in prompt


def test_build_prompt_is_non_empty():
    """_build_prompt() returns a non-empty string."""
    prompt = _build_prompt(_LAYERS, _CONTEXT)
    assert len(prompt) > 0
