"""
Recalibration layer — sufficiency-check data structures and backward-routing logic.

This module is intentionally distinct from verifier.py:
  - verifier.py answers "is this claim grounded in its source?" (correctness)
  - recalibration.py answers "did the upstream stage give enough to proceed?" (sufficiency)

Both are cross-cutting gates that sit between every agent handoff, but they ask
different questions and fire independently.

Phase 7.5.1 — RecalibrationRequest data structure.
Phase 7.5.2 — Sufficiency-check functions (one per pipeline stage).
Phase 7.5.3 — LoopGuard: per-(from_stage, to_stage) iteration counter, capped at 2 retries.
Phase 7.5.4 — accumulate_ingestion_context: merge re-ingestion output into existing context
               by appending (not replacing), so prior context survives recalibration.

Public API
-----------
    RecalibrationReason   — Literal type: "insufficient" | "unverified"
    RecalibrationRequest  — Data structure emitted when a stage decides it cannot
                            proceed with what it received from an upstream stage.
    SufficiencyResult     — Outcome of a per-stage sufficiency check (mirrors
                            VerificationResult in verifier.py).
    LoopGuard             — Stateful per-pipeline-run counter that tracks how many
                            times each (from_stage, to_stage) pair has looped back
                            and enforces a configurable retry cap (default: 2).
    accumulate_ingestion_context(existing, new_partial) -> IngestionContext
                          — Merge a targeted re-ingestion result into an existing
                            IngestionContext without discarding the original data.
    check_sufficiency_stack_mapping(stack_scope)         -> SufficiencyResult
    check_sufficiency_scenario_generation(scenario_set)  -> SufficiencyResult
    check_sufficiency_outcome_prediction(outcome_set)    -> SufficiencyResult
    check_sufficiency_dependency_diagnosis(diagnosis_set)-> SufficiencyResult
    check_sufficiency_orchestrator(verdict)              -> SufficiencyResult
    check_sufficiency_ingestion(context)                 -> SufficiencyResult

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
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    # Imported only for type annotations; avoids circular imports at runtime since
    # agent modules may eventually import from the verification layer.
    from app.agents.stack_mapping.stack_mapping_agent import StackScope
    from app.agents.scenario_generation.scenario_generation_agent import ScenarioSet
    from app.agents.outcome_prediction.outcome_prediction_agent import OutcomeSet
    from app.agents.dependency_diagnosis.dependency_diagnosis_agent import DiagnosisSet
    from app.agents.orchestrator.orchestrator_agent import OrchestratorVerdict

from app.agents.ingestion.sub_agents.context_synthesis_sub_agent import IngestionContext


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
    provider: str | None = None

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
        d = asdict(self)
        if self.provider is None:
            d.pop("provider", None)
        return d

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
            provider=data.get("provider"),
        )


# ---------------------------------------------------------------------------
# SufficiencyResult — mirrors VerificationResult in verifier.py
# ---------------------------------------------------------------------------

@dataclass
class SufficiencyResult:
    """The outcome of a per-stage sufficiency check.

    Mirrors :class:`~app.verification.verifier.VerificationResult` in structure
    so pipeline code can handle both verification and sufficiency results
    uniformly.

    Attributes
    ----------
    sufficient:
        ``True`` if the stage output meets the minimum threshold to proceed.
    stage:
        The pipeline stage whose output was checked
        (e.g. ``"stack_mapping"``, ``"scenario_generation"``).
    reason:
        Human-readable explanation of the outcome, suitable for audit logs
        and ``RecalibrationRequest.gap_description``.
    detail:
        Optional machine-readable detail (e.g. the count that was below
        threshold) for structured logging.
    """

    sufficient: bool
    stage: str
    reason: str
    detail: str = ""


# ---------------------------------------------------------------------------
# Per-stage sufficiency thresholds (documented constants)
# ---------------------------------------------------------------------------

# Stack-Mapping: must produce at least 2 surviving layers for Scenario-Generation
# to have meaningful scope to enumerate options against.
# 0 layers → nothing to enumerate; 1 layer → only one dimension, too narrow.
_STACK_MAPPING_MIN_LAYERS: int = 2

# Scenario-Generation: must produce at least 2 viable, refined scenarios for
# Outcome-Prediction to compare meaningfully.
# 1 scenario → no comparison; 0 → nothing to predict.
_SCENARIO_GENERATION_MIN_SCENARIOS: int = 2

# Outcome-Prediction: must produce at least 1 OutcomeProjection with a non-None
# trajectory AND at least 1 risk factor.
# A trajectory without risks is an incomplete prediction.
_OUTCOME_MIN_PROJECTIONS_WITH_TRAJECTORY: int = 1
_OUTCOME_MIN_RISK_FACTORS_TOTAL: int = 1

# Dependency-Diagnosis: must produce at least 1 DependencyDiagnosis with at
# least 1 identified dependency.  Generic / empty diagnoses cannot be acted on.
_DEPENDENCY_MIN_DIAGNOSES_WITH_DEPS: int = 1

# Orchestrator: must produce a non-empty verdict summary and at least 1
# key recommendation.  An empty verdict cannot be presented or acted on.
_ORCHESTRATOR_MIN_RECOMMENDATIONS: int = 1

# Ingestion: must produce a non-empty context_summary AND at least 1 key_fact.
# Downstream stages (Stack-Mapping) need factual grounding to work from.
_INGESTION_MIN_KEY_FACTS: int = 1


# ---------------------------------------------------------------------------
# Public sufficiency-check functions (one per pipeline stage)
# ---------------------------------------------------------------------------

def check_sufficiency_stack_mapping(stack_scope: "StackScope") -> SufficiencyResult:
    """Check that Stack-Mapping produced enough surviving layers to proceed.

    Threshold: ``len(stack_scope.layers) >= 2``.

    A single surviving layer is treated as insufficient because
    Scenario-Generation would have only one narrow dimension to enumerate
    options against, producing degenerate or trivially similar scenarios.

    Parameters
    ----------
    stack_scope:
        The :class:`~app.agents.stack_mapping.stack_mapping_agent.StackScope`
        returned by the Stack-Mapping Agent.

    Returns
    -------
    SufficiencyResult
        ``sufficient=True`` if the threshold is met; ``False`` otherwise.
    """
    count = len(stack_scope.layers)
    if count >= _STACK_MAPPING_MIN_LAYERS:
        return SufficiencyResult(
            sufficient=True,
            stage="stack_mapping",
            reason=f"Stack-Mapping produced {count} surviving layers (threshold ≥ {_STACK_MAPPING_MIN_LAYERS}).",
            detail=str(count),
        )
    return SufficiencyResult(
        sufficient=False,
        stage="stack_mapping",
        reason=(
            f"Stack-Mapping produced only {count} surviving layer(s) after relevance filtering "
            f"(threshold ≥ {_STACK_MAPPING_MIN_LAYERS}). "
            "Scenario-Generation cannot enumerate meaningful options without broader stack scope."
        ),
        detail=str(count),
    )


def check_sufficiency_scenario_generation(scenario_set: "ScenarioSet") -> SufficiencyResult:
    """Check that Scenario-Generation produced enough viable scenarios to proceed.

    Threshold: ``len(scenario_set.scenarios) >= 2``.

    A single scenario gives Outcome-Prediction nothing to compare; zero
    scenarios make the entire downstream pipeline vacuous.

    Parameters
    ----------
    scenario_set:
        The :class:`~app.agents.scenario_generation.scenario_generation_agent.ScenarioSet`
        returned by the Scenario-Generation Agent.

    Returns
    -------
    SufficiencyResult
        ``sufficient=True`` if the threshold is met; ``False`` otherwise.
    """
    count = len(scenario_set.scenarios)
    if count >= _SCENARIO_GENERATION_MIN_SCENARIOS:
        return SufficiencyResult(
            sufficient=True,
            stage="scenario_generation",
            reason=f"Scenario-Generation produced {count} viable scenarios (threshold ≥ {_SCENARIO_GENERATION_MIN_SCENARIOS}).",
            detail=str(count),
        )
    return SufficiencyResult(
        sufficient=False,
        stage="scenario_generation",
        reason=(
            f"Scenario-Generation produced only {count} viable scenario(s) after feasibility filtering "
            f"(threshold ≥ {_SCENARIO_GENERATION_MIN_SCENARIOS}). "
            "Outcome-Prediction requires at least two scenarios to produce a meaningful comparison."
        ),
        detail=str(count),
    )


def check_sufficiency_outcome_prediction(outcome_set: "OutcomeSet") -> SufficiencyResult:
    """Check that Outcome-Prediction produced usable projections with trajectories and risks.

    Thresholds:
      - At least 1 :class:`~app.agents.outcome_prediction.outcome_prediction_agent.OutcomeProjection`
        with a non-``None`` trajectory.
      - At least 1 risk factor across all projections combined.

    An outcome with no trajectories has no forward path to diagnose.
    An outcome with no risk factors is analytically empty.

    Parameters
    ----------
    outcome_set:
        The :class:`~app.agents.outcome_prediction.outcome_prediction_agent.OutcomeSet`
        returned by the Outcome-Prediction Agent.

    Returns
    -------
    SufficiencyResult
        ``sufficient=True`` if both thresholds are met; ``False`` otherwise.
    """
    projections_with_trajectory = sum(
        1 for o in outcome_set.outcomes if o.trajectory is not None
    )
    total_risk_factors = sum(len(o.risk_factors) for o in outcome_set.outcomes)

    if (
        projections_with_trajectory >= _OUTCOME_MIN_PROJECTIONS_WITH_TRAJECTORY
        and total_risk_factors >= _OUTCOME_MIN_RISK_FACTORS_TOTAL
    ):
        return SufficiencyResult(
            sufficient=True,
            stage="outcome_prediction",
            reason=(
                f"Outcome-Prediction produced {projections_with_trajectory} projection(s) with trajectories "
                f"and {total_risk_factors} risk factor(s)."
            ),
            detail=f"trajectories={projections_with_trajectory}, risk_factors={total_risk_factors}",
        )

    missing: list[str] = []
    if projections_with_trajectory < _OUTCOME_MIN_PROJECTIONS_WITH_TRAJECTORY:
        missing.append(
            f"only {projections_with_trajectory} projection(s) have a trajectory "
            f"(threshold ≥ {_OUTCOME_MIN_PROJECTIONS_WITH_TRAJECTORY})"
        )
    if total_risk_factors < _OUTCOME_MIN_RISK_FACTORS_TOTAL:
        missing.append(
            f"only {total_risk_factors} risk factor(s) identified across all projections "
            f"(threshold ≥ {_OUTCOME_MIN_RISK_FACTORS_TOTAL})"
        )
    return SufficiencyResult(
        sufficient=False,
        stage="outcome_prediction",
        reason=(
            "Outcome-Prediction output is insufficient for Dependency-Diagnosis: "
            + "; ".join(missing) + "."
        ),
        detail=f"trajectories={projections_with_trajectory}, risk_factors={total_risk_factors}",
    )


def check_sufficiency_dependency_diagnosis(diagnosis_set: "DiagnosisSet") -> SufficiencyResult:
    """Check that Dependency-Diagnosis identified at least one concrete dependency.

    Threshold: at least 1 :class:`~app.agents.dependency_diagnosis.dependency_diagnosis_agent.DependencyDiagnosis`
    in the set has a non-empty ``dependencies`` list.

    A diagnosis set where every path has zero identified dependencies is
    analytically empty — the Orchestrator cannot produce a differentiated verdict.

    Parameters
    ----------
    diagnosis_set:
        The :class:`~app.agents.dependency_diagnosis.dependency_diagnosis_agent.DiagnosisSet`
        returned by the Dependency-Diagnosis Agent.

    Returns
    -------
    SufficiencyResult
        ``sufficient=True`` if the threshold is met; ``False`` otherwise.
    """
    diagnoses_with_deps = sum(
        1 for d in diagnosis_set.diagnoses if d.dependencies
    )
    if diagnoses_with_deps >= _DEPENDENCY_MIN_DIAGNOSES_WITH_DEPS:
        return SufficiencyResult(
            sufficient=True,
            stage="dependency_diagnosis",
            reason=(
                f"Dependency-Diagnosis identified dependencies in {diagnoses_with_deps} path(s) "
                f"(threshold ≥ {_DEPENDENCY_MIN_DIAGNOSES_WITH_DEPS})."
            ),
            detail=str(diagnoses_with_deps),
        )
    return SufficiencyResult(
        sufficient=False,
        stage="dependency_diagnosis",
        reason=(
            f"Dependency-Diagnosis produced {diagnoses_with_deps} path(s) with identified dependencies "
            f"(threshold ≥ {_DEPENDENCY_MIN_DIAGNOSES_WITH_DEPS}). "
            "The Orchestrator cannot generate a differentiated verdict without concrete lock-in data."
        ),
        detail=str(diagnoses_with_deps),
    )


def check_sufficiency_orchestrator(verdict: "OrchestratorVerdict") -> SufficiencyResult:
    """Check that the Orchestrator produced a non-empty verdict summary and recommendations.

    Thresholds:
      - ``verdict.verdict_summary`` is non-empty.
      - ``len(verdict.key_recommendations) >= 1``.

    An empty summary or zero recommendations cannot be presented to a decision maker.

    Parameters
    ----------
    verdict:
        The :class:`~app.agents.orchestrator.orchestrator_agent.OrchestratorVerdict`
        returned by the Orchestrator Agent.

    Returns
    -------
    SufficiencyResult
        ``sufficient=True`` if both thresholds are met; ``False`` otherwise.
    """
    has_summary = bool(verdict.verdict_summary and verdict.verdict_summary.strip())
    rec_count = len(verdict.key_recommendations)

    if has_summary and rec_count >= _ORCHESTRATOR_MIN_RECOMMENDATIONS:
        return SufficiencyResult(
            sufficient=True,
            stage="orchestrator",
            reason=(
                f"Orchestrator produced a verdict summary and {rec_count} recommendation(s) "
                f"(threshold ≥ {_ORCHESTRATOR_MIN_RECOMMENDATIONS})."
            ),
            detail=f"has_summary=True, recommendations={rec_count}",
        )

    missing: list[str] = []
    if not has_summary:
        missing.append("verdict_summary is empty")
    if rec_count < _ORCHESTRATOR_MIN_RECOMMENDATIONS:
        missing.append(
            f"only {rec_count} recommendation(s) "
            f"(threshold ≥ {_ORCHESTRATOR_MIN_RECOMMENDATIONS})"
        )
    return SufficiencyResult(
        sufficient=False,
        stage="orchestrator",
        reason=(
            "Orchestrator output is insufficient: " + "; ".join(missing) + "."
        ),
        detail=f"has_summary={has_summary}, recommendations={rec_count}",
    )


def check_sufficiency_ingestion(context: "IngestionContext") -> SufficiencyResult:
    """Check that the Ingestion stage produced a usable context for Stack-Mapping.

    Thresholds:
      - ``context.context_summary`` is non-empty.
      - ``len(context.key_facts) >= 1``.

    Stack-Mapping's Layer-Identification sub-agent builds its prompt from both
    the summary and the key facts.  An empty summary with no facts gives the LLM
    nothing grounded to work from, producing hallucinated layer proposals.

    Parameters
    ----------
    context:
        The :class:`~app.agents.ingestion.sub_agents.context_synthesis_sub_agent.IngestionContext`
        returned by the Ingestion Agent.

    Returns
    -------
    SufficiencyResult
        ``sufficient=True`` if both thresholds are met; ``False`` otherwise.
    """
    has_summary = bool(context.context_summary and context.context_summary.strip())
    fact_count = len(context.key_facts)

    if has_summary and fact_count >= _INGESTION_MIN_KEY_FACTS:
        return SufficiencyResult(
            sufficient=True,
            stage="ingestion",
            reason=(
                f"Ingestion produced a context summary and {fact_count} key fact(s) "
                f"(threshold ≥ {_INGESTION_MIN_KEY_FACTS})."
            ),
            detail=f"has_summary=True, key_facts={fact_count}",
        )

    missing: list[str] = []
    if not has_summary:
        missing.append("context_summary is empty")
    if fact_count < _INGESTION_MIN_KEY_FACTS:
        missing.append(
            f"only {fact_count} key fact(s) extracted "
            f"(threshold ≥ {_INGESTION_MIN_KEY_FACTS})"
        )
    return SufficiencyResult(
        sufficient=False,
        stage="ingestion",
        reason=(
            "Ingestion output is insufficient for Stack-Mapping: "
            + "; ".join(missing) + "."
        ),
        detail=f"has_summary={has_summary}, key_facts={fact_count}",
    )


# ---------------------------------------------------------------------------
# Loop-guard
# ---------------------------------------------------------------------------

#: Maximum number of times a single ``(from_stage, to_stage)`` pair may loop
#: back before the loop-guard declares the cap exceeded.  Counting starts at
#: the *first* recalibration attempt, so a cap of 2 means:
#:   attempt 1 → allowed  (iteration_count == 1)
#:   attempt 2 → allowed  (iteration_count == 2)
#:   attempt 3 → cap exceeded — pipeline must enter terminal state
LOOP_GUARD_MAX_RETRIES: int = 2


class LoopGuard:
    """Per-pipeline-run tracker that enforces a retry cap on backward routes.

    One ``LoopGuard`` instance is created when a pipeline run starts and is
    threaded through every stage handoff.  When a stage emits a
    :class:`RecalibrationRequest`, it calls :meth:`record` before routing;
    if :meth:`cap_exceeded` returns ``True``, the pipeline must not loop
    and should instead invoke the partial-verdict terminal state (Phase 7.5.10).

    Design decisions
    ----------------
    * **Per-pair counting** — the counter is keyed on ``(from_stage, to_stage)``
      as a tuple.  A cap hit on ``(stack_mapping, ingestion)`` does not
      affect the counter for ``(scenario_generation, stack_mapping)`` or any
      other pair.  This matches the TASKS.md requirement: "does not reset
      across *unrelated* stage pairs."
    * **Cap of 2** — :data:`LOOP_GUARD_MAX_RETRIES` = 2, meaning each pair
      may attempt recalibration at most twice before the guard blocks further
      loops.
    * **Immutable cap** — ``max_retries`` is fixed at construction time.
      The pipeline router must not bypass or mutate it mid-run.
    * **Thread-safety** — the pipeline can run stage sub-agents concurrently
      (e.g. Phase 5 parallel sub-agents), but backward recalibration is
      always sequential (one stage at a time), so no locking is required.

    Parameters
    ----------
    max_retries:
        Maximum allowed loop-backs per ``(from_stage, to_stage)`` pair.
        Defaults to :data:`LOOP_GUARD_MAX_RETRIES` (2).

    Examples
    --------
    >>> guard = LoopGuard()
    >>> guard.record("stack_mapping", "ingestion")   # iteration 1 — allowed
    1
    >>> guard.record("stack_mapping", "ingestion")   # iteration 2 — allowed
    2
    >>> guard.cap_exceeded("stack_mapping", "ingestion")
    True                                             # 3rd attempt would be blocked
    >>> guard.cap_exceeded("scenario_generation", "stack_mapping")
    False                                            # unrelated pair unaffected
    """

    def __init__(self, max_retries: int = LOOP_GUARD_MAX_RETRIES) -> None:
        if max_retries < 1:
            raise ValueError(
                f"max_retries must be >= 1; got {max_retries}."
            )
        self._max_retries: int = max_retries
        # Maps (from_stage, to_stage) -> current iteration count.
        self._counts: dict[tuple[str, str], int] = {}

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def record(self, from_stage: str, to_stage: str) -> int:
        """Increment the counter for the given stage pair and return the new count.

        This must be called exactly once per recalibration attempt, *before*
        routing the backward edge.  The returned count is the value that should
        be stored in :attr:`RecalibrationRequest.iteration_count`.

        Parameters
        ----------
        from_stage:
            The stage that detected insufficiency.
        to_stage:
            The upstream stage being re-invoked.

        Returns
        -------
        int
            The new iteration count for this pair (starts at 1 on the first call).

        Raises
        ------
        ValueError
            If ``from_stage`` or ``to_stage`` is empty, or they are equal.
        """
        _validate_stage_pair(from_stage, to_stage)
        key = (from_stage, to_stage)
        self._counts[key] = self._counts.get(key, 0) + 1
        return self._counts[key]

    def cap_exceeded(self, from_stage: str, to_stage: str) -> bool:
        """Return ``True`` if this pair has already hit or exceeded the retry cap.

        The pipeline router calls this *before* allowing a backward edge.  If
        it returns ``True``, the pipeline must not record another attempt and
        must enter the terminal partial-verdict state instead.

        Parameters
        ----------
        from_stage:
            The stage that would be requesting recalibration.
        to_stage:
            The upstream stage that would be re-invoked.

        Returns
        -------
        bool
            ``True``  — cap reached; no further loops permitted for this pair.
            ``False`` — cap not yet reached; another attempt is allowed.
        """
        _validate_stage_pair(from_stage, to_stage)
        key = (from_stage, to_stage)
        return self._counts.get(key, 0) >= self._max_retries

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    def iteration_count(self, from_stage: str, to_stage: str) -> int:
        """Return the current iteration count for a stage pair (0 if never recorded).

        Parameters
        ----------
        from_stage:
            The requesting stage.
        to_stage:
            The upstream target stage.

        Returns
        -------
        int
            Number of times :meth:`record` has been called for this pair.
            Returns ``0`` if the pair has never looped.
        """
        _validate_stage_pair(from_stage, to_stage)
        return self._counts.get((from_stage, to_stage), 0)

    def all_counts(self) -> dict[tuple[str, str], int]:
        """Return a copy of the full counter dict for audit/logging purposes.

        Returns
        -------
        dict[tuple[str, str], int]
            A shallow copy mapping ``(from_stage, to_stage)`` → iteration count.
            Pairs that have never been recorded are absent (count is implicitly 0).
        """
        return dict(self._counts)

    @property
    def max_retries(self) -> int:
        """The retry cap this guard was configured with (read-only)."""
        return self._max_retries


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _validate_stage_pair(from_stage: str, to_stage: str) -> None:
    """Raise ``ValueError`` for invalid stage pair arguments.

    Used internally by :class:`LoopGuard` methods.
    """
    if not from_stage or not from_stage.strip():
        raise ValueError("from_stage must be a non-empty string.")
    if not to_stage or not to_stage.strip():
        raise ValueError("to_stage must be a non-empty string.")
    if from_stage == to_stage:
        raise ValueError(
            f"from_stage and to_stage must differ; both are '{from_stage}'."
        )


# ---------------------------------------------------------------------------
# Context Accumulation Helper (Phase 7.5.4)
# ---------------------------------------------------------------------------

def accumulate_ingestion_context(
    existing: IngestionContext,
    new_partial: IngestionContext,
) -> IngestionContext:
    """Merge a targeted re-ingestion result into an existing :class:`IngestionContext`.

    Recalibration does not discard or overwrite prior context. Instead, new
    findings are accumulated on top of the original context:
      - ``context_summary``: original summary preserved, appended with new summary
        (or preserved as-is if new summary is empty).
      - ``key_facts``: new unique facts appended to the existing list (order preserved).
      - ``sources``: new unique source URLs appended to the existing list (order preserved).
      - ``raw_retrieved_content``: concatenated with a double newline delimiter.
      - ``entity``, ``capability``, ``options``: preserved from ``existing``.

    Parameters
    ----------
    existing:
        The :class:`~app.agents.ingestion.sub_agents.context_synthesis_sub_agent.IngestionContext`
        already accumulated from previous passes.
    new_partial:
        The new :class:`~app.agents.ingestion.sub_agents.context_synthesis_sub_agent.IngestionContext`
        produced by the scoped re-ingestion pass.

    Returns
    -------
    IngestionContext
        A new combined :class:`IngestionContext` with both existing and new data.
    """
    # Accumulate context_summary
    if existing.context_summary and new_partial.context_summary:
        combined_summary = f"{existing.context_summary}\n\n[Recalibration Update]\n{new_partial.context_summary}"
    elif new_partial.context_summary:
        combined_summary = new_partial.context_summary
    else:
        combined_summary = existing.context_summary

    # Accumulate key_facts preserving order and deduplicating
    seen_facts = set(existing.key_facts)
    combined_key_facts = list(existing.key_facts)
    for fact in new_partial.key_facts:
        if fact not in seen_facts:
            seen_facts.add(fact)
            combined_key_facts.append(fact)

    # Accumulate sources preserving order and deduplicating
    seen_sources = set(existing.sources)
    combined_sources = list(existing.sources)
    for src in new_partial.sources:
        if src not in seen_sources:
            seen_sources.add(src)
            combined_sources.append(src)

    # Accumulate raw_retrieved_content
    if existing.raw_retrieved_content and new_partial.raw_retrieved_content:
        combined_raw = f"{existing.raw_retrieved_content}\n\n{new_partial.raw_retrieved_content}"
    elif new_partial.raw_retrieved_content:
        combined_raw = new_partial.raw_retrieved_content
    else:
        combined_raw = existing.raw_retrieved_content

    # Options: union preserving order from existing then new_partial
    seen_opts = set(existing.options)
    combined_options = list(existing.options)
    for opt in new_partial.options:
        if opt not in seen_opts:
            seen_opts.add(opt)
            combined_options.append(opt)

    return IngestionContext(
        entity=existing.entity,
        capability=existing.capability,
        options=combined_options,
        context_summary=combined_summary,
        key_facts=combined_key_facts,
        sources=combined_sources,
        raw_retrieved_content=combined_raw,
    )
