import { Link } from 'react-router-dom'
import { useMutationState } from '@tanstack/react-query'
import DashboardShell from '../components/dashboard/DashboardShell'
import type { DecisionRequest, DecisionResponse } from '../lib/api'

function Dashboard() {
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

  return (
    <>
      <DashboardShell response={latest.response} brief={latest.brief} />
      <div className="mx-auto flex max-w-screen-2xl gap-3 px-8 pb-10">
        <Link
          to="/result"
          className="inline-block rounded-sm border border-hairline bg-surface-raised px-3 py-1.5 font-ui text-body-ui text-primary hover:border-accent"
        >
          Back to result view
        </Link>
        <Link
          to="/"
          className="inline-block rounded-sm border border-hairline bg-surface-raised px-3 py-1.5 font-ui text-body-ui text-primary hover:border-accent"
        >
          New decision
        </Link>
      </div>
    </>
  )
}

export default Dashboard
