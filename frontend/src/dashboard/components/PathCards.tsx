import React from 'react';
import { Lock, AlertTriangle, TrendingUp } from 'lucide-react';
import type { CrossPathComparison } from '../api';

interface PathCardsProps {
  comparison: CrossPathComparison;
}

/** Color for severity: 0–3 green, 4–6 yellow, 7–10 red */
function severityColor(score: number): string {
  if (score <= 3) return 'var(--dash-success)';
  if (score <= 6) return 'var(--dash-warning)';
  return 'var(--dash-danger)';
}

function severityLabel(score: number): string {
  if (score <= 3) return 'LOW';
  if (score <= 6) return 'MEDIUM';
  return 'HIGH';
}

export const PathCards: React.FC<PathCardsProps> = ({ comparison }) => {
  return (
    <div className="dash-animate-in">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <span
          className="inline-flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-mono uppercase tracking-widest rounded"
          style={{ background: 'var(--dash-surface-raised)', border: '1px solid var(--dash-border-strong)', color: 'var(--dash-accent)' }}
        >
          PATH_COMPARISON
        </span>
      </div>

      {/* Comparative narrative */}
      {comparison.comparative_narrative && (
        <p className="text-sm leading-relaxed mb-5" style={{ color: 'var(--dash-text-secondary)' }}>
          {comparison.comparative_narrative}
        </p>
      )}

      {/* Cards grid */}
      <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${Math.min(comparison.path_comparisons.length, 3)}, 1fr)` }}>
        {comparison.path_comparisons.map((path, i) => (
          <div
            key={i}
            className="rounded p-4 flex flex-col gap-4 transition-all duration-200 hover:-translate-y-0.5"
            style={{
              background: 'var(--dash-surface)',
              border: '1px solid var(--dash-border)',
            }}
          >
            {/* Path name */}
            <h4 className="font-mono font-semibold text-sm tracking-wide" style={{ color: 'var(--dash-text-primary)' }}>
              {path.scenario_name}
            </h4>

            {/* Metrics row */}
            <div className="flex items-center gap-4">
              {/* Lock-in count */}
              <div className="flex items-center gap-1.5">
                <Lock className="w-3.5 h-3.5" style={{ color: 'var(--dash-text-muted)' }} />
                <span className="text-xs font-mono" style={{ color: 'var(--dash-text-secondary)' }}>
                  {path.lock_in_count} lock-in{path.lock_in_count !== 1 ? 's' : ''}
                </span>
              </div>

              {/* Severity */}
              <div className="flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5" style={{ color: severityColor(path.max_severity_score) }} />
                <span className="text-xs font-mono" style={{ color: severityColor(path.max_severity_score) }}>
                  {severityLabel(path.max_severity_score)} ({path.max_severity_score.toFixed(1)})
                </span>
              </div>
            </div>

            {/* Path summary */}
            {path.path_summary && (
              <p className="text-xs leading-relaxed" style={{ color: 'var(--dash-text-secondary)' }}>
                {path.path_summary}
              </p>
            )}

            {/* Key tradeoffs */}
            {path.key_tradeoffs.length > 0 && (
              <div>
                <p className="text-[10px] font-mono uppercase tracking-wider mb-2" style={{ color: 'var(--dash-text-muted)' }}>
                  Tradeoffs
                </p>
                <ul className="space-y-1.5">
                  {path.key_tradeoffs.map((tradeoff, j) => (
                    <li key={j} className="flex items-start gap-1.5 text-xs" style={{ color: 'var(--dash-text-secondary)' }}>
                      <TrendingUp className="w-3 h-3 mt-0.5 flex-shrink-0" style={{ color: 'var(--dash-text-muted)' }} />
                      <span>{tradeoff}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
