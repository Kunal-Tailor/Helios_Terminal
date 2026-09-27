"""
Timeline-Projection Sub-Agent — Outcome-Prediction Agent, Sub-Agent 3 of 3 (optional).

Role (ARCHITECTURE.md §3.4)
    Attaches time horizons (short-term, medium-term, long-term) and chronological
    milestones to each projected outcome trajectory.

Public API
----------
    run(trajectories, scenarios) -> list[TimelineProjection]

For each :class:`~app.agents.outcome_prediction.sub_agents.trajectory_modeling_sub_agent.Trajectory`,
the sub-agent calls the shared LLM client to project time horizons and milestones,
parses the structured response, and returns a list of :class:`TimelineProjection` objects.
If the LLM call fails or returns an unparseable response, it returns an empty list
(graceful degradation).

TimelineProjection is defined here as the canonical output type of this step.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from app.agents.outcome_prediction.sub_agents.trajectory_modeling_sub_agent import Trajectory
from app.agents.scenario_generation.sub_agents.scenario_refinement_sub_agent import Scenario
from app.llm.client import call_llm_with_fallback

logger = logging.getLogger(__name__)

# Maximum trajectories per LLM prompt call
_MAX_TRAJECTORIES_PER_CALL = 5


# ---------------------------------------------------------------------------
# Output type
# ---------------------------------------------------------------------------

@dataclass
class TimelineProjection:
    """Time-horizon projections and milestones for a scenario trajectory.

    Attributes
    ----------
    scenario_name:
        Name of the scenario this timeline projection applies to.
    short_term:
        0–6 months projection (initial rollout, setup, onboarding).
    medium_term:
        6–18 months projection (stabilisation, integration, initial costs/benefits).
    long_term:
        18+ months projection (steady state, technical debt accumulation, lock-in manifestation).
    milestones:
        Key chronological milestones or critical decision gates.
    """

    scenario_name: str
    short_term: str = ""
    medium_term: str = ""
    long_term: str = ""
    milestones: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(
    trajectories: list[Trajectory],
    scenarios: list[Scenario] | None = None,
) -> list[TimelineProjection]:
    """Project time horizons and milestones for projected *trajectories*.

    Parameters
    ----------
    trajectories:
        List of :class:`~app.agents.outcome_prediction.sub_agents.trajectory_modeling_sub_agent.Trajectory`
        objects produced by the Trajectory-Modeling Sub-Agent.
    scenarios:
        Optional list of :class:`~app.agents.scenario_generation.sub_agents.scenario_refinement_sub_agent.Scenario`
        objects for additional context.

    Returns
    -------
    list[TimelineProjection]
        Timeline projections for the input trajectories.
        Returns ``[]`` if *trajectories* is empty or if the LLM call fails.
    """
    if not trajectories:
        return []

    prompt = _build_prompt(trajectories, scenarios or [])
    try:
        response = call_llm_with_fallback(prompt)
        return _parse_response(response, trajectories)
    except Exception as exc:
        logger.error(
            "LLM call failed in timeline_projection_sub_agent (run): %s",
            exc,
            exc_info=True,
        )
        return []


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_prompt(
    trajectories: list[Trajectory],
    scenarios: list[Scenario],
) -> str:
    """Build the LLM prompt for timeline projection."""
    scenario_map = {sc.name: sc for sc in scenarios}

    traj_blocks = []
    for i, tr in enumerate(trajectories[:_MAX_TRAJECTORIES_PER_CALL]):
        outcomes_str = "\n".join(f"    - {out}" for out in tr.expected_outcomes) if tr.expected_outcomes else "    - Not specified"

        sc = scenario_map.get(tr.scenario_name)
        steps_str = (
            "\n".join(f"    - {s}" for s in sc.implementation_steps)
            if sc and sc.implementation_steps
            else "    - None listed"
        )

        block = (
            f"  TRAJECTORY {i + 1}: {tr.scenario_name}\n"
            f"  Summary: {tr.summary}\n"
            f"  Technical Impact: {tr.technical_impact}\n"
            f"  Operational Impact: {tr.operational_impact}\n"
            f"  Expected Outcomes:\n{outcomes_str}\n"
            f"  Implementation Steps:\n{steps_str}"
        )
        traj_blocks.append(block)

    trajectories_str = "\n\n".join(traj_blocks)

    return f"""You are an AI sourcing timeline analyst. Project the chronological timeline
and key milestones for each scenario over short-term (0-6 months), medium-term (6-18 months),
and long-term (18+ months) horizons.

PROJECTED TRAJECTORIES
{trajectories_str}

TASK
For each trajectory above, break down the expected timeline into short-term, medium-term,
and long-term projections, and list 3-4 chronological milestones.

Respond in exactly this repeating block format — one block per trajectory, separated by ---:

SCENARIO: <exact scenario name>
SHORT_TERM: <1-2 sentences on months 0-6: setup, initial deployment, and quick wins>
MEDIUM_TERM: <1-2 sentences on months 6-18: operational integration, scaling, and cost realization>
LONG_TERM: <1-2 sentences on months 18+: steady state, maintenance, and long-term impact>
MILESTONES:
- <milestone 1: month 1-3>
- <milestone 2: month 6>
- <milestone 3: month 12-18>
- <add minimum 3 bullets>
---
"""


def _parse_response(response: str, trajectories: list[Trajectory]) -> list[TimelineProjection]:
    """Parse the structured LLM response into a list of :class:`TimelineProjection` objects."""
    raw_blocks = re.split(r"\n---+\s*", response.strip())
    projections: list[TimelineProjection] = []

    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue

        scenario_name = _extract_field(block, "SCENARIO")
        if not scenario_name:
            continue

        short_term = _extract_field(block, "SHORT_TERM")
        medium_term = _extract_field(block, "MEDIUM_TERM")
        long_term = _extract_field(block, "LONG_TERM")
        milestones = _extract_bullet_list(block, "MILESTONES")

        projections.append(
            TimelineProjection(
                scenario_name=scenario_name,
                short_term=short_term,
                medium_term=medium_term,
                long_term=long_term,
                milestones=milestones,
            )
        )

    return projections


def _extract_field(block: str, field: str) -> str:
    """Extract a single-line or inline value for *field* from *block*."""
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
