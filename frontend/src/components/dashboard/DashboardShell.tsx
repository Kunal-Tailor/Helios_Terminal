import type { DecisionRequest, DecisionResponse } from '../../lib/api'
import { optionsNote } from '../../lib/decision-copy'
import DependencyGraph from '../dependency-graph/DependencyGraph'
import PathCard from '../verdict-panel/PathCard'
import VerdictBanner from '../verdict-panel/VerdictBanner'

interface DashboardShellProps {
  response: DecisionResponse
  brief: DecisionRequest
}

function DashboardShell({ response, brief }: DashboardShellProps) {
  const verdict = response.verdict
  const paths = verdict?.cross_path_comparison?.path_comparisons ?? []

  return (
    <main className="mx-auto max-w-screen-2xl space-y-4 px-8 py-10">
      <VerdictBanner
        entity={brief.entity}
        capability={brief.capability}
        optionsNote={optionsNote(brief)}
        summary={verdict?.verdict_summary ?? null}
        recommendedPath={verdict?.recommended_path || null}
      />
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-5">
        <section className="space-y-2 xl:col-span-3">
          <h2 className="font-mono text-metadata leading-[1.3] text-secondary">
            Dependency graph
          </h2>
          <DependencyGraph paths={paths} />
        </section>
        <section className="space-y-2 xl:col-span-2">
          <h2 className="font-mono text-metadata leading-[1.3] text-secondary">
            Path comparison
          </h2>
          <div className="space-y-4">
            {paths.map((path) => (
              <PathCard key={path.scenario_name} path={path} />
            ))}
          </div>
        </section>
      </div>
    </main>
  )
}

export default DashboardShell
