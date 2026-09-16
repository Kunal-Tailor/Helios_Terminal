"""
Option-Enumeration Sub-Agent — Scenario-Generation Agent, Sub-Agent 1 of 3.

Role (ARCHITECTURE.md §3.3)
    Generates a raw set of candidate sourcing options for the decision,
    grounded in the StackScope produced by the Stack-Mapping Agent.

    Candidate options are distinct paths the entity could take to acquire
    or develop the AI capability (e.g., "build in-house", "license open-weight
    model", "outsource to vendor", "hybrid approach").

Public API
----------
    run(stack_scope: StackScope) -> list[Option]

The sub-agent calls the shared LLM client with a structured prompt built from
the StackScope, parses the response into a list of :class:`Option` objects,
and returns them. If the LLM call fails or returns an unparseable response,
it returns an empty list (graceful degradation).

Option is defined here because it is the canonical output type of the
option-enumeration step; the Feasibility-Check Sub-Agent (5.10) imports it.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from app.agents.stack_mapping.stack_mapping_agent import StackScope
from app.llm.client import complete

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Output type
# ---------------------------------------------------------------------------

@dataclass
class Option:
    """One candidate sourcing option for this decision.

    Attributes
    ----------
    name:
        Short, canonical name for the option
        (e.g. ``"Build in-house"``, ``"License open-weight model"``).
    description:
        Brief description of what this option entails.
    rationale:
        Why this option is viable given the stack scope (e.g., which layers
        it addresses or dependencies it creates).
    grounded_in:
        Short direct restatement of the specific fact(s) from Stack-Mapping's
        context that justify why this option is realistic for this decision.
    """

    name: str
    description: str
    rationale: str = ""
    grounded_in: str = ""


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(stack_scope: StackScope) -> list[Option]:
    """Enumerate candidate sourcing options given *stack_scope*.

    Parameters
    ----------
    stack_scope:
        The :class:`~app.agents.stack_mapping.stack_mapping_agent.StackScope`
        produced by the Stack-Mapping Agent for this decision brief.

    Returns
    -------
    list[Option]
        Candidate sourcing options in the order the LLM proposes them.
        Returns ``[]`` if the LLM call fails or the response cannot be parsed.
    """
    prompt = _build_prompt(stack_scope)
    try:
        response = complete(prompt)
        return _parse_response(response)
    except Exception as exc:
        logger.error(
            "LLM call failed in option_enumeration_sub_agent (run): %s",
            exc,
            exc_info=True,
        )
        return []


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_prompt(stack_scope: StackScope) -> str:
    """Build the LLM prompt from the StackScope."""
    layers_str = "\n".join(
        f"- {layer.name}: {layer.rationale}"
        + (f" Evidence: {layer.evidence}" if layer.evidence else "")
        for layer in stack_scope.layers
    ) if stack_scope.layers else "No stack layers identified."

    links_str = "\n".join(
        f"- {link.from_layer} → {link.to_layer} ({link.dependency_type}): {link.description}"
        for link in stack_scope.links
    ) if stack_scope.links else "No inter-layer dependencies identified."

    return f"""You are an AI sourcing analyst enumerating candidate sourcing options
for a specific AI procurement decision.

DECISION BRIEF
Entity: {stack_scope.entity}
Capability sought: {stack_scope.capability}

STACK SCOPE — Identified Layers
{layers_str}

INTER-LAYER DEPENDENCIES
{links_str}

TASK
Generate a comprehensive set of distinct sourcing options the entity could pursue
to acquire or develop this AI capability. Each option should be a concrete path
that addresses the identified stack layers and their dependencies.

Focus on actionable, realistic options — not hypothetical edge cases. Consider:
- Build vs. buy vs. outsource decisions
- Open-source vs. proprietary choices
- In-house vs. cloud-hosted deployment
- Single-vendor vs. multi-vendor approaches

Respond in exactly this repeating block format — one block per option, separated by ---:

OPTION: <short canonical option name>
GROUNDED_IN: <copy or lightly rephrase ONE Evidence or layer rationale sentence from STACK SCOPE above. MUST reuse the same nouns/terms already present there. Do NOT invent new quantities, dataset sizes, product names, or infrastructure details that are not written above.>
DESCRIPTION: <2-3 sentences: what this option entails (mechanics, specific software/hardware frameworks)>
RATIONALE: <1-2 sentences: why this option makes sense given the stack scope>
---
OPTION: <next option name>
GROUNDED_IN: <direct restatement of grounded fact>
DESCRIPTION: <description>
RATIONALE: <rationale>
---
"""


def _parse_response(response: str) -> list[Option]:
    """Parse the structured LLM response into a list of :class:`Option` objects.

    Expected block format::

        OPTION: <name>
        GROUNDED_IN: <text>
        DESCRIPTION: <text>
        RATIONALE: <text>
        ---

    Blocks that are missing the OPTION field are skipped.
    If no blocks are found, returns ``[]``.
    """
    # Split on the --- separator; handle trailing separators gracefully.
    raw_blocks = re.split(r"\n---+\s*", response.strip())
    options: list[Option] = []

    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue

        name = _extract_field(block, "OPTION")
        if not name:
            continue  # skip malformed blocks

        grounded_in = _extract_field(block, "GROUNDED_IN")
        description = _extract_field(block, "DESCRIPTION")
        rationale = _extract_field(block, "RATIONALE")

        options.append(
            Option(
                name=name,
                description=description,
                rationale=rationale,
                grounded_in=grounded_in,
            )
        )

    return options


def _extract_field(block: str, field: str) -> str:
    """Extract the value of *field* from a text *block*.

    Matches ``FIELD: <value>`` where value runs to the next uppercase field
    name or end of block. Returns empty string if not found.
    """
    pattern = rf"^{field}:\s*(.+?)(?=\n[A-Z]+:|$)"
    match = re.search(pattern, block, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""
