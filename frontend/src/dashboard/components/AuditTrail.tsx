import React, { useState } from 'react';
import { ChevronDown, ChevronRight, CheckCircle2, XCircle, RotateCcw, FileText } from 'lucide-react';
import type { VerificationResult, RecalibrationTrailItem, ExplanationTrail } from '../api';

interface AuditTrailProps {
  verificationResults: VerificationResult[];
  recalibrationTrail: RecalibrationTrailItem[];
  explanationTrail: ExplanationTrail | null;
  verificationPassed: boolean;
  verificationFailedStage: string | null;
}

const CollapsibleSection: React.FC<{
  title: string;
  count?: number;
  icon: React.ReactNode;
  children: React.ReactNode;
  defaultOpen?: boolean;
}> = ({ title, count, icon, children, defaultOpen = false }) => {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div
      className="rounded overflow-hidden"
      style={{ border: '1px solid var(--dash-border)' }}
    >
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-2 px-4 py-3 text-left transition-colors"
        style={{ background: open ? 'var(--dash-surface-raised)' : 'var(--dash-surface)', color: 'var(--dash-text-primary)' }}
      >
        {open ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
        {icon}
        <span className="text-xs font-mono uppercase tracking-wider flex-1">{title}</span>
        {count !== undefined && (
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded"
                style={{ background: 'var(--dash-bg)', color: 'var(--dash-text-muted)' }}>
            {count}
          </span>
        )}
      </button>
      {open && (
        <div className="px-4 py-3" style={{ background: 'var(--dash-bg)', borderTop: '1px solid var(--dash-border)' }}>
          {children}
        </div>
      )}
    </div>
  );
};

export const AuditTrail: React.FC<AuditTrailProps> = ({
  verificationResults,
  recalibrationTrail,
  explanationTrail,
  verificationPassed,
  verificationFailedStage,
}) => {
  const passedCount = verificationResults.filter((v) => v.passed).length;
  const failedCount = verificationResults.filter((v) => !v.passed).length;

  return (
    <div className="dash-animate-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span
            className="inline-flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-mono uppercase tracking-widest rounded"
            style={{ background: 'var(--dash-surface-raised)', border: '1px solid var(--dash-border-strong)', color: 'var(--dash-accent)' }}
          >
            AUDIT_TRAIL
          </span>
        </div>
        <span className="text-[11px] font-mono" style={{
          color: verificationPassed ? 'var(--dash-success)' : 'var(--dash-danger)',
        }}>
          {verificationPassed ? '● ALL CLAIMS VERIFIED' : `● FAILED AT ${verificationFailedStage?.toUpperCase()}`}
        </span>
      </div>

      <div className="space-y-3">
        {/* Verification Results */}
        <CollapsibleSection
          title="Verification Results"
          count={verificationResults.length}
          icon={<CheckCircle2 className="w-3.5 h-3.5" style={{ color: 'var(--dash-success)' }} />}
        >
          {verificationResults.length === 0 ? (
            <p className="text-xs" style={{ color: 'var(--dash-text-muted)' }}>No verification results recorded.</p>
          ) : (
            <>
              <p className="text-xs mb-3" style={{ color: 'var(--dash-text-muted)' }}>
                {passedCount} passed · {failedCount} failed
              </p>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {verificationResults.map((vr, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-2 px-3 py-2 rounded text-xs"
                    style={{ background: 'var(--dash-surface)', border: '1px solid var(--dash-border)' }}
                  >
                    {vr.passed ? (
                      <CheckCircle2 className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" style={{ color: 'var(--dash-success)' }} />
                    ) : (
                      <XCircle className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" style={{ color: 'var(--dash-danger)' }} />
                    )}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-mono uppercase" style={{ color: 'var(--dash-text-muted)' }}>
                          {vr.agent_stage}
                        </span>
                        <span className="font-mono" style={{ color: vr.passed ? 'var(--dash-success)' : 'var(--dash-danger)' }}>
                          {(vr.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                      <p style={{ color: 'var(--dash-text-secondary)' }} className="break-words">{vr.claim}</p>
                      <p className="mt-1" style={{ color: 'var(--dash-text-muted)' }}>{vr.reason}</p>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </CollapsibleSection>

        {/* Recalibration Trail */}
        <CollapsibleSection
          title="Recalibration Trail"
          count={recalibrationTrail.length}
          icon={<RotateCcw className="w-3.5 h-3.5" style={{ color: 'var(--dash-warning)' }} />}
        >
          {recalibrationTrail.length === 0 ? (
            <p className="text-xs" style={{ color: 'var(--dash-text-muted)' }}>
              Clean run — no recalibration loops were triggered.
            </p>
          ) : (
            <div className="space-y-2">
              {recalibrationTrail.map((item, i) => (
                <div
                  key={i}
                  className="px-3 py-2.5 rounded text-xs"
                  style={{ background: 'var(--dash-surface)', border: '1px solid var(--dash-border)' }}
                >
                  <div className="flex items-center gap-2 mb-1.5">
                    <span className="font-mono font-medium" style={{ color: 'var(--dash-warning)' }}>
                      {item.from_stage} → {item.to_stage}
                    </span>
                    <span className="font-mono" style={{ color: 'var(--dash-text-muted)' }}>
                      iter {item.iteration_count} · {item.reason}
                    </span>
                  </div>
                  <p style={{ color: 'var(--dash-text-secondary)' }}>{item.gap_description}</p>
                </div>
              ))}
            </div>
          )}
        </CollapsibleSection>

        {/* Explanation Trail */}
        {explanationTrail && (
          <CollapsibleSection
            title="Explanation Trail"
            count={explanationTrail.steps.length}
            icon={<FileText className="w-3.5 h-3.5" style={{ color: 'var(--dash-accent)' }} />}
          >
            {explanationTrail.summary && (
              <p className="text-xs mb-3" style={{ color: 'var(--dash-text-secondary)' }}>
                {explanationTrail.summary}
              </p>
            )}
            {explanationTrail.steps.length > 0 && (
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {explanationTrail.steps.map((step, i) => (
                  <div
                    key={i}
                    className="px-3 py-2 rounded text-xs"
                    style={{ background: 'var(--dash-surface)', border: '1px solid var(--dash-border)' }}
                  >
                    <span className="font-mono uppercase" style={{ color: 'var(--dash-text-muted)' }}>
                      {step.stage}
                    </span>
                    <p className="mt-1" style={{ color: 'var(--dash-text-primary)' }}>{step.claim}</p>
                    <p className="mt-1" style={{ color: 'var(--dash-text-muted)' }}>Evidence: {step.evidence}</p>
                  </div>
                ))}
              </div>
            )}
            {explanationTrail.sources.length > 0 && (
              <div className="mt-3">
                <p className="text-[10px] font-mono uppercase tracking-wider mb-1.5" style={{ color: 'var(--dash-text-muted)' }}>
                  Sources
                </p>
                <ul className="space-y-1">
                  {explanationTrail.sources.map((src, i) => (
                    <li key={i} className="text-xs break-all" style={{ color: 'var(--dash-text-secondary)' }}>
                      {src}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CollapsibleSection>
        )}
      </div>
    </div>
  );
};
