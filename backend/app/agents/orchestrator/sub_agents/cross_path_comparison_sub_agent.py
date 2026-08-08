"""
Cross-Path Comparison Sub-Agent — Orchestrator Agent, Sub-Agent 1 of 3.

Role (ARCHITECTURE.md §3.6)
    Compares the dependency diagnoses across all candidate scenario paths side by side,
    highlighting key tradeoffs, lock-in counts, maximum severity ratings, and relative risk profiles.

Public API
----------
    run(diagnoses: list[DependencyDiagnosis]) -> CrossPathComparison

For the input :class:`~app.agents.dependency_diagnosis.dependency_diagnosis_agent.DependencyDiagnosis` objects,
the sub-agent calls the shared LLM client to perform a side-by-side comparison,
parses the response, and returns a :class:`CrossPathComparison` object.
If the LLM call fails or returns an unparseable response, it returns an empty object
(graceful degradation).

CrossPathComparison and PathComparison are defined here as canonical output types.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from app.agents.dependency_diagnosis.dependency_diagnosis_agent import DependencyDiagnosis
from app.llm.client import complete

logger = logging.getLogger(__name__)

# Maximum diagnoses to compare in a single prompt call
_MAX_DIAGNOSES_PER_CALL = 5


# ---------------------------------------------------------------------------
# Output types
# ---------------------------------------------------------------------------

@dataclass
class PathComparison:
    """Side-by-side comparative summary for a single scenario path.

    Attributes
    ----------
    scenario_name:
        Name of the scenario path.
    lock_in_count:
        Number of identified dependencies or lock-in points for this path.
    max_severity_score:
        Highest severity score assigned to any dependency in this path.
    key_tradeoffs:
        Key tradeoffs of choosing this path over others.
    path_summary:
        Brief narrative comparing this path's risk profile against other options.
    """

    scenario_name: str
    lock_in_count: int = 0
    max_severity_score: float = 0.0
    key_tradeoffs: list[str] = field(default_factory=list)
    path_summary: str = ""


@dataclass
class CrossPathComparison:
    """Cross-path comparison results comparing all scenario paths side by side.

    Attributes
    ----------
    comparative_narrative:
        Overall narrative analysis comparing all paths side by side.
    path_comparisons:
        Per-path comparative breakdowns.
    """

    comparative_narrative: str = ""
    path_comparisons: list[PathComparison] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(diagnoses: list[DependencyDiagnosis]) -> CrossPathComparison:
    """Compare dependency diagnoses across all scenario paths side by side.

    Parameters
    ----------
    diagnoses:
        List of :class:`~app.agents.dependency_diagnosis.dependency_diagnosis_agent.DependencyDiagnosis`
        objects produced by the Dependency-Diagnosis Agent.

    Returns
    -------
    CrossPathComparison
        Side-by-side comparison matrix and narrative.
        Returns empty :class:`CrossPathComparison` if *diagnoses* is empty or if the LLM call fails.
    """
    if not diagnoses:
        return CrossPathComparison()

    prompt = _build_prompt(diagnoses)
    try:
        response = complete(prompt)
        return _parse_response(response, diagnoses)
    except Exception as exc:
        logger.error(
            "LLM call failed in cross_path_comparison_sub_agent (run): %s",
            exc,
            exc_info=True,
        )
        return CrossPathComparison()


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_prompt(diagnoses: list[DependencyDiagnosis]) -> str:
    """Build the LLM prompt for cross-path comparison."""
    diag_blocks = []
    for i, diag in enumerate(diagnoses[:_MAX_DIAGNOSES_PER_CALL]):
        deps_str = (
            "\n".join(f"    - [{dep.lock_in_type}] {dep.dependency_name}: {dep.description}" for dep in diag.dependencies)
            if diag.dependencies
            else "    - None identified"
        )

        scores_str = (
            "\n".join(f"    - {s.dependency_name}: Severity {s.severity_score}/10, Urgency {s.urgency_score}/10 ({s.risk_level})" for s in diag.severity_scores)
            if diag.severity_scores
            else "    - None scored"
        )

        fms_str = (
            "\n".join(f"    - {fm.failure_mode_title}: {fm.what_breaks}" for fm in diag.failure_modes)
            if diag.failure_modes
            else "    - None listed"
        )

        block = (
            f"  PATH {i + 1}: {diag.scenario_name}\n"
            f"  Identified Dependencies:\n{deps_str}\n"
            f"  Severity Ratings:\n{scores_str}\n"
            f"  Projected Failure Modes:\n{fms_str}"
        )
        diag_blocks.append(block)

    diagnoses_str = "\n\n".join(diag_blocks)

    return f"""You are a strategic AI sourcing advisor performing a side-by-side comparative analysis
of candidate scenario paths and their diagnosed dependency risks.

DIAGNOSED SCENARIO PATHS
{diagnoses_str}

TASK
1. Provide an overall side-by-side comparative analysis comparing all paths in terms of lock-in risks,
   tradeoffs, and long-term strategic viability.
2. Provide a structured comparison block for each path highlighting lock-in counts, maximum severity,
   key tradeoffs, and a comparative summary.

Respond in exactly this format — start with OVERALL ANALYSIS, followed by PATH COMPARISON blocks separated by ---:

OVERALL ANALYSIS:
<2-3 paragraph comparative analysis comparing all paths side by side>

---
PATH COMPARISON: <exact scenario name>
LOCK_IN_COUNT: <number of lock-ins>
MAX_SEVERITY: <highest severity score e.g. 8.5>
TRADEOFFS:
- <key tradeoff 1>
- <key tradeoff 2>
PATH_SUMMARY: <1-2 sentences comparing this path's risk profile against other options>
---
"""


def _parse_response(
    response: str,
    diagnoses: list[DependencyDiagnosis],
) -> CrossPathComparison:
    """Parse the structured LLM response into a :class:`CrossPathComparison` object."""
    stripped = response.strip()

    # Extract overall comparative narrative
    narrative_match = re.search(
        r"OVERALL ANALYSIS:\s*\n(.*?)(?=\n---+|\nPATH COMPARISON:|\Z)", stripped, re.DOTALL
    )
    comparative_narrative = narrative_match.group(1).strip() if narrative_match else ""

    raw_blocks = re.split(r"\n---+\s*", stripped)
    path_comparisons: list[PathComparison] = []

    for block in raw_blocks:
        block = block.strip()
        if not block or "OVERALL ANALYSIS:" in block and "PATH COMPARISON:" not in block:
            continue

        name = _extract_field(block, "PATH COMPARISON")
        if not name:
            continue

        count_raw = _extract_field(block, "LOCK_IN_COUNT")
        sev_raw = _extract_field(block, "MAX_SEVERITY")
        tradeoffs = _extract_bullet_list(block, "TRADEOFFS")
        summary = _extract_field(block, "PATH_SUMMARY")

        try:
            lock_in_count = int(re.findall(r"\d+", count_raw)[0]) if count_raw else 0
        except (IndexError, ValueError):
            lock_in_count = 0

        try:
            max_severity = float(re.findall(r"\d+(?:\.\d+)?", sev_raw)[0]) if sev_raw else 0.0
        except (IndexError, ValueError):
            max_severity = 0.0

        path_comparisons.append(
            PathComparison(
                scenario_name=name,
                lock_in_count=lock_in_count,
                max_severity_score=max_severity,
                key_tradeoffs=tradeoffs,
                path_summary=summary,
            )
        )

    return CrossPathComparison(
        comparative_narrative=comparative_narrative,
        path_comparisons=path_comparisons,
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
