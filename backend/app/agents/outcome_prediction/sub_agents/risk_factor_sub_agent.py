"""
Risk-Factor Sub-Agent — Outcome-Prediction Agent, Sub-Agent 2 of 3.

Role (ARCHITECTURE.md §3.4)
    Identifies specific events, external conditions, or technical triggers
    that could alter or disrupt the projected forward trajectory of each scenario.

Public API
----------
    run(trajectories, scenarios) -> list[RiskFactor]

For each :class:`~app.agents.outcome_prediction.sub_agents.trajectory_modeling_sub_agent.Trajectory`,
the sub-agent calls the shared LLM client to identify critical risk factors that could alter
that trajectory, parses the structured response, and returns a list of :class:`RiskFactor` objects.
If the LLM call fails or returns an unparseable response, it returns an empty list
(graceful degradation).

RiskFactor is defined here as the canonical output type of this step.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from app.agents.outcome_prediction.sub_agents.trajectory_modeling_sub_agent import Trajectory
from app.agents.scenario_generation.sub_agents.scenario_refinement_sub_agent import Scenario
from app.llm.client import complete

logger = logging.getLogger(__name__)

# Maximum trajectories per LLM prompt call
_MAX_TRAJECTORIES_PER_CALL = 5


# ---------------------------------------------------------------------------
# Output type
# ---------------------------------------------------------------------------

@dataclass
class RiskFactor:
    """An event or condition that could alter a scenario's projected trajectory.

    Attributes
    ----------
    scenario_name:
        Name of the scenario this risk factor applies to.
    factor_name:
        Short title of the risk event or condition.
    description:
        Explanation of how this risk factor alters the projected trajectory.
    likelihood:
        Estimated likelihood (e.g. "High", "Medium", "Low").
    impact_severity:
        Estimated severity if triggered (e.g. "High", "Medium", "Low").
    mitigation_strategy:
        Potential action or safeguard to mitigate this risk factor.
    """

    scenario_name: str
    factor_name: str
    description: str
    likelihood: str = "Medium"
    impact_severity: str = "Medium"
    mitigation_strategy: str = ""


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(
    trajectories: list[Trajectory],
    scenarios: list[Scenario] | None = None,
) -> list[RiskFactor]:
    """Identify key risk factors that could alter projected *trajectories*.

    Parameters
    ----------
    trajectories:
        List of :class:`~app.agents.outcome_prediction.sub_agents.trajectory_modeling_sub_agent.Trajectory`
        objects produced by the Trajectory-Modeling Sub-Agent.
    scenarios:
        Optional list of :class:`~app.agents.scenario_generation.sub_agents.scenario_refinement_sub_agent.Scenario`
        objects for additional context on implementation steps and key risks.

    Returns
    -------
    list[RiskFactor]
        Risk factors for the input trajectories.
        Returns ``[]`` if *trajectories* is empty or if the LLM call fails.
    """
    if not trajectories:
        return []

    prompt = _build_prompt(trajectories, scenarios or [])
    try:
        response = complete(prompt)
        return _parse_response(response, trajectories)
    except Exception as exc:
        logger.error(
            "LLM call failed in risk_factor_sub_agent (run): %s",
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
    """Build the LLM prompt for risk factor identification."""
    scenario_map = {sc.name: sc for sc in scenarios}

    traj_blocks = []
    for i, tr in enumerate(trajectories[:_MAX_TRAJECTORIES_PER_CALL]):
        outcomes_str = "\n".join(f"    - {out}" for out in tr.expected_outcomes) if tr.expected_outcomes else "    - Not specified"

        sc = scenario_map.get(tr.scenario_name)
        known_risks_str = (
            "\n".join(f"    - {r}" for r in sc.key_risks)
            if sc and sc.key_risks
            else "    - None listed"
        )

        block = (
            f"  TRAJECTORY {i + 1}: {tr.scenario_name}\n"
            f"  Summary: {tr.summary}\n"
            f"  Technical Impact: {tr.technical_impact}\n"
            f"  Operational Impact: {tr.operational_impact}\n"
            f"  Expected Outcomes:\n{outcomes_str}\n"
            f"  Scenario Known Risks:\n{known_risks_str}"
        )
        traj_blocks.append(block)

    trajectories_str = "\n\n".join(traj_blocks)

    return f"""You are an AI sourcing decision risk analyst. Identify specific external events,
regulatory shifts, technical failures, or vendor changes that could alter or derail
the projected forward trajectory of each scenario.

PROJECTED TRAJECTORIES
{trajectories_str}

TASK
For each trajectory above, identify 2-3 specific risk factors (events or conditions) that could
alter the trajectory, estimate their likelihood and impact severity, and suggest a mitigation strategy.

Respond in exactly this repeating block format — one block per risk factor, separated by ---:

RISK FACTOR: <short title of the risk event/condition>
SCENARIO: <exact scenario name>
DESCRIPTION: <1-2 sentences explaining how this risk alters or disrupts the trajectory>
LIKELIHOOD: <High, Medium, or Low>
SEVERITY: <High, Medium, or Low>
MITIGATION: <1 sentence suggesting a practical mitigation safeguard>
---
"""


def _parse_response(response: str, trajectories: list[Trajectory]) -> list[RiskFactor]:
    """Parse the structured LLM response into a list of :class:`RiskFactor` objects."""
    raw_blocks = re.split(r"\n---+\s*", response.strip())
    risk_factors: list[RiskFactor] = []

    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue

        factor_name = _extract_field(block, "RISK FACTOR")
        scenario_name = _extract_field(block, "SCENARIO")
        if not factor_name or not scenario_name:
            continue

        description = _extract_field(block, "DESCRIPTION")
        likelihood = _extract_field(block, "LIKELIHOOD") or "Medium"
        severity = _extract_field(block, "SEVERITY") or "Medium"
        mitigation = _extract_field(block, "MITIGATION")

        risk_factors.append(
            RiskFactor(
                scenario_name=scenario_name,
                factor_name=factor_name,
                description=description,
                likelihood=likelihood,
                impact_severity=severity,
                mitigation_strategy=mitigation,
            )
        )

    return risk_factors


def _extract_field(block: str, field: str) -> str:
    """Extract a single-line or inline value for *field* from *block*."""
    pattern = rf"^{field}:\s*(.+?)(?=\n[A-Z]+[^a-z]|$)"
    match = re.search(pattern, block, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""
