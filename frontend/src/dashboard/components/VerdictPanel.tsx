import React from 'react';
import { Award, Lightbulb, ArrowRight } from 'lucide-react';
import type { OrchestratorVerdict } from '../api';

interface VerdictPanelProps {
  verdict: OrchestratorVerdict;
  caveats: string[];
}

export const VerdictPanel: React.FC<VerdictPanelProps> = ({ verdict, caveats }) => {
  return (
    <div className="dash-animate-in">
      {/* Header */}
      <div className="flex items-center gap-2 mb-6">
        <span
          className="inline-flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-mono uppercase tracking-widest rounded"
          style={{ background: 'var(--dash-surface-raised)', border: '1px solid var(--dash-border-strong)', color: 'var(--dash-success)' }}
        >
          VERDICT_RENDERED
        </span>
      </div>

      {/* Recommended path */}
      {verdict.recommended_path && (
        <div
          className="px-5 py-4 rounded mb-5"
          style={{ background: 'rgba(63, 167, 179, 0.08)', border: '1px solid var(--dash-accent)' }}
        >
          <div className="flex items-center gap-2 mb-2">
            <Award className="w-4 h-4" style={{ color: 'var(--dash-accent)' }} />
            <span className="text-xs font-mono uppercase tracking-wider" style={{ color: 'var(--dash-accent)' }}>
              Recommended Path
            </span>
          </div>
          <p className="text-lg font-serif font-semibold" style={{ color: 'var(--dash-text-primary)' }}>
            {verdict.recommended_path}
          </p>
        </div>
      )}

      {/* Verdict summary */}
      {verdict.verdict_summary && (
        <div className="mb-5">
          <h3 className="text-xs font-mono uppercase tracking-wider mb-2" style={{ color: 'var(--dash-text-muted)' }}>
            Summary
          </h3>
          <p className="text-sm leading-relaxed" style={{ color: 'var(--dash-text-secondary)' }}>
            {verdict.verdict_summary}
          </p>
        </div>
      )}

      {/* Key recommendations */}
      {verdict.key_recommendations.length > 0 && (
        <div className="mb-5">
          <h3 className="text-xs font-mono uppercase tracking-wider mb-3 flex items-center gap-1.5"
              style={{ color: 'var(--dash-text-muted)' }}>
            <Lightbulb className="w-3.5 h-3.5" />
            Key Recommendations
          </h3>
          <ul className="space-y-2">
            {verdict.key_recommendations.map((rec, i) => (
              <li key={i} className="flex items-start gap-2 text-sm" style={{ color: 'var(--dash-text-secondary)' }}>
                <ArrowRight className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" style={{ color: 'var(--dash-accent)' }} />
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Path stances */}
      {Object.keys(verdict.path_stances).length > 0 && (
        <div className="mb-5">
          <h3 className="text-xs font-mono uppercase tracking-wider mb-3" style={{ color: 'var(--dash-text-muted)' }}>
            Path Stances
          </h3>
          <div className="space-y-2">
            {Object.entries(verdict.path_stances).map(([path, stance]) => (
              <div
                key={path}
                className="flex items-start gap-3 px-3 py-2.5 rounded text-sm"
                style={{ background: 'var(--dash-bg)', border: '1px solid var(--dash-border)' }}
              >
                <span className="font-mono font-medium flex-shrink-0" style={{ color: 'var(--dash-text-primary)' }}>
                  {path}
                </span>
                <span style={{ color: 'var(--dash-text-secondary)' }}>— {stance}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Caveats */}
      {caveats.length > 0 && (
        <div
          className="px-4 py-3 rounded text-sm"
          style={{ background: 'rgba(210, 153, 34, 0.1)', border: '1px solid var(--dash-warning)' }}
        >
          <p className="font-mono text-xs uppercase tracking-wider mb-2" style={{ color: 'var(--dash-warning)' }}>
            ⚠ Partial Verdict — Caveats
          </p>
          <ul className="space-y-1">
            {caveats.map((caveat, i) => (
              <li key={i} style={{ color: 'var(--dash-text-secondary)' }}>{caveat}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
