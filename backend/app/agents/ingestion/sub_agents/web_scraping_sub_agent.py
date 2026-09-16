"""
Web-Scraping Sub-Agent — Ingestion Agent, Sub-Agent 1 of 3.

Role (ARCHITECTURE.md §3.1)
    Pulls public information on the entity and capability from live web search.
    Returns raw :class:`~app.retrieval.web_search.SearchResult` objects for the
    parent Ingestion Agent (or the Context-Synthesis Sub-Agent) to merge.

Public API
----------
    run(entity, capability, options, max_results_per_query) -> list[SearchResult]

The sub-agent formulates several targeted search queries from the decision brief
fields, runs each through the shared web-search wrapper, deduplicates by URL,
and returns the combined result set ordered by relevance score (descending).

No LLM call is made here — this sub-agent is purely retrieval.
The parent agent is responsible for passing the results to the LLM for synthesis.
"""

from __future__ import annotations

from app.retrieval.web_search import SearchResult, search


# Number of results to fetch per individual query (before deduplication).
_RESULTS_PER_QUERY: int = 5


def run(
    entity: str,
    capability: str,
    options: list[str] | None = None,
    max_results_per_query: int = _RESULTS_PER_QUERY,
) -> list[SearchResult]:
    """Fetch web search results relevant to a sourcing decision brief.

    Formulates multiple targeted queries from the brief fields, runs each
    through :func:`app.retrieval.web_search.search`, deduplicates by URL,
    and returns results sorted by relevance score (highest first).

    Parameters
    ----------
    entity:
        The organisation or unit making the AI sourcing decision
        (e.g. ``"Indian Army signals division"``).
    capability:
        The AI capability being sourced
        (e.g. ``"small language model for edge inference"``).
    options:
        Optional list of candidate sourcing paths provided by the user
        (e.g. ``["build in-house", "license from vendor", "outsource to partner"]``).
        A query is generated per option so sourcing-specific context is fetched.
    max_results_per_query:
        Maximum results to fetch per individual query (default 5, hard-capped
        downstream by the web-search wrapper at 10).

    Returns
    -------
    list[SearchResult]
        Deduplicated results across all queries, sorted by score descending.
        May be empty if all queries return no results.
    """
    queries = _build_queries(entity, capability, options or [])
    seen_urls: set[str] = set()
    combined: list[SearchResult] = []

    for query in queries:
        results = search(query, max_results=max_results_per_query)
        for result in results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                combined.append(result)

    # Sort by relevance score, highest first.
    combined.sort(key=lambda r: r.score, reverse=True)
    return combined


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_queries(
    entity: str,
    capability: str,
    options: list[str],
) -> list[str]:
    """Return a list of search query strings for the given brief fields.

    Strategy
    --------
    - One broad query covering entity + capability context.
    - One sourcing-strategy query (build / buy / outsource framing).
    - One per user-supplied option, to fetch option-specific evidence.
    """
    queries: list[str] = [
        f"{entity} {capability} AI technology",
        f"{entity} AI sourcing strategy {capability}",
    ]
    for option in options:
        queries.append(f"{entity} {capability} {option}")
    return queries
