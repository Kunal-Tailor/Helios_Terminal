"""
Scenario-Refinement Sub-Agent — Scenario-Generation Agent, Sub-Agent 3 of 3 (optional).

Role (ARCHITECTURE.md §3.3)
    Sharpens each feasible option from the Feasibility-Check Sub-Agent (5.10)
    into a fully-specified scenario: a concrete, decision-ready description with
    implementation steps, key risks, and stack-layer coverage.

    If this sub-agent is skipped, the parent Scenario-Generation Agent returns
    the raw feasible options as its output instead.

Public API
----------
    run(options, stack_scope) -> list[Scenario]

For each feasible :class:`~option_enumeration_sub_agent.Option`, the LLM
produces a fully-specified :class:`Scenario`.  Scenarios are the canonical
input to the Outcome-Prediction Agent (5.13+).

Scenario is defined here as the canonical output type of the
Scenario-Generation stage.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.agents.scenario_generation.sub_agents.option_enumeration_sub_agent import Option
from app.agents.stack_mapping.stack_mapping_agent import StackScope
from app.llm.client import complete

# Maximum number of options to refine in a single LLM call.
# If there are more, they are batched to keep prompts token-efficient.
_MAX_OPTIONS_PER_CALL = 5


# ---------------------------------------------------------------------------
# Output type — canonical output of the Scenario-Generation stage
# ---------------------------------------------------------------------------

@dataclass
class Scenario:
    """A fully-specified sourcing scenario, refined from a feasible option.

    Attributes
    ----------
    name:
        Short canonical name, matching the originating :class:`Option` name.
    option_name:
        The exact ``Option.name`` this scenario was refined from.
    description:
        Detailed description of what pursuing this scenario entails.
    implementation_steps:
        Ordered list of concrete steps the entity would take to execute
        this scenario.
    key_risks:
        List of specific risks or failure modes for this scenario in the
        context of the decision brief.
    layers_addressed:
        Names of the stack layers (from StackScope) that this scenario
        directly addresses or resolves.
    """

    name: str
    option_name: str
    description: str
    implementation_steps: list[str] = field(default_factory=list)
    key_risks: list[str] = field(default_factory=list)
    layers_addressed: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(options: list[Option], stack_scope: StackScope) -> list[Scenario]:
    """Refine feasible *options* into fully-specified scenarios.

    Parameters
    ----------
    options:
        Feasible :class:`~option_enumeration_sub_agent.Option` objects from
        the Feasibility-Check Sub-Agent (5.10).
    stack_scope:
        The :class:`~app.agents.stack_mapping.stack_mapping_agent.StackScope`
        for this decision, used to ground each scenario in the identified
        stack layers.

    Returns
    -------
    list[Scenario]
        One :class:`Scenario` per feasible option, in the same order.
        Returns ``[]`` if *options* is empty or if the LLM call fails.
    """
    if not options:
        return []

    prompt = _build_prompt(options, stack_scope)
    try:
        response = complete(prompt)
        return _parse_response(response, options)
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_prompt(options: list[Option], stack_scope: StackScope) -> str:
    """Build the LLM scenario-refinement prompt."""
    options_str = "\n\n".join(
        f"  OPTION {i + 1}: {opt.name}\n"
        f"  Description: {opt.description}\n"
        f"  Rationale: {opt.rationale}"
        for i, opt in enumerate(options[:_MAX_OPTIONS_PER_CALL])
    )

    layers_str = (
        "\n".join(f"  - {layer.name}: {layer.rationale}" for layer in stack_scope.layers)
        if stack_scope.layers
        else "  No stack layers identified."
    )

    links_str = (
        "\n".join(
            f"  - {link.from_layer} → {link.to_layer} ({link.dependency_type})"
            for link in stack_scope.links
        )
        if stack_scope.links
        else "  No inter-layer dependencies identified."
    )

    return f"""You are an AI sourcing analyst refining feasible sourcing options into
fully-specified scenarios for a specific AI procurement decision.

DECISION BRIEF
Entity: {stack_scope.entity}
Capability sought: {stack_scope.capability}

STACK SCOPE — Relevant Layers
{layers_str}

INTER-LAYER DEPENDENCIES
{links_str}

FEASIBLE OPTIONS TO REFINE
{options_str}

TASK
For each option above, produce a fully-specified scenario: a concrete,
decision-ready plan with implementation steps, key risks, and the stack
layers it addresses. Be specific to this entity and this decision — not generic.

Respond in exactly this repeating block format — one block per option, separated by ---:

SCENARIO: <exact option name>
DESCRIPTION: <2-3 sentence detailed description of what pursuing this scenario entails>
STEPS:
- <implementation step 1>
- <implementation step 2>
- <add as many steps as needed, minimum 3>
RISKS:
- <key risk or failure mode 1>
- <key risk or failure mode 2>
- <add as many risks as needed, minimum 2>
LAYERS: <comma-separated list of stack layer names this scenario directly addresses>
---
"""


def _parse_response(response: str, options: list[Option]) -> list[Scenario]:
    """Parse the structured LLM response into a list of :class:`Scenario` objects.

    Expected block format::

        SCENARIO: <name>
        DESCRIPTION: <text>
        STEPS:
        - step 1
        - step 2
        RISKS:
        - risk 1
        LAYERS: <comma-separated names>
        ---

    Blocks missing the SCENARIO field are skipped.
    Returns ``[]`` if no valid blocks are found.
    """
    raw_blocks = re.split(r"\n---+\s*", response.strip())
    scenarios: list[Scenario] = []

    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue

        name = _extract_field(block, "SCENARIO")
        if not name:
            continue

        description = _extract_field(block, "DESCRIPTION")
        steps = _extract_bullet_list(block, "STEPS")
        risks = _extract_bullet_list(block, "RISKS")
        layers_raw = _extract_field(block, "LAYERS")
        layers_addressed = [
            layer.strip()
            for layer in layers_raw.split(",")
            if layer.strip()
        ]

        scenarios.append(
            Scenario(
                name=name,
                option_name=name,  # scenario name matches its source option
                description=description,
                implementation_steps=steps,
                key_risks=risks,
                layers_addressed=layers_addressed,
            )
        )

    return scenarios


def _extract_field(block: str, field: str) -> str:
    """Extract a single-line or short inline value for *field* from *block*.

    Stops at the next uppercase section label (e.g. STEPS:, RISKS:) or end
    of block.  Returns empty string if not found.
    """
    pattern = rf"^{field}:\s*(.+?)(?=\n[A-Z]+[^a-z]|$)"
    match = re.search(pattern, block, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def _extract_bullet_list(block: str, section: str) -> list[str]:
    """Extract a ``- item`` bullet list following the *section* label in *block*.

    Returns a list of stripped strings, one per bullet point.
    Returns ``[]`` if the section is absent or has no bullets.
    """
    # Find the section header and capture everything until the next section.
    pattern = rf"^{section}:\s*\n(.*?)(?=\n[A-Z]{{2,}}[^a-z]|\Z)"
    match = re.search(pattern, block, re.MULTILINE | re.DOTALL)
    if not match:
        return []

    raw = match.group(1)
    items = []
    for line in raw.splitlines():
        line = line.strip().lstrip("-").strip()
        if line:
            items.append(line)
    return items
