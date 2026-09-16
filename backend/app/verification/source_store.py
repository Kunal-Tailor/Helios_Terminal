"""
Source store — data structures for the verification layer.

Defines the two types the verifier (4.2) and the pipeline (6.x) operate on:

  SourcedClaim   — a single claim made by an agent, paired with its cited source.
  SourceStore    — an ordered collection of SourcedClaims for one pipeline run.

No verification logic lives here.  This module is data-only so it can be
imported by agents, the verifier, and the pipeline without circular dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SourcedClaim:
    """A single claim produced by an agent stage, with its supporting source.

    Attributes
    ----------
    claim:
        The exact assertion made by the agent (a full sentence or short paragraph).
    source_text:
        The raw text from the source that supports (or is claimed to support) this claim.
        This is what the verifier checks the claim against.
    agent_stage:
        The name of the pipeline stage that produced this claim
        (e.g. ``"ingestion"``, ``"stack_mapping"``).
        Used in error messages and audit trails.
    source_url:
        Optional URL or identifier for the source document.
        Informational — the verifier works on ``source_text``, not the URL.
    verified:
        Set to ``True`` by the verifier once the claim passes its check.
        Defaults to ``False`` so unverified claims are the safe default.
    """

    claim: str
    source_text: str
    agent_stage: str
    source_url: Optional[str] = None
    verified: bool = False


@dataclass
class SourceStore:
    """An ordered collection of :class:`SourcedClaim` objects for one pipeline run.

    One ``SourceStore`` is created per pipeline execution and passed through
    each stage so every agent's claims can be accumulated and later audited.

    Attributes
    ----------
    claims:
        All claims recorded so far, in the order they were added.
    """

    claims: list[SourcedClaim] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Mutation helpers
    # ------------------------------------------------------------------

    def add(self, claim: SourcedClaim) -> None:
        """Append *claim* to the store."""
        self.claims.append(claim)

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def for_stage(self, agent_stage: str) -> list[SourcedClaim]:
        """Return all claims produced by *agent_stage*."""
        return [c for c in self.claims if c.agent_stage == agent_stage]

    def unverified(self) -> list[SourcedClaim]:
        """Return all claims that have not yet been verified."""
        return [c for c in self.claims if not c.verified]

    def all_verified(self) -> bool:
        """Return ``True`` if every claim in the store has been verified."""
        return all(c.verified for c in self.claims)
