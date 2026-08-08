"""
Relevance-Filter Sub-Agent — Stack-Mapping Agent, Sub-Agent 2 of 3.

Role (ARCHITECTURE.md §3.2)
    Narrows the candidate AI-stack layers proposed by the Layer-Identification
    Sub-Agent (5.5) to only the layers this specific decision actually touches.
    Prevents the Stack-Mapping Agent from defaulting to a full-footprint audit.

Public API
----------
    run(layers, context) -> list[StackLayer]

For each candidate :class:`~layer_identification_sub_agent.StackLayer` the LLM
decides KEEP or DISCARD, citing a short reason.  The sub-agent returns the
filtered list preserving the original ``StackLayer`` objects (name, rationale,
evidence from 5.5 are unchanged).

Fallback behaviour
------------------
If the LLM call fails or the response cannot be parsed, all candidate layers
are returned unchanged.  Over-including is safer than over-excluding here —
the downstream Dependency-Linkage Sub-Agent (5.7) and Stack-Mapping parent
(5.8) can tolerate a broader scope, but silently dropping layers would make
the system blind to real dependencies.
"""

from __future__ import annotations

import logging
import re

from app.agents.ingestion.sub_agents.context_synthesis_sub_agent import IngestionContext
from app.agents.stack_mapping.sub_agents.layer_identification_sub_agent import StackLayer
from app.llm.client import complete

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(layers: list[StackLayer], context: IngestionContext) -> list[StackLayer]:
    """Filter *layers* to those genuinely touched by the decision in *context*.

    Parameters
    ----------
    layers:
        Candidate :class:`StackLayer` objects from the Layer-Identification
        Sub-Agent (5.5).
    context:
        The :class:`~app.agents.ingestion.sub_agents.context_synthesis_sub_agent.IngestionContext`
        for this decision, used to ground the filtering decision.

    Returns
    -------
    list[StackLayer]
        The subset of *layers* that the LLM judges as relevant to this decision,
        in their original order.  Returns all *layers* unchanged if the LLM
        call fails or the response is unparseable (safe fallback).
    """
    if not layers:
        return []

    prompt = _build_prompt(layers, context)
    try:
        response = complete(prompt)
        keep_names = _parse_keep_names(response)
        return _filter_layers(layers, keep_names)
    except Exception as exc:
        logger.error(
            "LLM call failed in relevance_filter_sub_agent (run): %s",
            exc,
            exc_info=True,
        )
        # Safe fallback: return all candidates unchanged.
        return list(layers)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_prompt(layers: list[StackLayer], context: IngestionContext) -> str:
    """Build the LLM filtering prompt from the candidate layers and context."""
    options_str = ", ".join(context.options) if context.options else "not specified"

    layer_blocks = []
    for layer in layers:
        block = (
            f"  Layer name: {layer.name}\n"
            f"  Rationale: {layer.rationale}\n"
            f"  Evidence: {layer.evidence}"
        )
        layer_blocks.append(block)
    layers_str = "\n\n".join(layer_blocks)

    return f"""You are an AI sourcing analyst deciding which AI-stack layers are genuinely
implicated by a specific procurement decision.

DECISION BRIEF
Entity: {context.entity}
Capability sought: {context.capability}
Candidate options: {options_str}

CANDIDATE LAYERS TO EVALUATE
{layers_str}

TASK
For each candidate layer above, decide whether the decision DIRECTLY implicates
or creates a dependency on that layer.

Rules:
  - KEEP a layer only if the specific decision (entity + capability + options)
    creates a concrete dependency or risk at that layer.
  - DISCARD a layer if it is generic, speculative, or not directly touched by
    this particular decision.
  - Keep at least one layer (never discard all).

Respond in exactly this repeating block format, one block per layer, separated by ---:

LAYER: <exact layer name from the list above>
DECISION: KEEP
REASON: <one sentence explaining why this decision touches this layer>
---
LAYER: <exact layer name>
DECISION: DISCARD
REASON: <one sentence explaining why this layer is not directly implicated>
---
"""


def _parse_keep_names(response: str) -> set[str]:
    """Return the set of layer names marked KEEP in the LLM response.

    Parses blocks of the form::

        LAYER: <name>
        DECISION: KEEP
        REASON: <text>
        ---

    Case-insensitive DECISION match (``keep`` / ``KEEP``).
    Returns an empty set if no blocks are found.
    """
    keep_names: set[str] = set()
    raw_blocks = re.split(r"\n---+\s*", response.strip())

    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue

        name_match = re.search(r"^LAYER:\s*(.+)", block, re.MULTILINE)
        decision_match = re.search(r"^DECISION:\s*(\w+)", block, re.MULTILINE)

        if name_match and decision_match:
            name = name_match.group(1).strip()
            decision = decision_match.group(1).strip().upper()
            if decision == "KEEP":
                keep_names.add(name)

    return keep_names


def _filter_layers(
    layers: list[StackLayer],
    keep_names: set[str],
) -> list[StackLayer]:
    """Return the subset of *layers* whose names appear in *keep_names*.

    Matching is case-insensitive to tolerate minor LLM capitalisation drift.
    If *keep_names* is empty (no KEEP decisions parsed), returns all *layers*
    as a safe fallback.
    """
    if not keep_names:
        return list(layers)

    keep_lower = {n.lower() for n in keep_names}
    filtered = [layer for layer in layers if layer.name.lower() in keep_lower]

    # If the filter removed everything (shouldn't happen per prompt rules, but
    # guard against it), fall back to the full list.
    return filtered if filtered else list(layers)
