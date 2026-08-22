export const SEVERITY_CRITICAL_THRESHOLD = 7.0
export const SEVERITY_ELEVATED_THRESHOLD = 4.0

export function severityLabel(score: number): string {
  if (score >= SEVERITY_CRITICAL_THRESHOLD) {
    return 'Critical'
  }
  if (score >= SEVERITY_ELEVATED_THRESHOLD) {
    return 'Elevated'
  }
  return 'Low'
}
