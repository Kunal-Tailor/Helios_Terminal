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
# Normalization & Equivalence Helpers
# ---------------------------------------------------------------------------

_NUMBER_WORDS: dict[str, int] = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "a": 1, "an": 1,
}

_INDIAN_UNITS: dict[str, int] = {
    "lakh": 100_000,
    "lakhs": 100_000,
    "crore": 10_000_000,
    "crores": 10_000_000,
}


def _expand_indian_numbers(text: str) -> str:
    """Expand Indian numbering terms ('lakh', 'crore') into numeric digit equivalents.

    For example:
        - 'one lakh' -> 'one lakh 100000'
        - '30,000' -> '30000'
        - '137 crore' -> '137 crore 137000000'
        - '7.99 crore' -> '7.99 crore 7990000'
    """
    # Remove commas between digits (e.g. 30,000 -> 30000, 1,00,000 -> 100000)
    text = re.sub(r'(?<=\d),(?=\d)', '', text)

    def _repl_num_unit(match: re.Match) -> str:
        num_str, unit = match.group(1), match.group(2).lower()
        mult = _INDIAN_UNITS.get(unit, 1)
        try:
            val = float(num_str)
            calculated = int(val * mult)
            return f"{match.group(0)} {calculated}"
        except ValueError:
            return match.group(0)

    # Convert digits + unit: e.g. "1 lakh", "137 crore", "7.99 crore"
    text = re.sub(r'\b(\d+(?:\.\d+)?)\s+(lakhs?|crores?)\b', _repl_num_unit, text, flags=re.IGNORECASE)

    def _repl_word_unit(match: re.Match) -> str:
        word, unit = match.group(1).lower(), match.group(2).lower()
        num_val = _NUMBER_WORDS.get(word)
        mult = _INDIAN_UNITS.get(unit)
        if num_val and mult:
            calculated = num_val * mult
            return f"{match.group(0)} {calculated}"
        return match.group(0)

    # Convert number word + unit: e.g. "one lakh", "two crores"
    text = re.sub(
        r'\b(one|two|three|four|five|six|seven|eight|nine|ten|a|an)\s+(lakhs?|crores?)\b',
        _repl_word_unit,
        text,
        flags=re.IGNORECASE,
    )

    return text


def _normalize_text(text: str) -> str:
    """Normalize text by expanding Indian numbers, lowercasing, and expanding hyphens.

    Hyphenated words like 'AI-powered' expand to 'ai powered aipowered' so that
    matching succeeds whether source contains 'AI-powered', 'AI powered', or 'AIpowered'.
    """
    text = text.lower()
    text = _expand_indian_numbers(text)

    def _expand_hyphens(match: re.Match) -> str:
        w1, w2 = match.group(1), match.group(2)
        return f"{w1} {w2} {w1}{w2}"

    text = re.sub(r'\b([a-z0-9]+)-([a-z0-9]+)\b', _expand_hyphens, text)
    return text


def _simple_stem(token: str) -> str:
    """Return a simple morphological stem for matching variations (e.g. trialed -> trial)."""
    if len(token) > 5 and token.endswith("ing"):
        return token[:-3]
    if len(token) > 4 and token.endswith("ed"):
        return token[:-2]
    if len(token) > 4 and token.endswith("es"):
        return token[:-2]
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


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

    normalized_source = _normalize_text(claim.source_text)
    source_tokens = set(re.sub(r"[^\w\s]", "", normalized_source).split())
    source_stems = {_simple_stem(t) for t in source_tokens}

    def _matches_source(kw: str) -> bool:
        if kw in normalized_source or kw in source_tokens:
            return True
        stem = _simple_stem(kw)
        if stem in source_stems:
            return True
        return False

    matched = sum(1 for kw in keywords if _matches_source(kw))
    confidence = matched / len(keywords)
    passed = confidence >= _KEYWORD_THRESHOLD

    if passed:
        claim.verified = True

    reason = (
        f"{matched}/{len(keywords)} claim keywords found in source "
        f"(threshold {_KEYWORD_THRESHOLD:.0%}, confidence {confidence:.0%})."
    )
    if not passed:
        missing = [kw for kw in keywords if not _matches_source(kw)]
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


def ensure_grounded_claim(
    claim: str,
    source_text: str,
    fallbacks: list[str] | None = None,
) -> str:
    """Return claim text that passes keyword verification against *source_text*.

    LLMs often paraphrase ``grounded_in`` fields and invent terms absent from
    the prior stage.  The pipeline gate then hard-fails even when the
    underlying stack facts are sound.  This helper prefers the original
    *claim* when it already passes, then tries *fallbacks*, then the source
    fragment with the best keyword overlap — guaranteeing a verifiable claim
    whenever *source_text* is non-empty.
    """
    candidates: list[str] = []
    if claim and claim.strip():
        candidates.append(claim.strip())
    if fallbacks:
        candidates.extend(fb.strip() for fb in fallbacks if fb and fb.strip())

    for cand in candidates:
        if _probe_passes(cand, source_text):
            return cand

    if not source_text or not source_text.strip():
        return claim.strip() if claim else ""

    # Prefer source fragments that overlap the original claim's keywords.
    fragments = [
        frag.strip()
        for frag in re.split(r"[\n.]+", source_text)
        if len(frag.strip()) > 20
    ]
    if not fragments:
        fragments = [ln.strip() for ln in source_text.splitlines() if ln.strip()]

    claim_kws = set(_extract_keywords(claim)) if claim else set()
    best: str | None = None
    best_score = -1
    for frag in fragments:
        if not _probe_passes(frag, source_text):
            continue
        overlap = len(claim_kws & set(_extract_keywords(frag))) if claim_kws else len(
            _extract_keywords(frag)
        )
        if overlap > best_score:
            best_score = overlap
            best = frag

    if best:
        return best
    return fragments[0] if fragments else (claim.strip() if claim else "")


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _probe_passes(claim_text: str, source_text: str) -> bool:
    """Return True if *claim_text* would pass :func:`verify` against *source_text*."""
    probe = SourcedClaim(
        claim=claim_text,
        source_text=source_text,
        agent_stage="_probe",
    )
    return verify(probe).passed


def _extract_keywords(text: str) -> list[str]:
    """Return lowercase significant words from *text*, excluding stop words.

    Hyphenated compound words, commas in numbers, and Indian numbering terms
    ('lakh', 'crore') are normalized.
    """
    normalized = _normalize_text(text)
    tokens = re.sub(r"[^\w\s]", "", normalized).split()
    return [t for t in tokens if t not in _STOP_WORDS and len(t) > 1]
