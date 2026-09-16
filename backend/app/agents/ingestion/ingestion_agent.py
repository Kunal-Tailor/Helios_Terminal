"""
Ingestion Agent — parent orchestrator for the Ingestion stage.

Role (ARCHITECTURE.md §3.1)
    Takes the decision brief, runs its three sub-agents, and returns one
    :class:`~app.agents.ingestion.sub_agents.context_synthesis_sub_agent.IngestionContext`
    object ready for the Stack-Mapping Agent.

Sub-agent execution order (ARCHITECTURE.md §3.8)
    ┌─────────────────────────────┐
    │      Ingestion Agent        │
    └──────────────┬──────────────┘
      ┌────────────┼──────────────┐
      ▼            ▼              ▼ (parallel — independent of each other)
  Web-Scraping  Structured-  Context-Synthesis
  Sub-Agent     Source       Sub-Agent (sequential —
  (5.1)         Sub-Agent    needs 5.1 + 5.2 output)
                (5.2)

  5.1 and 5.2 are dispatched concurrently via ThreadPoolExecutor.
  5.3 (context synthesis) runs after both complete, receiving their merged outputs.

Public API
----------
    run(entity, capability, options) -> IngestionContext
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

from app.agents.ingestion.sub_agents import (
    context_synthesis_sub_agent,
    structured_source_sub_agent,
    web_scraping_sub_agent,
)
from app.agents.ingestion.sub_agents.context_synthesis_sub_agent import IngestionContext
from app.agents.ingestion.sub_agents.structured_source_sub_agent import StructuredSourceResult
from app.retrieval.web_search import SearchResult


def run(
    entity: str,
    capability: str,
    options: Optional[list[str]] = None,
) -> IngestionContext:
    """Run the full Ingestion Agent pipeline for one decision brief.

    Parameters
    ----------
    entity:
        The organisation or unit making the AI sourcing decision.
    capability:
        The AI capability being sourced.
    options:
        Candidate sourcing paths supplied by the user (e.g.
        ``["build in-house", "license from vendor"]``).
        Pass ``None`` or ``[]`` if the user has not specified options —
        the Scenario-Generation Agent will infer them later.

    Returns
    -------
    IngestionContext
        Structured context for the decision, ready for the Stack-Mapping Agent.
    """
    options = options or []

    # ------------------------------------------------------------------
    # Step 1: Run web-scraping and structured-source sub-agents in parallel.
    # They are independent (neither needs the other's output), so concurrency
    # is safe and reduces total wall-clock time.
    # ------------------------------------------------------------------
    web_results: list[SearchResult] = []
    structured_results: list[StructuredSourceResult] = []

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_web = executor.submit(
            web_scraping_sub_agent.run,
            entity=entity,
            capability=capability,
            options=options,
        )
        future_struct = executor.submit(
            structured_source_sub_agent.run,
            entity=entity,
            capability=capability,
        )

        # Collect results; individual failures are already handled inside
        # each sub-agent (they return [] on error), so we only need to
        # re-raise unexpected executor-level exceptions.
        web_results = future_web.result()
        structured_results = future_struct.result()

    # ------------------------------------------------------------------
    # Step 2: Run context synthesis sequentially — it needs both outputs.
    # ------------------------------------------------------------------
    context: IngestionContext = context_synthesis_sub_agent.run(
        entity=entity,
        capability=capability,
        options=options,
        web_results=web_results,
        structured_results=structured_results,
    )

    return context
