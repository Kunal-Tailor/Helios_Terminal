import React, { useState } from 'react';
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
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  Zap,
} from 'lucide-react';
import type { JobStatusResponse, VerificationResult, RecalibrationTrailItem } from '../api';
import { terminalAudio } from '../utils/terminalAudio';

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
  subAgents: { name: string; desc: string }[];
  focus: string;
  icon: React.ElementType;
}

const PIPELINE_STAGES: StageInfo[] = [
  {
    key: 'ingestion',
    name: 'Ingestion Agent',
    code: 'STAGE_01',
    subAgents: [
      { name: 'Web Scraping Sub-Agent', desc: 'Queries real-time market data & tech reports via Tavily' },
      { name: 'Structured Registry Sub-Agent', desc: 'Validates BIS export controls & Hugging Face licensing' },
      { name: 'Context Synthesis Sub-Agent', desc: 'Merges multi-source evidence into structured brief context' },
    ],
    focus: 'Gathers raw market groundings, open-weight licenses, and export control boundaries.',
    icon: Cpu,
  },
  {
    key: 'stack_mapping',
    name: 'Stack-Mapping Agent',
    code: 'STAGE_02',
    subAgents: [
      { name: 'Layer Identification Sub-Agent', desc: 'Proposes full-stack AI layers from silicon to frontend' },
      { name: 'Relevance Filter Sub-Agent', desc: 'Narrows scope to layers directly touched by this decision' },
      { name: 'Dependency Linkage Sub-Agent', desc: 'Maps upstream hardware & downstream API coupling' },
    ],
    focus: 'Maps AI stack layers from silicon accelerators to tensor runtimes and API wrappers.',
    icon: Layers,
  },
  {
    key: 'scenario_generation',
    name: 'Scenario Generation',
    code: 'STAGE_03',
    subAgents: [
      { name: 'Option Enumeration Sub-Agent', desc: 'Enumerates raw build, buy, and outsource candidate paths' },
      { name: 'Feasibility Check Sub-Agent', desc: 'Filters out infeasible or prohibited sourcing options' },
      { name: 'Scenario Refinement Sub-Agent', desc: 'Polishes viable variants into concrete execution blueprints' },
    ],
    focus: 'Generates plausible build, buy, and outsource variants grounded in institutional constraints.',
    icon: GitBranch,
  },
  {
    key: 'outcome_prediction',
    name: 'Outcome Prediction',
    code: 'STAGE_04',
    subAgents: [
      { name: 'Trajectory Modeling Sub-Agent', desc: 'Projects forward 5-year cost and maintenance curves' },
      { name: 'Timeline Projection Sub-Agent', desc: 'Estimates deployment ramp-up and migration friction' },
      { name: 'Risk Factor Discovery Sub-Agent', desc: 'Isolates potential failure modes per candidate trajectory' },
    ],
    focus: 'Projects 5-year trajectories, cost escalation curves, and operational failure modes.',
    icon: TrendingUp,
  },
  {
    key: 'dependency_diagnosis',
    name: 'Dependency Diagnosis',
    code: 'STAGE_05',
    subAgents: [
      { name: 'Lock-In Identification Sub-Agent', desc: 'Isolates data gravity, proprietary API & vendor lock-in' },
      { name: 'Failure Mode Matrix Sub-Agent', desc: 'Catalogs severe operational blackout & license revocation risks' },
      { name: 'Severity Scoring Sub-Agent', desc: 'Computes normalized 0-10 lock-in severity index per path' },
    ],
    focus: 'Isolates high-risk lock-in vectors (Data Gravity, Proprietary APIs, Talent Scarcity).',
    icon: ShieldAlert,
  },
  {
    key: 'orchestrator',
    name: 'Orchestrator Agent',
    code: 'STAGE_06',
    subAgents: [
      { name: 'Cross-Path Comparison Sub-Agent', desc: 'Synthesizes side-by-side comparative stance' },
      { name: 'Explanation Trail Sub-Agent', desc: 'Builds verifiable claim-to-source audit inspection trail' },
      { name: 'Verdict Synthesis Sub-Agent', desc: 'Formulates final executive recommendation and caveats' },
    ],
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
  const [activeStageIdx, setActiveStageIdx] = useState<number>(
    status === 'completed' ? 5 : status === 'processing' ? 2 : 0
  );
  const [expandedStageKey, setExpandedStageKey] = useState<string | null>(null);

  React.useEffect(() => {
    if (status === 'processing') {
      const interval = setInterval(() => {
        setActiveStageIdx((prev) => (prev < 5 ? prev + 1 : prev));
      }, 4500);
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

  const handleToggleStage = (key: string) => {
    terminalAudio.playBlip();
    setExpandedStageKey((prev) => (prev === key ? null : key));
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
            <span className="bb-badge bb-badge-green flex items-center gap-1">
              <ShieldCheck className="w-3 h-3" />
              {verificationResults.length} AUDIT GATES
            </span>
          )}
          {recalibrationTrail.length > 0 && (
            <span className="bb-badge bb-badge-amber">
              <RefreshCw className="w-2.5 h-2.5 animate-spin" />
              RECALIBRATION ({recalibrationTrail.length})
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
          const isExpanded = expandedStageKey === stage.key;
          const stageVerification = verificationResults.find((v) => v.agent_stage === stage.key);

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
              <div
                className="flex items-center justify-between cursor-pointer select-none"
                onClick={() => handleToggleStage(stage.key)}
              >
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
                    <span className="text-[9px] px-1.5 py-0.2 bg-[var(--bb-bg-surface)] text-[var(--bb-cyan)] border border-[var(--bb-cyan)]/40 rounded font-mono uppercase tracking-tight">
                      {stageProviders[stage.key]}
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-2">
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
                  {isExpanded ? (
                    <ChevronUp className="w-3.5 h-3.5 text-[var(--bb-text-dim)]" />
                  ) : (
                    <ChevronDown className="w-3.5 h-3.5 text-[var(--bb-text-dim)]" />
                  )}
                </div>
              </div>

              {/* Collapsed view pills */}
              {!isExpanded && (
                <div className="flex flex-wrap gap-1 mt-1.5">
                  {stage.subAgents.map((sub, sIdx) => (
                    <span
                      key={sIdx}
                      className="text-[9px] px-1.5 py-0.5 bg-[var(--bb-bg-surface)] text-[var(--bb-text-secondary)] border border-[var(--bb-border-subtle)] rounded"
                    >
                      • {sub.name.replace(' Sub-Agent', '')}
                    </span>
                  ))}
                </div>
              )}

              {/* Expanded details view */}
              {isExpanded && (
                <div className="mt-2.5 pt-2 border-t border-[var(--bb-border-subtle)] space-y-2">
                  <p className="text-[10px] text-[var(--bb-text-secondary)] leading-relaxed">
                    {stage.focus}
                  </p>

                  <div className="space-y-1">
                    <span className="text-[9px] text-[var(--bb-text-muted)] uppercase block">
                      PARALLEL SUB-AGENTS:
                    </span>
                    {stage.subAgents.map((sub, sIdx) => (
                      <div
                        key={sIdx}
                        className="p-1.5 bg-[var(--bb-bg-surface)] border border-[var(--bb-border-subtle)] rounded text-[10px] flex items-start gap-1.5"
                      >
                        <Zap className="w-2.5 h-2.5 text-[var(--bb-amber)] mt-0.5 flex-shrink-0" />
                        <div>
                          <span className="font-bold text-[var(--bb-text-bright)] block">
                            {sub.name}
                          </span>
                          <span className="text-[9px] text-[var(--bb-text-dim)]">
                            {sub.desc}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>

                  {stageVerification && (
                    <div className="p-2 bg-[var(--bb-green-dim)] border border-[var(--bb-green)] rounded text-[10px] flex items-center justify-between">
                      <span className="font-bold text-[var(--bb-green)]">
                        CLAIM VERIFICATION CONFIDENCE: {(stageVerification.confidence * 100).toFixed(0)}%
                      </span>
                      <span className="text-[9px] text-[var(--bb-text-secondary)]">
                        {stageVerification.reason}
                      </span>
                    </div>
                  )}
                </div>
              )}

              {/* Progress bar for active stage */}
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
