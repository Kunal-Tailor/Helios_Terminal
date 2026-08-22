import { useMutation } from '@tanstack/react-query'
import DecisionInputForm from '../components/decision-input/DecisionInputForm'
import PipelineStatusStrip from '../components/pipeline-status/PipelineStatusStrip'
import type { StripPhase } from '../components/pipeline-status/PipelineStatusStrip'
import { ApiError, submitDecision } from '../lib/api'
import type { DecisionRequest } from '../lib/api'

function Home() {
  const mutation = useMutation({ mutationFn: (brief: DecisionRequest) => submitDecision(brief) })

  const phase: StripPhase | null = mutation.isPending
    ? 'running'
    : mutation.isError
      ? mutation.error instanceof ApiError && mutation.error.status === 0
        ? 'unreachable'
        : 'error'
      : mutation.data
        ? mutation.data.verification_passed
          ? 'complete'
          : 'halted'
        : null

  const showForm =
    phase === null || phase === 'halted' || phase === 'unreachable' || phase === 'error'

  return (
    <main>
      <h1>Helios Terminal</h1>
      {phase !== null && (
        <PipelineStatusStrip
          phase={phase}
          failedStage={
            phase === 'halted' ? (mutation.data?.verification_failed_stage ?? null) : null
          }
          onRetry={
            mutation.variables ? () => mutation.mutate(mutation.variables) : undefined
          }
        />
      )}
      {showForm && <DecisionInputForm onSubmit={(brief) => mutation.mutate(brief)} />}
    </main>
  )
}

export default Home
