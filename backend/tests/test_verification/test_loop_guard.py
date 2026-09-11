"""
Unit tests for app.verification.recalibration — LoopGuard (Phase 7.5.3).

Covers:
  Construction
  - default max_retries is LOOP_GUARD_MAX_RETRIES (2)
  - custom max_retries is stored correctly
  - max_retries=0 raises ValueError

  record()
  - increments counter from 0 to 1 on first call
  - increments to 2 on second call for the same pair
  - returns the new count (not the old one)
  - different pairs have independent counters (core isolation requirement)
  - empty/invalid stage pair arguments raise ValueError

  cap_exceeded()
  - returns False before any record() calls (0 < 2)
  - returns False after 1 record() call (1 < 2)
  - returns True after 2 record() calls (2 >= 2)  ← cap hit
  - a cap hit on pair A does NOT affect pair B (cross-pair isolation)
  - works correctly with a custom cap of 1
  - works correctly with a custom cap of 3

  iteration_count()
  - returns 0 for a never-recorded pair
  - returns current count accurately
  - invalid args raise ValueError

  all_counts()
  - returns empty dict on fresh guard
  - reflects all recorded pairs
  - returned dict is a copy (mutation does not affect guard state)

  Integration scenario
  - two pairs loop independently; one hits cap while other stays under
  - simulates the TASKS.md "does not reset across unrelated stage pairs"
    requirement explicitly
"""

import pytest

from app.verification.recalibration import LOOP_GUARD_MAX_RETRIES, LoopGuard


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SM = "stack_mapping"
ING = "ingestion"
SG = "scenario_generation"
OP = "outcome_prediction"


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestLoopGuardConstruction:
    def test_default_max_retries_is_module_constant(self):
        guard = LoopGuard()
        assert guard.max_retries == LOOP_GUARD_MAX_RETRIES

    def test_module_constant_is_two(self):
        """The task spec says cap == 2; verify the constant itself."""
        assert LOOP_GUARD_MAX_RETRIES == 2

    def test_custom_max_retries_stored(self):
        guard = LoopGuard(max_retries=5)
        assert guard.max_retries == 5

    def test_max_retries_one_is_valid(self):
        guard = LoopGuard(max_retries=1)
        assert guard.max_retries == 1

    def test_max_retries_zero_raises(self):
        with pytest.raises(ValueError, match="max_retries"):
            LoopGuard(max_retries=0)

    def test_max_retries_negative_raises(self):
        with pytest.raises(ValueError, match="max_retries"):
            LoopGuard(max_retries=-1)

    def test_starts_with_empty_counts(self):
        guard = LoopGuard()
        assert guard.all_counts() == {}


# ---------------------------------------------------------------------------
# record()
# ---------------------------------------------------------------------------

class TestLoopGuardRecord:
    def test_first_record_returns_one(self):
        guard = LoopGuard()
        count = guard.record(SM, ING)
        assert count == 1

    def test_second_record_returns_two(self):
        guard = LoopGuard()
        guard.record(SM, ING)
        count = guard.record(SM, ING)
        assert count == 2

    def test_third_record_returns_three(self):
        """record() keeps counting beyond the cap — cap_exceeded() is what blocks."""
        guard = LoopGuard()
        guard.record(SM, ING)
        guard.record(SM, ING)
        count = guard.record(SM, ING)
        assert count == 3

    def test_returns_new_count_not_old(self):
        """record() must return the post-increment value."""
        guard = LoopGuard()
        assert guard.record(SM, ING) == 1
        assert guard.record(SM, ING) == 2

    def test_different_pairs_counted_independently(self):
        """Recording pair A does not affect pair B's counter."""
        guard = LoopGuard()
        guard.record(SM, ING)
        guard.record(SM, ING)
        # Pair B hasn't been touched yet
        count_b = guard.record(SG, SM)
        assert count_b == 1
        # And pair A is still at 2
        assert guard.iteration_count(SM, ING) == 2

    def test_empty_from_stage_raises(self):
        guard = LoopGuard()
        with pytest.raises(ValueError, match="from_stage"):
            guard.record("", ING)

    def test_whitespace_from_stage_raises(self):
        guard = LoopGuard()
        with pytest.raises(ValueError, match="from_stage"):
            guard.record("   ", ING)

    def test_empty_to_stage_raises(self):
        guard = LoopGuard()
        with pytest.raises(ValueError, match="to_stage"):
            guard.record(SM, "")

    def test_same_stage_raises(self):
        guard = LoopGuard()
        with pytest.raises(ValueError, match="from_stage and to_stage must differ"):
            guard.record(SM, SM)


# ---------------------------------------------------------------------------
# cap_exceeded()
# ---------------------------------------------------------------------------

class TestLoopGuardCapExceeded:
    def test_false_before_any_record(self):
        guard = LoopGuard()
        assert guard.cap_exceeded(SM, ING) is False

    def test_false_after_one_record(self):
        guard = LoopGuard()
        guard.record(SM, ING)
        assert guard.cap_exceeded(SM, ING) is False

    def test_true_after_two_records_default_cap(self):
        """After 2 records with cap=2, cap_exceeded must return True."""
        guard = LoopGuard()
        guard.record(SM, ING)
        guard.record(SM, ING)
        assert guard.cap_exceeded(SM, ING) is True

    def test_cap_hit_on_pair_a_does_not_affect_pair_b(self):
        """Core isolation: cap on (SM, ING) must not bleed into (SG, SM)."""
        guard = LoopGuard()
        guard.record(SM, ING)
        guard.record(SM, ING)
        assert guard.cap_exceeded(SM, ING) is True       # pair A: capped
        assert guard.cap_exceeded(SG, SM) is False       # pair B: untouched

    def test_cap_hit_on_pair_b_does_not_affect_pair_a(self):
        """Symmetrical check: cap on pair B doesn't reset pair A."""
        guard = LoopGuard()
        guard.record(SM, ING)                            # pair A: 1
        guard.record(SG, SM)
        guard.record(SG, SM)                             # pair B: capped at 2
        assert guard.cap_exceeded(SG, SM) is True
        assert guard.cap_exceeded(SM, ING) is False      # pair A still at 1

    def test_multiple_independent_pairs_all_reach_cap_independently(self):
        guard = LoopGuard()
        pairs = [(SM, ING), (SG, SM), (OP, SG)]
        for pair in pairs:
            guard.record(*pair)
            guard.record(*pair)
        for pair in pairs:
            assert guard.cap_exceeded(*pair) is True

    def test_custom_cap_one_exceeded_after_one_record(self):
        guard = LoopGuard(max_retries=1)
        guard.record(SM, ING)
        assert guard.cap_exceeded(SM, ING) is True

    def test_custom_cap_one_not_exceeded_before_any_record(self):
        guard = LoopGuard(max_retries=1)
        assert guard.cap_exceeded(SM, ING) is False

    def test_custom_cap_three_not_exceeded_after_two_records(self):
        guard = LoopGuard(max_retries=3)
        guard.record(SM, ING)
        guard.record(SM, ING)
        assert guard.cap_exceeded(SM, ING) is False

    def test_custom_cap_three_exceeded_after_three_records(self):
        guard = LoopGuard(max_retries=3)
        guard.record(SM, ING)
        guard.record(SM, ING)
        guard.record(SM, ING)
        assert guard.cap_exceeded(SM, ING) is True

    def test_invalid_args_raise(self):
        guard = LoopGuard()
        with pytest.raises(ValueError):
            guard.cap_exceeded("", ING)
        with pytest.raises(ValueError):
            guard.cap_exceeded(SM, SM)


# ---------------------------------------------------------------------------
# iteration_count()
# ---------------------------------------------------------------------------

class TestLoopGuardIterationCount:
    def test_zero_for_never_recorded_pair(self):
        guard = LoopGuard()
        assert guard.iteration_count(SM, ING) == 0

    def test_one_after_one_record(self):
        guard = LoopGuard()
        guard.record(SM, ING)
        assert guard.iteration_count(SM, ING) == 1

    def test_two_after_two_records(self):
        guard = LoopGuard()
        guard.record(SM, ING)
        guard.record(SM, ING)
        assert guard.iteration_count(SM, ING) == 2

    def test_unrelated_pair_still_zero(self):
        guard = LoopGuard()
        guard.record(SM, ING)
        guard.record(SM, ING)
        assert guard.iteration_count(SG, SM) == 0

    def test_invalid_args_raise(self):
        guard = LoopGuard()
        with pytest.raises(ValueError):
            guard.iteration_count("", ING)
        with pytest.raises(ValueError):
            guard.iteration_count(SM, SM)


# ---------------------------------------------------------------------------
# all_counts()
# ---------------------------------------------------------------------------

class TestLoopGuardAllCounts:
    def test_empty_on_fresh_guard(self):
        guard = LoopGuard()
        assert guard.all_counts() == {}

    def test_reflects_all_recorded_pairs(self):
        guard = LoopGuard()
        guard.record(SM, ING)
        guard.record(SM, ING)
        guard.record(SG, SM)
        counts = guard.all_counts()
        assert counts == {(SM, ING): 2, (SG, SM): 1}

    def test_returned_dict_is_a_copy(self):
        """Mutating the returned dict must not alter the guard's internal state."""
        guard = LoopGuard()
        guard.record(SM, ING)
        snapshot = guard.all_counts()
        snapshot[(SM, ING)] = 999          # mutate copy
        assert guard.iteration_count(SM, ING) == 1  # internal unchanged

    def test_absent_pairs_have_no_key(self):
        """Pairs never recorded are absent from all_counts() (not present as 0)."""
        guard = LoopGuard()
        guard.record(SM, ING)
        counts = guard.all_counts()
        assert (SG, SM) not in counts


# ---------------------------------------------------------------------------
# Integration scenario — the key TASKS.md requirement
# ---------------------------------------------------------------------------

class TestLoopGuardIntegration:
    def test_two_pairs_loop_independently_one_hits_cap_other_does_not(self):
        """
        Simulates the exact scenario from the task description:
        'does not reset across unrelated stage pairs'.

        Pair A (stack_mapping → ingestion):   loops 2× → cap hit
        Pair B (scenario_generation → stack_mapping): loops 1× → still allowed
        """
        guard = LoopGuard()

        # Pair A: first attempt
        count_a1 = guard.record(SM, ING)
        assert count_a1 == 1
        assert guard.cap_exceeded(SM, ING) is False

        # Pair B: first attempt (independent)
        count_b1 = guard.record(SG, SM)
        assert count_b1 == 1
        assert guard.cap_exceeded(SG, SM) is False

        # Pair A: second attempt — hits cap
        count_a2 = guard.record(SM, ING)
        assert count_a2 == 2
        assert guard.cap_exceeded(SM, ING) is True   # ← capped

        # Pair B: still under its own cap (only 1 loop so far)
        assert guard.cap_exceeded(SG, SM) is False   # ← NOT affected by A's cap

        # Final state audit
        counts = guard.all_counts()
        assert counts[(SM, ING)] == 2
        assert counts[(SG, SM)] == 1

    def test_simulate_full_pipeline_recalibration_sequence(self):
        """
        Walk through a realistic multi-stage recalibration sequence:
          1. stack_mapping → ingestion × 2  (cap hit)
          2. scenario_generation → stack_mapping × 1 (still allowed)
          3. outcome_prediction → scenario_generation × 2 (cap hit)
        Verify each pair's cap state at the end.
        """
        guard = LoopGuard()

        # stack_mapping → ingestion loops
        guard.record(SM, ING)
        guard.record(SM, ING)
        assert guard.cap_exceeded(SM, ING) is True

        # scenario_generation → stack_mapping loop
        guard.record(SG, SM)
        assert guard.cap_exceeded(SG, SM) is False

        # outcome_prediction → scenario_generation loops
        guard.record(OP, SG)
        guard.record(OP, SG)
        assert guard.cap_exceeded(OP, SG) is True

        # Pair B should still be uncapped
        assert guard.cap_exceeded(SG, SM) is False

        all_c = guard.all_counts()
        assert all_c[(SM, ING)] == 2
        assert all_c[(SG, SM)] == 1
        assert all_c[(OP, SG)] == 2
