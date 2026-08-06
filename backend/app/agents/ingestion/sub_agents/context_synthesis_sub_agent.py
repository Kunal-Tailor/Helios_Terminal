"""
Context-Synthesis Sub-Agent — Ingestion Agent, Sub-Agent 3 of 3 (optional).

Role (ARCHITECTURE.md §3.1)
    Merges the raw outputs of the Web-Scraping Sub-Agent (5.1) and the
    Structured-Source Sub-Agent (5.2) into a single, LLM-synthesized
    structured context object.  If this sub-agent is omitted, the parent
    Ingestion Agent performs this merge directly.

Public API
----------
    run(entity, capability, options, web_results, structured_results) -> IngestionContext

The sub-agent builds a compact text representation of the retrieved results,
calls the shared LLM client for a synthesis, parses the structured response,
and returns an :class:`IngestionContext` object ready for the Stack-Mapping
Agent to consume.

IngestionContext is defined here because it is the canonical output type of
the Ingestion stage; downstream agents (Stack-Mapping) import it from here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.llm.client import complete
from app.retrieval.web_search import SearchResult

# Import the structured-source result type for type annotations.
from app.agents.ingestion.sub_agents.structured_source_sub_agent import (
    StructuredSourceResult,
)

# ---------------------------------------------------------------------------
# Output type — canonical context object for the Ingestion stage
# ---------------------------------------------------------------------------

@dataclass
class IngestionContext:
    """Structured context produced by the Ingestion Agent for one decision brief.

    Attributes
    ----------
    entity:
        The organisation or unit making the AI sourcing decision.
    capability:
        The AI capability being sourced.
    options:
        Candidate sourcing paths (may be empty if not supplied by the user).
    context_summary:
        LLM-synthesized narrative summarising the entity, the capability
        landscape, and what the retrieved sources reveal.
    key_facts:
        Bullet-point facts extracted by the LLM from the retrieved content.
        Each item is a single, self-contained factual statement.
    sources:
        Deduplicated list of source URLs cited across all retrieved results.
    """

    entity: str
    capability: str
    options: list[str] = field(default_factory=list)
    context_summary: str = ""
    key_facts: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

_MAX_SNIPPETS = 10   # cap on how many result snippets are fed to the LLM
_MAX_SNIPPET_CHARS = 300  # cap per snippet to keep the prompt token-efficient


def run(
    entity: str,
    capability: str,
    options: list[str],
    web_results: list[SearchResult],
    structured_results: list[StructuredSourceResult],
) -> IngestionContext:
    """Synthesise retrieved results into a structured :class:`IngestionContext`.

    Parameters
    ----------
    entity:
        The organisation or unit making the sourcing decision.
    capability:
        The AI capability being sourced.
    options:
        Candidate sourcing paths from the decision brief.
    web_results:
        Raw results from the Web-Scraping Sub-Agent (5.1).
    structured_results:
        Raw results from the Structured-Source Sub-Agent (5.2).

    Returns
    -------
    IngestionContext
        A structured context object ready for the Stack-Mapping Agent.
        If the LLM call fails, ``context_summary`` and ``key_facts`` are
        left empty and sources are still populated (graceful degradation).
    """
    sources = _collect_sources(web_results, structured_results)
    prompt = _build_prompt(entity, capability, options, web_results, structured_results)

    try:
        llm_response = complete(prompt)
        context_summary, key_facts = _parse_llm_response(llm_response)
    except Exception:
        context_summary = ""
        key_facts = []

    return IngestionContext(
        entity=entity,
        capability=capability,
        options=options,
        context_summary=context_summary,
        key_facts=key_facts,
        sources=sources,
    )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _collect_sources(
    web_results: list[SearchResult],
    structured_results: list[StructuredSourceResult],
) -> list[str]:
    """Return a deduplicated list of source URLs from both result sets."""
    seen: set[str] = set()
    urls: list[str] = []
    for r in web_results:
        if r.url and r.url not in seen:
            seen.add(r.url)
            urls.append(r.url)
    for r in structured_results:
        if r.url and r.url not in seen:
            seen.add(r.url)
            urls.append(r.url)
    return urls


def _build_prompt(
    entity: str,
    capability: str,
    options: list[str],
    web_results: list[SearchResult],
    structured_results: list[StructuredSourceResult],
) -> str:
    """Build the LLM synthesis prompt from the decision brief and retrieved results."""
    options_str = ", ".join(options) if options else "not specified by user"

    # Build a compact snippet block from web results
    web_block_lines: list[str] = []
    for r in web_results[:_MAX_SNIPPETS]:
        snippet = r.content[:_MAX_SNIPPET_CHARS].replace("\n", " ")
        web_block_lines.append(f"- [{r.title}]({r.url}): {snippet}")
    web_block = "\n".join(web_block_lines) or "No web results retrieved."

    # Build a compact snippet block from structured results
    struct_block_lines: list[str] = []
    for r in structured_results[:_MAX_SNIPPETS]:
        snippet = r.content[:_MAX_SNIPPET_CHARS].replace("\n", " ")
        struct_block_lines.append(f"- [{r.source_name}] {r.title}: {snippet}")
    struct_block = "\n".join(struct_block_lines) or "No structured source results retrieved."

    return f"""You are an AI sourcing decision analyst.  Given the retrieved information below,
produce a structured context summary for the decision brief.

DECISION BRIEF
Entity: {entity}
Capability sought: {capability}
Candidate options: {options_str}

RETRIEVED WEB CONTENT
{web_block}

RETRIEVED STRUCTURED SOURCES (HF Hub, BIS Entity List, TPDi, Market Reports)
{struct_block}

Respond in exactly this format — no extra text before or after:

SUMMARY:
<2-3 paragraph narrative covering the entity, the capability landscape, and what the sources reveal about the sourcing options>

KEY FACTS:
- <one self-contained factual statement per bullet>
- <one self-contained factual statement per bullet>
- <add as many bullets as the evidence supports, minimum 3>
"""


def _parse_llm_response(response: str) -> tuple[str, list[str]]:
    """Parse the structured LLM response into (summary, key_facts).

    Expected format::

        SUMMARY:
        <text>

        KEY FACTS:
        - fact 1
        - fact 2

    If the format is not matched, returns the full response as the summary
    with an empty key_facts list (graceful fallback).
    """
    summary_match = re.search(
        r"SUMMARY:\s*\n(.*?)(?=\nKEY FACTS:|\Z)", response, re.DOTALL
    )
    facts_match = re.search(r"KEY FACTS:\s*\n(.*)", response, re.DOTALL)

    if summary_match:
        context_summary = summary_match.group(1).strip()
    else:
        context_summary = response.strip()

    key_facts: list[str] = []
    if facts_match:
        raw_facts = facts_match.group(1)
        for line in raw_facts.splitlines():
            line = line.strip().lstrip("-").strip()
            if line:
                key_facts.append(line)

    return context_summary, key_facts
