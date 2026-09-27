"""
Layer-Identification Sub-Agent — Stack-Mapping Agent, Sub-Agent 1 of 3.

Role (ARCHITECTURE.md §3.2)
    Proposes the candidate AI-stack layers implicated by the decision brief,
    grounded in the IngestionContext produced by the Ingestion Agent.

    Candidate layers include (but are not limited to):
      - Model weights
      - Training data
      - Inference infrastructure
      - Fine-tuning pipeline
      - Licensing terms
      - Data governance / compliance layer

Public API
----------
    run(context: IngestionContext) -> list[StackLayer]

The sub-agent calls the shared LLM client with a structured prompt built from
the IngestionContext, parses the response into a list of :class:`StackLayer`
objects, and returns them.  If the LLM call fails or returns an unparseable
response, it returns an empty list (graceful degradation).

StackLayer is defined here because it is the canonical output type of the
layer-identification step; the Relevance-Filter Sub-Agent (5.6) imports it.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from app.agents.ingestion.sub_agents.context_synthesis_sub_agent import IngestionContext
from app.llm.client import call_llm_with_fallback

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Output type
# ---------------------------------------------------------------------------

@dataclass
class StackLayer:
    """One candidate AI-stack layer proposed for this decision.

    Attributes
    ----------
    name:
        Short, canonical name for the layer
        (e.g. ``"Model Weights"``, ``"Inference Infrastructure"``).
    rationale:
        Why this layer is implicated by the decision brief.
    evidence:
        Specific text from the ingested context that supports including
        this layer (quoted snippet or paraphrase).
    """

    name: str
    rationale: str
    evidence: str = ""


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(context: IngestionContext) -> list[StackLayer]:
    """Propose candidate AI-stack layers from *context*.

    Parameters
    ----------
    context:
        The :class:`~app.agents.ingestion.sub_agents.context_synthesis_sub_agent.IngestionContext`
        produced by the Ingestion Agent for this decision brief.

    Returns
    -------
    list[StackLayer]
        Candidate AI-stack layers in the order the LLM proposes them.
        Returns ``[]`` if the LLM call fails or the response cannot be parsed.
    """
    prompt = _build_prompt(context)
    try:
        response = call_llm_with_fallback(prompt)
        return _parse_response(response)
    except Exception as exc:
        logger.error(
            "LLM call failed in layer_identification_sub_agent (run): %s",
            exc,
            exc_info=True,
        )
        return []


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_prompt(context: IngestionContext) -> str:
    """Build the LLM prompt from the IngestionContext."""
    options_str = ", ".join(context.options) if context.options else "not specified"
    facts_str = (
        "\n".join(f"- {f}" for f in context.key_facts)
        if context.key_facts
        else "No key facts available."
    )
    summary_str = context.context_summary or "No context summary available."

    return f"""You are an AI sourcing analyst mapping the technology stack implications
of a specific AI procurement decision.

DECISION BRIEF
Entity: {context.entity}
Capability sought: {context.capability}
Candidate options: {options_str}

INGESTED CONTEXT SUMMARY
{summary_str}

KEY FACTS FROM SOURCES
{facts_str}

TASK
Identify every AI-stack layer that this decision directly touches or creates a
dependency on. Focus only on layers relevant to this specific decision — do not
list every possible AI-stack layer.

Candidate layer types (use these names where applicable, or introduce new ones if needed):
  - Model Weights
  - Training Data
  - Inference Infrastructure
  - Fine-Tuning Pipeline
  - Licensing Terms
  - Data Governance / Compliance
  - Hardware / Compute
  - API / Integration Layer

Respond in exactly this repeating block format — one block per layer, separated by ---:

LAYER: <short canonical layer name>
RATIONALE: <one sentence: analytical inference explaining why this decision implicates this layer>
EVIDENCE: <short direct restatement or quote of the specific fact strictly from the Key Facts or Ingested Context Summary above that justifies why this layer is implicated. MUST closely echo the actual wording and terms from the key facts or context summary. DO NOT quote or reference the candidate options; only quote from Key Facts or Ingested Context Summary.>
---
LAYER: <next layer name>
RATIONALE: <analytical inference rationale>
EVIDENCE: <direct restatement of grounded fact from Key Facts or Context Summary>
---
"""


def _parse_response(response: str) -> list[StackLayer]:
    """Parse the structured LLM response into a list of :class:`StackLayer` objects.

    Expected block format::

        LAYER: <name>
        RATIONALE: <text>
        EVIDENCE: <text>
        ---

    Blocks that are missing the LAYER field are skipped.
    If no blocks are found, returns ``[]``.
    """
    # Split on the --- separator; handle trailing separators gracefully.
    raw_blocks = re.split(r"\n---+\s*", response.strip())
    layers: list[StackLayer] = []

    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue

        name = _extract_field(block, "LAYER")
        if not name:
            continue  # skip malformed blocks

        rationale = _extract_field(block, "RATIONALE")
        evidence = _extract_field(block, "EVIDENCE")

        layers.append(StackLayer(name=name, rationale=rationale, evidence=evidence))

    return layers


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
