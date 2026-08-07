"""
Lock-in Identification Sub-Agent — Dependency-Diagnosis Agent, Sub-Agent 1 of 3.

Role (ARCHITECTURE.md §3.5)
    Identifies and names the specific technological, architectural, vendor, or data
    dependencies and lock-in points created by each predicted scenario outcome.

Public API
----------
    run(outcomes: list[OutcomeProjection]) -> list[LockInDependency]

For each :class:`~app.agents.outcome_prediction.outcome_prediction_agent.OutcomeProjection`,
the sub-agent calls the shared LLM client to diagnose specific lock-ins and dependencies,
parses the structured response, and returns a list of :class:`LockInDependency` objects.
If the LLM call fails or returns an unparseable response, it returns an empty list
(graceful degradation).

LockInDependency is defined here as the canonical output type of this step.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.agents.outcome_prediction.outcome_prediction_agent import OutcomeProjection
from app.llm.client import complete

# Maximum outcomes per LLM prompt call
_MAX_OUTCOMES_PER_CALL = 5


# ---------------------------------------------------------------------------
# Output type
# ---------------------------------------------------------------------------

@dataclass
class LockInDependency:
    """A specific dependency or lock-in created by a scenario outcome.

    Attributes
    ----------
    scenario_name:
        Name of the scenario this dependency applies to.
    dependency_name:
        Short canonical name of the dependency or lock-in point.
    layer_name:
        The specific stack layer implicated (e.g. "Model Weights", "Hardware").
    lock_in_type:
        Category of lock-in (e.g. "Vendor Lock-in", "Architectural Entanglement", "Data Lock-in").
    description:
        Explanation of how this dependency is created and maintained.
    """

    scenario_name: str
    dependency_name: str
    layer_name: str = ""
    lock_in_type: str = ""
    description: str = ""


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(outcomes: list[OutcomeProjection]) -> list[LockInDependency]:
    """Diagnose specific lock-ins and dependencies for projected *outcomes*.

    Parameters
    ----------
    outcomes:
        List of :class:`~app.agents.outcome_prediction.outcome_prediction_agent.OutcomeProjection`
        objects produced by the Outcome-Prediction Agent.

    Returns
    -------
    list[LockInDependency]
        Diagnosed dependencies and lock-in points across all input outcomes.
        Returns ``[]`` if *outcomes* is empty or if the LLM call fails.
    """
    if not outcomes:
        return []

    prompt = _build_prompt(outcomes)
    try:
        response = complete(prompt)
        return _parse_response(response, outcomes)
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_prompt(outcomes: list[OutcomeProjection]) -> str:
    """Build the LLM prompt for lock-in identification."""
    outcome_blocks = []
    for i, out in enumerate(outcomes[:_MAX_OUTCOMES_PER_CALL]):
        tr_summary = out.trajectory.summary if out.trajectory else "Not specified"
        tech_impact = out.trajectory.technical_impact if out.trajectory else "Not specified"
        ops_impact = out.trajectory.operational_impact if out.trajectory else "Not specified"

        risks_str = (
            "\n".join(f"    - {r.factor_name}: {r.description}" for r in out.risk_factors)
            if out.risk_factors
            else "    - None listed"
        )

        block = (
            f"  OUTCOME {i + 1}: {out.scenario_name}\n"
            f"  Trajectory Summary: {tr_summary}\n"
            f"  Technical Impact: {tech_impact}\n"
            f"  Operational Impact: {ops_impact}\n"
            f"  Risk Factors:\n{risks_str}"
        )
        outcome_blocks.append(block)

    outcomes_str = "\n\n".join(outcome_blocks)

    return f"""You are an AI technology dependency & lock-in diagnostic analyst.
Analyze the predicted outcomes below and identify the specific technological, vendor,
architectural, or data lock-ins created by each path.

PREDICTED SCENARIO OUTCOMES
{outcomes_str}

TASK
For each outcome, identify 1-3 specific lock-in points or critical dependencies that the entity
will acquire if it pursues this path. Specify the implicated stack layer and category of lock-in.

Respond in exactly this repeating block format — one block per lock-in point, separated by ---:

LOCK_IN: <short canonical dependency/lock-in name>
SCENARIO: <exact scenario name>
LAYER: <implicated stack layer, e.g. Model Weights, Inference Infra, Training Data>
TYPE: <Vendor Lock-in, Architectural Entanglement, Data Lock-in, or Skill Set Lock-in>
DESCRIPTION: <1-2 sentences explaining how this dependency is created by the outcome>
---
"""


def _parse_response(response: str, outcomes: list[OutcomeProjection]) -> list[LockInDependency]:
    """Parse the structured LLM response into a list of :class:`LockInDependency` objects."""
    raw_blocks = re.split(r"\n---+\s*", response.strip())
    dependencies: list[LockInDependency] = []

    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue

        dep_name = _extract_field(block, "LOCK_IN")
        scenario_name = _extract_field(block, "SCENARIO")
        if not dep_name or not scenario_name:
            continue

        layer_name = _extract_field(block, "LAYER")
        lock_in_type = _extract_field(block, "TYPE")
        description = _extract_field(block, "DESCRIPTION")

        dependencies.append(
            LockInDependency(
                scenario_name=scenario_name,
                dependency_name=dep_name,
                layer_name=layer_name,
                lock_in_type=lock_in_type,
                description=description,
            )
        )

    return dependencies


def _extract_field(block: str, field: str) -> str:
    """Extract a single-line or inline value for *field* from *block*."""
    pattern = rf"^{field}:\s*(.+?)(?=\n[A-Z]+[^a-z]|$)"
    match = re.search(pattern, block, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""
