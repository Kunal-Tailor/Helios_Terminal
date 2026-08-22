import type { DecisionRequest } from './api'

export function optionsNote(brief: DecisionRequest): string {
  return brief.options && brief.options.length > 0
    ? 'Candidate options specified manually.'
    : 'Candidate options left blank — inferred by Helios.'
}
