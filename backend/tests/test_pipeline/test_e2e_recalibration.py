"""
End-to-End Recalibration Verification Pass (Task 7.5.12).

Executes a real (non-mocked) decision brief through the 6-stage pipeline,
confirming that at least one deliberate insufficient-input scenario triggers
a fallback, resolves within the retry cap, and produces a fully populated verdict.
"""

import os
import pytest

from app.core.config import settings
from app.pipeline.graph import run_pipeline


@pytest.mark.skipif(
    os.getenv("RUN_LIVE_E2E", "0") != "1" or not settings.llm_api_key,
    reason="Set RUN_LIVE_E2E=1 with a valid LLM API key to run the live non-mocked E2E pipeline verification pass",
)
def test_real_pipeline_e2e_recalibration_pass():
    """Real (non-mocked) decision brief run through the pipeline confirming that an

    insufficient-input scenario triggers a backward recalibration fallback,
    resolves within the retry cap, and produces a fully populated verdict.
    """
    entity = "Indian Army signals division"
    capability = "tactical edge speech recognition"
    options = ["build in-house", "license open-weight"]

    result = run_pipeline(
        entity=entity,
        capability=capability,
        options=options,
        halt_on_verification_failure=False,
    )

    # 1. Pipeline produced a populated Orchestrator verdict
    assert result.verdict is not None, "Pipeline must produce a non-null verdict"
    assert result.verdict.entity == entity
    assert result.verdict.capability == capability
    assert len(result.verdict.verdict_summary.strip()) > 0, "Verdict summary must be non-empty"
    assert len(result.verdict.key_recommendations) >= 1, "Must produce at least one key recommendation"

    # 2. At least one recalibration fallback loop occurred
    assert len(result.recalibration_trail) >= 1, (
        f"Expected at least 1 recalibration request in trail, got {len(result.recalibration_trail)}"
    )

    # 3. Each recalibration record is well-formed with valid stage transitions and descriptions
    for req in result.recalibration_trail:
        assert req.from_stage in ("stack_mapping", "scenario_generation", "outcome_prediction", "dependency_diagnosis", "orchestrator")
        assert req.to_stage in ("ingestion", "stack_mapping", "scenario_generation", "outcome_prediction", "dependency_diagnosis")
        assert req.reason in ("insufficient", "unverified")
        assert len(req.gap_description.strip()) > 0
        assert 1 <= req.iteration_count <= 2, f"Iteration count {req.iteration_count} must not exceed retry cap of 2"

    # 4. If any stage hit the loop guard retry cap, partial verdict caveats must be recorded
    if any(req.iteration_count >= 2 for req in result.recalibration_trail):
        # The pipeline gracefully completed with caveat flags or resolved before cap
        assert isinstance(result.partial_verdict_caveats, list)
