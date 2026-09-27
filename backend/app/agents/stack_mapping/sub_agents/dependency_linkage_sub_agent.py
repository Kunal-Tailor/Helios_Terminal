"""
Dependency-Linkage Sub-Agent — Stack-Mapping Agent, Sub-Agent 3 of 3 (optional).

Role (ARCHITECTURE.md §3.2)
    Maps how the surviving (filtered) AI-stack layers interconnect.
    Example: "Fine-Tuning Pipeline depends on Training Data licensing terms."

    This step enriches the Stack-Mapping output before it reaches the
    Scenario-Generation Agent, ensuring downstream agents understand that
    a decision touching one layer may cascade into adjacent layers.

Public API
----------
    run(layers, context) -> list[LayerLink]

For each pair of surviving layers, the LLM identifies whether a directional
dependency exists and describes it.  Returns a list of :class:`LayerLink`
objects.  Returns ``[]`` on LLM failure (graceful degradation — the parent
Stack-Mapping Agent will still return the filtered layer list).

LayerLink is defined here as the canonical output type of this step.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from app.agents.ingestion.sub_agents.context_synthesis_sub_agent import IngestionContext
from app.agents.stack_mapping.sub_agents.layer_identification_sub_agent import StackLayer
from app.llm.client import call_llm_with_fallback

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Output type
# ---------------------------------------------------------------------------

@dataclass
class LayerLink:
    """A directional dependency between two AI-stack layers.

    Attributes
    ----------
    from_layer:
        The layer that depends on or is constrained by another.
    to_layer:
        The layer being depended on.
    dependency_type:
        Short label for the relationship, e.g. ``"depends on"``,
        ``"constrained by"``, ``"requires"``.
    description:
        One-sentence explanation of why this dependency exists in the
        context of the specific decision.
    """

    from_layer: str
    to_layer: str
    dependency_type: str
    description: str


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(layers: list[StackLayer], context: IngestionContext) -> list[LayerLink]:
    """Map dependencies between the surviving filtered layers.

    Parameters
    ----------
    layers:
        Filtered :class:`StackLayer` objects from the Relevance-Filter
        Sub-Agent (5.6).  Must contain at least two layers for any links
        to be possible.
    context:
        The :class:`~app.agents.ingestion.sub_agents.context_synthesis_sub_agent.IngestionContext`
        for this decision, used to ground the dependency reasoning.

    Returns
    -------
    list[LayerLink]
        Directional dependency links between layers.  May be empty if the
        LLM finds no dependencies, if fewer than two layers are provided,
        or if the LLM call fails.
    """
    if len(layers) < 2:
        # Cannot form any links with fewer than two layers.
        return []

    prompt = _build_prompt(layers, context)
    try:
        response = call_llm_with_fallback(prompt)
        return _parse_response(response)
    except Exception as exc:
        logger.error(
            "LLM call failed in dependency_linkage_sub_agent (run): %s",
            exc,
            exc_info=True,
        )
        return []


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_prompt(layers: list[StackLayer], context: IngestionContext) -> str:
    """Build the LLM dependency-mapping prompt."""
    options_str = ", ".join(context.options) if context.options else "not specified"
    layer_names = "\n".join(f"  - {layer.name}" for layer in layers)

    return f"""You are an AI sourcing analyst mapping how AI-stack layers interconnect
for a specific procurement decision.

DECISION BRIEF
Entity: {context.entity}
Capability sought: {context.capability}
Candidate options: {options_str}

SURVIVING LAYERS (already filtered to those relevant to this decision)
{layer_names}

TASK
For each pair of layers above, decide whether one layer creates a direct
dependency on another within the scope of this decision.

Rules:
  - Only report dependencies that are real and decision-specific, not generic.
  - A dependency is directional: FROM (dependent layer) → TO (required layer).
  - If no dependency exists between a pair, do not include it.
  - Use short dependency type labels: "depends on", "constrained by",
    "requires", "determines", "gates".

If no inter-layer dependencies exist, respond with exactly: NO DEPENDENCIES

Otherwise respond in exactly this repeating block format, separated by ---:

FROM: <exact layer name>
TO: <exact layer name>
TYPE: <dependency type label>
DESCRIPTION: <one sentence explaining the dependency in this decision's context>
---
"""


def _parse_response(response: str) -> list[LayerLink]:
    """Parse the structured LLM response into a list of :class:`LayerLink` objects.

    Returns ``[]`` for ``NO DEPENDENCIES`` responses or unparseable output.
    """
    stripped = response.strip()

    # Explicit no-dependency signal from the LLM.
    if "NO DEPENDENCIES" in stripped.upper():
        return []

    raw_blocks = re.split(r"\n---+\s*", stripped)
    links: list[LayerLink] = []

    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue

        from_layer = _extract_field(block, "FROM")
        to_layer = _extract_field(block, "TO")
        dep_type = _extract_field(block, "TYPE")
        description = _extract_field(block, "DESCRIPTION")

        # Require at minimum FROM and TO to form a valid link.
        if not from_layer or not to_layer:
            continue

        links.append(
            LayerLink(
                from_layer=from_layer,
                to_layer=to_layer,
                dependency_type=dep_type,
                description=description,
            )
        )

    return links


def _extract_field(block: str, field: str) -> str:
    """Extract the value of *field* from a text *block*.

    Matches ``FIELD: <value>`` where value runs to the next uppercase field
    name or end of block.  Returns empty string if not found.
    """
    pattern = rf"^{field}:\s*(.+?)(?=\n[A-Z]+:|$)"
    match = re.search(pattern, block, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""
