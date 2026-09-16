"""
Scenario-Generation Agent — parent orchestrator for the Scenario-Generation stage.

Role (ARCHITECTURE.md §3.3)
    Receives the StackScope from the Stack-Mapping Agent, orchestrates its three
    sub-agents in sequence, and returns one :class:`ScenarioSet` object containing
    the fully-specified scenarios ready for the Outcome-Prediction Agent.

Sub-agent execution order
    All three sub-agents are sequential — each depends on the previous output:

        StackScope
             │
             ▼
     Option-Enumeration (5.9)     → candidate Option list
             │
             ▼
     Feasibility-Check (5.10)     → filtered Option list (feasible only)
             │
             ▼
     Scenario-Refinement (5.11)   → fully-specified Scenario list
             │
             ▼
          ScenarioSet

Public API
----------
    run(stack_scope: StackScope) -> ScenarioSet

ScenarioSet is the canonical output type of the Scenario-Generation stage and
is defined here so the Outcome-Prediction Agent can import it from one place.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.agents.scenario_generation.sub_agents import (
    feasibility_check_sub_agent,
    option_enumeration_sub_agent,
    scenario_refinement_sub_agent,
)
from app.agents.scenario_generation.sub_agents.option_enumeration_sub_agent import Option
from app.agents.scenario_generation.sub_agents.scenario_refinement_sub_agent import Scenario
from app.agents.stack_mapping.stack_mapping_agent import StackScope


# ---------------------------------------------------------------------------
# Output type
# ---------------------------------------------------------------------------

@dataclass
class ScenarioSet:
    """The scenario-generation output for one decision brief.

    Attributes
    ----------
    entity:
        The organisation making the decision (carried through for traceability).
    capability:
        The AI capability being sourced.
    scenarios:
        Fully-specified sourcing scenarios, each refined from a feasible option.
        May be empty if all sub-agents return empty results.
    """

    entity: str
    capability: str
    scenarios: list[Scenario] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(stack_scope: StackScope) -> ScenarioSet:
    """Run the full Scenario-Generation pipeline for one decision brief.

    Parameters
    ----------
    stack_scope:
        The :class:`~app.agents.stack_mapping.stack_mapping_agent.StackScope`
        produced by the Stack-Mapping Agent.

    Returns
    -------
    ScenarioSet
        Fully-specified scenarios ready for the Outcome-Prediction Agent.
        Returns a :class:`ScenarioSet` with an empty ``scenarios`` list if
        no viable scenarios could be generated.
    """
    # Step 1 — enumerate candidate sourcing options from the stack scope.
    candidate_options: list[Option] = option_enumeration_sub_agent.run(stack_scope)

    # Step 2 — filter to feasible options given the stack scope constraints.
    feasible_options: list[Option] = feasibility_check_sub_agent.run(
        options=candidate_options,
        stack_scope=stack_scope,
    )

    # Step 3 — refine each feasible option into a fully-specified scenario.
    scenarios: list[Scenario] = scenario_refinement_sub_agent.run(
        options=feasible_options,
        stack_scope=stack_scope,
    )

    return ScenarioSet(
        entity=stack_scope.entity,
        capability=stack_scope.capability,
        scenarios=scenarios,
    )
