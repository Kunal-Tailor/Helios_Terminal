# 07_API_CONTRACT.md — Helios Terminal Frontend

## Status: synced against backend schemas (Phase 8.3)

Originally drafted from `PRD.md`, `ARCHITECTURE.md`, and `FEATURES.md`. During Phase 8.3 every field name and shape below was diffed against `backend/app/api/schemas/decision.py` and `backend/app/api/routes/decisions.py`, and the draft was corrected to match the live backend. Where the frontend would prefer a different shape (e.g. a severity enum), that is recorded explicitly as a known divergence / candidate backend addition — not silently assumed.

## Endpoints

Primary (used by `lib/api.ts`):

`POST /decisions` — synchronous, HTTP 200. Accepts a decision brief, runs the 6-stage pipeline with verification gating inline, returns the full `DecisionResponse`.

Background variants exist and are live (Phase 7.3), but are intentionally not wired into the client yet:

- `POST /decisions/async` — HTTP 202, returns a `JobStatusResponse` (`job_id`, `status`, `created_at`)
- `GET /decisions/jobs/{job_id}` — poll for `status: queued | processing | completed | failed`; `result` carries a full `DecisionResponse` once completed

## Request shape

```json
{
  "entity": "string",
  "capability": "string",
  "options": ["string", "..."]
}
```

- Field is `options`, not `candidate_options` (draft naming corrected during sync).
- `entity` and `capability` require `min_length=1` (empty strings rejected server-side).
- `options` is optional; omitting it or sending `[]` are both valid and equivalent — both trigger the "let Helios infer" path from `03_UX_FLOWS.md`.

## Response shape

```json
{
  "entity": "string",
  "capability": "string",
  "options": ["string", "..."],
  "verdict": {
    "entity": "string",
    "capability": "string",
    "recommended_path": "string",
    "verdict_summary": "string",
    "key_recommendations": ["string", "..."],
    "path_stances": { "Build": "string", "Buy": "string" },
    "cross_path_comparison": {
      "comparative_narrative": "string",
      "path_comparisons": [
        {
          "scenario_name": "string",
          "lock_in_count": 0,
          "max_severity_score": 0.0,
          "key_tradeoffs": ["string"],
          "path_summary": "string"
        }
      ]
    },
    "explanation_trail": {
      "summary": "string",
      "steps": [
        { "stage": "string", "claim": "string", "evidence": "string" }
      ],
      "sources": ["string"]
    }
  },
  "verification_passed": true,
  "verification_failed_stage": null,
  "verification_results": [
    {
      "passed": true,
      "confidence": 0.0,
      "reason": "string",
      "claim": "string",
      "agent_stage": "string"
    }
  ]
}
```

Nullability / absence semantics confirmed against the schema:

- `verdict` is `null` if the pipeline halted before the Orchestrator stage (e.g. verification gate failure).
- `recommended_path` is `""` when unset — the backend never emits `null` for it.
- `cross_path_comparison` and `explanation_trail` are nullable members of `verdict`.
- Verification fields are **flat, top-level**: `verification_passed`, `verification_failed_stage` (nullable — populated when a gate halts the pipeline), plus per-claim `verification_results`.
- There is no nested `decision_brief` object and no `paths[]` array. Per-path data lives in `verdict.path_stances` (name → stance text) and `verdict.cross_path_comparison.path_comparisons[]`.
- There is no `options_source` field distinguishing user-specified from system-inferred options; if the UI ever needs that distinction it requires a backend addition.

Known divergences / candidate backend additions:

- **Severity enum does not exist.** The draft assumed `"critical | elevated | low"` per dependency. The backend exposes numeric scoring instead: `max_severity_score: float` on each entry of `cross_path_comparison.path_comparisons`. If badge-style enum severities are wanted later, either band the numbers client-side or request the addition server-side — decided at component time, not assumed here.
- `verification.failed_stage` from the draft maps to the real `verification_failed_stage` — confirmed surfaced on halt, so the `PipelineStatusStrip` failure state can show *which* stage failed.

## Error shape (standard FastAPI/HTTP error)

```json
{
  "detail": "string | array"
}
```

Note `detail` is an array of validation-error objects on 422 responses. The frontend should not render `detail` raw — map known error cases (verification halt, timeout, malformed brief) to the plain-language copy defined in `03_UX_FLOWS.md`'s Flow C at render time.

## Sync checklist (completed Phase 8.3)

- [x] Confirm actual field names in `backend/app/api/schemas/` match this draft — draft corrected (`candidate_options` → `options`, `summary` → `verdict_summary`, flat verification fields, no `decision_brief`/`paths[]`)
- [x] Confirm whether `POST /decisions` is synchronous or requires polling — synchronous is live and is what `lib/api.ts` calls; async job endpoints also exist
- [x] Confirm `severity` classification exists or needs to be added — does not exist as an enum; numeric `max_severity_score` only; recorded above as a known divergence
- [x] Confirm `verification.failed_stage` (or equivalent) is actually returned on halt — confirmed: top-level `verification_failed_stage`
- [x] Update this file's status line once confirmed — done; "draft" status removed
