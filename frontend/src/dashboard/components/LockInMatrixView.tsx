import React from 'react';
import {
  Lock,
} from 'lucide-react';

interface LockInVector {
  dimension: string;
  buildScore: number;
  buyScore: number;
  outsourceScore: number;
  criticalNotes: string;
}

interface LockInMatrixViewProps {
  vectors?: LockInVector[];
}

const DEFAULT_VECTORS: LockInVector[] = [
  {
    dimension: 'Data Sovereignty & Air-Gap Compliance',
    buildScore: 1.2,
    buyScore: 7.8,
    outsourceScore: 8.9,
    criticalNotes: 'Cloud API endpoints cannot operate in Level-5 Air-Gapped military or banking perimeters.',
  },
  {
    dimension: 'Model Weights Portability & Customization',
    buildScore: 1.5,
    buyScore: 8.4,
    outsourceScore: 9.2,
    criticalNotes: 'Proprietary runtime bindings prevent migration to sovereign NPU hardware.',
  },
  {
    dimension: 'Export Control & BIS Sanctions Exposure',
    buildScore: 2.0,
    buyScore: 8.9,
    outsourceScore: 6.5,
    criticalNotes: 'Foreign vendor license revocations create sudden operational blackout risk.',
  },
  {
    dimension: 'Long-term Inference TCO & Scalability',
    buildScore: 3.4,
    buyScore: 7.5,
    outsourceScore: 8.8,
    criticalNotes: 'Self-hosted quantized open-weight models achieve predictable fixed-cost amortizations.',
  },
  {
    dimension: 'Talent & Internal Engineering Ownership',
    buildScore: 6.2,
    buyScore: 3.1,
    outsourceScore: 2.0,
    criticalNotes: 'Self-hosting requires maintaining specialized in-house MLSecOps and systems cadres.',
  },
];

export const LockInMatrixView: React.FC<LockInMatrixViewProps> = ({
  vectors = DEFAULT_VECTORS,
}) => {
  const getScoreColor = (score: number) => {
    if (score <= 3.5) return 'text-[var(--bb-green)] bg-[var(--bb-green-dim)] border-[var(--bb-green)]';
    if (score <= 6.5) return 'text-[var(--bb-amber)] bg-[var(--bb-amber-dim)] border-[var(--bb-amber)]';
    return 'text-[var(--bb-red)] bg-[var(--bb-red-dim)] border-[var(--bb-red)]';
  };

  const getBarWidth = (score: number) => `${Math.min(100, Math.max(10, score * 10))}%`;

  return (
    <div className="flex flex-col h-full bg-[var(--bb-bg-surface)] text-[var(--bb-text-primary)]">
      {/* Panel Header */}
      <div className="bb-panel-header">
        <div className="flex items-center gap-2">
          <Lock className="w-3.5 h-3.5 text-[var(--bb-red)]" />
          <span>LOCK-IN MULTI-VECTOR MATRIX & SEVERITY HEATMAP</span>
          <span className="text-[10px] text-[var(--bb-text-muted)]">[FUNCTION 04]</span>
        </div>
        <span className="bb-badge bb-badge-red">5-DIMENSIONAL RISK EVAL</span>
      </div>

      <div className="p-4 space-y-4 overflow-y-auto bb-scroll flex-1 text-xs font-mono">
        <div className="flex items-center justify-between text-[11px] text-[var(--bb-text-secondary)]">
          <p>
            Comparative lock-in diagnosis across critical operational dimensions (Lower score = Lower risk / Greater autonomy).
          </p>
        </div>

        {/* Heatmap Table */}
        <div className="border border-[var(--bb-border-subtle)] rounded overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-[var(--bb-bg-raised)] border-b border-[var(--bb-border-subtle)] text-[10px] text-[var(--bb-text-muted)]">
                <th className="p-3 uppercase">RISK DIMENSION</th>
                <th className="p-3 uppercase text-center w-36">BUILD (IN-HOUSE)</th>
                <th className="p-3 uppercase text-center w-36">BUY (CLOUD API)</th>
                <th className="p-3 uppercase text-center w-36">OUTSOURCE (SAAS)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--bb-border-subtle)] bg-[var(--bb-bg-surface)]">
              {vectors.map((vec, idx) => (
                <tr key={idx} className="hover:bg-[var(--bb-bg-raised)] transition-colors">
                  <td className="p-3">
                    <span className="font-bold text-[11px] text-[var(--bb-text-bright)] block mb-1">
                      {vec.dimension}
                    </span>
                    <span className="text-[10px] text-[var(--bb-text-dim)] leading-normal block">
                      {vec.criticalNotes}
                    </span>
                  </td>

                  {/* Build Score */}
                  <td className="p-3 text-center">
                    <div className="flex flex-col items-center gap-1">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${getScoreColor(vec.buildScore)}`}>
                        {vec.buildScore.toFixed(1)} / 10
                      </span>
                      <div className="w-24 bg-[var(--bb-bg-base)] h-1.5 rounded overflow-hidden">
                        <div
                          className={`h-full ${vec.buildScore <= 3.5 ? 'bg-[var(--bb-green)]' : vec.buildScore <= 6.5 ? 'bg-[var(--bb-amber)]' : 'bg-[var(--bb-red)]'}`}
                          style={{ width: getBarWidth(vec.buildScore) }}
                        />
                      </div>
                    </div>
                  </td>

                  {/* Buy Score */}
                  <td className="p-3 text-center">
                    <div className="flex flex-col items-center gap-1">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${getScoreColor(vec.buyScore)}`}>
                        {vec.buyScore.toFixed(1)} / 10
                      </span>
                      <div className="w-24 bg-[var(--bb-bg-base)] h-1.5 rounded overflow-hidden">
                        <div
                          className={`h-full ${vec.buyScore <= 3.5 ? 'bg-[var(--bb-green)]' : vec.buyScore <= 6.5 ? 'bg-[var(--bb-amber)]' : 'bg-[var(--bb-red)]'}`}
                          style={{ width: getBarWidth(vec.buyScore) }}
                        />
                      </div>
                    </div>
                  </td>

                  {/* Outsource Score */}
                  <td className="p-3 text-center">
                    <div className="flex flex-col items-center gap-1">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${getScoreColor(vec.outsourceScore)}`}>
                        {vec.outsourceScore.toFixed(1)} / 10
                      </span>
                      <div className="w-24 bg-[var(--bb-bg-base)] h-1.5 rounded overflow-hidden">
                        <div
                          className={`h-full ${vec.outsourceScore <= 3.5 ? 'bg-[var(--bb-green)]' : vec.outsourceScore <= 6.5 ? 'bg-[var(--bb-amber)]' : 'bg-[var(--bb-red)]'}`}
                          style={{ width: getBarWidth(vec.outsourceScore) }}
                        />
                      </div>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
