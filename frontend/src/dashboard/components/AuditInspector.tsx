import React, { useState } from 'react';
import {
  ShieldCheck,
  CheckCircle2,
  XCircle,
  ExternalLink,
  Search,
  Database,
} from 'lucide-react';
import type { VerificationResult, RecalibrationTrailItem, ExplanationTrail } from '../api';

interface AuditInspectorProps {
  verificationResults: VerificationResult[];
  recalibrationTrail: RecalibrationTrailItem[];
  explanationTrail?: ExplanationTrail | null;
  verificationPassed: boolean;
  verificationFailedStage?: string | null;
}

export const AuditInspector: React.FC<AuditInspectorProps> = ({
  verificationResults,
  recalibrationTrail,
  explanationTrail,
  verificationPassed,
  verificationFailedStage,
}) => {
  const [filterMode, setFilterMode] = useState<'ALL' | 'PASSED' | 'FAILED'>('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const passedCount = verificationResults.filter((v) => v.passed).length;
  const failedCount = verificationResults.filter((v) => !v.passed).length;

  const filteredResults = verificationResults.filter((item) => {
    if (filterMode === 'PASSED' && !item.passed) return false;
    if (filterMode === 'FAILED' && item.passed) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      return (
        item.claim.toLowerCase().includes(q) ||
        item.reason.toLowerCase().includes(q) ||
        item.agent_stage.toLowerCase().includes(q)
      );
    }
    return true;
  });

  return (
    <div className="flex flex-col h-full bg-[var(--bb-bg-surface)] text-[var(--bb-text-primary)]">
      {/* Panel Header */}
      <div className="bb-panel-header">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-3.5 h-3.5 text-[var(--bb-green)]" />
          <span>GROUNDED AUDIT TRAIL & VERIFIER INSPECTOR</span>
          <span className="text-[10px] text-[var(--bb-text-muted)]">[FUNCTION 05]</span>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`bb-badge ${
              verificationPassed ? 'bb-badge-green' : 'bb-badge-red'
            }`}
          >
            {verificationPassed
              ? 'ALL CLAIMS GROUNDED (100%)'
              : `GATE FAILED: ${verificationFailedStage?.toUpperCase()}`}
          </span>
        </div>
      </div>

      <div className="p-4 space-y-4 overflow-y-auto bb-scroll flex-1 text-xs font-mono">
        {/* Verification Summary KPIs */}
        <div className="grid grid-cols-4 gap-2">
          <div className="p-2.5 bg-[var(--bb-bg-base)] border border-[var(--bb-border-subtle)] rounded">
            <span className="text-[10px] text-[var(--bb-text-muted)] block mb-1">TOTAL AUDIT STEPS</span>
            <span className="text-sm font-bold text-[var(--bb-text-bright)] bb-tabular">
              {verificationResults.length} CLAIMS
            </span>
          </div>
          <div className="p-2.5 bg-[var(--bb-bg-base)] border border-[var(--bb-border-subtle)] rounded">
            <span className="text-[10px] text-[var(--bb-text-muted)] block mb-1">VERIFIED GROUNDINGS</span>
            <span className="text-sm font-bold text-[var(--bb-green)] bb-tabular">
              {passedCount} PASSED
            </span>
          </div>
          <div className="p-2.5 bg-[var(--bb-bg-base)] border border-[var(--bb-border-subtle)] rounded">
            <span className="text-[10px] text-[var(--bb-text-muted)] block mb-1">REJECTED CLAIMS</span>
            <span className="text-sm font-bold text-[var(--bb-red)] bb-tabular">
              {failedCount} FAILED
            </span>
          </div>
          <div className="p-2.5 bg-[var(--bb-bg-base)] border border-[var(--bb-border-subtle)] rounded">
            <span className="text-[10px] text-[var(--bb-text-muted)] block mb-1">RECALIBRATIONS</span>
            <span className="text-sm font-bold text-[var(--bb-amber)] bb-tabular">
              {recalibrationTrail.length} LOOPS
            </span>
          </div>
        </div>

        {/* Filter and Search Bar */}
        <div className="flex items-center justify-between gap-3 pt-2">
          <div className="flex items-center gap-1 bg-[var(--bb-bg-base)] p-1 rounded border border-[var(--bb-border-subtle)]">
            {(['ALL', 'PASSED', 'FAILED'] as const).map((m) => (
              <button
                key={m}
                type="button"
                onClick={() => setFilterMode(m)}
                className={`px-2 py-0.5 text-[9px] font-bold rounded ${
                  filterMode === m
                    ? 'bg-[var(--bb-amber)] text-black'
                    : 'text-[var(--bb-text-muted)] hover:text-[var(--bb-text-primary)]'
                }`}
              >
                {m}
              </button>
            ))}
          </div>

          <div className="relative flex-1 max-w-xs">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search claims, agents, or reasons..."
              className="w-full bg-[var(--bb-bg-input)] border border-[var(--bb-border-mid)] focus:border-[var(--bb-amber)] text-[var(--bb-text-bright)] px-2.5 py-1 text-xs font-mono rounded outline-none pl-7"
            />
            <Search className="w-3.5 h-3.5 absolute left-2 top-2 text-[var(--bb-text-dim)]" />
          </div>
        </div>

        {/* Verification Items List */}
        <div className="space-y-2">
          {filteredResults.length === 0 ? (
            <div className="p-6 text-center text-[var(--bb-text-muted)] border border-[var(--bb-border-subtle)] rounded bg-[var(--bb-bg-base)]">
              No verification steps match the active query.
            </div>
          ) : (
            filteredResults.map((vr, i) => (
              <div
                key={i}
                className="p-3 bg-[var(--bb-bg-raised)] border border-[var(--bb-border-subtle)] rounded hover:border-[var(--bb-border-mid)] transition-colors"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-2">
                    {vr.passed ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-[var(--bb-green)] flex-shrink-0" />
                    ) : (
                      <XCircle className="w-3.5 h-3.5 text-[var(--bb-red)] flex-shrink-0" />
                    )}
                    <span className="font-bold text-[11px] text-[var(--bb-amber)] uppercase">
                      {vr.agent_stage}
                    </span>
                    {vr.provider && (
                      <span className="text-[9px] px-1.5 py-0.2 bg-[var(--bb-bg-surface)] text-[var(--bb-cyan)] border border-[var(--bb-cyan)]/40 rounded font-mono uppercase tracking-tight">
                        {vr.provider}
                      </span>
                    )}
                  </div>
                  <span
                    className={`text-[9px] px-1.5 py-0.5 rounded font-bold ${
                      vr.passed
                        ? 'bg-[var(--bb-green-dim)] text-[var(--bb-green)]'
                        : 'bg-[var(--bb-red-dim)] text-[var(--bb-red)]'
                    }`}
                  >
                    CONFIDENCE: {(vr.confidence * 100).toFixed(0)}%
                  </span>
                </div>

                <p className="text-[11px] font-medium text-[var(--bb-text-bright)] mb-1 leading-snug">
                  "{vr.claim}"
                </p>
                <p className="text-[10px] text-[var(--bb-text-secondary)] leading-normal">
                  <span className="text-[var(--bb-text-dim)]">GROUNDING REASON:</span> {vr.reason}
                </p>
              </div>
            ))
          )}
        </div>

        {/* Cited Evidence Sources */}
        {explanationTrail && explanationTrail.sources && explanationTrail.sources.length > 0 && (
          <div className="pt-3 border-t border-[var(--bb-border-subtle)]">
            <span className="text-[10px] text-[var(--bb-text-muted)] uppercase tracking-wider block mb-2 flex items-center gap-1.5">
              <Database className="w-3 h-3 text-[var(--bb-cyan)]" />
              AUTHENTICATED GROUNDING SOURCES ({explanationTrail.sources.length})
            </span>
            <div className="space-y-1">
              {explanationTrail.sources.map((src, sIdx) => (
                <a
                  key={sIdx}
                  href={src.startsWith('http') ? src : undefined}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-between p-2 bg-[var(--bb-bg-base)] border border-[var(--bb-border-subtle)] rounded hover:border-[var(--bb-cyan)] transition-colors group"
                >
                  <span className="text-[10px] text-[var(--bb-text-secondary)] group-hover:text-[var(--bb-cyan)] truncate pr-2">
                    {src}
                  </span>
                  <ExternalLink className="w-3 h-3 text-[var(--bb-text-dim)] group-hover:text-[var(--bb-cyan)] flex-shrink-0" />
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
