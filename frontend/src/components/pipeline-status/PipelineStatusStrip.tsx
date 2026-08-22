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
  isRateLimit?: boolean
}

function stageMarkText(mark: StageMark): string {
  if (mark === 'complete') return 'completed'
  if (mark === 'failed') return 'failed'
  return 'not run'
}

const MARK_SYMBOL_CLASS: Record<StageMark, string> = {
  complete: 'text-accent',
  failed: 'text-risk-critical',
  pending: 'text-tertiary',
}

const HEADER_TEXT: Record<StripPhase, string> = {
  running: 'Running pipeline…',
  complete: 'Pipeline complete',
  halted: 'Stage failed verification',
  unreachable: "Couldn't reach Helios",
  error: 'Request failed',
}

function PipelineStatusStrip({ phase, failedStage, onRetry, isRateLimit }: PipelineStatusStripProps) {
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
    <section
      aria-live="polite"
      className="space-y-3 rounded-sm border border-hairline bg-surface p-4 font-mono text-body-mono leading-[1.3]"
    >
      <h2
        className={
          phase === 'halted'
            ? 'text-risk-critical'
            : phase === 'complete'
              ? 'text-accent'
              : 'text-primary'
        }
      >
        {HEADER_TEXT[phase]}
      </h2>
      <ol className="space-y-1">
        {STAGES.map((stage, index) => {
          const mark = marks[index]
          const symbol = mark === 'complete' ? '✓' : mark === 'failed' ? '✗' : '·'
          const emphasized = mark === 'failed' || mark === 'complete'
          return (
            <li
              key={stage.id}
              data-state={mark}
              title={`${stage.label}: ${stageMarkText(mark)}`}
              className={emphasized ? 'text-primary' : 'text-secondary'}
            >
              <span aria-hidden="true" className={`mr-1.5 ${MARK_SYMBOL_CLASS[mark]}`}>
                {symbol}
              </span>
              {stage.label}
            </li>
          )
        })}
      </ol>
      {phase === 'running' && (
        <p className="text-secondary">All six stages run with verification gates between them.</p>
      )}
      {phase === 'halted' && (
        <>
          <p className="text-primary">
            {failedLabel
              ? `The ${failedLabel} stage could not be verified against its sources.`
              : 'A stage could not be verified against its sources.'}
          </p>
          {onRetry && (
            <button
              type="button"
              onClick={onRetry}
              className="rounded-sm border border-hairline bg-surface-raised px-3 py-1.5 font-ui text-body-ui text-primary hover:border-accent"
            >
              Try again
            </button>
          )}
        </>
      )}
      {phase === 'unreachable' && (
        <>
          <p className="text-primary">Check your connection and try again.</p>
          {onRetry && (
            <button
              type="button"
              onClick={onRetry}
              className="rounded-sm border border-hairline bg-surface-raised px-3 py-1.5 font-ui text-body-ui text-primary hover:border-accent"
            >
              Try again
            </button>
          )}
        </>
      )}
      {phase === 'error' && (
        <>
          <p className="text-primary">
            {isRateLimit
              ? 'LLM API rate limit exceeded. Please try again in a few moments.'
              : 'Helios returned an unexpected response.'}
          </p>
          {onRetry && (
            <button
              type="button"
              onClick={onRetry}
              className="rounded-sm border border-hairline bg-surface-raised px-3 py-1.5 font-ui text-body-ui text-primary hover:border-accent"
            >
              Try again
            </button>
          )}
        </>
      )}
    </section>
  )
}

export default PipelineStatusStrip
