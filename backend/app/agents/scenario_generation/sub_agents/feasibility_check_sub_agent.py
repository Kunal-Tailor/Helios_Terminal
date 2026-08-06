"""
Feasibility-Check Sub-Agent — Scenario-Generation Agent, Sub-Agent 2 of 3.

Role (ARCHITECTURE.md §3.3)
    Filters the raw candidate options from the Option-Enumeration Sub-Agent (5.9)
    to remove unrealistic or infeasible options, keeping only those that are
    practically achievable given the entity's context and constraints.

    Feasibility factors include: technical capability, resource availability,
    regulatory compliance, timeline constraints, and strategic alignment.

Public API
----------
    run(options: list[Option], stack_scope: StackScope) -> list[Option]

The sub-agent calls the shared LLM client with a structured prompt built from
the candidate options and StackScope, evaluates each option for feasibility,
and returns only the options that pass the feasibility check. If the LLM call
fails or returns an unparseable response, it returns the original list
(graceful degradation — better to keep options than lose them all).

The Option type is imported from option_enumeration_sub_agent (5.9).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.agents.scenario_generation.sub_agents.option_enumeration_sub_agent import Option
from app.agents.stack_mapping.stack_mapping_agent import StackScope
from app.llm.client import complete


# ---------------------------------------------------------------------------
# Output type
# ---------------------------------------------------------------------------

@dataclass
class FeasibilityResult:
    """Feasibility assessment for a single option.

    Attributes
    ----------
    option:
        The original Option being evaluated.
    is_feasible:
        Whether the option is practically achievable (True/False).
    reason:
        Brief explanation of why it is feasible or why it fails.
    """

    option: Option
    is_feasible: bool
    reason: str = ""


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(options: list[Option], stack_scope: StackScope) -> list[Option]:
    """Filter *options* to keep only feasible ones given *stack_scope*.

    Parameters
    ----------
    options:
        Candidate :class:`Option` objects from the Option-Enumeration
        Sub-Agent (5.9).
    stack_scope:
        The :class:`~app.agents.stack_mapping.stack_mapping_agent.StackScope`
        for this decision, used to ground feasibility reasoning.

    Returns
    -------
    list[Option]
        Options that pass the feasibility check, in their original order.
        Returns the original *options* list if the LLM call fails or the
        response cannot be parsed (graceful degradation).
    """
    if not options:
        return []

    prompt = _build_prompt(options, stack_scope)
    try:
        response = complete(prompt)
        results = _parse_response(response, options)
        # If parsing returned no results, treat as parse failure and return all options.
        if not results:
            return options
        # Return only feasible options, preserving original order.
        feasible = [r.option for r in results if r.is_feasible]
        # If all options were deemed infeasible, still return them (better to keep options than lose all).
        return feasible if feasible else options
    except Exception:
        # Graceful degradation: return all options if LLM fails.
        return options


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_prompt(options: list[Option], stack_scope: StackScope) -> str:
    """Build the LLM feasibility-check prompt."""
    options_str = "\n".join(
        f"{i+1}. {opt.name}\n   Description: {opt.description}\n   Rationale: {opt.rationale}"
        for i, opt in enumerate(options)
    )

    layers_str = "\n".join(
        f"- {layer.name}: {layer.rationale}"
        for layer in stack_scope.layers
    ) if stack_scope.layers else "No stack layers identified."

    return f"""You are an AI sourcing analyst evaluating the feasibility of candidate
sourcing options for a specific AI procurement decision.

DECISION BRIEF
Entity: {stack_scope.entity}
Capability sought: {stack_scope.capability}

STACK SCOPE — Identified Layers
{layers_str}

CANDIDATE OPTIONS (from option enumeration)
{options_str}

TASK
Evaluate each candidate option for practical feasibility given the entity's
context, the identified stack layers, and realistic constraints.

Feasibility factors to consider:
- Technical capability: Does the entity have or can it acquire the required expertise?
- Resource availability: Budget, talent, infrastructure, and time constraints.
- Regulatory compliance: Legal, licensing, and data governance requirements.
- Strategic alignment: Fit with the entity's long-term goals and risk tolerance.
- Vendor landscape: Are viable vendors/partners available for the option?

For each option, decide if it is FEASIBLE or NOT FEASIBLE and provide a brief reason.

Respond in exactly this repeating block format — one block per option, separated by ---:

OPTION: <exact option name from the list above>
FEASIBLE: <YES or NO>
REASON: <1-2 sentences explaining the feasibility decision>
---
OPTION: <next option name>
FEASIBLE: <YES or NO>
REASON: <reason>
---
"""


def _parse_response(response: str, options: list[Option]) -> list[FeasibilityResult]:
    """Parse the structured LLM response into a list of :class:`FeasibilityResult` objects.

    Expected block format::

        OPTION: <name>
        FEASIBLE: <YES or NO>
        REASON: <text>
        ---

    Blocks that reference option names not in the original list are skipped.
    If no blocks are found, returns an empty list (which triggers graceful degradation).
    """
    # Build a mapping from option name to Option object for lookup.
    option_map = {opt.name: opt for opt in options}

    raw_blocks = re.split(r"\n---+\s*", response.strip())
    results: list[FeasibilityResult] = []

    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue

        name = _extract_field(block, "OPTION")
        if not name or name not in option_map:
            continue  # skip unknown or malformed blocks

        feasible_str = _extract_field(block, "FEASIBLE")
        is_feasible = feasible_str.upper() == "YES"
        reason = _extract_field(block, "REASON")

        results.append(
            FeasibilityResult(
                option=option_map[name],
                is_feasible=is_feasible,
                reason=reason,
            )
        )

    return results


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
