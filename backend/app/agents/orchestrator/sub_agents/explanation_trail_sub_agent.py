"""
Explanation-Trail Sub-Agent — Orchestrator Agent, Sub-Agent 3 of 3 (optional).

Role (ARCHITECTURE.md §3.6)
    Assembles a source-grounded, audit-ready reasoning trail explaining how data flowed
    from initial ingestion context and stack mapping through to the final comparative verdict.

Public API
----------
    run(diagnoses, verdict, sources) -> ExplanationTrail

The sub-agent calls the shared LLM client to assemble an audit reasoning trail,
parses the structured response, and returns an :class:`ExplanationTrail` object.
If the LLM call fails or returns an unparseable response, it returns an empty object
(graceful degradation).

ExplanationTrail and AuditStep are defined here as canonical output types.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from app.agents.dependency_diagnosis.dependency_diagnosis_agent import DependencyDiagnosis
from app.agents.orchestrator.sub_agents.verdict_synthesis_sub_agent import VerdictSynthesis
from app.llm.client import complete

logger = logging.getLogger(__name__)

# Maximum diagnoses to process in a single prompt call
_MAX_DIAGNOSES_PER_CALL = 5


# ---------------------------------------------------------------------------
# Output types
# ---------------------------------------------------------------------------

@dataclass
class AuditStep:
    """A single audit step in the explanation reasoning trail.

    Attributes
    ----------
    stage:
        The pipeline stage or capability layer (e.g. "Ingestion", "Stack-Mapping", "Diagnosis", "Verdict").
    claim:
        The key finding, decision claim, or constraint identified.
    evidence:
        The underlying fact, source citation, or logical justification supporting the claim.
    grounded_in:
        Short direct restatement of the specific dependency diagnosis fact from Dependency-Diagnosis's context
        that this step is based on.
    """

    stage: str
    claim: str
    evidence: str = ""
    grounded_in: str = ""


@dataclass
class ExplanationTrail:
    """Complete source-grounded audit reasoning trail for explainability.

    Attributes
    ----------
    summary:
        High-level overview of the evidence-to-verdict audit trail.
    steps:
        Ordered list of :class:`AuditStep` objects tracing key findings.
    sources:
        Deduplicated list of source URLs or citations referenced.
    """

    summary: str = ""
    steps: list[AuditStep] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(
    diagnoses: list[DependencyDiagnosis],
    verdict: VerdictSynthesis | None = None,
    sources: list[str] | None = None,
) -> ExplanationTrail:
    """Assemble a source-grounded audit reasoning trail for the decision.

    Parameters
    ----------
    diagnoses:
        List of :class:`~app.agents.dependency_diagnosis.dependency_diagnosis_agent.DependencyDiagnosis`
        objects from the Dependency-Diagnosis Agent.
    verdict:
        Optional :class:`~app.agents.orchestrator.sub_agents.verdict_synthesis_sub_agent.VerdictSynthesis`
        object from the Verdict-Synthesis Sub-Agent.
    sources:
        Optional list of source URLs accumulated during Ingestion.

    Returns
    -------
    ExplanationTrail
        Audit-ready reasoning trail with summary, steps, and source citations.
        Returns empty :class:`ExplanationTrail` if inputs are empty or if the LLM call fails.
    """
    if not diagnoses and not verdict:
        return ExplanationTrail(sources=sources or [])

    prompt = _build_prompt(diagnoses, verdict, sources or [])
    try:
        response = complete(prompt)
        trail = _parse_response(response)
        trail.sources = list(dict.fromkeys(sources or []))
        return trail
    except Exception as exc:
        logger.error(
            "LLM call failed in explanation_trail_sub_agent (run): %s",
            exc,
            exc_info=True,
        )
        return ExplanationTrail(sources=sources or [])


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_prompt(
    diagnoses: list[DependencyDiagnosis],
    verdict: VerdictSynthesis | None,
    sources: list[str],
) -> str:
    """Build the LLM prompt for explanation trail assembly."""
    verdict_rec = verdict.recommended_path if verdict else "Not specified"
    verdict_summary = verdict.verdict_summary if verdict else "Not specified"

    diag_blocks = []
    for i, diag in enumerate(diagnoses[:_MAX_DIAGNOSES_PER_CALL]):
        deps_str = (
            ", ".join(d.dependency_name for d in diag.dependencies)
            if diag.dependencies
            else "None identified"
        )
        scores_str = (
            ", ".join(f"{s.dependency_name} ({s.risk_level})" for s in diag.severity_scores)
            if diag.severity_scores
            else "None scored"
        )

        block = (
            f"  SCENARIO {i + 1}: {diag.scenario_name}\n"
            f"  Dependencies: {deps_str}\n"
            f"  Risk Ratings: {scores_str}"
        )
        diag_blocks.append(block)

    diagnoses_str = "\n".join(diag_blocks) if diag_blocks else "No diagnoses available."
    sources_str = "\n".join(f"  - {url}" for url in sources[:10]) if sources else "No source URLs cited."

    return f"""You are an AI sourcing audit & explainability analyst. Assemble a clear,
transparent, step-by-step reasoning trail tracing how evidence led to the final verdict.

FINAL VERDICT RECOMMENDATION: {verdict_rec}
VERDICT SUMMARY: {verdict_summary}

DIAGNOSED SCENARIO PATHS
{diagnoses_str}

INGESTED SOURCES
{sources_str}

TASK
1. Provide a brief 1-2 paragraph audit summary explaining how evidence drove the verdict.
2. Formulate 3-5 structured audit steps tracing key findings across stages (e.g. Ingestion, Stack-Mapping, Diagnosis, Verdict).

Respond in exactly this format — start with TRAIL SUMMARY, followed by AUDIT STEP blocks separated by ---:

TRAIL SUMMARY:
<1-2 paragraph audit trail summary>

---
AUDIT STEP: <stage name, e.g. Ingestion, Stack-Mapping, Diagnosis, Verdict>
GROUNDED_IN: <short direct restatement of the specific dependency diagnosis fact from the DIAGNOSED SCENARIO PATHS above that this step is based on. MUST closely echo the actual wording and terms of the source diagnosis above.>
CLAIM: <1 sentence stating the key claim or finding>
EVIDENCE: <1 sentence citing the source-grounded evidence or justification>
---
"""


def _parse_response(response: str) -> ExplanationTrail:
    """Parse the structured LLM response into an :class:`ExplanationTrail` object."""
    stripped = response.strip()

    summary_match = re.search(
        r"TRAIL SUMMARY:\s*\n(.*?)(?=\n---+|\nAUDIT STEP:|\Z)", stripped, re.DOTALL
    )
    summary = summary_match.group(1).strip() if summary_match else ""

    raw_blocks = re.split(r"\n---+\s*", stripped)
    steps: list[AuditStep] = []

    for block in raw_blocks:
        block = block.strip()
        if not block or ("TRAIL SUMMARY:" in block and "AUDIT STEP:" not in block):
            continue

        stage = _extract_field(block, "AUDIT STEP")
        if not stage:
            continue

        grounded_in = _extract_field(block, "GROUNDED_IN")
        claim = _extract_field(block, "CLAIM")
        evidence = _extract_field(block, "EVIDENCE")

        steps.append(
            AuditStep(
                stage=stage,
                claim=claim,
                evidence=evidence,
                grounded_in=grounded_in,
            )
        )

    return ExplanationTrail(
        summary=summary,
        steps=steps,
    )


def _extract_field(block: str, field: str) -> str:
    """Extract a single-line or inline value for *field* from *block*."""
    pattern = rf"^{field}:\s*(.+?)(?=\n[A-Z]+[^a-z]|$)"
    match = re.search(pattern, block, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""
