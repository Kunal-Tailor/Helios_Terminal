import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { DecisionRequest, DecisionResponse } from '../../lib/api'
import { optionsNote } from '../../lib/decision-copy'
import CommandBar from '../command-bar/CommandBar'
import DependencyGraph from '../dependency-graph/DependencyGraph'
import PathCard from '../verdict-panel/PathCard'
import VerdictBanner from '../verdict-panel/VerdictBanner'

interface DashboardShellProps {
  response: DecisionResponse
  brief: DecisionRequest
}

type ActivePane = 'verdict' | 'graph' | null

function DashboardShell({ response, brief }: DashboardShellProps) {
  const navigate = useNavigate()
  const [activePane, setActivePane] = useState<ActivePane>(null)
  const verdictPaneRef = useRef<HTMLDivElement>(null)
  const graphPaneRef = useRef<HTMLDivElement>(null)

  const verdict = response.verdict
  const paths = verdict?.cross_path_comparison?.path_comparisons ?? []

  return (
    <>
      <main className="mx-auto max-w-screen-2xl space-y-4 px-8 pb-20 pt-10">
        <div
          ref={verdictPaneRef}
          className={
            activePane === 'verdict'
              ? 'panel-transition rounded-sm border border-accent'
              : 'panel-transition rounded-sm border border-transparent'
          }
        >
          <VerdictBanner
            entity={brief.entity}
            capability={brief.capability}
            optionsNote={optionsNote(brief)}
            summary={verdict?.verdict_summary ?? null}
            recommendedPath={verdict?.recommended_path || null}
          />
        </div>
        <div className="grid grid-cols-1 gap-4 xl:grid-cols-5">
          <section className="space-y-2 xl:col-span-3">
            <h2 className="font-mono text-metadata leading-[1.3] text-secondary">
              Dependency graph
            </h2>
            <div
              ref={graphPaneRef}
              className={
                activePane === 'graph'
                  ? 'panel-transition rounded-sm border border-accent'
                  : 'panel-transition rounded-sm border border-transparent'
              }
            >
              <DependencyGraph paths={paths} />
            </div>
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
      <div className="fixed inset-x-0 bottom-0 z-10 border-t border-hairline bg-base px-8 py-1.5">
        <CommandBar
          onVerdict={() => {
            setActivePane('verdict')
            verdictPaneRef.current?.scrollIntoView()
          }}
          onGraph={() => {
            setActivePane('graph')
            graphPaneRef.current?.scrollIntoView()
          }}
          onNew={() => navigate('/')}
        />
      </div>
    </>
  )
}

export default DashboardShell
