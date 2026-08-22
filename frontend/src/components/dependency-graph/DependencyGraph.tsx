import { useMemo, useState } from 'react'
import { Background, ReactFlow } from '@xyflow/react'
import type { Edge, Node } from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import type { PathComparison } from '../../lib/api'
import { severityLabel } from '../../lib/severity'

const SEVERITY_BORDER_CLASS: Record<string, string> = {
  Critical: 'border-risk-critical',
  Elevated: 'border-risk-elevated',
  Low: 'border-risk-low',
}

const PATH_X = 0
const LOCK_X = 280
const PATH_GAP = 150
const LOCK_GAP = 56

interface DependencyGraphProps {
  paths: PathComparison[]
}

function DependencyGraph({ paths }: DependencyGraphProps) {
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const nodes = useMemo<Node[]>(() => {
    const result: Node[] = []
    paths.forEach((path, pathIndex) => {
      const pathY = pathIndex * PATH_GAP
      const band = severityLabel(path.max_severity_score)
      result.push({
        id: `path:${path.scenario_name}`,
        position: { x: PATH_X, y: pathY },
        data: {
          label: (
            <div className="text-left">
              <div className="font-mono text-body-mono leading-[1.3] text-primary">
                {path.scenario_name}
              </div>
              <div className="font-mono text-metadata leading-[1.3] text-secondary">
                {path.lock_in_count} lock-ins · {band} ({path.max_severity_score.toFixed(1)})
              </div>
            </div>
          ),
        },
        className: `rounded-sm border ${SEVERITY_BORDER_CLASS[band]} !bg-surface px-3 py-2`,
        draggable: false,
      })
      for (let lockIndex = 0; lockIndex < path.lock_in_count; lockIndex += 1) {
        result.push({
          id: `lock:${path.scenario_name}:${lockIndex}`,
          position: {
            x: LOCK_X,
            y:
              pathY -
              ((path.lock_in_count - 1) * LOCK_GAP) / 2 +
              lockIndex * LOCK_GAP,
          },
          data: { label: <span className="font-mono text-metadata text-secondary">Lock-in</span> },
          className: 'rounded-sm border border-hairline !bg-base px-2 py-1',
          draggable: false,
        })
      }
    })
    return result
  }, [paths])

  const edges = useMemo<Edge[]>(() => {
    const result: Edge[] = []
    paths.forEach((path) => {
      for (let lockIndex = 0; lockIndex < path.lock_in_count; lockIndex += 1) {
        result.push({
          id: `edge:${path.scenario_name}:${lockIndex}`,
          source: `path:${path.scenario_name}`,
          target: `lock:${path.scenario_name}:${lockIndex}`,
          style: { stroke: 'var(--border-hairline)' },
        })
      }
    })
    return result
  }, [paths])

  const selectedPath = useMemo(() => {
    if (!selectedId || !selectedId.startsWith('path:')) return null
    const name = selectedId.slice('path:'.length)
    return paths.find((path) => path.scenario_name === name) ?? null
  }, [selectedId, paths])

  if (paths.length === 0) {
    return (
      <div className="rounded-sm border border-hairline bg-surface p-8 font-mono text-metadata leading-[1.3] text-secondary">
        No paths to graph yet — run a decision first.
      </div>
    )
  }

  return (
    <div className="flex gap-4">
      <div className="dependency-graph h-[440px] flex-1 overflow-hidden rounded-sm border border-hairline bg-surface">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          fitView
          minZoom={0.4}
          nodesDraggable={false}
          onNodeClick={(_, node) => setSelectedId(node.id)}
          onPaneClick={() => setSelectedId(null)}
        >
          <Background color="var(--border-hairline)" gap={16} />
        </ReactFlow>
      </div>
      <aside className="w-64 shrink-0 space-y-3 rounded-sm border border-hairline bg-surface p-4 leading-[1.6]">
        {!selectedId && (
          <p className="font-mono text-metadata leading-[1.3] text-secondary">
            Select a node to inspect it.
          </p>
        )}
        {selectedPath && (
          <>
            <h4 className="font-mono text-body-mono leading-[1.3] text-primary">
              {selectedPath.scenario_name}
            </h4>
            <p className="font-serif text-prose text-primary">
              {selectedPath.path_summary || 'No outcome summary available.'}
            </p>
            <ul className="list-disc space-y-1 pl-5 font-serif text-prose text-primary">
              {selectedPath.key_tradeoffs.map((tradeoff) => (
                <li key={tradeoff}>{tradeoff}</li>
              ))}
            </ul>
          </>
        )}
        {selectedId?.startsWith('lock:') && (
          <>
            <h4 className="font-mono text-body-mono leading-[1.3] text-primary">Lock-in</h4>
            <p className="font-serif text-prose text-secondary">
              Unnamed dependency of{' '}
              <span className="font-mono text-metadata">
                {selectedId.slice('lock:'.length).split(':')[0]}
              </span>
              . Per-dependency names and failure modes are not exposed by the backend yet — see
              the path card for its combined analysis.
            </p>
          </>
        )}
      </aside>
    </div>
  )
}

export default DependencyGraph
