"""
Verification layer — claim-source consistency checker.

Public API
----------
    verify(claim: SourcedClaim) -> VerificationResult
        Check one claim against its source_text.
        Mutates claim.verified = True if the check passes.

    verify_stage(store: SourceStore, agent_stage: str) -> list[VerificationResult]
        Run verify() over every claim in *store* that belongs to *agent_stage*.
        Returns one VerificationResult per claim.  Used by the pipeline gate (6.2)
        to decide whether a stage's output is safe to pass downstream.

Implementation note — "start simple"
--------------------------------------
MVP uses a **keyword-presence check**:
  1. Extract significant words from the claim (lowercase, strip punctuation,
     remove common stop words).
  2. Count how many of those keywords appear anywhere in the source_text.
  3. If the match fraction meets the threshold (default 0.6), the claim passes.

This catches obvious fabrications (a claim mentions an entity/figure/fact that
has no trace in the cited source) without requiring a live LLM call.  A richer
semantic check (embedding similarity or LLM-based contradiction detection) is a
documented future extension — see PRD.md Open Questions.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.verification.source_store import SourcedClaim, SourceStore

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Fraction of claim keywords that must be found in the source to pass.
_KEYWORD_THRESHOLD: float = 0.6

# Common English words that carry no factual content — excluded from keyword
# extraction so they don't inflate or deflate match scores.
_STOP_WORDS: frozenset[str] = frozenset({
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "has", "have", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "of", "in", "on", "at",
    "to", "for", "with", "by", "from", "this", "that", "these", "those",
    "it", "its", "and", "or", "but", "not", "no", "as", "if", "so",
    "than", "then", "also", "each", "which", "who", "whom", "what",
    "when", "where", "how", "all", "any", "both", "few", "more", "most",
    "other", "some", "such", "own", "same", "too", "very", "just",
})


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class VerificationResult:
    """The outcome of checking one :class:`~source_store.SourcedClaim`.

    Attributes
    ----------
    passed:
        ``True`` if the claim meets the verification threshold.
    confidence:
        Fraction of claim keywords found in the source (0.0 – 1.0).
    reason:
        Human-readable explanation of the outcome, suitable for audit logs.
    claim:
        The claim text that was checked (copied for easy logging).
    agent_stage:
        The pipeline stage that produced the claim.
    """

    passed: bool
    confidence: float
    reason: str
    claim: str
    agent_stage: str


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def verify(claim: SourcedClaim) -> VerificationResult:
    """Check *claim* against its ``source_text`` using a keyword-presence check.

    If the check passes, ``claim.verified`` is set to ``True`` in-place.

    Parameters
    ----------
    claim:
        The :class:`~source_store.SourcedClaim` to verify.

    Returns
    -------
    VerificationResult
        The detailed outcome of the check.
    """
    keywords = _extract_keywords(claim.claim)

    # Edge case: no checkable keywords (e.g. claim is all stop words or empty).
    # Pass by default — there is nothing to contradict.
    if not keywords:
        claim.verified = True
        return VerificationResult(
            passed=True,
            confidence=1.0,
            reason="No checkable keywords in claim — passed by default.",
            claim=claim.claim,
            agent_stage=claim.agent_stage,
        )

    source_lower = claim.source_text.lower()
    matched = sum(1 for kw in keywords if kw in source_lower)
    confidence = matched / len(keywords)
    passed = confidence >= _KEYWORD_THRESHOLD

    if passed:
        claim.verified = True

    reason = (
        f"{matched}/{len(keywords)} claim keywords found in source "
        f"(threshold {_KEYWORD_THRESHOLD:.0%}, confidence {confidence:.0%})."
    )
    if not passed:
        missing = [kw for kw in keywords if kw not in source_lower]
        reason += f" Missing keywords: {missing[:5]}"  # cap at 5 to keep logs readable

    return VerificationResult(
        passed=passed,
        confidence=confidence,
        reason=reason,
        claim=claim.claim,
        agent_stage=claim.agent_stage,
    )


def verify_stage(store: SourceStore, agent_stage: str) -> list[VerificationResult]:
    """Verify all claims in *store* that belong to *agent_stage*.

    Runs :func:`verify` on each matching claim.  The pipeline gate (Phase 6)
    calls this at every agent handoff boundary.

    Parameters
    ----------
    store:
        The :class:`~source_store.SourceStore` for the current pipeline run.
    agent_stage:
        The stage whose claims should be verified (e.g. ``"ingestion"``).

    Returns
    -------
    list[VerificationResult]
        One result per claim in the stage, in the order they were added.
        Empty list if the stage has no claims.
    """
    return [verify(c) for c in store.for_stage(agent_stage)]


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _extract_keywords(text: str) -> list[str]:
    """Return lowercase significant words from *text*, excluding stop words.

    Strips punctuation, lowercases, splits on whitespace, and filters out
    words in :data:`_STOP_WORDS` and single-character tokens.
    """
    # Remove punctuation, lowercase, split
    tokens = re.sub(r"[^\w\s]", "", text.lower()).split()
    return [t for t in tokens if t not in _STOP_WORDS and len(t) > 1]
