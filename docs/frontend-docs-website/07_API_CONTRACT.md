# 07 — API contract (frontend & dashboard)

This document outlines the complete API contract consumed by the Helios Terminal frontend, covering both static website assets and the live FastAPI backend integration (`src/dashboard/api.ts`).

---

## 1. Marketing Website (Static Contract)

The marketing website (`/`, `/architecture`, `/about`, `/team`) operates without live API dependencies:

| Interaction | Route | Mechanism | Target / Resource |
| --- | --- | --- | --- |
| Dashboard CTA | `/` → `/dashboard` | Client-side SPA route transition (`react-router-dom`) | Internal React Router transition |
| Synopsis Download | `/about` | Static bundled asset via HTML5 `download` | `/assets/Helios-Terminal-Synopsis.docx` |
| Code Repositories | `/team`, `/about` | External hyperlink (`target="_blank"`) | GitHub project repository |

---

## 2. Dashboard Workstation Backend Contract (`src/dashboard/api.ts`)

The Dashboard connects to the FastAPI backend service configured via `VITE_API_BASE_URL` (defaulting to `http://127.0.0.1:8000`).

### 2.1 Service Health Check

- **Endpoint:** `GET /health`
- **Purpose:** Telemetry beacon displayed in `BloombergHeader.tsx` indicating if the backend multi-agent pipeline is reachable.
- **Response Shape:**
  ```json
  {
    "status": "ok"
  }
  ```

---

### 2.2 Asynchronous Decision Analysis (Standard Path)

Because multi-agent analysis involves web context retrieval, LLM reasoning, and cross-stage verification (taking 30–90 seconds), the terminal uses an asynchronous non-blocking job model.

#### Step 1: Submit Decision Brief
- **Endpoint:** `POST /decisions/async`
- **Request Headers:** `Content-Type: application/json`
- **Request Payload (`DecisionRequest`):**
  ```typescript
  interface DecisionRequest {
    entity: string;        // e.g. "UK Ministry of Defence"
    capability: string;    // e.g. "Small Language Model for tactical edge drones"
    options: string[];     // e.g. ["Build in-house private SLM", "License Mistral NeMo", "Outsource to Palantir/AIP"]
  }
  ```
- **Response Shape (`JobStatusResponse`):**
  ```json
  {
    "job_id": "job_d9a8e23f-48bc-4b11",
    "status": "queued",
    "created_at": "2026-09-17T22:30:00Z",
    "completed_at": null,
    "result": null,
    "error": null
  }
  ```

#### Step 2: Poll Job Status
- **Endpoint:** `GET /decisions/jobs/{job_id}`
- **Polling Interval:** Every `2500ms` until status is `"completed"` or `"failed"`.
- **Response Status Values:**
  - `"queued"`: Waiting in pipeline queue.
  - `"processing"`: Multi-agent pipeline is active (agents 01 through 06).
  - `"completed"`: Analysis complete; includes full `result` payload.
  - `"failed"`: Fatal exception or verification failure; includes `error` message.

---

### 2.3 Comprehensive Response Schema (`DecisionResponse`)

Upon job completion, the backend returns a structured `DecisionResponse` mapped directly into dashboard visualization panels:

```typescript
export interface DecisionResponse {
  entity: string;
  capability: string;
  options: string[];
  verdict: OrchestratorVerdict | null;
  verification_passed: boolean;
  verification_failed_stage: string | null;
  verification_results: VerificationResult[];
  recalibration_trail: RecalibrationTrailItem[];
  partial_verdict_caveats: string[];
}

export interface OrchestratorVerdict {
  entity: string;
  capability: string;
  recommended_path: string;
  verdict_summary: string;
  key_recommendations: string[];
  path_stances: Record<string, 'RECOMMENDED' | 'HIGH CAUTION' | 'DISQUALIFIED'>;
  cross_path_comparison: {
    comparative_narrative: string;
    path_comparisons: Array<{
      scenario_name: string;
      lock_in_count: number;
      max_severity_score: number;
      key_tradeoffs: string[];
      path_summary: string;
    }>;
  };
  explanation_trail: {
    summary: string;
    steps: Array<{ stage: string; claim: string; evidence: string }>;
    sources: string[];
  };
}

export interface VerificationResult {
  passed: boolean;
  confidence: number;
  reason: string;
  claim: string;
  agent_stage: string;
}

export interface RecalibrationTrailItem {
  from_stage: string;
  to_stage: string;
  reason: string;
  gap_description: string;
  iteration_count: number;
}
```

---

### 2.4 Synchronous Fallback / Testing Endpoint

- **Endpoint:** `POST /decisions`
- **Request:** `DecisionRequest`
- **Behavior:** Blocks until full pipeline execution completes; returns `DecisionResponse` directly. Used for automated testing and single-run CLI evaluations.
