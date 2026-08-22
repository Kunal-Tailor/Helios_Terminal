import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import DecisionInputForm from '../components/decision-input/DecisionInputForm'
import PipelineStatusStrip from '../components/pipeline-status/PipelineStatusStrip'
import type { StripPhase } from '../components/pipeline-status/PipelineStatusStrip'
import { ApiError, submitDecision } from '../lib/api'
import type { DecisionRequest } from '../lib/api'

function Home() {
  const navigate = useNavigate()
  const mutation = useMutation({
    mutationKey: ['submitDecision'],
    mutationFn: (brief: DecisionRequest) => submitDecision(brief),
  })

  useEffect(() => {
    if (mutation.isSuccess && mutation.data && mutation.data.verification_passed) {
      navigate('/result')
    }
  }, [mutation.isSuccess, mutation.data, navigate])

  const isRateLimitError = mutation.isError &&
    mutation.error instanceof ApiError &&
    mutation.error.isRateLimit

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
    <main className="panel-transition mx-auto max-w-2xl space-y-6 px-8 py-10">
      <h1 className="font-mono text-section-header leading-[1.3] text-primary">
        Helios Terminal
      </h1>
      {phase !== null && (
        <PipelineStatusStrip
          phase={phase}
          failedStage={
            phase === 'halted' ? (mutation.data?.verification_failed_stage ?? null) : null
          }
          onRetry={
            mutation.variables ? () => mutation.mutate(mutation.variables) : undefined
          }
          isRateLimit={isRateLimitError}
        />
      )}
      {showForm && <DecisionInputForm onSubmit={(brief) => mutation.mutate(brief)} />}
    </main>
  )
}

export default Home
