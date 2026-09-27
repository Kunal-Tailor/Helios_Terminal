"""
Trajectory-Modeling Sub-Agent — Outcome-Prediction Agent, Sub-Agent 1 of 3.

Role (ARCHITECTURE.md §3.4)
    Projects the plausible forward trajectory for each scenario in the scenario set,
    modeling where each path leads in terms of technical stack evolution,
    operational impact, and expected outcomes.

Public API
----------
    run(scenarios: list[Scenario]) -> list[Trajectory]

For each :class:`~app.agents.scenario_generation.sub_agents.scenario_refinement_sub_agent.Scenario`,
the sub-agent calls the shared LLM client to project a forward trajectory,
parses the structured response, and returns a list of :class:`Trajectory` objects.
If the LLM call fails or returns an unparseable response, it returns an empty list
(graceful degradation).

Trajectory is defined here as the canonical output type of this step.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from app.agents.scenario_generation.sub_agents.scenario_refinement_sub_agent import Scenario
from app.llm.client import call_llm_with_fallback

logger = logging.getLogger(__name__)

# Maximum number of scenarios to process in a single prompt call
_MAX_SCENARIOS_PER_CALL = 5


# ---------------------------------------------------------------------------
# Output type
# ---------------------------------------------------------------------------

@dataclass
class Trajectory:
    """Projected forward path for a single scenario.

    Attributes
    ----------
    scenario_name:
        Name of the scenario this trajectory models.
    summary:
        Narrative summary of the projected forward path.
    expected_outcomes:
        Key projected outcomes over the operational lifecycle.
    technical_impact:
        Projected impact on tech stack control, architecture, and technical debt.
    operational_impact:
        Projected impact on operational processes, team skills, and vendor reliance.
    grounded_in:
        Short direct restatement of the specific scenario/option from Scenario-Generation's
        context that this projection is about.
    """

    scenario_name: str
    summary: str
    expected_outcomes: list[str] = field(default_factory=list)
    technical_impact: str = ""
    operational_impact: str = ""
    grounded_in: str = ""


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(scenarios: list[Scenario]) -> list[Trajectory]:
    """Project forward trajectories for the given *scenarios*.

    Parameters
    ----------
    scenarios:
        List of :class:`~app.agents.scenario_generation.sub_agents.scenario_refinement_sub_agent.Scenario`
        objects produced during scenario generation.

    Returns
    -------
    list[Trajectory]
        One :class:`Trajectory` per input scenario.
        Returns ``[]`` if *scenarios* is empty or if the LLM call fails.
    """
    if not scenarios:
        return []

    prompt = _build_prompt(scenarios)
    try:
        response = call_llm_with_fallback(prompt)
        return _parse_response(response, scenarios)
    except Exception as exc:
        logger.error(
            "LLM call failed in trajectory_modeling_sub_agent (run): %s",
            exc,
            exc_info=True,
        )
        return []


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_prompt(scenarios: list[Scenario]) -> str:
    """Build the LLM prompt for trajectory modeling."""
    scenario_blocks = []
    for i, sc in enumerate(scenarios[:_MAX_SCENARIOS_PER_CALL]):
        steps_str = "\n".join(f"    - {step}" for step in sc.implementation_steps) if sc.implementation_steps else "    - Not specified"
        risks_str = "\n".join(f"    - {risk}" for risk in sc.key_risks) if sc.key_risks else "    - Not specified"
        layers_str = ", ".join(sc.layers_addressed) if sc.layers_addressed else "Not specified"

        block = (
            f"  SCENARIO {i + 1}: {sc.name}\n"
            f"  Description: {sc.description}\n"
            f"  Addressed Layers: {layers_str}\n"
            f"  Implementation Steps:\n{steps_str}\n"
            f"  Key Risks:\n{risks_str}"
        )
        scenario_blocks.append(block)

    scenarios_str = "\n\n".join(scenario_blocks)

    return f"""You are an AI sourcing decision analyst projecting the forward trajectory
of candidate sourcing scenarios over their operational lifecycle.

SCENARIOS TO MODEL
{scenarios_str}

TASK
For each scenario above, project its plausible forward trajectory over time.
Consider how the implementation steps play out, how key risks manifest, how tech stack
control evolves, and what operational changes occur.

Respond in exactly this repeating block format — one block per scenario, separated by ---:

TRAJECTORY: <exact scenario name>
GROUNDED_IN: <short direct restatement of the specific scenario/option from the SCENARIOS above that this projection is about. MUST closely echo the actual wording and terms of the source scenario above.>
SUMMARY: <2-3 sentence overview of where this scenario leads over time>
EXPECTED OUTCOMES:
- <projected outcome 1>
- <projected outcome 2>
- <add minimum 2 bullets>
TECHNICAL IMPACT: <1-2 sentences on stack architecture, control, and technical debt>
OPERATIONAL IMPACT: <1-2 sentences on team skills, vendor reliance, and processes>
---
"""


def _parse_response(response: str, scenarios: list[Scenario]) -> list[Trajectory]:
    """Parse the structured LLM response into a list of :class:`Trajectory` objects.

    Expected block format::

        TRAJECTORY: <scenario_name>
        GROUNDED_IN: <text>
        SUMMARY: <text>
        EXPECTED OUTCOMES:
        - outcome 1
        - outcome 2
        TECHNICAL IMPACT: <text>
        OPERATIONAL IMPACT: <text>
        ---
    """
    raw_blocks = re.split(r"\n---+\s*", response.strip())
    trajectories: list[Trajectory] = []

    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue

        name = _extract_field(block, "TRAJECTORY")
        if not name:
            continue

        grounded_in = _extract_field(block, "GROUNDED_IN")
        summary = _extract_field(block, "SUMMARY")
        outcomes = _extract_bullet_list(block, "EXPECTED OUTCOMES")
        tech_impact = _extract_field(block, "TECHNICAL IMPACT")
        ops_impact = _extract_field(block, "OPERATIONAL IMPACT")

        trajectories.append(
            Trajectory(
                scenario_name=name,
                summary=summary,
                expected_outcomes=outcomes,
                technical_impact=tech_impact,
                operational_impact=ops_impact,
                grounded_in=grounded_in,
            )
        )

    return trajectories


def _extract_field(block: str, field: str) -> str:
    """Extract a single-line or inline value for *field* from *block*.

    Stops at the next uppercase section label or end of block.
    """
    pattern = rf"^{field}:\s*(.+?)(?=\n[A-Z]+[^a-z]|$)"
    match = re.search(pattern, block, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def _extract_bullet_list(block: str, section: str) -> list[str]:
    """Extract bullet items following the *section* label in *block*."""
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
