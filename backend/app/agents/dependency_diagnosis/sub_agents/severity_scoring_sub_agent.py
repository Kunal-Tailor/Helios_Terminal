"""
Severity-Scoring Sub-Agent — Dependency-Diagnosis Agent, Sub-Agent 3 of 3 (optional).

Role (ARCHITECTURE.md §3.5)
    Evaluates and assigns quantitative severity and urgency scores to each diagnosed
    dependency or lock-in point, helping decision-makers prioritize risks.

Public API
----------
    run(dependencies, failure_modes) -> list[DependencySeverityScore]

For each :class:`~app.agents.dependency_diagnosis.sub_agents.lock_in_identification_sub_agent.LockInDependency`,
the sub-agent calls the shared LLM client to score severity and urgency, parses the structured response,
and returns a list of :class:`DependencySeverityScore` objects.
If the LLM call fails or returns an unparseable response, it returns an empty list
(graceful degradation).

DependencySeverityScore is defined here as the canonical output type of this step.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.agents.dependency_diagnosis.sub_agents.failure_mode_sub_agent import FailureMode
from app.agents.dependency_diagnosis.sub_agents.lock_in_identification_sub_agent import LockInDependency
from app.llm.client import complete

# Maximum dependencies per LLM prompt call
_MAX_DEPENDENCIES_PER_CALL = 5


# ---------------------------------------------------------------------------
# Output type
# ---------------------------------------------------------------------------

@dataclass
class DependencySeverityScore:
    """Quantitative severity and urgency evaluation for a lock-in dependency.

    Attributes
    ----------
    scenario_name:
        Name of the scenario this dependency applies to.
    dependency_name:
        Name of the evaluated dependency or lock-in point.
    severity_score:
        Severity rating on a scale of 1.0 (minimal impact) to 10.0 (catastrophic).
    urgency_score:
        Urgency rating on a scale of 1.0 (long-term/deferrable) to 10.0 (immediate action needed).
    risk_level:
        Overall qualitative risk level (e.g. "Critical", "High", "Medium", "Low").
    rationale:
        Explanation of why these scores and risk level were assigned.
    """

    scenario_name: str
    dependency_name: str
    severity_score: float = 5.0
    urgency_score: float = 5.0
    risk_level: str = "Medium"
    rationale: str = ""


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(
    dependencies: list[LockInDependency],
    failure_modes: list[FailureMode] | None = None,
) -> list[DependencySeverityScore]:
    """Assign quantitative severity and urgency scores to *dependencies*.

    Parameters
    ----------
    dependencies:
        List of :class:`~app.agents.dependency_diagnosis.sub_agents.lock_in_identification_sub_agent.LockInDependency`
        objects produced by the Lock-in Identification Sub-Agent.
    failure_modes:
        Optional list of :class:`~app.agents.dependency_diagnosis.sub_agents.failure_mode_sub_agent.FailureMode`
        objects for broader context on failure consequences.

    Returns
    -------
    list[DependencySeverityScore]
        Scored dependencies with severity, urgency, risk level, and rationale.
        Returns ``[]`` if *dependencies* is empty or if the LLM call fails.
    """
    if not dependencies:
        return []

    prompt = _build_prompt(dependencies, failure_modes or [])
    try:
        response = complete(prompt)
        return _parse_response(response, dependencies)
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_prompt(
    dependencies: list[LockInDependency],
    failure_modes: list[FailureMode],
) -> str:
    """Build the LLM prompt for severity and urgency scoring."""
    fm_map: dict[str, list[FailureMode]] = {}
    for fm in failure_modes:
        fm_map.setdefault(fm.dependency_name.lower(), []).append(fm)

    dep_blocks = []
    for i, dep in enumerate(dependencies[:_MAX_DEPENDENCIES_PER_CALL]):
        fms = fm_map.get(dep.dependency_name.lower(), [])
        fms_str = (
            "\n".join(f"    - {fm.failure_mode_title}: {fm.what_breaks}" for fm in fms)
            if fms
            else "    - None listed"
        )

        block = (
            f"  DEPENDENCY {i + 1}: {dep.dependency_name}\n"
            f"  Scenario: {dep.scenario_name}\n"
            f"  Implicated Layer: {dep.layer_name}\n"
            f"  Lock-in Type: {dep.lock_in_type}\n"
            f"  Description: {dep.description}\n"
            f"  Associated Failure Modes:\n{fms_str}"
        )
        dep_blocks.append(block)

    deps_str = "\n\n".join(dep_blocks)

    return f"""You are an AI technology risk scoring analyst. Score each dependency/lock-in
point on severity (impact magnitude) and urgency (time sensitivity), on a 1.0 to 10.0 scale.

IDENTIFIED DEPENDENCIES & FAILURE MODES
{deps_str}

TASK
For each dependency above, assign a severity score (1.0 - 10.0), an urgency score (1.0 - 10.0),
an overall risk level (Critical, High, Medium, or Low), and a 1-sentence rationale.

Respond in exactly this repeating block format — one block per dependency, separated by ---:

DEPENDENCY: <exact dependency name>
SCENARIO: <exact scenario name>
SEVERITY_SCORE: <numeric value between 1.0 and 10.0>
URGENCY_SCORE: <numeric value between 1.0 and 10.0>
RISK_LEVEL: <Critical, High, Medium, or Low>
RATIONALE: <1 sentence explaining why these ratings were assigned>
---
"""


def _parse_response(
    response: str,
    dependencies: list[LockInDependency],
) -> list[DependencySeverityScore]:
    """Parse the structured LLM response into a list of :class:`DependencySeverityScore` objects."""
    raw_blocks = re.split(r"\n---+\s*", response.strip())
    scores: list[DependencySeverityScore] = []

    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue

        dep_name = _extract_field(block, "DEPENDENCY")
        scenario_name = _extract_field(block, "SCENARIO")
        if not dep_name or not scenario_name:
            continue

        sev_raw = _extract_field(block, "SEVERITY_SCORE")
        urg_raw = _extract_field(block, "URGENCY_SCORE")
        risk_level = _extract_field(block, "RISK_LEVEL") or "Medium"
        rationale = _extract_field(block, "RATIONALE")

        try:
            sev_score = float(re.findall(r"\d+(?:\.\d+)?", sev_raw)[0]) if sev_raw else 5.0
        except (IndexError, ValueError):
            sev_score = 5.0

        try:
            urg_score = float(re.findall(r"\d+(?:\.\d+)?", urg_raw)[0]) if urg_raw else 5.0
        except (IndexError, ValueError):
            urg_score = 5.0

        scores.append(
            DependencySeverityScore(
                scenario_name=scenario_name,
                dependency_name=dep_name,
                severity_score=sev_score,
                urgency_score=urg_score,
                risk_level=risk_level,
                rationale=rationale,
            )
        )

    return scores


def _extract_field(block: str, field: str) -> str:
    """Extract a single-line or inline value for *field* from *block*."""
    pattern = rf"^{field}:\s*(.+?)(?=\n[A-Z]+[^a-z]|$)"
    match = re.search(pattern, block, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""
