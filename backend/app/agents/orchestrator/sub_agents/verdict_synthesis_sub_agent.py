"""
Verdict-Synthesis Sub-Agent — Orchestrator Agent, Sub-Agent 2 of 3.

Role (ARCHITECTURE.md §3.6)
    Synthesizes the cross-path comparison analysis and dependency diagnoses into a final
    comparative verdict text, including a primary recommended path, executive summary,
    actionable key recommendations, and path-by-path decision stances.

Public API
----------
    run(comparison, diagnoses, entity, capability) -> VerdictSynthesis

The sub-agent calls the shared LLM client to synthesize the final verdict,
parses the response, and returns a :class:`VerdictSynthesis` object.
If the LLM call fails or returns an unparseable response, it returns an empty object
(graceful degradation).

VerdictSynthesis is defined here as a canonical output type.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from app.agents.dependency_diagnosis.dependency_diagnosis_agent import DependencyDiagnosis
from app.agents.orchestrator.sub_agents.cross_path_comparison_sub_agent import CrossPathComparison
from app.llm.client import complete

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Output type
# ---------------------------------------------------------------------------

@dataclass
class VerdictSynthesis:
    """Final comparative verdict text and recommendation summary.

    Attributes
    ----------
    recommended_path:
        Name of the primary recommended scenario path.
    verdict_summary:
        Executive summary narrative of the comparative verdict.
    key_recommendations:
        Actionable recommendations for decision makers.
    path_stances:
        Decision stance per scenario path (e.g. {"Build in-house": "High risk", "License open-weight": "Recommended"}).
    """

    recommended_path: str = ""
    verdict_summary: str = ""
    key_recommendations: list[str] = field(default_factory=list)
    path_stances: dict[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(
    comparison: CrossPathComparison,
    diagnoses: list[DependencyDiagnosis],
    entity: str = "",
    capability: str = "",
) -> VerdictSynthesis:
    """Synthesize final comparative verdict text for the given *comparison* and *diagnoses*.

    Parameters
    ----------
    comparison:
        The :class:`~app.agents.orchestrator.sub_agents.cross_path_comparison_sub_agent.CrossPathComparison`
        object from the Cross-Path Comparison Sub-Agent.
    diagnoses:
        List of :class:`~app.agents.dependency_diagnosis.dependency_diagnosis_agent.DependencyDiagnosis`
        objects produced by the Dependency-Diagnosis Agent.
    entity:
        Optional entity name for context.
    capability:
        Optional capability name for context.

    Returns
    -------
    VerdictSynthesis
        Synthesized verdict with recommended path, summary, recommendations, and path stances.
        Returns empty :class:`VerdictSynthesis` if *diagnoses* and *comparison* are empty or if LLM fails.
    """
    if not diagnoses and not comparison.path_comparisons:
        return VerdictSynthesis()

    prompt = _build_prompt(comparison, diagnoses, entity, capability)
    try:
        response = complete(prompt)
        return _parse_response(response)
    except Exception as exc:
        logger.error(
            "LLM call failed in verdict_synthesis_sub_agent (run): %s",
            exc,
            exc_info=True,
        )
        return VerdictSynthesis()


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_prompt(
    comparison: CrossPathComparison,
    diagnoses: list[DependencyDiagnosis],
    entity: str,
    capability: str,
) -> str:
    """Build the LLM prompt for verdict synthesis."""
    narrative_str = comparison.comparative_narrative or "No comparative narrative available."

    path_blocks = []
    for pc in comparison.path_comparisons:
        tradeoffs_str = ", ".join(pc.key_tradeoffs) if pc.key_tradeoffs else "None listed"
        block = (
            f"  PATH: {pc.scenario_name}\n"
            f"  Lock-ins Count: {pc.lock_in_count}\n"
            f"  Max Severity: {pc.max_severity_score}/10\n"
            f"  Tradeoffs: {tradeoffs_str}\n"
            f"  Summary: {pc.path_summary}"
        )
        path_blocks.append(block)

    paths_str = "\n\n".join(path_blocks) if path_blocks else "No path comparisons available."

    return f"""You are an executive AI sourcing advisor synthesizing the final comparative verdict
for a critical AI procurement decision.

DECISION CONTEXT
Entity: {entity or "Not specified"}
Capability: {capability or "Not specified"}

CROSS-PATH COMPARISON NARRATIVE
{narrative_str}

PATH COMPARISON BREAKDOWNS
{paths_str}

TASK
Synthesize a definitive, strategic executive verdict.
1. Select the single best recommended scenario path.
2. Provide a 2-3 paragraph executive summary of the verdict.
3. List 3-4 actionable key recommendations for leadership.
4. Provide a clear decision stance for each path (e.g. Recommended, Conditional, High Risk/Avoid).

Respond in exactly this format — no extra header text:

RECOMMENDED PATH: <exact name of single recommended scenario path>
VERDICT SUMMARY:
<2-3 paragraph executive summary narrative>

RECOMMENDATIONS:
- <actionable recommendation 1>
- <actionable recommendation 2>

PATH STANCES:
- <scenario name 1>: <stance summary e.g. Recommended - best balance of control and cost>
- <scenario name 2>: <stance summary e.g. High Risk - severe hardware lock-in>
"""


def _parse_response(response: str) -> VerdictSynthesis:
    """Parse the structured LLM response into a :class:`VerdictSynthesis` object."""
    stripped = response.strip()

    rec_path = _extract_field(stripped, "RECOMMENDED PATH")

    summary_match = re.search(
        r"VERDICT SUMMARY:\s*\n(.*?)(?=\nRECOMMENDATIONS:|\Z)", stripped, re.DOTALL
    )
    verdict_summary = summary_match.group(1).strip() if summary_match else ""

    recommendations = _extract_bullet_list(stripped, "RECOMMENDATIONS")

    stances_raw = _extract_bullet_list(stripped, "PATH STANCES")
    path_stances: dict[str, str] = {}
    for item in stances_raw:
        if ":" in item:
            key, val = item.split(":", 1)
            path_stances[key.strip()] = val.strip()
        else:
            path_stances[item.strip()] = "Evaluated"

    return VerdictSynthesis(
        recommended_path=rec_path,
        verdict_summary=verdict_summary,
        key_recommendations=recommendations,
        path_stances=path_stances,
    )


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
