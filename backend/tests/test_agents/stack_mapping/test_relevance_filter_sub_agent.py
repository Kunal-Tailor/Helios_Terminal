"""
Unit tests for app.agents.stack_mapping.sub_agents.relevance_filter_sub_agent.

All LLM calls are mocked — no network access, no API key required.

Tests cover:
  - run() returns a list of StackLayer objects
  - run() returns only layers marked KEEP by the LLM
  - run() preserves original StackLayer objects (not recreated from LLM text)
  - run() returns [] when input layers is empty
  - run() returns all layers when LLM raises (safe fallback)
  - run() returns all layers when response is unparseable (safe fallback)
  - _parse_keep_names() extracts KEEP layer names correctly
  - _parse_keep_names() ignores DISCARD layers
  - _parse_keep_names() is case-insensitive for the DECISION field
  - _parse_keep_names() returns empty set for empty response
  - _filter_layers() matches layer names case-insensitively
  - _filter_layers() falls back to all layers when keep_names is empty
  - _build_prompt() includes entity, capability, and all layer names
"""

from unittest.mock import patch

import pytest

from app.agents.ingestion.sub_agents.context_synthesis_sub_agent import IngestionContext
from app.agents.stack_mapping.sub_agents.layer_identification_sub_agent import StackLayer
from app.agents.stack_mapping.sub_agents.relevance_filter_sub_agent import (
    _build_prompt,
    _filter_layers,
    _parse_keep_names,
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
        name="Inference Infrastructure",
        rationale="Edge deployment requires dedicated hardware or endpoints.",
        evidence="Evaluating edge deployment options.",
    ),
    StackLayer(
        name="Licensing Terms",
        rationale="Open-weight licences restrict redistribution.",
        evidence="DeepSeek available under open licence.",
    ),
]

_KEEP_RESPONSE = """\
LAYER: Model Weights
DECISION: KEEP
REASON: Decision directly determines ownership of model weights.
---
LAYER: Inference Infrastructure
DECISION: KEEP
REASON: Edge deployment creates a direct dependency on inference hardware.
---
LAYER: Licensing Terms
DECISION: DISCARD
REASON: Licensing is a secondary concern for an internal edge deployment.
---
"""

_LLM_PATH = "app.agents.stack_mapping.sub_agents.relevance_filter_sub_agent.call_llm_with_fallback"


# ---------------------------------------------------------------------------
# run() — return type and filtering behaviour
# ---------------------------------------------------------------------------

def test_run_returns_list_of_stack_layers():
    """run() returns a list of StackLayer instances."""
    with patch(_LLM_PATH, return_value=_KEEP_RESPONSE):
        result = run(_LAYERS, _CONTEXT)

    assert isinstance(result, list)
    assert all(isinstance(layer, StackLayer) for layer in result)


def test_run_returns_only_keep_layers():
    """run() returns only layers the LLM marked KEEP."""
    with patch(_LLM_PATH, return_value=_KEEP_RESPONSE):
        result = run(_LAYERS, _CONTEXT)

    names = [layer.name for layer in result]
    assert "Model Weights" in names
    assert "Inference Infrastructure" in names
    assert "Licensing Terms" not in names


def test_run_returns_correct_count():
    """run() returns the correct number of KEEP layers."""
    with patch(_LLM_PATH, return_value=_KEEP_RESPONSE):
        result = run(_LAYERS, _CONTEXT)

    assert len(result) == 2


def test_run_preserves_original_stack_layer_objects():
    """run() returns the original StackLayer objects from the input list."""
    with patch(_LLM_PATH, return_value=_KEEP_RESPONSE):
        result = run(_LAYERS, _CONTEXT)

    # Objects should be the same instances, not re-created from LLM text.
    original_by_name = {layer.name: layer for layer in _LAYERS}
    for returned_layer in result:
        assert returned_layer is original_by_name[returned_layer.name]


def test_run_returns_empty_list_for_empty_input():
    """run() returns [] immediately when no candidate layers are provided."""
    with patch(_LLM_PATH, return_value=_KEEP_RESPONSE) as mock_llm:
        result = run([], _CONTEXT)

    assert result == []
    mock_llm.assert_not_called()


def test_run_calls_llm_once():
    """run() makes exactly one LLM call."""
    with patch(_LLM_PATH, return_value=_KEEP_RESPONSE) as mock_llm:
        run(_LAYERS, _CONTEXT)

    assert mock_llm.call_count == 1


# ---------------------------------------------------------------------------
# run() — safe fallback behaviour
# ---------------------------------------------------------------------------

def test_run_returns_all_layers_when_llm_raises():
    """run() returns all candidate layers unchanged when the LLM call fails."""
    with patch(_LLM_PATH, side_effect=RuntimeError("DEEPSEEK_API_KEY not set")):
        result = run(_LAYERS, _CONTEXT)

    assert len(result) == len(_LAYERS)


def test_run_returns_all_layers_when_response_unparseable():
    """run() returns all layers when the LLM returns an unparseable response."""
    with patch(_LLM_PATH, return_value="Sorry, I cannot process this request."):
        result = run(_LAYERS, _CONTEXT)

    assert len(result) == len(_LAYERS)


# ---------------------------------------------------------------------------
# _parse_keep_names()
# ---------------------------------------------------------------------------

def test_parse_keep_names_extracts_keep_layers():
    """_parse_keep_names() returns only names with DECISION: KEEP."""
    keep_names = _parse_keep_names(_KEEP_RESPONSE)
    assert "Model Weights" in keep_names
    assert "Inference Infrastructure" in keep_names


def test_parse_keep_names_excludes_discard_layers():
    """_parse_keep_names() does not include names with DECISION: DISCARD."""
    keep_names = _parse_keep_names(_KEEP_RESPONSE)
    assert "Licensing Terms" not in keep_names


def test_parse_keep_names_is_case_insensitive_for_decision():
    """_parse_keep_names() accepts 'keep' and 'Keep' in addition to 'KEEP'."""
    mixed_case = """\
LAYER: Model Weights
DECISION: keep
REASON: Still relevant.
---
LAYER: Training Data
DECISION: Keep
REASON: Also relevant.
---
"""
    keep_names = _parse_keep_names(mixed_case)
    assert "Model Weights" in keep_names
    assert "Training Data" in keep_names


def test_parse_keep_names_returns_empty_set_for_empty_response():
    """_parse_keep_names() returns an empty set for an empty string."""
    assert _parse_keep_names("") == set()


def test_parse_keep_names_returns_empty_set_for_all_discard():
    """_parse_keep_names() returns empty set when all layers are DISCARD."""
    all_discard = """\
LAYER: Model Weights
DECISION: DISCARD
REASON: Not relevant.
---
"""
    assert _parse_keep_names(all_discard) == set()


# ---------------------------------------------------------------------------
# _filter_layers()
# ---------------------------------------------------------------------------

def test_filter_layers_matches_case_insensitively():
    """_filter_layers() matches keep_names regardless of capitalisation."""
    # LLM might return "model weights" (lowercase) vs original "Model Weights"
    result = _filter_layers(_LAYERS, {"model weights", "inference infrastructure"})
    names = [layer.name for layer in result]
    assert "Model Weights" in names
    assert "Inference Infrastructure" in names


def test_filter_layers_returns_all_layers_when_keep_names_empty():
    """_filter_layers() falls back to all layers when keep_names is empty."""
    result = _filter_layers(_LAYERS, set())
    assert len(result) == len(_LAYERS)


def test_filter_layers_returns_all_layers_when_nothing_matches():
    """_filter_layers() falls back to all layers when no name matches."""
    result = _filter_layers(_LAYERS, {"Unknown Layer Name"})
    assert len(result) == len(_LAYERS)


# ---------------------------------------------------------------------------
# _build_prompt()
# ---------------------------------------------------------------------------

def test_build_prompt_includes_entity_and_capability():
    """_build_prompt() contains the entity and capability from context."""
    prompt = _build_prompt(_LAYERS, _CONTEXT)
    assert "ACME Corp" in prompt
    assert "edge inference LLM" in prompt


def test_build_prompt_includes_all_layer_names():
    """_build_prompt() lists every candidate layer name."""
    prompt = _build_prompt(_LAYERS, _CONTEXT)
    for layer in _LAYERS:
        assert layer.name in prompt
