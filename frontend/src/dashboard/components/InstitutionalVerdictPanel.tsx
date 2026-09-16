import React from 'react';
import {
  Award,
  AlertTriangle,
  Lightbulb,
  ArrowRight,
  ShieldCheck,
  Zap,
} from 'lucide-react';
import type { OrchestratorVerdict } from '../api';

interface InstitutionalVerdictPanelProps {
  verdict: OrchestratorVerdict | null;
  caveats?: string[];
  verificationPassed?: boolean;
}

export const InstitutionalVerdictPanel: React.FC<InstitutionalVerdictPanelProps> = ({
  verdict,
  caveats = [],
  verificationPassed = true,
}) => {
  if (!verdict) {
    return (
      <div className="flex flex-col h-full bg-[var(--bb-bg-surface)] text-[var(--bb-text-muted)] p-6 items-center justify-center font-mono text-xs">
        <Award className="w-8 h-8 text-[var(--bb-border-mid)] mb-3" />
        <span className="text-[var(--bb-text-secondary)] font-bold mb-1 uppercase tracking-wider">
          AWAITING SYNTHESIS EXECUTION
        </span>
        <span className="text-[10px] text-center max-w-xs text-[var(--bb-text-dim)]">
          Submit a decision brief or load an institutional preset from Console [F2] to synthesize comparative verdict.
        </span>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-[var(--bb-bg-surface)] text-[var(--bb-text-primary)]">
      {/* Panel Header */}
      <div className="bb-panel-header">
        <div className="flex items-center gap-2">
          <Award className="w-3.5 h-3.5 text-[var(--bb-green)]" />
          <span>INSTITUTIONAL SOURCING VERDICT</span>
          <span className="text-[10px] text-[var(--bb-text-muted)]">[ORCHESTRATOR SYNTHESIS]</span>
        </div>
        <span
          className={`bb-badge ${
            verificationPassed ? 'bb-badge-green' : 'bb-badge-amber'
          } flex items-center gap-1`}
        >
          <ShieldCheck className="w-3 h-3" />
          {verificationPassed ? 'VERIFIED DECISION' : 'PARTIAL VERIFICATION'}
        </span>
      </div>

      <div className="p-4 space-y-4 overflow-y-auto bb-scroll flex-1 text-xs font-mono">
        {/* Recommended Path Banner */}
        <div className="p-3 bg-[var(--bb-green-dim)] border border-[var(--bb-green)] rounded">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[10px] text-[var(--bb-green-bright)] uppercase tracking-wider font-bold flex items-center gap-1.5">
              <Zap className="w-3 h-3" /> PRIMARY STRATEGIC RECOMMENDATION:
            </span>
            <span className="text-[9px] px-1.5 py-0.5 bg-[var(--bb-bg-base)] text-[var(--bb-green)] border border-[var(--bb-green)] rounded font-bold">
              OPTIMAL TCO & SOVEREIGNTY
            </span>
          </div>
          <h2 className="text-sm font-bold text-[var(--bb-text-bright)] leading-snug">
            {verdict.recommended_path}
          </h2>
        </div>

        {/* Verdict Summary Narrative */}
        <div>
          <span className="text-[10px] text-[var(--bb-text-muted)] uppercase tracking-wider block mb-1">
            EXECUTIVE RATIONALE & SYNTHESIS:
          </span>
          <p className="text-xs leading-relaxed text-[var(--bb-text-primary)] bg-[var(--bb-bg-raised)] p-3 rounded border border-[var(--bb-border-subtle)]">
            {verdict.verdict_summary}
          </p>
        </div>

        {/* Path Stances Matrix */}
        {verdict.path_stances && Object.keys(verdict.path_stances).length > 0 && (
          <div>
            <span className="text-[10px] text-[var(--bb-text-muted)] uppercase tracking-wider block mb-2">
              PATH-BY-PATH STRATEGIC STANCES:
            </span>
            <div className="space-y-1.5">
              {Object.entries(verdict.path_stances).map(([path, stance], i) => {
                const isPositive =
                  stance.includes('RECOMMENDED') || stance.includes('OPTIMAL') || stance.includes('ACCEPTABLE');
                const isCritical =
                  stance.includes('CRITICAL') || stance.includes('UNACCEPTABLE') || stance.includes('HIGH RISK');

                return (
                  <div
                    key={i}
                    className="p-2.5 bg-[var(--bb-bg-raised)] border border-[var(--bb-border-subtle)] rounded flex flex-col gap-1"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-[11px] text-[var(--bb-text-bright)]">
                        {path}
                      </span>
                      <span
                        className={`text-[9px] px-1.5 py-0.5 rounded font-bold uppercase ${
                          isPositive
                            ? 'bg-[var(--bb-green-dim)] text-[var(--bb-green)] border border-[var(--bb-green)]'
                            : isCritical
                            ? 'bg-[var(--bb-red-dim)] text-[var(--bb-red)] border border-[var(--bb-red)]'
                            : 'bg-[var(--bb-amber-dim)] text-[var(--bb-amber)] border border-[var(--bb-amber)]'
                        }`}
                      >
                        {stance.split('—')[0]?.trim() || 'ASSESSED'}
                      </span>
                    </div>
                    <span className="text-[10px] text-[var(--bb-text-secondary)] leading-relaxed">
                      {stance.includes('—') ? stance.split('—')[1]?.trim() : stance}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Actionable Directives */}
        {verdict.key_recommendations && verdict.key_recommendations.length > 0 && (
          <div>
            <span className="text-[10px] text-[var(--bb-text-muted)] uppercase tracking-wider block mb-2 flex items-center gap-1">
              <Lightbulb className="w-3 h-3 text-[var(--bb-amber)]" />
              ACTIONABLE IMPLEMENTATION DIRECTIVES:
            </span>
            <div className="space-y-1.5">
              {verdict.key_recommendations.map((rec, i) => (
                <div
                  key={i}
                  className="flex items-start gap-2 p-2 bg-[var(--bb-bg-base)] border border-[var(--bb-border-subtle)] rounded text-xs text-[var(--bb-text-secondary)]"
                >
                  <ArrowRight className="w-3 h-3 text-[var(--bb-amber)] mt-0.5 flex-shrink-0" />
                  <span className="leading-relaxed">{rec}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Caveats */}
        {caveats.length > 0 && (
          <div className="p-3 bg-[var(--bb-amber-dim)] border border-[var(--bb-amber)] rounded">
            <div className="flex items-center gap-1.5 text-[10px] font-bold text-[var(--bb-amber)] uppercase tracking-wider mb-1.5">
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>STRATEGIC CAVEATS & REGULATORY BOUNDARIES:</span>
            </div>
            <ul className="space-y-1">
              {caveats.map((c, i) => (
                <li key={i} className="text-[11px] text-[var(--bb-text-primary)] leading-normal">
                  • {c}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};
