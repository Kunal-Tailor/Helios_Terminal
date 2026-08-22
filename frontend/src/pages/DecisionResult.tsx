import { Link } from 'react-router-dom'
import { useMutationState } from '@tanstack/react-query'
import PathCard from '../components/verdict-panel/PathCard'
import VerdictBanner from '../components/verdict-panel/VerdictBanner'
import type { DecisionRequest, DecisionResponse } from '../lib/api'

function optionsNote(brief: DecisionRequest): string {
  return brief.options && brief.options.length > 0
    ? 'Candidate options specified manually.'
    : 'Candidate options left blank — inferred by Helios.'
}

function DecisionResult() {
  const entries = useMutationState({
    filters: { mutationKey: ['submitDecision'], status: 'success' },
    select: (mutation) => ({
      response: mutation.state.data as DecisionResponse,
      brief: mutation.state.variables as DecisionRequest,
    }),
  })

  const latest = entries[entries.length - 1]

  if (!latest) {
    return (
      <main className="mx-auto max-w-2xl space-y-6 px-8 py-10">
        <p className="font-mono text-body-mono leading-[1.3] text-secondary">
          No completed decision to show.
        </p>
        <Link
          to="/"
          className="inline-block rounded-sm border border-hairline bg-surface-raised px-3 py-1.5 font-ui text-body-ui text-primary hover:border-accent"
        >
          New decision
        </Link>
      </main>
    )
  }

  const paths = latest.response.verdict?.cross_path_comparison?.path_comparisons ?? []

  return (
    <main className="mx-auto max-w-5xl space-y-6 px-8 py-10">
      <VerdictBanner
        entity={latest.brief.entity}
        capability={latest.brief.capability}
        optionsNote={optionsNote(latest.brief)}
        summary={latest.response.verdict?.verdict_summary ?? null}
        recommendedPath={latest.response.verdict?.recommended_path || null}
      />
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        {paths.map((path) => (
          <PathCard key={path.scenario_name} path={path} />
        ))}
      </div>
      <Link
        to="/"
        className="inline-block rounded-sm border border-hairline bg-surface-raised px-3 py-1.5 font-ui text-body-ui text-primary hover:border-accent"
      >
        New decision
      </Link>
    </main>
  )
}

export default DecisionResult
