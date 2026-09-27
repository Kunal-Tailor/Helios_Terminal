"""
Failure-Mode Sub-Agent — Dependency-Diagnosis Agent, Sub-Agent 2 of 3.

Role (ARCHITECTURE.md §3.5)
    Explains what breaks later if each identified dependency or lock-in point
    is left unmanaged over the scenario's lifecycle.

Public API
----------
    run(dependencies, outcomes) -> list[FailureMode]

For each :class:`~app.agents.dependency_diagnosis.sub_agents.lock_in_identification_sub_agent.LockInDependency`,
the sub-agent calls the shared LLM client to project failure modes, parses the structured response,
and returns a list of :class:`FailureMode` objects.
If the LLM call fails or returns an unparseable response, it returns an empty list
(graceful degradation).

FailureMode is defined here as the canonical output type of this step.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from app.agents.dependency_diagnosis.sub_agents.lock_in_identification_sub_agent import LockInDependency
from app.agents.outcome_prediction.outcome_prediction_agent import OutcomeProjection
from app.llm.client import call_llm_with_fallback

logger = logging.getLogger(__name__)

# Maximum dependencies per LLM prompt call
_MAX_DEPENDENCIES_PER_CALL = 5


# ---------------------------------------------------------------------------
# Output type
# ---------------------------------------------------------------------------

@dataclass
class FailureMode:
    """A projected failure mode resulting from an unmanaged dependency or lock-in.

    Attributes
    ----------
    scenario_name:
        Name of the scenario this failure mode applies to.
    dependency_name:
        Name of the originating lock-in or dependency.
    failure_mode_title:
        Short title describing what breaks.
    what_breaks:
        Detailed explanation of what system, process, or financial component breaks later.
    trigger_condition:
        The event or threshold that triggers the failure mode.
    time_horizon:
        Estimated time horizon when this failure mode typically manifests.
    """

    scenario_name: str
    dependency_name: str
    failure_mode_title: str
    what_breaks: str = ""
    trigger_condition: str = ""
    time_horizon: str = ""
    grounded_in: str = ""


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(
    dependencies: list[LockInDependency],
    outcomes: list[OutcomeProjection] | None = None,
) -> list[FailureMode]:
    """Diagnose what breaks later if *dependencies* go unmanaged.

    Parameters
    ----------
    dependencies:
        List of :class:`~app.agents.dependency_diagnosis.sub_agents.lock_in_identification_sub_agent.LockInDependency`
        objects produced by the Lock-in Identification Sub-Agent.
    outcomes:
        Optional list of :class:`~app.agents.outcome_prediction.outcome_prediction_agent.OutcomeProjection`
        objects for broader context.

    Returns
    -------
    list[FailureMode]
        Diagnosed failure modes for the input dependencies.
        Returns ``[]`` if *dependencies* is empty or if the LLM call fails.
    """
    if not dependencies:
        return []

    prompt = _build_prompt(dependencies, outcomes or [])
    try:
        response = call_llm_with_fallback(prompt)
        return _parse_response(response, dependencies)
    except Exception as exc:
        logger.error(
            "LLM call failed in failure_mode_sub_agent (run): %s",
            exc,
            exc_info=True,
        )
        return []


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_prompt(
    dependencies: list[LockInDependency],
    outcomes: list[OutcomeProjection],
) -> str:
    """Build the LLM prompt for failure mode diagnosis."""
    dep_blocks = []
    for i, dep in enumerate(dependencies[:_MAX_DEPENDENCIES_PER_CALL]):
        block = (
            f"  DEPENDENCY {i + 1}: {dep.dependency_name}\n"
            f"  Scenario: {dep.scenario_name}\n"
            f"  Implicated Layer: {dep.layer_name}\n"
            f"  Lock-in Type: {dep.lock_in_type}\n"
            f"  Description: {dep.description}"
        )
        dep_blocks.append(block)

    deps_str = "\n\n".join(dep_blocks)

    return f"""You are an AI technology failure-mode analyst. For each identified lock-in or dependency,
project what breaks later if this dependency is left unmanaged by the organisation.

IDENTIFIED DEPENDENCIES & LOCK-INS
{deps_str}

TASK
For each dependency above, project 1-2 specific failure modes (what breaks later), the trigger condition,
and when it is likely to manifest.

Respond in exactly this repeating block format — one block per failure mode, separated by ---:

FAILURE_MODE: <short title of what breaks>
SCENARIO: <exact scenario name>
DEPENDENCY: <exact dependency name>
GROUNDED_IN: <short direct restatement of the specific outcome/trajectory fact from the DEPENDENCIES or outcomes above that this diagnosis applies to. MUST closely echo the actual wording and terms of the source trajectory above.>
WHAT_BREAKS: <1-2 sentences explaining what breaks later if unmanaged>
TRIGGER: <1 sentence explaining the trigger condition>
HORIZON: <estimated time horizon, e.g. 6-12 months, 18-24 months>
---
"""


def _parse_response(
    response: str,
    dependencies: list[LockInDependency],
) -> list[FailureMode]:
    """Parse the structured LLM response into a list of :class:`FailureMode` objects."""
    dep_map = {dep.dependency_name.lower(): dep for dep in dependencies}
    raw_blocks = re.split(r"\n---+\s*", response.strip())
    failure_modes: list[FailureMode] = []

    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue

        title = _extract_field(block, "FAILURE_MODE")
        scenario_name = _extract_field(block, "SCENARIO")
        dep_name = _extract_field(block, "DEPENDENCY")
        if not title or not scenario_name or not dep_name:
            continue

        grounded_in = _extract_field(block, "GROUNDED_IN")
        if not grounded_in and dep_name.lower() in dep_map:
            dep_obj = dep_map[dep_name.lower()]
            grounded_in = dep_obj.grounded_in or dep_obj.description or dep_obj.dependency_name

        what_breaks = _extract_field(block, "WHAT_BREAKS")
        trigger = _extract_field(block, "TRIGGER")
        horizon = _extract_field(block, "HORIZON")

        failure_modes.append(
            FailureMode(
                scenario_name=scenario_name,
                dependency_name=dep_name,
                failure_mode_title=title,
                what_breaks=what_breaks,
                trigger_condition=trigger,
                time_horizon=horizon,
                grounded_in=grounded_in,
            )
        )

    return failure_modes


def _extract_field(block: str, field: str) -> str:
    """Extract a single-line or inline value for *field* from *block*."""
    pattern = rf"^{field}:\s*(.+?)(?=\n[A-Z]+[^a-z]|$)"
    match = re.search(pattern, block, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""
