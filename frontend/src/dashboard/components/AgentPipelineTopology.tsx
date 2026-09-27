import React from 'react';
import {
  Activity,
  CheckCircle2,
  Circle,
  Loader2,
  AlertTriangle,
  RefreshCw,
  Cpu,
  Layers,
  GitBranch,
  TrendingUp,
  ShieldAlert,
  Award,
} from 'lucide-react';
import type { JobStatusResponse, VerificationResult, RecalibrationTrailItem } from '../api';

interface AgentPipelineTopologyProps {
  status: JobStatusResponse['status'] | 'idle';
  verificationResults?: VerificationResult[];
  recalibrationTrail?: RecalibrationTrailItem[];
  stageProviders?: Record<string, string>;
  error?: string | null;
}

interface StageInfo {
  key: string;
  name: string;
  code: string;
  subAgents: string[];
  focus: string;
  icon: React.ElementType;
}

const PIPELINE_STAGES: StageInfo[] = [
  {
    key: 'ingestion',
    name: 'Ingestion Agent',
    code: 'STAGE_01',
    subAgents: ['Web Scraping', 'BIS & HF Hub Source Registry', 'Context Synthesis'],
    focus: 'Gathers raw market groundings, open-weight licenses, and export control boundaries.',
    icon: Cpu,
  },
  {
    key: 'stack_mapping',
    name: 'Stack-Mapping Agent',
    code: 'STAGE_02',
    subAgents: ['Layer Identification', 'Relevance Filtering', 'Dependency Linkage'],
    focus: 'Maps AI stack layers from silicon accelerators to tensor runtimes and API wrappers.',
    icon: Layers,
  },
  {
    key: 'scenario_generation',
    name: 'Scenario Generation',
    code: 'STAGE_03',
    subAgents: ['Option Enumeration', 'Feasibility Check', 'Scenario Refinement'],
    focus: 'Generates plausible build, buy, and outsource variants grounded in institutional constraints.',
    icon: GitBranch,
  },
  {
    key: 'outcome_prediction',
    name: 'Outcome Prediction',
    code: 'STAGE_04',
    subAgents: ['Trajectory Modeling', 'Risk Factor Discovery', 'Timeline Projection'],
    focus: 'Projects 5-year trajectories, cost escalation curves, and operational failure modes.',
    icon: TrendingUp,
  },
  {
    key: 'dependency_diagnosis',
    name: 'Dependency Diagnosis',
    code: 'STAGE_05',
    subAgents: ['Lock-In Identification', 'Failure Mode Matrix', 'Severity Scoring'],
    focus: 'Isolates high-risk lock-in vectors (Data Gravity, Proprietary APIs, Talent Scarcity).',
    icon: ShieldAlert,
  },
  {
    key: 'orchestrator',
    name: 'Orchestrator Agent',
    code: 'STAGE_06',
    subAgents: ['Cross-Path Comparison', 'Explanation Trail', 'Verdict Synthesis'],
    focus: 'Synthesizes final comparative stance, grounded evidence trail, and strategic caveats.',
    icon: Award,
  },
];

export const AgentPipelineTopology: React.FC<AgentPipelineTopologyProps> = ({
  status,
  verificationResults = [],
  recalibrationTrail = [],
  stageProviders,
  error,
}) => {
  const [activeStageIdx, setActiveStageIdx] = React.useState<number>(
    status === 'completed' ? 5 : status === 'processing' ? 2 : 0
  );

  React.useEffect(() => {
    if (status === 'processing') {
      const interval = setInterval(() => {
        setActiveStageIdx((prev) => (prev < 5 ? prev + 1 : prev));
      }, 5000);
      return () => clearInterval(interval);
    } else if (status === 'completed') {
      setActiveStageIdx(5);
    }
  }, [status]);

  const getStageStatus = (idx: number) => {
    if (status === 'completed') return 'DONE';
    if (status === 'failed') return idx <= activeStageIdx ? 'ERROR' : 'IDLE';
    if (status === 'processing') {
      if (idx < activeStageIdx) return 'DONE';
      if (idx === activeStageIdx) return 'ACTIVE';
      return 'QUEUED';
    }
    return 'STANDBY';
  };

  return (
    <div className="flex flex-col h-full bg-[var(--bb-bg-surface)] text-[var(--bb-text-primary)]">
      {/* Panel Header */}
      <div className="bb-panel-header">
        <div className="flex items-center gap-2">
          <Activity className="w-3.5 h-3.5 text-[var(--bb-cyan)]" />
          <span>6-STAGE AGENT PIPELINE TOPOLOGY</span>
          <span className="text-[10px] text-[var(--bb-text-muted)]">[18 SUB-AGENTS]</span>
        </div>
        <div className="flex items-center gap-2">
          {verificationResults.length > 0 && (
            <span className="bb-badge bb-badge-dim">
              {verificationResults.length} AUDIT GATES
            </span>
          )}
          {recalibrationTrail.length > 0 && (
            <span className="bb-badge bb-badge-amber">
              <RefreshCw className="w-2.5 h-2.5 animate-spin" />
              RECALIBRATION ACTIVE ({recalibrationTrail.length})
            </span>
          )}
          <span
            className={`bb-badge ${
              status === 'completed'
                ? 'bb-badge-green'
                : status === 'processing'
                ? 'bb-badge-cyan bb-live-indicator'
                : status === 'failed'
                ? 'bb-badge-red'
                : 'bb-badge-dim'
            }`}
          >
            {status.toUpperCase()}
          </span>
        </div>
      </div>

      <div className="p-3 space-y-2.5 overflow-y-auto bb-scroll flex-1 text-xs font-mono">
        {/* Stages list */}
        {PIPELINE_STAGES.map((stage, idx) => {
          const stageState = getStageStatus(idx);
          const IconComp = stage.icon;

          return (
            <div
              key={stage.key}
              className={`p-2.5 rounded border transition-all ${
                stageState === 'ACTIVE'
                  ? 'bg-[var(--bb-bg-raised)] border-[var(--bb-cyan)] shadow-md'
                  : stageState === 'DONE'
                  ? 'bg-[var(--bb-bg-raised)] border-[var(--bb-border-subtle)]'
                  : 'bg-[var(--bb-bg-base)] border-[var(--bb-border-subtle)] opacity-50'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-bold text-[var(--bb-amber)]">
                    {stage.code}
                  </span>
                  <span className="text-[var(--bb-border-mid)]">/</span>
                  <IconComp
                    className={`w-3.5 h-3.5 ${
                      stageState === 'DONE'
                        ? 'text-[var(--bb-green)]'
                        : stageState === 'ACTIVE'
                        ? 'text-[var(--bb-cyan)]'
                        : 'text-[var(--bb-text-muted)]'
                    }`}
                  />
                  <span className="font-bold text-[11px] text-[var(--bb-text-bright)]">
                    {stage.name}
                  </span>
                  {stageProviders?.[stage.key] && (
                    <span className="text-[9px] px-1.5 py-0.5 bg-[var(--bb-bg-surface)] text-[var(--bb-cyan)] border border-[var(--bb-cyan)]/40 rounded font-mono uppercase tracking-tight">
                      {stageProviders[stage.key]}
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-1.5">
                  {stageState === 'DONE' && (
                    <span className="text-[10px] text-[var(--bb-green)] flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3" /> VERIFIED
                    </span>
                  )}
                  {stageState === 'ACTIVE' && (
                    <span className="text-[10px] text-[var(--bb-cyan)] flex items-center gap-1 font-bold">
                      <Loader2 className="w-3 h-3 animate-spin" /> SYNTHESIZING
                    </span>
                  )}
                  {stageState === 'QUEUED' && (
                    <span className="text-[10px] text-[var(--bb-text-muted)] flex items-center gap-1">
                      <Circle className="w-2.5 h-2.5" /> QUEUED
                    </span>
                  )}
                  {stageState === 'STANDBY' && (
                    <span className="text-[9px] text-[var(--bb-text-dim)]">STANDBY</span>
                  )}
                </div>
              </div>

              {/* Sub-agents pills */}
              <div className="flex flex-wrap gap-1 mb-1.5">
                {stage.subAgents.map((sub, sIdx) => (
                  <span
                    key={sIdx}
                    className="text-[9px] px-1.5 py-0.5 bg-[var(--bb-bg-surface)] text-[var(--bb-text-secondary)] border border-[var(--bb-border-subtle)] rounded"
                  >
                    • {sub}
                  </span>
                ))}
              </div>

              <p className="text-[10px] text-[var(--bb-text-dim)] line-clamp-1 leading-normal">
                {stage.focus}
              </p>

              {/* Progress line for active stage */}
              {stageState === 'ACTIVE' && (
                <div className="w-full bg-[var(--bb-border-subtle)] h-0.5 rounded overflow-hidden mt-2">
                  <div className="bg-[var(--bb-cyan)] h-full w-2/3 animate-pulse" />
                </div>
              )}
            </div>
          );
        })}

        {/* Error notification if failed */}
        {status === 'failed' && error && (
          <div className="p-3 bg-[var(--bb-red-dim)] border border-[var(--bb-red)] rounded text-xs text-[var(--bb-red-bright)] flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <div>
              <span className="font-bold block">PIPELINE EXECUTION EXCEPTION</span>
              <p className="mt-1 text-[11px] text-[var(--bb-text-primary)]">{error}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
