"""
Unit and integration tests for app.agents.stack_mapping.stack_mapping_agent.

UNIT TESTS (mock all sub-agents at their run() boundary)
  - run() returns a StackScope
  - run() copies entity and capability from context to StackScope
  - run() calls layer-identification sub-agent with the context
  - run() passes layer-identification output to relevance-filter sub-agent
  - run() passes relevance-filter output to dependency-linkage sub-agent
  - run() populates StackScope.layers from relevance-filter output
  - run() populates StackScope.links from dependency-linkage output
  - run() handles empty sub-agent outputs (empty layers, empty links)

INTEGRATION TESTS (mock at LLM boundary; real sub-agent logic executes)
  - Full pipeline produces a StackScope with correct entity/capability
  - StackScope.layers is a list of StackLayer objects
  - StackScope.links is a list of LayerLink objects (or empty list)
  - Pipeline tolerates all sub-agents returning empty results
"""

from unittest.mock import patch

import pytest

from app.agents.ingestion.sub_agents.context_synthesis_sub_agent import IngestionContext
from app.agents.stack_mapping.stack_mapping_agent import StackScope, run
from app.agents.stack_mapping.sub_agents.dependency_linkage_sub_agent import LayerLink
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

_CANDIDATE_LAYERS = [
    StackLayer("Model Weights", "Controls weight ownership.", "Open-weight models on HF."),
    StackLayer("Licensing Terms", "Governs usage restrictions.", "DeepSeek open licence."),
    StackLayer("Inference Infrastructure", "Required for edge deployment.", "Edge eval."),
]

_FILTERED_LAYERS = [
    StackLayer("Model Weights", "Controls weight ownership.", "Open-weight models on HF."),
    StackLayer("Inference Infrastructure", "Required for edge deployment.", "Edge eval."),
]

_LINKS = [
    LayerLink(
        from_layer="Model Weights",
        to_layer="Licensing Terms",
        dependency_type="constrained by",
        description="Weights use is constrained by licence terms.",
    ),
]

_LAYER_ID_PATH = "app.agents.stack_mapping.stack_mapping_agent.layer_identification_sub_agent.run"
_REL_FILTER_PATH = "app.agents.stack_mapping.stack_mapping_agent.relevance_filter_sub_agent.run"
_DEP_LINK_PATH = "app.agents.stack_mapping.stack_mapping_agent.dependency_linkage_sub_agent.run"


# ---------------------------------------------------------------------------
# Unit tests — sub-agent run() functions are mocked
# ---------------------------------------------------------------------------

def test_unit_run_returns_stack_scope():
    """run() returns a StackScope instance."""
    with patch(_LAYER_ID_PATH, return_value=_CANDIDATE_LAYERS), \
         patch(_REL_FILTER_PATH, return_value=_FILTERED_LAYERS), \
         patch(_DEP_LINK_PATH, return_value=_LINKS):
        result = run(_CONTEXT)

    assert isinstance(result, StackScope)


def test_unit_run_copies_entity_and_capability():
    """run() carries entity and capability from context into StackScope."""
    with patch(_LAYER_ID_PATH, return_value=_CANDIDATE_LAYERS), \
         patch(_REL_FILTER_PATH, return_value=_FILTERED_LAYERS), \
         patch(_DEP_LINK_PATH, return_value=_LINKS):
        result = run(_CONTEXT)

    assert result.entity == "ACME Corp"
    assert result.capability == "edge inference LLM"


def test_unit_run_calls_layer_identification_with_context():
    """run() calls layer-identification sub-agent with the IngestionContext."""
    with patch(_LAYER_ID_PATH, return_value=_CANDIDATE_LAYERS) as mock_li, \
         patch(_REL_FILTER_PATH, return_value=_FILTERED_LAYERS), \
         patch(_DEP_LINK_PATH, return_value=_LINKS):
        run(_CONTEXT)

    mock_li.assert_called_once_with(_CONTEXT)


def test_unit_run_passes_candidates_to_relevance_filter():
    """run() passes layer-identification output as layers to the relevance filter."""
    with patch(_LAYER_ID_PATH, return_value=_CANDIDATE_LAYERS), \
         patch(_REL_FILTER_PATH, return_value=_FILTERED_LAYERS) as mock_rf, \
         patch(_DEP_LINK_PATH, return_value=_LINKS):
        run(_CONTEXT)

    mock_rf.assert_called_once_with(layers=_CANDIDATE_LAYERS, context=_CONTEXT)


def test_unit_run_passes_filtered_layers_to_dependency_linkage():
    """run() passes relevance-filter output as layers to dependency-linkage."""
    with patch(_LAYER_ID_PATH, return_value=_CANDIDATE_LAYERS), \
         patch(_REL_FILTER_PATH, return_value=_FILTERED_LAYERS), \
         patch(_DEP_LINK_PATH, return_value=_LINKS) as mock_dl:
        run(_CONTEXT)

    mock_dl.assert_called_once_with(layers=_FILTERED_LAYERS, context=_CONTEXT)


def test_unit_run_populates_layers_from_relevance_filter():
    """StackScope.layers comes from the relevance-filter sub-agent output."""
    with patch(_LAYER_ID_PATH, return_value=_CANDIDATE_LAYERS), \
         patch(_REL_FILTER_PATH, return_value=_FILTERED_LAYERS), \
         patch(_DEP_LINK_PATH, return_value=_LINKS):
        result = run(_CONTEXT)

    assert result.layers is _FILTERED_LAYERS


def test_unit_run_populates_links_from_dependency_linkage():
    """StackScope.links comes from the dependency-linkage sub-agent output."""
    with patch(_LAYER_ID_PATH, return_value=_CANDIDATE_LAYERS), \
         patch(_REL_FILTER_PATH, return_value=_FILTERED_LAYERS), \
         patch(_DEP_LINK_PATH, return_value=_LINKS):
        result = run(_CONTEXT)

    assert result.links is _LINKS


def test_unit_run_handles_all_empty_sub_agent_outputs():
    """run() returns a valid StackScope even when all sub-agents return empty."""
    with patch(_LAYER_ID_PATH, return_value=[]), \
         patch(_REL_FILTER_PATH, return_value=[]), \
         patch(_DEP_LINK_PATH, return_value=[]):
        result = run(_CONTEXT)

    assert isinstance(result, StackScope)
    assert result.layers == []
    assert result.links == []


# ---------------------------------------------------------------------------
# Integration tests — mocked at the LLM boundary
# Real sub-agent logic executes end-to-end through the parent
# ---------------------------------------------------------------------------

_LLM_PATH = "app.agents.stack_mapping.sub_agents.layer_identification_sub_agent.complete"
_FILTER_LLM_PATH = "app.agents.stack_mapping.sub_agents.relevance_filter_sub_agent.complete"
_LINK_LLM_PATH = "app.agents.stack_mapping.sub_agents.dependency_linkage_sub_agent.complete"

_LAYER_ID_RESPONSE = """\
LAYER: Model Weights
RATIONALE: Decision determines weight ownership.
EVIDENCE: Open-weight models on Hugging Face.
---
LAYER: Inference Infrastructure
RATIONALE: Edge deployment requires hardware.
EVIDENCE: Evaluating edge deployment options.
---
"""

_FILTER_RESPONSE = """\
LAYER: Model Weights
DECISION: KEEP
REASON: Directly determines weight control.
---
LAYER: Inference Infrastructure
DECISION: KEEP
REASON: Required for edge deployment.
---
"""

_LINK_RESPONSE = """\
FROM: Model Weights
TO: Inference Infrastructure
TYPE: depends on
DESCRIPTION: Model weights format must be compatible with inference hardware.
---
"""


def test_integration_run_returns_stack_scope():
    """Integration: full pipeline returns a StackScope."""
    with patch(_LLM_PATH, return_value=_LAYER_ID_RESPONSE), \
         patch(_FILTER_LLM_PATH, return_value=_FILTER_RESPONSE), \
         patch(_LINK_LLM_PATH, return_value=_LINK_RESPONSE):
        result = run(_CONTEXT)

    assert isinstance(result, StackScope)
    assert result.entity == "ACME Corp"
    assert result.capability == "edge inference LLM"


def test_integration_run_layers_are_stack_layer_instances():
    """Integration: StackScope.layers contains StackLayer objects."""
    with patch(_LLM_PATH, return_value=_LAYER_ID_RESPONSE), \
         patch(_FILTER_LLM_PATH, return_value=_FILTER_RESPONSE), \
         patch(_LINK_LLM_PATH, return_value=_LINK_RESPONSE):
        result = run(_CONTEXT)

    assert all(isinstance(layer, StackLayer) for layer in result.layers)


def test_integration_run_links_are_layer_link_instances():
    """Integration: StackScope.links contains LayerLink objects."""
    with patch(_LLM_PATH, return_value=_LAYER_ID_RESPONSE), \
         patch(_FILTER_LLM_PATH, return_value=_FILTER_RESPONSE), \
         patch(_LINK_LLM_PATH, return_value=_LINK_RESPONSE):
        result = run(_CONTEXT)

    assert all(isinstance(link, LayerLink) for link in result.links)


def test_integration_pipeline_tolerates_all_llm_failures():
    """Integration: pipeline returns StackScope even when all LLM calls fail."""
    with patch(_LLM_PATH, side_effect=RuntimeError("LLM down")), \
         patch(_FILTER_LLM_PATH, side_effect=RuntimeError("LLM down")), \
         patch(_LINK_LLM_PATH, side_effect=RuntimeError("LLM down")):
        result = run(_CONTEXT)

    assert isinstance(result, StackScope)
    assert result.layers == []
    assert result.links == []
