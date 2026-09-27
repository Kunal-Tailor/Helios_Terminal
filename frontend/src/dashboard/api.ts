/**
 * Dashboard API client — typed fetch wrapper for Helios Terminal backend.
 *
 * Uses the async decision endpoint (POST /decisions/async + polling)
 * to avoid blocking the browser during the 1–3 minute pipeline run.
 */

// ---------------------------------------------------------------------------
// Base URL
// ---------------------------------------------------------------------------

export const API_BASE = (() => {
  try {
    // Vite exposes env vars via import.meta.env
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const env = (import.meta as any).env;
    return env?.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
  } catch {
    return 'http://127.0.0.1:8000';
  }
})();

/**
 * Checks if the backend server is reachable and reports healthy status.
 */
export async function checkBackendHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`, { method: 'GET' });
    return res.ok;
  } catch {
    return false;
  }
}

// ---------------------------------------------------------------------------
// TypeScript interfaces (mirror backend Pydantic schemas)
// ---------------------------------------------------------------------------

export interface DecisionRequest {
  entity: string;
  capability: string;
  options: string[];
  data_sovereignty_weight?: 'CRITICAL' | 'STANDARD' | 'LOW' | string;
  latency_tolerance?: 'SUB_20MS' | 'BALANCED' | 'BATCH' | string;
}

export interface AuditStep {
  stage: string;
  claim: string;
  evidence: string;
}

export interface ExplanationTrail {
  summary: string;
  steps: AuditStep[];
  sources: string[];
}

export interface PathComparison {
  scenario_name: string;
  lock_in_count: number;
  max_severity_score: number;
  key_tradeoffs: string[];
  path_summary: string;
}

export interface CrossPathComparison {
  comparative_narrative: string;
  path_comparisons: PathComparison[];
}

export interface VerificationResult {
  passed: boolean;
  confidence: number;
  reason: string;
  claim: string;
  agent_stage: string;
  provider?: string | null;
}

export interface RecalibrationTrailItem {
  from_stage: string;
  to_stage: string;
  reason: string;
  gap_description: string;
  iteration_count: number;
  provider?: string | null;
}

export interface OrchestratorVerdict {
  entity: string;
  capability: string;
  recommended_path: string;
  verdict_summary: string;
  key_recommendations: string[];
  path_stances: Record<string, string>;
  cross_path_comparison: CrossPathComparison | null;
  explanation_trail: ExplanationTrail | null;
}

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
  stage_providers?: Record<string, string>;
  data_sovereignty_weight?: string | null;
  latency_tolerance?: string | null;
}

export interface JobStatusResponse {
  job_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  created_at: string;
  completed_at: string | null;
  result: DecisionResponse | null;
  error: string | null;
}

// ---------------------------------------------------------------------------
// API functions
// ---------------------------------------------------------------------------

/**
 * Submit a decision brief for async background processing.
 * Returns a JobStatusResponse with a job_id to poll.
 */
export async function submitDecision(
  brief: DecisionRequest,
): Promise<JobStatusResponse> {
  const res = await fetch(`${API_BASE}/decisions/async`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(brief),
  });

  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText);
    throw new Error(`Failed to submit decision: ${res.status} — ${detail}`);
  }

  return res.json();
}

/**
 * Poll the status of a background decision job.
 */
export async function pollJobStatus(
  jobId: string,
): Promise<JobStatusResponse> {
  const res = await fetch(`${API_BASE}/decisions/jobs/${jobId}`);

  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText);
    throw new Error(`Failed to poll job: ${res.status} — ${detail}`);
  }

  return res.json();
}

/**
 * Submit a decision synchronously (blocks until pipeline completes).
 * Use only for quick test runs or fallback.
 */
export async function submitDecisionSync(
  brief: DecisionRequest,
): Promise<DecisionResponse> {
  const res = await fetch(`${API_BASE}/decisions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(brief),
  });

  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText);
    throw new Error(`Decision failed: ${res.status} — ${detail}`);
  }

  return res.json();
}
