"""
Stack-Mapping Agent — parent orchestrator for the Stack-Mapping stage.

Role (ARCHITECTURE.md §3.2)
    Receives the IngestionContext from the Ingestion Agent, orchestrates its
    three sub-agents in sequence, and returns one :class:`StackScope` object
    describing the AI-stack layers and their inter-layer dependencies for this
    specific decision.

Sub-agent execution order
    All three sub-agents are sequential — each needs the previous one's output:

        IngestionContext
              │
              ▼
      Layer-Identification (5.5)   → candidate StackLayers
              │
              ▼
      Relevance-Filter (5.6)       → filtered StackLayers
              │
              ▼
      Dependency-Linkage (5.7)     → LayerLinks between filtered layers
              │
              ▼
           StackScope

Public API
----------
    run(context: IngestionContext) -> StackScope

StackScope is the canonical output type of the Stack-Mapping stage and is
defined here so the Scenario-Generation Agent can import it from one place.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.agents.ingestion.sub_agents.context_synthesis_sub_agent import IngestionContext
from app.agents.stack_mapping.sub_agents import (
    dependency_linkage_sub_agent,
    layer_identification_sub_agent,
    relevance_filter_sub_agent,
)
from app.agents.stack_mapping.sub_agents.dependency_linkage_sub_agent import LayerLink
from app.agents.stack_mapping.sub_agents.layer_identification_sub_agent import StackLayer


# ---------------------------------------------------------------------------
# Output type
# ---------------------------------------------------------------------------

@dataclass
class StackScope:
    """The stack-mapping output for one decision brief.

    Attributes
    ----------
    entity:
        The organisation making the decision (carried through for traceability).
    capability:
        The AI capability being sourced.
    layers:
        Filtered, relevant AI-stack layers for this decision.
    links:
        Directional dependency links between the surviving layers.
        May be empty if no inter-layer dependencies were found or if the
        Dependency-Linkage Sub-Agent was skipped / returned nothing.
    """

    entity: str
    capability: str
    layers: list[StackLayer] = field(default_factory=list)
    links: list[LayerLink] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(context: IngestionContext) -> StackScope:
    """Run the full Stack-Mapping pipeline for one decision brief.

    Parameters
    ----------
    context:
        The :class:`~app.agents.ingestion.sub_agents.context_synthesis_sub_agent.IngestionContext`
        produced by the Ingestion Agent.

    Returns
    -------
    StackScope
        The filtered stack layers and their inter-layer dependency links,
        ready for the Scenario-Generation Agent.
    """
    # Step 1 — identify candidate layers from ingested context.
    candidate_layers: list[StackLayer] = layer_identification_sub_agent.run(context)

    # Step 2 — filter to only layers genuinely touched by this decision.
    filtered_layers: list[StackLayer] = relevance_filter_sub_agent.run(
        layers=candidate_layers,
        context=context,
    )

    # Step 3 — map inter-layer dependencies among the surviving layers.
    links: list[LayerLink] = dependency_linkage_sub_agent.run(
        layers=filtered_layers,
        context=context,
    )

    return StackScope(
        entity=context.entity,
        capability=context.capability,
        layers=filtered_layers,
        links=links,
    )
