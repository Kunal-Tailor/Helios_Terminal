import React from 'react';
import {
  FileText,
  Printer,
  Download,
  Copy,
  Check,
  X,
} from 'lucide-react';
import type { DecisionResponse } from '../api';
import { terminalAudio } from '../utils/terminalAudio';

interface ExecutiveDossierModalProps {
  result: DecisionResponse | null;
  onClose: () => void;
}

export const ExecutiveDossierModal: React.FC<ExecutiveDossierModalProps> = ({
  result,
  onClose,
}) => {
  const [copied, setCopied] = React.useState(false);

  if (!result || !result.verdict) {
    return (
      <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4">
        <div className="bg-[var(--bb-bg-surface)] border border-[var(--bb-border-bright)] p-6 rounded max-w-md w-full text-center font-mono text-xs">
          <p className="text-[var(--bb-text-secondary)] mb-4">
            No completed decision dossier is currently available. Please execute a decision brief first.
          </p>
          <button
            onClick={onClose}
            className="bb-button bb-button-ghost px-4 py-2"
          >
            CLOSE
          </button>
        </div>
      </div>
    );
  }

  const handleCopyJson = () => {
    terminalAudio.playBlip();
    navigator.clipboard.writeText(JSON.stringify(result, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handlePrint = () => {
    terminalAudio.playBlip();
    window.print();
  };

  const handleDownloadCsv = () => {
    terminalAudio.playBlip();
    if (!result.verdict?.cross_path_comparison) return;
    const paths = result.verdict.cross_path_comparison.path_comparisons;
    const csvContent = [
      'Scenario,LockInCount,MaxSeverityScore,Summary',
      ...paths.map(
        (p) => `"${p.scenario_name}",${p.lock_in_count},${p.max_severity_score},"${p.path_summary.replace(/"/g, '""')}"`
      ),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `helios_decision_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/85 flex items-center justify-center p-4 backdrop-blur-sm">
      <div className="bg-[var(--bb-bg-surface)] border border-[var(--bb-border-bright)] rounded max-w-4xl w-full max-h-[90vh] flex flex-col font-mono shadow-2xl overflow-hidden">
        {/* Modal Header Bar */}
        <div className="bb-panel-header">
          <div className="flex items-center gap-2">
            <FileText className="w-3.5 h-3.5 text-[var(--bb-amber)]" />
            <span>INSTITUTIONAL DECISION BRIEFING DOSSIER // EXECUTIVE SUMMARY</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleCopyJson}
              className="bb-button bb-button-ghost px-2.5 py-1 text-[10px]"
              title="Copy Raw Decision JSON"
            >
              {copied ? <Check className="w-3 h-3 text-[var(--bb-green)]" /> : <Copy className="w-3 h-3" />}
              <span>{copied ? 'COPIED JSON' : 'COPY JSON'}</span>
            </button>

            <button
              type="button"
              onClick={handleDownloadCsv}
              className="bb-button bb-button-ghost px-2.5 py-1 text-[10px]"
              title="Export CSV Table"
            >
              <Download className="w-3 h-3" />
              <span>EXPORT CSV</span>
            </button>

            <button
              type="button"
              onClick={handlePrint}
              className="bb-button bb-button-go px-2.5 py-1 text-[10px]"
              title="Print Official Dossier"
            >
              <Printer className="w-3 h-3" />
              <span>PRINT DOSSIER</span>
            </button>

            <button
              type="button"
              onClick={onClose}
              className="text-[var(--bb-text-muted)] hover:text-[var(--bb-text-bright)] p-1 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Printable Memo Body */}
        <div className="p-6 space-y-5 overflow-y-auto bb-scroll text-xs text-[var(--bb-text-primary)]">
          {/* Institutional Memo Header */}
          <div className="border-b border-[var(--bb-border-subtle)] pb-4">
            <div className="flex items-center justify-between text-[10px] text-[var(--bb-text-muted)] uppercase mb-2">
              <span>DOCUMENT REF: HELIOS-DOSSIER-{Date.now().toString().slice(-6)}</span>
              <span>CLASSIFICATION: STRATEGIC AUTONOMY LEVEL-1</span>
            </div>

            <h1 className="text-lg font-bold text-[var(--bb-text-bright)] mb-1">
              AI SOURCING STRATEGY & DEPENDENCY RISK DOSSIER
            </h1>
            <p className="text-xs text-[var(--bb-amber)] font-medium">
              ENTITY: {result.entity} // CAPABILITY: {result.capability}
            </p>
          </div>

          {/* Primary Recommended Stance */}
          <div className="p-4 bg-[var(--bb-green-dim)] border border-[var(--bb-green)] rounded">
            <span className="text-[10px] font-bold text-[var(--bb-green-bright)] uppercase tracking-wider block mb-1">
              RECOMMENDED SOURCING TRAJECTORY:
            </span>
            <p className="text-base font-bold text-[var(--bb-text-bright)]">
              {result.verdict.recommended_path}
            </p>
          </div>

          {/* Executive Synthesis */}
          <div>
            <span className="text-[10px] text-[var(--bb-text-muted)] uppercase tracking-wider block mb-1">
              EXECUTIVE SYNTHESIS:
            </span>
            <p className="text-xs leading-relaxed text-[var(--bb-text-primary)] bg-[var(--bb-bg-raised)] p-3 rounded border border-[var(--bb-border-subtle)]">
              {result.verdict.verdict_summary}
            </p>
          </div>

          {/* Comparative Paths Table */}
          {result.verdict.cross_path_comparison && (
            <div>
              <span className="text-[10px] text-[var(--bb-text-muted)] uppercase tracking-wider block mb-2">
                COMPARATIVE SOURCING MATRIX:
              </span>
              <div className="border border-[var(--bb-border-subtle)] rounded overflow-hidden">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-[var(--bb-bg-raised)] text-[10px] text-[var(--bb-text-muted)] border-b border-[var(--bb-border-subtle)]">
                      <th className="p-2.5">CANDIDATE PATH</th>
                      <th className="p-2.5 text-center">LOCK-IN VECTORS</th>
                      <th className="p-2.5 text-center">MAX SEVERITY</th>
                      <th className="p-2.5">KEY TRADEOFFS</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[var(--bb-border-subtle)]">
                    {result.verdict.cross_path_comparison.path_comparisons.map((p, idx) => (
                      <tr key={idx} className="bg-[var(--bb-bg-surface)]">
                        <td className="p-2.5 font-bold text-[var(--bb-text-bright)]">
                          {p.scenario_name}
                        </td>
                        <td className="p-2.5 text-center font-bold text-[var(--bb-amber)]">
                          {p.lock_in_count}
                        </td>
                        <td className="p-2.5 text-center">
                          <span
                            className={`px-1.5 py-0.5 rounded font-bold text-[9px] ${
                              p.max_severity_score <= 3.5
                                ? 'bg-[var(--bb-green-dim)] text-[var(--bb-green)]'
                                : 'bg-[var(--bb-red-dim)] text-[var(--bb-red)]'
                            }`}
                          >
                            {p.max_severity_score.toFixed(1)} / 10
                          </span>
                        </td>
                        <td className="p-2.5 text-[10px] text-[var(--bb-text-secondary)]">
                          {p.key_tradeoffs.join(' · ')}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Strategic Action Directives */}
          {result.verdict.key_recommendations.length > 0 && (
            <div>
              <span className="text-[10px] text-[var(--bb-text-muted)] uppercase tracking-wider block mb-2">
                STRATEGIC ACTION DIRECTIVES:
              </span>
              <ul className="space-y-1.5 bg-[var(--bb-bg-raised)] p-3 rounded border border-[var(--bb-border-subtle)]">
                {result.verdict.key_recommendations.map((rec, rIdx) => (
                  <li key={rIdx} className="text-xs text-[var(--bb-text-secondary)] leading-relaxed">
                    [{rIdx + 1}] {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Footer Sign-off */}
          <div className="pt-4 border-t border-[var(--bb-border-subtle)] flex items-center justify-between text-[10px] text-[var(--bb-text-dim)]">
            <span>HELIOS MULTI-AGENT DECISION PLATFORM // 6-STAGE VERIFIED</span>
            <span>VERIFICATION STATUS: {result.verification_passed ? 'PASSED (100%)' : 'PARTIAL'}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
