"""
Unit tests for app.verification.verifier.

Covers:
  - verify() passes a known-good claim/source pair
  - verify() fails a known-bad claim/source pair
  - verify() sets claim.verified=True on pass, leaves False on fail
  - verify() handles an empty/stop-word-only claim gracefully
  - verify() includes missing keywords in the failure reason
  - verify_stage() verifies all claims for a given stage
  - verify_stage() returns [] for a stage with no claims
  - _extract_keywords() is tested indirectly through verify() outcomes
"""

import pytest

from app.verification.source_store import SourceStore, SourcedClaim
from app.verification.verifier import VerificationResult, verify, verify_stage


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _claim(claim_text: str, source_text: str, stage: str = "ingestion") -> SourcedClaim:
    return SourcedClaim(
        claim=claim_text,
        source_text=source_text,
        agent_stage=stage,
    )


# ---------------------------------------------------------------------------
# Known-good claim/source pair — claim keywords ARE present in source
# ---------------------------------------------------------------------------

def test_verify_passes_known_good_pair():
    """A claim whose key terms all appear in the source should pass."""
    sc = _claim(
        claim_text="DeepSeek obtained a Hugging Face model licence for its LLM weights.",
        source_text=(
            "DeepSeek has published its LLM weights on Hugging Face under a "
            "model licence that restricts commercial redistribution."
        ),
    )
    result = verify(sc)
    assert result.passed is True
    assert result.confidence >= 0.6


def test_verify_sets_verified_true_on_pass():
    """verify() mutates claim.verified to True when the check passes."""
    sc = _claim(
        claim_text="DeepSeek obtained a Hugging Face model licence for its LLM weights.",
        source_text=(
            "DeepSeek has published its LLM weights on Hugging Face under a "
            "model licence that restricts commercial redistribution."
        ),
    )
    assert sc.verified is False
    verify(sc)
    assert sc.verified is True


def test_verify_passes_hyphenated_compound_word():
    """verify() passes when claim or source uses hyphenated compound words vs space-separated."""
    sc = _claim(
        claim_text="Indian Army tested an AI-powered autonomous drone interceptor.",
        source_text="India's AI powered autonomous drone interceptor cleared Army trials.",
    )
    result = verify(sc)
    assert result.passed is True
    assert result.confidence >= 0.6


def test_verify_passes_comma_formatted_number():
    """verify() passes when claim uses unformatted number and source has comma formatting."""
    sc = _claim(
        claim_text="The army deployed 30000 drones across the border.",
        source_text="The army deployed 30,000 drones across the border.",
    )
    result = verify(sc)
    assert result.passed is True
    assert result.confidence >= 0.6


def test_verify_passes_lakh_crore_equivalence():
    """verify() passes when numbers are expressed in lakh or crore equivalence."""
    sc = _claim(
        claim_text="The roadmap targets 100,000 trained personnel and 137000000 rupees.",
        source_text="The roadmap targets training one lakh personnel and 137 crore emergency procurement.",
    )
    result = verify(sc)
    assert result.passed is True
    assert result.confidence >= 0.6

def test_verify_fails_known_bad_pair():
    """A claim whose key terms are absent from the source should fail."""
    sc = _claim(
        claim_text="The vendor holds an exclusive US Department of Defense contract.",
        source_text=(
            "The company primarily sells consumer electronics in South-East Asia "
            "and has no disclosed government contracts."
        ),
    )
    result = verify(sc)
    assert result.passed is False
    assert result.confidence < 0.6


def test_verify_leaves_verified_false_on_fail():
    """verify() does NOT set claim.verified when the check fails."""
    sc = _claim(
        claim_text="The vendor holds an exclusive US Department of Defense contract.",
        source_text=(
            "The company primarily sells consumer electronics in South-East Asia "
            "and has no disclosed government contracts."
        ),
    )
    verify(sc)
    assert sc.verified is False


# ---------------------------------------------------------------------------
# Result structure
# ---------------------------------------------------------------------------

def test_verify_result_contains_claim_and_stage():
    """VerificationResult carries the original claim text and agent_stage."""
    sc = _claim(
        claim_text="NVIDIA manufactures GPUs used in AI training.",
        source_text="NVIDIA is a leading GPU manufacturer widely used for AI workloads.",
        stage="stack_mapping",
    )
    result = verify(sc)
    assert result.claim == sc.claim
    assert result.agent_stage == "stack_mapping"


def test_verify_result_reason_is_non_empty():
    """VerificationResult.reason is always a non-empty string."""
    sc = _claim(
        claim_text="NVIDIA manufactures GPUs.",
        source_text="NVIDIA is a GPU company.",
    )
    result = verify(sc)
    assert isinstance(result.reason, str)
    assert len(result.reason) > 0


def test_verify_failure_reason_mentions_missing_keywords():
    """On failure the reason string references missing keywords."""
    sc = _claim(
        claim_text="The vendor holds a Pentagon contract worth billions.",
        source_text="The company sells B2C products and has no government ties.",
    )
    result = verify(sc)
    assert result.passed is False
    assert "Missing keywords" in result.reason


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_verify_passes_claim_with_only_stop_words():
    """A claim reduced to only stop words has no keywords — passes by default."""
    sc = _claim(
        claim_text="it is and the or",   # all stop words
        source_text="completely unrelated source text about something else entirely",
    )
    result = verify(sc)
    assert result.passed is True
    assert result.confidence == 1.0


def test_verify_passes_empty_claim():
    """An empty claim string has no keywords — passes by default."""
    sc = _claim(claim_text="", source_text="some source text")
    result = verify(sc)
    assert result.passed is True


def test_verify_confidence_is_between_0_and_1():
    """VerificationResult.confidence is always in [0.0, 1.0]."""
    sc = _claim(
        claim_text="quantum computing breakthrough enables sub-second inference",
        source_text="classical hardware improvements continue",
    )
    result = verify(sc)
    assert 0.0 <= result.confidence <= 1.0


# ---------------------------------------------------------------------------
# verify_stage()
# ---------------------------------------------------------------------------

def test_verify_stage_verifies_all_claims_for_stage():
    """verify_stage() returns one result per claim in the specified stage."""
    store = SourceStore()
    store.add(_claim(
        claim_text="NVIDIA manufactures GPUs used in AI training.",
        source_text="NVIDIA is a GPU manufacturer used in AI workloads.",
        stage="stack_mapping",
    ))
    store.add(_claim(
        claim_text="Model weights are stored on Hugging Face.",
        source_text="The model weights are hosted on Hugging Face Hub.",
        stage="stack_mapping",
    ))
    store.add(_claim(
        claim_text="This claim belongs to ingestion.",
        source_text="ingestion source",
        stage="ingestion",
    ))

    results = verify_stage(store, "stack_mapping")
    assert len(results) == 2
    assert all(isinstance(r, VerificationResult) for r in results)


def test_verify_stage_returns_empty_for_unknown_stage():
    """verify_stage() returns [] when no claims exist for the given stage."""
    store = SourceStore()
    store.add(_claim("Some claim.", "Some source.", stage="ingestion"))
    results = verify_stage(store, "orchestrator")
    assert results == []


def test_verify_stage_updates_verified_flags_in_store():
    """verify_stage() mutates claim.verified in the SourceStore in-place."""
    store = SourceStore()
    store.add(_claim(
        claim_text="NVIDIA GPU hardware is widely used for AI model training workloads.",
        source_text=(
            "NVIDIA GPU hardware dominates the AI training market and is widely used "
            "for large-scale model training workloads across cloud providers."
        ),
        stage="stack_mapping",
    ))
    assert not store.all_verified()
    verify_stage(store, "stack_mapping")
    assert store.all_verified()


# ---------------------------------------------------------------------------
# ensure_grounded_claim()
# ---------------------------------------------------------------------------

def test_ensure_grounded_claim_keeps_passing_claim():
    """ensure_grounded_claim returns the original claim when it already passes."""
    from app.verification.verifier import ensure_grounded_claim

    claim = "NVIDIA manufactures GPUs used in AI training."
    source = "NVIDIA is a leading GPU manufacturer widely used for AI workloads and training."
    assert ensure_grounded_claim(claim, source) == claim


def test_ensure_grounded_claim_rewrites_invented_paraphrase():
    """Invented grounded_in terms are replaced with a verifiable prior-stage fact."""
    from app.verification.verifier import ensure_grounded_claim

    invented = (
        "Managing and processing petabytes of proprietary multi-camera autonomous "
        "driving video datasets necessitates massive distributed compute infrastructure."
    )
    prior_fact = (
        "Tesla's established strategy relies on proprietary, in-house scaling, "
        "advanced computer vision architectures, and deep integration with its own "
        "vehicle hardware and data collection infrastructure."
    )
    source = f"Strategy: in-house scaling. {prior_fact}"
    fixed = ensure_grounded_claim(invented, source, fallbacks=[prior_fact])
    result = verify(_claim(fixed, source, stage="scenario_generation"))
    assert result.passed is True
    assert "petabytes" not in fixed.lower()


def test_ensure_grounded_claim_falls_back_to_source_fragment():
    """When no fallback passes, a source fragment is selected."""
    from app.verification.verifier import ensure_grounded_claim

    invented = "Petabyte-scale orbital laser communication arrays enable FTL inference."
    source = (
        "Core components of Tesla's existing AI infrastructure include HydraNet, "
        "a multi-task learning architecture that processes input from eight surround-cameras."
    )
    fixed = ensure_grounded_claim(invented, source, fallbacks=[])
    result = verify(_claim(fixed, source, stage="scenario_generation"))
    assert result.passed is True
    assert "HydraNet" in fixed or "surround" in fixed.lower() or "cameras" in fixed.lower()
