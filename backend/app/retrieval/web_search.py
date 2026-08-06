"""
Web-search retrieval wrapper.

Public API
----------
    search(query: str, max_results: int = 5) -> list[SearchResult]

Thin layer over the Tavily search API.  Returns a list of structured
results so callers never touch the raw SDK response directly — this
isolates the rest of the codebase from Tavily SDK changes.

Reads TAVILY_API_KEY from app.core.config.settings.
Raises RuntimeError if the key is not set.
"""

from __future__ import annotations

from dataclasses import dataclass

from tavily import TavilyClient

from app.core.config import settings


@dataclass
class SearchResult:
    """A single search result returned by :func:`search`."""

    title: str
    url: str
    content: str   # snippet / summary text returned by Tavily
    score: float   # relevance score in [0, 1] as reported by Tavily


def search(query: str, max_results: int = 5) -> list[SearchResult]:
    """Search the web for *query* and return up to *max_results* results.

    Parameters
    ----------
    query:
        The search query string.
    max_results:
        Maximum number of results to return (default 5, capped at 10
        to keep token usage predictable for downstream agents).

    Returns
    -------
    list[SearchResult]
        Ordered list of results, most relevant first.

    Raises
    ------
    RuntimeError
        If TAVILY_API_KEY is not configured.
    """
    if not settings.tavily_api_key:
        raise RuntimeError(
            "TAVILY_API_KEY is not set. "
            "Add it to your .env file or environment before running retrieval."
        )

    max_results = min(max_results, 10)  # hard cap — keeps agent token budgets predictable

    client = TavilyClient(api_key=settings.tavily_api_key)
    raw = client.search(query=query, max_results=max_results)

    return [
        SearchResult(
            title=r.get("title", ""),
            url=r.get("url", ""),
            content=r.get("content", ""),
            score=float(r.get("score", 0.0)),
        )
        for r in raw.get("results", [])
    ]
