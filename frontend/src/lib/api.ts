const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8001'

export interface DecisionRequest {
  entity: string
  capability: string
  options?: string[]
}

export interface AuditStep {
  stage: string
  claim: string
  evidence: string
}

export interface ExplanationTrail {
  summary: string
  steps: AuditStep[]
  sources: string[]
}

export interface PathComparison {
  scenario_name: string
  lock_in_count: number
  max_severity_score: number
  key_tradeoffs: string[]
  path_summary: string
}

export interface CrossPathComparison {
  comparative_narrative: string
  path_comparisons: PathComparison[]
}

export interface OrchestratorVerdict {
  entity: string
  capability: string
  recommended_path: string
  verdict_summary: string
  key_recommendations: string[]
  path_stances: Record<string, string>
  cross_path_comparison: CrossPathComparison | null
  explanation_trail: ExplanationTrail | null
}

export interface VerificationResult {
  passed: boolean
  confidence: number
  reason: string
  claim: string
  agent_stage: string
}

export interface DecisionResponse {
  entity: string
  capability: string
  options: string[]
  verdict: OrchestratorVerdict | null
  verification_passed: boolean
  verification_failed_stage: string | null
  verification_results: VerificationResult[]
}

export class ApiError extends Error {
  readonly status: number
  readonly detail: unknown
  readonly isRateLimit: boolean

  constructor(status: number, detail: unknown) {
    super(`Decision request failed with status ${status}`)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
    this.isRateLimit = status === 503
  }
}

export async function submitDecision(
  request: DecisionRequest,
  signal?: AbortSignal,
): Promise<DecisionResponse> {
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}/decisions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
      signal,
    })
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw error
    }
    throw new ApiError(0, error instanceof Error ? error.message : String(error))
  }

  if (!response.ok) {
    let detail: unknown = null
    try {
      detail = await response.json()
    } catch {
      detail = await response.text().catch(() => null)
    }
    throw new ApiError(response.status, detail)
  }

  return (await response.json()) as DecisionResponse
}
