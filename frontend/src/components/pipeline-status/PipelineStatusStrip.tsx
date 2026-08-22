const STAGES = [
  { id: 'ingestion', label: 'Ingestion' },
  { id: 'stack_mapping', label: 'Stack-Mapping' },
  { id: 'scenario_generation', label: 'Scenario-Generation' },
  { id: 'outcome_prediction', label: 'Outcome-Prediction' },
  { id: 'dependency_diagnosis', label: 'Dependency-Diagnosis' },
  { id: 'orchestrator', label: 'Orchestrator' },
] as const

export type StripPhase = 'running' | 'complete' | 'halted' | 'unreachable' | 'error'

type StageMark = 'pending' | 'complete' | 'failed'

interface PipelineStatusStripProps {
  phase: StripPhase
  failedStage?: string | null
  onRetry?: () => void
}

function stageMarkText(mark: StageMark): string {
  if (mark === 'complete') return 'completed'
  if (mark === 'failed') return 'failed'
  return 'not run'
}

function PipelineStatusStrip({ phase, failedStage, onRetry }: PipelineStatusStripProps) {
  let marks: StageMark[]
  if (phase === 'complete') {
    marks = STAGES.map(() => 'complete')
  } else if (phase === 'halted') {
    const failedIndex = STAGES.findIndex((stage) => stage.id === failedStage)
    marks =
      failedIndex === -1
        ? STAGES.map(() => 'pending')
        : STAGES.map((_, index) =>
            index < failedIndex ? 'complete' : index === failedIndex ? 'failed' : 'pending',
          )
  } else {
    marks = STAGES.map(() => 'pending')
  }

  const failedLabel =
    phase === 'halted'
      ? (STAGES.find((stage) => stage.id === failedStage)?.label ?? null)
      : null

  return (
    <section aria-live="polite">
      <h2>
        {phase === 'running' && 'Running pipeline…'}
        {phase === 'complete' && 'Pipeline complete'}
        {phase === 'halted' && 'Stage failed verification'}
        {phase === 'unreachable' && "Couldn't reach Helios"}
        {phase === 'error' && 'Request failed'}
      </h2>
      <ol>
        {STAGES.map((stage, index) => {
          const mark = marks[index]
          const symbol = mark === 'complete' ? '✓' : mark === 'failed' ? '✗' : '·'
          return (
            <li key={stage.id} data-state={mark} title={`${stage.label}: ${stageMarkText(mark)}`}>
              <span aria-hidden="true">{symbol}</span> {stage.label}
            </li>
          )
        })}
      </ol>
      {phase === 'running' && <p>All six stages run with verification gates between them.</p>}
      {phase === 'halted' && (
        <>
          <p>
            {failedLabel
              ? `The ${failedLabel} stage could not be verified against its sources.`
              : 'A stage could not be verified against its sources.'}
          </p>
          {onRetry && (
            <button type="button" onClick={onRetry}>
              Try again
            </button>
          )}
        </>
      )}
      {phase === 'unreachable' && (
        <>
          <p>Check your connection and try again.</p>
          {onRetry && (
            <button type="button" onClick={onRetry}>
              Try again
            </button>
          )}
        </>
      )}
      {phase === 'error' && (
        <>
          <p>Helios returned an unexpected response.</p>
          {onRetry && (
            <button type="button" onClick={onRetry}>
              Try again
            </button>
          )}
        </>
      )}
    </section>
  )
}

export default PipelineStatusStrip
