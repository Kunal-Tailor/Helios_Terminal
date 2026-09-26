# 07_API_CONTRACT.md — Helios Terminal Frontend

## Status: draft, needs sync against real backend schemas

This is drafted from `PRD.md`, `ARCHITECTURE.md`, and `FEATURES.md` — it has **not** been checked against the actual Pydantic models in `backend/app/api/schemas/` (Phase 7.1). Before Phase 8.3 (API client), diff this file against the real schema file and correct any field-name or shape mismatches. Treat divergence between this doc and the live schema as a bug in this doc, not in the backend.

## Endpoint

`POST /decisions`

Per `PRD.md` §6 and `ARCHITECTURE.md` §7.2 — accepts a decision brief, runs the pipeline synchronously (or via background job if Phase 7.3's async handling is active — check whether polling or a single blocking response is what's live before building `lib/api.ts`), returns a verdict.

## Request shape (draft)

```json
{
  "entity": "string",
  "capability": "string",
  "candidate_options": ["string", "..."]   // may be empty — triggers system inference
}
```

- `candidate_options: []` is a valid, meaningful input (not an error state) — maps directly to the "let Helios infer" path in `03_UX_FLOWS.md`. Confirm the backend accepts an empty array vs. expecting the field omitted entirely.

## Response shape (draft)

```json
{
  "decision_brief": {
    "entity": "string",
    "capability": "string",
    "candidate_options": ["string", "..."],
    "options_source": "user_specified | system_inferred"
  },
  "paths": [
    {
      "name": "string",              // e.g. "Build", "Buy", "Outsource"
      "outcome": "string",           // Outcome-Prediction Agent output
      "dependency": {
        "name": "string",            // Dependency-Diagnosis Agent output
        "failure_mode": "string",    // what breaks later if unmanaged
        "severity": "critical | elevated | low"
      }
    }
  ],
  "verdict": {
    "summary": "string",             // Orchestrator Agent's comparative synthesis
    "recommended_path": "string | null"
  },
  "verification": {
    "passed": true,
    "failed_stage": "string | null"  // populated only if verification halted the pipeline
  }
}
```

- `severity` as an enum is a frontend assumption to drive `StatusBadge`/risk-color tokens (`05_DESIGN_SYSTEM.md`) — confirm whether the backend actually classifies severity today or whether this needs to be requested as a backend addition. Per project memory, `key_recommendations` and `cross_path_comparison` exist in the verdict object on the backend side too — reconcile field names against the real schema rather than assuming this draft's naming.
- `verification.failed_stage` is required for the `PipelineStatusStrip` failure state in `06_COMPONENT_BREAKDOWN.md` to show *which* stage failed, not just that something failed. Flag this to the backend team explicitly if it isn't already surfaced — this is exactly the kind of field a frontend-only doc can silently assume exists.

## Error shape (draft — standard FastAPI/HTTP error assumed)

```json
{
  "detail": "string"
}
```

Frontend should not assume `detail` is user-presentable copy — map known error cases (verification halt, timeout, malformed brief) to the plain-language copy defined in `03_UX_FLOWS.md`'s Flow C, rather than rendering `detail` directly.

## Sync checklist (do before Phase 8.3)

- [ ] Confirm actual field names in `backend/app/api/schemas/` match this draft
- [ ] Confirm whether `POST /decisions` is synchronous or requires polling a job ID (Phase 7.3)
- [ ] Confirm `severity` classification exists or needs to be added
- [ ] Confirm `verification.failed_stage` (or equivalent) is actually returned on halt
- [ ] Update this file's status line once confirmed — remove "draft" status
