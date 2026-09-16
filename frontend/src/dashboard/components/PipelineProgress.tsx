import React from 'react';
import { CheckCircle2, Circle, Loader2, XCircle } from 'lucide-react';

const STAGES = [
  { key: 'ingestion', label: 'Ingest', num: '01' },
  { key: 'stack_mapping', label: 'Map Stack', num: '02' },
  { key: 'scenario_generation', label: 'Generate', num: '03' },
  { key: 'outcome_prediction', label: 'Predict', num: '04' },
  { key: 'dependency_diagnosis', label: 'Diagnose', num: '05' },
  { key: 'orchestrator', label: 'Verdict', num: '06' },
];

interface PipelineProgressProps {
  status: 'queued' | 'processing' | 'completed' | 'failed';
  error?: string | null;
}

export const PipelineProgress: React.FC<PipelineProgressProps> = ({ status, error }) => {
  // For a real-time stage tracker we'd need per-stage status from the backend.
  // Since the backend only reports overall status, we simulate progressive activation.
  const [activeStage, setActiveStage] = React.useState(0);

  React.useEffect(() => {
    if (status !== 'processing') return;

    const interval = setInterval(() => {
      setActiveStage((prev) => {
        if (prev >= STAGES.length - 1) return prev;
        return prev + 1;
      });
    }, 12000); // ~12s per stage to cover ~1-3 min total

    return () => clearInterval(interval);
  }, [status]);

  React.useEffect(() => {
    if (status === 'completed') {
      setActiveStage(STAGES.length); // all done
    }
  }, [status]);

  const getStageState = (index: number) => {
    if (status === 'failed') return index <= activeStage ? 'failed' : 'pending';
    if (status === 'completed') return 'done';
    if (status === 'queued') return 'pending';
    // processing
    if (index < activeStage) return 'done';
    if (index === activeStage) return 'active';
    return 'pending';
  };

  return (
    <div className="dash-animate-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <span
            className="inline-flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-mono uppercase tracking-widest rounded"
            style={{ background: 'var(--dash-surface-raised)', border: '1px solid var(--dash-border-strong)', color: 'var(--dash-accent)' }}
          >
            PIPELINE_STATUS
          </span>
        </div>
        <span className="text-[11px] font-mono uppercase tracking-wider" style={{
          color: status === 'completed' ? 'var(--dash-success)' :
                 status === 'failed' ? 'var(--dash-danger)' :
                 'var(--dash-warning)',
        }}>
          {status === 'queued' && '● QUEUED'}
          {status === 'processing' && '● PROCESSING'}
          {status === 'completed' && '● COMPLETE'}
          {status === 'failed' && '● FAILED'}
        </span>
      </div>

      {/* Stage cards */}
      <div className="space-y-2">
        {STAGES.map((stage, i) => {
          const state = getStageState(i);
          return (
            <div
              key={stage.key}
              className="flex items-center gap-3 px-4 py-3 rounded transition-all duration-300"
              style={{
                background: state === 'active' ? 'var(--dash-surface-raised)' : 'transparent',
                border: `1px solid ${state === 'active' ? 'var(--dash-border-strong)' : 'var(--dash-border)'}`,
                opacity: state === 'pending' ? 0.4 : 1,
              }}
            >
              {/* Status icon */}
              <div className="flex-shrink-0">
                {state === 'done' && <CheckCircle2 className="w-4 h-4" style={{ color: 'var(--dash-success)' }} />}
                {state === 'active' && <Loader2 className="w-4 h-4 animate-spin" style={{ color: 'var(--dash-accent)' }} />}
                {state === 'pending' && <Circle className="w-4 h-4" style={{ color: 'var(--dash-text-muted)' }} />}
                {state === 'failed' && <XCircle className="w-4 h-4" style={{ color: 'var(--dash-danger)' }} />}
              </div>

              {/* Stage number */}
              <span className="text-[10px] font-mono tracking-wider" style={{
                color: state === 'active' ? 'var(--dash-accent)' : 'var(--dash-text-muted)',
              }}>
                {stage.num}
              </span>

              {/* Stage name */}
              <span className="text-sm font-sans font-medium" style={{
                color: state === 'done' ? 'var(--dash-text-primary)' :
                       state === 'active' ? 'var(--dash-text-primary)' :
                       'var(--dash-text-muted)',
              }}>
                {stage.label}
              </span>

              {/* Scan line for active stage */}
              {state === 'active' && (
                <div className="flex-1 h-px overflow-hidden ml-2 relative">
                  <div
                    className="absolute inset-0 h-full dash-animate-scan"
                    style={{
                      background: 'linear-gradient(90deg, transparent, var(--dash-accent), transparent)',
                      width: '60%',
                    }}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Error message */}
      {status === 'failed' && error && (
        <div
          className="mt-4 px-4 py-3 rounded text-sm font-mono"
          style={{ background: 'rgba(248, 81, 73, 0.1)', border: '1px solid var(--dash-danger)', color: 'var(--dash-danger)' }}
        >
          ERROR: {error}
        </div>
      )}

      {/* Processing note */}
      {status === 'processing' && (
        <p className="mt-4 text-xs font-mono" style={{ color: 'var(--dash-text-muted)' }}>
          Pipeline executing 6 stages with 18 sub-agents. This typically takes 1–3 minutes.
        </p>
      )}
    </div>
  );
};
