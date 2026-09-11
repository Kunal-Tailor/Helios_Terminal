"""
Unit tests for app.verification.recalibration — RecalibrationRequest (Phase 7.5.1).

Covers:
  - Valid construction with both reason values ("insufficient", "unverified")
  - __post_init__ validation: empty from_stage, empty to_stage, same stage names,
    invalid reason, empty gap_description, iteration_count < 1
  - to_dict() serialises all five fields as JSON-native types
  - from_dict() round-trips back to an equal RecalibrationRequest
  - from_dict() raises KeyError on missing field
  - from_dict() re-runs validation (invalid reason raises ValueError)
  - iteration_count is preserved exactly (boundary: 1, arbitrary positive int)
"""

import pytest

from app.verification.recalibration import RecalibrationRequest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make(**overrides) -> RecalibrationRequest:
    """Return a valid RecalibrationRequest, with any field overridden by kwargs."""
    defaults = dict(
        from_stage="stack_mapping",
        to_stage="ingestion",
        reason="insufficient",
        gap_description="No surviving AI-stack layers after relevance filtering.",
        iteration_count=1,
    )
    defaults.update(overrides)
    return RecalibrationRequest(**defaults)


# ---------------------------------------------------------------------------
# Valid construction
# ---------------------------------------------------------------------------

class TestConstruction:
    def test_valid_insufficient(self):
        """RecalibrationRequest constructs without error for reason='insufficient'."""
        req = _make(reason="insufficient")
        assert req.from_stage == "stack_mapping"
        assert req.to_stage == "ingestion"
        assert req.reason == "insufficient"
        assert req.gap_description == "No surviving AI-stack layers after relevance filtering."
        assert req.iteration_count == 1

    def test_valid_unverified(self):
        """RecalibrationRequest constructs without error for reason='unverified'."""
        req = _make(reason="unverified", from_stage="scenario_generation", to_stage="stack_mapping")
        assert req.reason == "unverified"
        assert req.from_stage == "scenario_generation"
        assert req.to_stage == "stack_mapping"

    def test_iteration_count_boundary_one(self):
        """iteration_count=1 is the minimum valid value and is accepted."""
        req = _make(iteration_count=1)
        assert req.iteration_count == 1

    def test_iteration_count_arbitrary_positive(self):
        """iteration_count accepts any integer >= 1."""
        req = _make(iteration_count=42)
        assert req.iteration_count == 42

    def test_gap_description_preserved_exactly(self):
        """gap_description is stored verbatim, including whitespace and punctuation."""
        desc = "  Missing vendor data: no known GPU suppliers in context.  "
        req = _make(gap_description=desc)
        assert req.gap_description == desc


# ---------------------------------------------------------------------------
# Validation — __post_init__ rejects bad inputs
# ---------------------------------------------------------------------------

class TestValidation:
    def test_empty_from_stage_raises(self):
        with pytest.raises(ValueError, match="from_stage"):
            _make(from_stage="")

    def test_whitespace_only_from_stage_raises(self):
        with pytest.raises(ValueError, match="from_stage"):
            _make(from_stage="   ")

    def test_empty_to_stage_raises(self):
        with pytest.raises(ValueError, match="to_stage"):
            _make(to_stage="")

    def test_whitespace_only_to_stage_raises(self):
        with pytest.raises(ValueError, match="to_stage"):
            _make(to_stage="   ")

    def test_same_from_and_to_stage_raises(self):
        """A stage cannot recalibrate back to itself."""
        with pytest.raises(ValueError, match="from_stage and to_stage must differ"):
            _make(from_stage="ingestion", to_stage="ingestion")

    def test_invalid_reason_raises(self):
        with pytest.raises(ValueError, match="reason must be"):
            _make(reason="wrong")  # type: ignore[arg-type]

    def test_empty_gap_description_raises(self):
        with pytest.raises(ValueError, match="gap_description"):
            _make(gap_description="")

    def test_whitespace_only_gap_description_raises(self):
        with pytest.raises(ValueError, match="gap_description"):
            _make(gap_description="   ")

    def test_iteration_count_zero_raises(self):
        with pytest.raises(ValueError, match="iteration_count"):
            _make(iteration_count=0)

    def test_iteration_count_negative_raises(self):
        with pytest.raises(ValueError, match="iteration_count"):
            _make(iteration_count=-1)


# ---------------------------------------------------------------------------
# Serialisation — to_dict()
# ---------------------------------------------------------------------------

class TestToDict:
    def test_to_dict_contains_all_five_fields(self):
        """to_dict() output has exactly the five documented keys."""
        req = _make()
        d = req.to_dict()
        assert set(d.keys()) == {"from_stage", "to_stage", "reason", "gap_description", "iteration_count"}

    def test_to_dict_values_match_attributes(self):
        """to_dict() values match the RecalibrationRequest attributes exactly."""
        req = _make(
            from_stage="outcome_prediction",
            to_stage="scenario_generation",
            reason="unverified",
            gap_description="Three upstream claims failed verification.",
            iteration_count=2,
        )
        d = req.to_dict()
        assert d["from_stage"] == "outcome_prediction"
        assert d["to_stage"] == "scenario_generation"
        assert d["reason"] == "unverified"
        assert d["gap_description"] == "Three upstream claims failed verification."
        assert d["iteration_count"] == 2

    def test_to_dict_values_are_json_native_types(self):
        """to_dict() contains only str and int — no custom objects."""
        req = _make()
        d = req.to_dict()
        assert isinstance(d["from_stage"], str)
        assert isinstance(d["to_stage"], str)
        assert isinstance(d["reason"], str)
        assert isinstance(d["gap_description"], str)
        assert isinstance(d["iteration_count"], int)

    def test_to_dict_does_not_mutate_original(self):
        """Calling to_dict() does not change the RecalibrationRequest's own fields."""
        req = _make(iteration_count=3)
        req.to_dict()
        assert req.iteration_count == 3


# ---------------------------------------------------------------------------
# Deserialisation — from_dict()
# ---------------------------------------------------------------------------

class TestFromDict:
    def test_round_trip_insufficient(self):
        """from_dict(to_dict()) produces an equal RecalibrationRequest."""
        original = _make(reason="insufficient", iteration_count=2)
        restored = RecalibrationRequest.from_dict(original.to_dict())
        assert restored == original

    def test_round_trip_unverified(self):
        """Round-trip works for reason='unverified' as well."""
        original = _make(
            from_stage="dependency_diagnosis",
            to_stage="outcome_prediction",
            reason="unverified",
            gap_description="Lock-in analysis references trajectory not present in outcomes.",
            iteration_count=1,
        )
        restored = RecalibrationRequest.from_dict(original.to_dict())
        assert restored == original

    def test_from_dict_raises_key_error_on_missing_field(self):
        """from_dict() raises KeyError when a required key is absent."""
        d = _make().to_dict()
        del d["gap_description"]
        with pytest.raises(KeyError):
            RecalibrationRequest.from_dict(d)

    def test_from_dict_reruns_validation_invalid_reason(self):
        """from_dict() re-runs __post_init__ so an invalid reason still raises ValueError."""
        d = _make().to_dict()
        d["reason"] = "bad_reason"
        with pytest.raises(ValueError, match="reason must be"):
            RecalibrationRequest.from_dict(d)

    def test_from_dict_reruns_validation_same_stage(self):
        """from_dict() raises ValueError when from_stage == to_stage."""
        d = _make().to_dict()
        d["to_stage"] = d["from_stage"]
        with pytest.raises(ValueError, match="from_stage and to_stage must differ"):
            RecalibrationRequest.from_dict(d)
