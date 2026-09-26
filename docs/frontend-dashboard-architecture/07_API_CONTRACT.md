# 07_API_CONTRACT.md — Helios Terminal Dashboard

## Status: implemented and matched against live Pydantic schemas

Unlike the website's `07_API_CONTRACT.md` (which was a draft), this document reflects the **actual TypeScript interfaces** in `frontend/src/dashboard/api.ts`, which were written to mirror the live backend Pydantic models exactly. Field names and shapes here are correct as of Phase 9 completion.

---

## Base URL

Resolved from `import.meta.env.VITE_API_BASE_URL` at build time, falling back to `http://127.0.0.1:8000`. Configured per-environment via Vite's `env` system.

```typescript
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
```

---

## Endpoint 1: Submit async decision job

**`POST /decisions/async`**

Accepts a decision brief and immediately returns a job ID for polling. Does not block until the pipeline completes.

### Request body (`DecisionRequest`)

```typescript
interface DecisionRequest {
  entity: string;      // Institutional entity name (e.g. "Indian Army Signals Directorate")
  capability: string;  // AI capability required (e.g. "Tactical SLM for Edge SIGINT")
  options: string[];   // Candidate sourcing paths. Empty array is valid — backend infers paths.
}
```

### Response body (`JobStatusResponse`)

```typescript
interface JobStatusResponse {
  job_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  created_at: string;           // ISO 8601 timestamp
  completed_at: string | null;  // null until job finishes
  result: DecisionResponse | null;  // null until status === 'completed'
  error: string | null;         // error message if status === 'failed'
}
```

The immediate response after `POST` will have `status: 'queued'` and `result: null`. Polling begins immediately.

### Function signature

```typescript
async function submitDecision(brief: DecisionRequest): Promise<JobStatusResponse>
```

### Error handling

Throws `Error` with message `"Failed to submit decision: {status} — {detail}"` on non-2xx response. The catch block in `DashboardPlaceholder.tsx` triggers the offline synthesis fallback.

---

## Endpoint 2: Poll job status

**`GET /decisions/jobs/{job_id}`**

Polled every `POLL_INTERVAL_MS = 2500` milliseconds. Returns the same `JobStatusResponse` shape as the submit response, progressively updating `status` and populating `result` when complete.

### Function signature

```typescript
async function pollJobStatus(jobId: string): Promise<JobStatusResponse>
```

### Status transitions (backend side)

```
queued → processing → completed
                   → failed
```

The frontend polls until `status` is `completed` or `failed`, then clears the interval.

---

## Endpoint 3: Synchronous submission (test/fallback)

**`POST /decisions`**

Blocks until the full pipeline completes. Not used in the primary user flow — included in `api.ts` as a utility for quick test runs. Returns `DecisionResponse` directly (no job wrapper).

### Function signature

```typescript
async function submitDecisionSync(brief: DecisionRequest): Promise<DecisionResponse>
```

---

## Full type reference (`api.ts`)

### `DecisionResponse`

The primary result object, returned in `JobStatusResponse.result` when `status === 'completed'`.

```typescript
interface DecisionResponse {
  entity: string;
  capability: string;
  options: string[];
  verdict: OrchestratorVerdict | null;
  verification_passed: boolean;
  verification_failed_stage: string | null;  // stage name if pipeline halted at verification
  verification_results: VerificationResult[];
  recalibration_trail: RecalibrationTrailItem[];
  partial_verdict_caveats: string[];
}
```

### `OrchestratorVerdict`

```typescript
interface OrchestratorVerdict {
  entity: string;
  capability: string;
  recommended_path: string;
  verdict_summary: string;
  key_recommendations: string[];
  path_stances: Record<string, string>;       // path name → stance string (e.g. "RECOMMENDED — ...")
  cross_path_comparison: CrossPathComparison | null;
  explanation_trail: ExplanationTrail | null;
}
```

### `CrossPathComparison`

```typescript
interface CrossPathComparison {
  comparative_narrative: string;
  path_comparisons: PathComparison[];
}

interface PathComparison {
  scenario_name: string;
  lock_in_count: number;
  max_severity_score: number;
  key_tradeoffs: string[];
  path_summary: string;
}
```

### `ExplanationTrail`

```typescript
interface ExplanationTrail {
  summary: string;
  steps: AuditStep[];
  sources: string[];
}

interface AuditStep {
  stage: string;     // e.g. "Ingestion", "Stack-Mapping", "Orchestrator"
  claim: string;
  evidence: string;
}
```

### `VerificationResult`

```typescript
interface VerificationResult {
  passed: boolean;
  confidence: number;     // 0.0 – 1.0
  reason: string;
  claim: string;
  agent_stage: string;
}
```

### `RecalibrationTrailItem`

```typescript
interface RecalibrationTrailItem {
  from_stage: string;
  to_stage: string;
  reason: string;
  gap_description: string;
  iteration_count: number;
}
```

---

## Component-to-field mapping

| Component | Fields consumed |
|---|---|
| `InstitutionalVerdictPanel` | `verdict.recommended_path`, `verdict.verdict_summary`, `verdict.path_stances`, `verdict.key_recommendations`, `partial_verdict_caveats`, `verification_passed` |
| `TrajectoryChartPanel` | `verdict.cross_path_comparison` + `PresetScenario.trajectoryData` (local) |
| `AgentPipelineTopology` | `verification_results`, `recalibration_trail`, `error` |
| `AuditInspector` | `verification_results`, `recalibration_trail`, `verdict.explanation_trail`, `verification_passed`, `verification_failed_stage` |
| `ExecutiveDossierModal` | full `DecisionResponse` |
| `LockInMatrixView` | `PresetScenario.lockInVectors` (local, not from API) |

---

## Health check

**`GET /health`** — used only for the backend beacon in `DashboardPlaceholder.tsx`. Expected response: `{ "status": "ok" }` with HTTP 200. The frontend only checks `response.ok`; the body is not parsed.

---

## Offline contract (presetScenarios.ts)

When the API is unreachable, the frontend synthesizes a response from `presetScenarios.ts`. The `PresetScenario` type wraps `DecisionRequest` and `DecisionResponse` with additional local-only fields:

```typescript
interface PresetScenario {
  id: string;
  code: string;           // e.g. 'DEF-SLM', 'FIN-RAG', 'MED-AI'
  title: string;
  category: 'DEFENSE' | 'FINTECH' | 'HEALTHCARE' | 'AUTONOMOUS' | 'ENTERPRISE';
  description: string;
  brief: DecisionRequest;
  result: DecisionResponse;     // pre-computed, matches API response shape exactly
  trajectoryData: TrajectoryDataPoint[];
  lockInVectors: LockInVector[];
}
```

`trajectoryData` and `lockInVectors` are local-only fields not present in the backend API schema — they provide the data for `TrajectoryChartPanel` and `LockInMatrixView` respectively.
