"""
Unit tests for app.verification.source_store.

Tests cover the data structure behaviour only — no verification logic.
  - SourcedClaim stores fields correctly and defaults verified=False
  - SourceStore.add() accumulates claims in order
  - SourceStore.for_stage() filters by agent_stage
  - SourceStore.unverified() returns only unverified claims
  - SourceStore.all_verified() reflects the correct aggregate state
"""

import pytest

from app.verification.source_store import SourceStore, SourcedClaim


# ---------------------------------------------------------------------------
# SourcedClaim
# ---------------------------------------------------------------------------

def test_sourced_claim_stores_fields():
    """SourcedClaim retains all supplied field values."""
    sc = SourcedClaim(
        claim="The entity holds a US export licence.",
        source_text="Entity XYZ was granted EAR licence #12345 on 2024-01-01.",
        agent_stage="ingestion",
        source_url="https://example.gov/licences/12345",
    )
    assert sc.claim == "The entity holds a US export licence."
    assert sc.source_text == "Entity XYZ was granted EAR licence #12345 on 2024-01-01."
    assert sc.agent_stage == "ingestion"
    assert sc.source_url == "https://example.gov/licences/12345"


def test_sourced_claim_defaults_verified_false():
    """SourcedClaim.verified defaults to False."""
    sc = SourcedClaim(
        claim="Some claim.",
        source_text="Some source.",
        agent_stage="stack_mapping",
    )
    assert sc.verified is False


def test_sourced_claim_source_url_optional():
    """SourcedClaim can be created without a source_url."""
    sc = SourcedClaim(
        claim="Some claim.",
        source_text="Some source.",
        agent_stage="ingestion",
    )
    assert sc.source_url is None


# ---------------------------------------------------------------------------
# SourceStore — accumulation
# ---------------------------------------------------------------------------

def _make_claim(claim: str, stage: str, verified: bool = False) -> SourcedClaim:
    sc = SourcedClaim(claim=claim, source_text="source text", agent_stage=stage)
    sc.verified = verified
    return sc


def test_source_store_starts_empty():
    """A new SourceStore has no claims."""
    store = SourceStore()
    assert store.claims == []


def test_source_store_add_accumulates_in_order():
    """SourceStore.add() appends claims in insertion order."""
    store = SourceStore()
    c1 = _make_claim("Claim A", "ingestion")
    c2 = _make_claim("Claim B", "stack_mapping")
    store.add(c1)
    store.add(c2)
    assert store.claims == [c1, c2]


# ---------------------------------------------------------------------------
# SourceStore — queries
# ---------------------------------------------------------------------------

def test_for_stage_returns_matching_claims():
    """SourceStore.for_stage() returns only claims from the given stage."""
    store = SourceStore()
    store.add(_make_claim("Claim A", "ingestion"))
    store.add(_make_claim("Claim B", "stack_mapping"))
    store.add(_make_claim("Claim C", "ingestion"))

    ingestion_claims = store.for_stage("ingestion")
    assert len(ingestion_claims) == 2
    assert all(c.agent_stage == "ingestion" for c in ingestion_claims)


def test_for_stage_returns_empty_for_unknown_stage():
    """SourceStore.for_stage() returns [] for a stage with no claims."""
    store = SourceStore()
    store.add(_make_claim("Claim A", "ingestion"))
    assert store.for_stage("orchestrator") == []


def test_unverified_returns_only_unverified():
    """SourceStore.unverified() excludes claims with verified=True."""
    store = SourceStore()
    store.add(_make_claim("Unverified claim", "ingestion", verified=False))
    store.add(_make_claim("Verified claim", "ingestion", verified=True))

    unverified = store.unverified()
    assert len(unverified) == 1
    assert unverified[0].claim == "Unverified claim"


def test_all_verified_true_when_all_verified():
    """SourceStore.all_verified() returns True when every claim is verified."""
    store = SourceStore()
    store.add(_make_claim("Claim A", "ingestion", verified=True))
    store.add(_make_claim("Claim B", "stack_mapping", verified=True))
    assert store.all_verified() is True


def test_all_verified_false_when_any_unverified():
    """SourceStore.all_verified() returns False if any claim is unverified."""
    store = SourceStore()
    store.add(_make_claim("Claim A", "ingestion", verified=True))
    store.add(_make_claim("Claim B", "stack_mapping", verified=False))
    assert store.all_verified() is False


def test_all_verified_true_for_empty_store():
    """SourceStore.all_verified() returns True vacuously for an empty store."""
    store = SourceStore()
    assert store.all_verified() is True
