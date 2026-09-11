"""
Recalibration layer — sufficiency-check data structures and backward-routing logic.

This module is intentionally distinct from verifier.py:
  - verifier.py answers "is this claim grounded in its source?" (correctness)
  - recalibration.py answers "did the upstream stage give enough to proceed?" (sufficiency)

Both are cross-cutting gates that sit between every agent handoff, but they ask
different questions and fire independently.

Phase 7.5.1 — RecalibrationRequest data structure only.
Sufficiency-check functions, loop-guard, and context accumulation are added in
subsequent tasks (7.5.2 – 7.5.4).

Public API (this task)
-----------------------
    RecalibrationReason   — Literal type: "insufficient" | "unverified"
    RecalibrationRequest  — Data structure emitted when a stage decides it cannot
                            proceed with what it received from an upstream stage.

Usage
-----
    from app.verification.recalibration import RecalibrationRequest

    request = RecalibrationRequest(
        from_stage="stack_mapping",
        to_stage="ingestion",
        reason="insufficient",
        gap_description="No surviving AI-stack layers after relevance filtering.",
        iteration_count=1,
    )
    payload = request.to_dict()   # serialise for pipeline state / API trail
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal


# ---------------------------------------------------------------------------
# Reason type
# ---------------------------------------------------------------------------

RecalibrationReason = Literal["insufficient", "unverified"]
"""The category of failure that triggered a recalibration backward-route.

``"insufficient"``
    The upstream stage produced output that is formally valid but does not
    contain enough usable signal for the current stage to proceed meaningfully.
    Example: Stack-Mapping returned 0 surviving layers, so Scenario-Generation
    cannot enumerate options.

``"unverified"``
    One or more of the upstream stage's claims failed the verification gate
    (Phase 4 / 6.2), and the current stage is refusing to consume unverified
    input rather than propagating a bad signal forward.
"""


# ---------------------------------------------------------------------------
# RecalibrationRequest
# ---------------------------------------------------------------------------

@dataclass
class RecalibrationRequest:
    """Emitted by a stage that cannot proceed with what it received upstream.

    A ``RecalibrationRequest`` is the signal that turns the pipeline from a
    straight sequence into a conditional graph: the pipeline router reads it
    and re-invokes the target stage (``to_stage``) scoped to the
    ``gap_description``, then re-runs the requesting stage with the new output.

    Attributes
    ----------
    from_stage:
        The stage that detected insufficiency and is requesting recalibration.
        Must be a recognised pipeline stage name
        (e.g. ``"stack_mapping"``, ``"scenario_generation"``).
    to_stage:
        The upstream stage that should be re-invoked to fill the gap.
        Must be a stage that ran *before* ``from_stage`` in the current
        execution (the pipeline router enforces this to prevent forward loops).
    reason:
        Category of failure — ``"insufficient"`` (not enough usable signal) or
        ``"unverified"`` (upstream claims failed verification).
    gap_description:
        A concise, human-readable description of exactly what is missing.
        The re-invoked stage receives this as a scoping hint so it only
        regenerates the missing part rather than restarting from scratch.
        Example: ``"No surviving AI-stack layers after relevance filtering."``
    iteration_count:
        How many times this specific ``(from_stage, to_stage)`` pair has
        already looped back.  Starts at 1 on the first recalibration.
        The loop-guard (Phase 7.5.3) reads this to enforce the retry cap.
    """

    from_stage: str
    to_stage: str
    reason: RecalibrationReason
    gap_description: str
    iteration_count: int

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def __post_init__(self) -> None:
        """Validate field values on construction.

        Raises
        ------
        ValueError
            If any field violates its documented contract.
        """
        if not self.from_stage or not self.from_stage.strip():
            raise ValueError("from_stage must be a non-empty string.")
        if not self.to_stage or not self.to_stage.strip():
            raise ValueError("to_stage must be a non-empty string.")
        if self.from_stage == self.to_stage:
            raise ValueError(
                f"from_stage and to_stage must differ; both are '{self.from_stage}'."
            )
        if self.reason not in ("insufficient", "unverified"):
            raise ValueError(
                f"reason must be 'insufficient' or 'unverified'; got '{self.reason}'."
            )
        if not self.gap_description or not self.gap_description.strip():
            raise ValueError("gap_description must be a non-empty string.")
        if self.iteration_count < 1:
            raise ValueError(
                f"iteration_count must be >= 1; got {self.iteration_count}."
            )

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Return a plain-dict representation suitable for JSON serialisation.

        The returned dict contains exactly the five documented fields, all as
        JSON-native types (str, int).  This is the format stored in the
        pipeline's ``recalibration_trail`` (Phase 7.5.11).

        Returns
        -------
        dict
            ``{"from_stage": ..., "to_stage": ..., "reason": ...,
               "gap_description": ..., "iteration_count": ...}``
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "RecalibrationRequest":
        """Reconstruct a :class:`RecalibrationRequest` from a plain dict.

        Useful when deserialising from a stored pipeline state or API response.

        Parameters
        ----------
        data:
            A dict with keys matching the five dataclass fields.

        Returns
        -------
        RecalibrationRequest
            A fully validated instance.

        Raises
        ------
        KeyError
            If a required key is missing from *data*.
        ValueError
            If a field value is invalid (delegated to :meth:`__post_init__`).
        """
        return cls(
            from_stage=data["from_stage"],
            to_stage=data["to_stage"],
            reason=data["reason"],
            gap_description=data["gap_description"],
            iteration_count=data["iteration_count"],
        )
