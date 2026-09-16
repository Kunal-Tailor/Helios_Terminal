"""
Structured-Source Sub-Agent — Ingestion Agent, Sub-Agent 2 of 3.

Role (ARCHITECTURE.md §3.1)
    Pulls from known structured / authoritative sources rather than open web
    search.  The sources targeted are:
      - Hugging Face Hub  — public model registry (REST API, no auth required)
      - BIS Entity List   — US Bureau of Industry and Security export-control list
      - TPDi              — Technology Procurement and Dependency Intelligence
      - Market-share reports — cloud AI infrastructure market context

Public API
----------
    run(entity, capability) -> list[StructuredSourceResult]

No LLM call is made here — this is purely retrieval from authoritative sources.
The parent Ingestion Agent is responsible for passing these results to the LLM.

Implementation note
-------------------
Hugging Face Hub is queried via its public JSON REST API (httpx, no auth).
BIS Entity List, TPDi, and market-share reports are queried via targeted web
searches through the shared web-search wrapper (focused queries on known
authoritative domains/publications rather than open-ended web crawl).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import httpx

from app.retrieval.web_search import search as web_search

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_HF_HUB_API_URL = "https://huggingface.co/api/models"
_HF_HUB_MAX_RESULTS = 5
_HF_REQUEST_TIMEOUT_S = 10.0


# ---------------------------------------------------------------------------
# Return type
# ---------------------------------------------------------------------------

@dataclass
class StructuredSourceResult:
    """A result pulled from one of the known structured / authoritative sources.

    Attributes
    ----------
    source_name:
        Human-readable name of the source (e.g. ``"Hugging Face Hub"``).
    title:
        Title or name of the retrieved item (model name, report heading, etc.).
    content:
        Key facts / summary text from the source.
    url:
        Canonical URL for the item.  May be empty if the source does not
        provide a direct URL (e.g. some market-share report snippets).
    raw_score:
        Relevance signal from the source (HF downloads, web-search score, etc.).
        Comparable only within the same source; not normalised across sources.
    """

    source_name: str
    title: str
    content: str
    url: str
    raw_score: float = 0.0


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(entity: str, capability: str) -> list[StructuredSourceResult]:
    """Pull structured / authoritative context for an AI sourcing decision.

    Parameters
    ----------
    entity:
        The organisation or unit making the sourcing decision.
    capability:
        The AI capability being sourced.

    Returns
    -------
    list[StructuredSourceResult]
        Results from all targeted sources, combined in source order.
        Individual source failures are silently skipped (graceful degradation)
        so one unavailable source does not abort the whole ingestion stage.
    """
    results: list[StructuredSourceResult] = []
    results.extend(_query_hf_hub(capability))
    results.extend(_query_bis_entity_list(entity))
    results.extend(_query_tpdi(entity, capability))
    results.extend(_query_market_share_reports(capability))
    return results


# ---------------------------------------------------------------------------
# Per-source helpers
# ---------------------------------------------------------------------------

def _query_hf_hub(capability: str) -> list[StructuredSourceResult]:
    """Query the Hugging Face Hub public model registry for *capability*.

    Uses the HF Hub REST API (no authentication required for public models).
    Returns at most :data:`_HF_HUB_MAX_RESULTS` results.
    Returns ``[]`` on any network or parse error (graceful degradation).
    """
    try:
        response = httpx.get(
            _HF_HUB_API_URL,
            params={"search": capability, "limit": _HF_HUB_MAX_RESULTS},
            timeout=_HF_REQUEST_TIMEOUT_S,
        )
        response.raise_for_status()
        models = response.json()
    except Exception as exc:
        logger.error("HuggingFace Hub query failed in structured_source_sub_agent: %s", exc, exc_info=True)
        return []

    results = []
    for model in models:
        model_id = model.get("modelId") or model.get("id", "")
        downloads = model.get("downloads", 0)
        pipeline_tag = model.get("pipeline_tag", "")
        results.append(
            StructuredSourceResult(
                source_name="Hugging Face Hub",
                title=model_id,
                content=(
                    f"Model: {model_id}. "
                    f"Task: {pipeline_tag}. "
                    f"Downloads (30d): {downloads}."
                ),
                url=f"https://huggingface.co/{model_id}",
                raw_score=float(downloads),
            )
        )
    return results


def _query_bis_entity_list(entity: str) -> list[StructuredSourceResult]:
    """Search the US BIS Entity List for *entity*.

    Uses a targeted web search on the BIS domain so no direct database
    access is required.  Returns results as :class:`StructuredSourceResult`.
    """
    query = f"site:bis.doc.gov entity list {entity}"
    try:
        raw = web_search(query, max_results=3)
    except Exception as exc:
        logger.error("BIS Entity List query failed in structured_source_sub_agent: %s", exc, exc_info=True)
        return []
    return [
        StructuredSourceResult(
            source_name="BIS Entity List",
            title=r.title,
            content=r.content,
            url=r.url,
            raw_score=r.score,
        )
        for r in raw
    ]


def _query_tpdi(entity: str, capability: str) -> list[StructuredSourceResult]:
    """Search for TPDi-style technology procurement / dependency intelligence.

    Targets defence and procurement intelligence publications.
    """
    query = f"{entity} {capability} technology procurement dependency intelligence assessment"
    try:
        raw = web_search(query, max_results=3)
    except Exception as exc:
        logger.error("TPDi query failed in structured_source_sub_agent: %s", exc, exc_info=True)
        return []
    return [
        StructuredSourceResult(
            source_name="TPDi / Procurement Intelligence",
            title=r.title,
            content=r.content,
            url=r.url,
            raw_score=r.score,
        )
        for r in raw
    ]


def _query_market_share_reports(capability: str) -> list[StructuredSourceResult]:
    """Search for cloud AI infrastructure market-share context for *capability*."""
    query = f"{capability} AI cloud market share infrastructure report"
    try:
        raw = web_search(query, max_results=3)
    except Exception as exc:
        logger.error("Market share reports query failed in structured_source_sub_agent: %s", exc, exc_info=True)
        return []
    return [
        StructuredSourceResult(
            source_name="Market Share Reports",
            title=r.title,
            content=r.content,
            url=r.url,
            raw_score=r.score,
        )
        for r in raw
    ]
