import React, { useState } from 'react';
import {
  Award,
  AlertTriangle,
  Lightbulb,
  ArrowRight,
  ShieldCheck,
  Zap,
  Copy,
  Check,
  Sparkles,
} from 'lucide-react';
import type { OrchestratorVerdict } from '../api';
import { useToast } from './TerminalToast';
import { terminalAudio } from '../utils/terminalAudio';

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
  const { showToast } = useToast();
  const [viewMode, setViewMode] = useState<'technical' | 'plain'>('technical');
  const [copied, setCopied] = useState(false);

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

  const handleCopy = () => {
    terminalAudio.playBlip();
    const text = `HELIOS VERDICT // ${verdict.entity}\nRECOMMENDED PATH: ${verdict.recommended_path}\n\nSUMMARY:\n${verdict.verdict_summary}\n\nKEY DIRECTIVES:\n${verdict.key_recommendations.map((r, i) => `[${i + 1}] ${r}`).join('\n')}`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    showToast('success', 'VERDICT COPIED', 'Summary & directives copied to clipboard');
    setTimeout(() => setCopied(false), 2000);
  };

  // Generate a plain english explanation based on recommendation
  const getPlainEnglishSummary = () => {
    const path = verdict.recommended_path.toLowerCase();
    if (path.includes('self-hosted') || path.includes('open weights') || path.includes('build')) {
      return {
        bottomLine: 'Build and run this model inside your own infrastructure.',
        why: 'While setting up in-house compute takes more effort initially, it completely protects you from unexpected price hikes, vendor policy lock-in, and regulatory blackouts.',
        riskTier: 'LOW DEPENDENCY RISK (HIGH SOVEREIGN CONTROL)',
        riskLevel: 'LOW',
      };
    } else if (path.includes('cloud') || path.includes('licensed') || path.includes('buy')) {
      return {
        bottomLine: 'License private sovereign cloud infrastructure from an approved provider.',
        why: 'This provides fast time-to-market while keeping service-level agreements guaranteed, with moderate exposure to vendor pricing shifts over 5 years.',
        riskTier: 'MODERATE DEPENDENCY RISK (BALANCED TCO)',
        riskLevel: 'MODERATE',
      };
    } else {
      return {
        bottomLine: 'Proceed with caution when outsourcing full AI pipelines.',
        why: 'Outsourcing delivers fast upfront deployment, but creates steep long-term switching costs and high data gravity dependencies.',
        riskTier: 'HIGH DEPENDENCY HAZARD (STEEP SWITCHING COSTS)',
        riskLevel: 'HIGH',
      };
    }
  };

  const plainInfo = getPlainEnglishSummary();

  return (
    <div className="flex flex-col h-full bg-[var(--bb-bg-surface)] text-[var(--bb-text-primary)]">
      {/* Panel Header */}
      <div className="bb-panel-header">
        <div className="flex items-center gap-2">
          <Award className="w-3.5 h-3.5 text-[var(--bb-green)]" />
          <span>INSTITUTIONAL SOURCING VERDICT</span>
          <span className="text-[10px] text-[var(--bb-text-muted)]">[ORCHESTRATOR]</span>
        </div>

        <div className="flex items-center gap-2">
          {/* View Mode Toggle: Plain English vs Technical */}
          <div className="flex items-center gap-1 bg-[var(--bb-bg-base)] p-0.5 rounded border border-[var(--bb-border-subtle)]">
            <button
              type="button"
              onClick={() => {
                terminalAudio.playBlip();
                setViewMode('technical');
              }}
              className={`px-2 py-0.5 text-[9px] font-bold rounded ${
                viewMode === 'technical'
                  ? 'bg-[var(--bb-green)] text-black'
                  : 'text-[var(--bb-text-muted)] hover:text-[var(--bb-text-primary)]'
              }`}
            >
              TECHNICAL
            </button>
            <button
              type="button"
              onClick={() => {
                terminalAudio.playBlip();
                setViewMode('plain');
              }}
              className={`px-2 py-0.5 text-[9px] font-bold rounded ${
                viewMode === 'plain'
                  ? 'bg-[var(--bb-amber)] text-black'
                  : 'text-[var(--bb-text-muted)] hover:text-[var(--bb-text-primary)]'
              }`}
            >
              PLAIN ENGLISH
            </button>
          </div>

          <button
            type="button"
            onClick={handleCopy}
            className="p-1 text-[var(--bb-text-muted)] hover:text-[var(--bb-text-bright)] transition-colors"
            title="Copy Verdict Summary"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-[var(--bb-green)]" /> : <Copy className="w-3.5 h-3.5 text-[var(--bb-text-secondary)]" />}
          </button>

          <span
            className={`bb-badge ${
              verificationPassed ? 'bb-badge-green' : 'bb-badge-amber'
            } flex items-center gap-1`}
          >
            <ShieldCheck className="w-3 h-3" />
            {verificationPassed ? 'VERIFIED' : 'PARTIAL'}
          </span>
        </div>
      </div>

      <div className="p-4 space-y-4 overflow-y-auto bb-scroll flex-1 text-xs font-mono">
        {/* Recommended Path Banner */}
        <div className="p-3 bg-[var(--bb-green-dim)] border border-[var(--bb-green)] rounded shadow-sm">
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

        {/* PLAIN ENGLISH MODE VIEW */}
        {viewMode === 'plain' ? (
          <div className="space-y-3 bg-[var(--bb-bg-raised)] p-3.5 rounded border border-[var(--bb-amber)] shadow-md">
            <div className="flex items-center justify-between border-b border-[var(--bb-border-subtle)] pb-2">
              <span className="text-[11px] font-bold text-[var(--bb-amber)] flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5" /> EXECUTIVE SUMMARY (FOR LEADERSHIP)
              </span>
              <span
                className={`text-[9px] px-1.5 py-0.5 rounded font-bold ${
                  plainInfo.riskLevel === 'LOW'
                    ? 'bg-[var(--bb-green-dim)] text-[var(--bb-green)] border border-[var(--bb-green)]'
                    : plainInfo.riskLevel === 'MODERATE'
                    ? 'bg-[var(--bb-amber-dim)] text-[var(--bb-amber)] border border-[var(--bb-amber)]'
                    : 'bg-[var(--bb-red-dim)] text-[var(--bb-red)] border border-[var(--bb-red)]'
                }`}
              >
                {plainInfo.riskTier}
              </span>
            </div>

            <div className="space-y-1">
              <span className="text-[10px] text-[var(--bb-text-muted)] uppercase block">
                THE BOTTOM LINE:
              </span>
              <p className="text-xs font-bold text-[var(--bb-text-bright)] leading-relaxed">
                {plainInfo.bottomLine}
              </p>
            </div>

            <div className="space-y-1">
              <span className="text-[10px] text-[var(--bb-text-muted)] uppercase block">
                WHY HELIOS RECOMMENDS THIS:
              </span>
              <p className="text-[11px] text-[var(--bb-text-secondary)] leading-relaxed">
                {plainInfo.why}
              </p>
            </div>
          </div>
        ) : (
          /* TECHNICAL SYNTHESIS NARRATIVE */
          <div>
            <span className="text-[10px] text-[var(--bb-text-muted)] uppercase tracking-wider block mb-1">
              EXECUTIVE RATIONALE & SYNTHESIS:
            </span>
            <p className="text-xs leading-relaxed text-[var(--bb-text-primary)] bg-[var(--bb-bg-raised)] p-3 rounded border border-[var(--bb-border-subtle)]">
              {verdict.verdict_summary}
            </p>
          </div>
        )}

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
