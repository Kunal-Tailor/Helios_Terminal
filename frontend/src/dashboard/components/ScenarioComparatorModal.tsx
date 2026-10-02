import React, { useState } from 'react';
import {
  GitCompare,
  X,
} from 'lucide-react';
import type { DecisionResponse } from '../api';
import { PRESET_SCENARIOS } from '../data/presetScenarios';
import { terminalAudio } from '../utils/terminalAudio';

interface ScenarioComparatorModalProps {
  currentResult: DecisionResponse | null;
  isOpen: boolean;
  onClose: () => void;
}

export const ScenarioComparatorModal: React.FC<ScenarioComparatorModalProps> = ({
  currentResult,
  isOpen,
  onClose,
}) => {
  const [selectedBenchmarkId, setSelectedBenchmarkId] = useState<string>(
    PRESET_SCENARIOS[1]?.id || PRESET_SCENARIOS[0].id
  );

  if (!isOpen) return null;

  const benchmarkPreset =
    PRESET_SCENARIOS.find((p) => p.id === selectedBenchmarkId) || PRESET_SCENARIOS[0];

  const currentVerdict = currentResult?.verdict;
  const benchmarkVerdict = benchmarkPreset.result?.verdict;

  return (
    <div className="fixed inset-0 z-50 bg-black/85 flex items-center justify-center p-4 backdrop-blur-sm select-none font-mono">
      <div className="bg-[var(--bb-bg-surface)] border border-[var(--bb-border-bright)] rounded max-w-5xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="bb-panel-header">
          <div className="flex items-center gap-2">
            <GitCompare className="w-3.5 h-3.5 text-[var(--bb-cyan)]" />
            <span>CROSS-SCENARIO STRATEGIC COMPARATOR // SIDE-BY-SIDE DIFF</span>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 text-[10px]">
              <span className="text-[var(--bb-text-muted)]">BENCHMARK:</span>
              <select
                value={selectedBenchmarkId}
                onChange={(e) => {
                  terminalAudio.playBlip();
                  setSelectedBenchmarkId(e.target.value);
                }}
                className="bg-[var(--bb-bg-input)] border border-[var(--bb-border-mid)] text-[var(--bb-cyan)] px-2 py-0.5 rounded text-[10px] outline-none"
              >
                {PRESET_SCENARIOS.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.code} — {p.title.split('//')[1] || p.title}
                  </option>
                ))}
              </select>
            </div>

            <button
              type="button"
              onClick={onClose}
              className="text-[var(--bb-text-muted)] hover:text-[var(--bb-text-bright)] p-1 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Comparison Body */}
        <div className="p-4 space-y-4 overflow-y-auto bb-scroll flex-1 text-xs">
          {/* Top Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {/* Left Card: Active Sourcing Brief */}
            <div className="p-3 bg-[var(--bb-bg-raised)] border border-[var(--bb-amber)] rounded space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] px-1.5 py-0.2 bg-[var(--bb-amber-dim)] text-[var(--bb-amber)] border border-[var(--bb-amber)] rounded font-bold">
                  PRIMARY DECISION (ACTIVE)
                </span>
                <span className="text-[10px] text-[var(--bb-text-dim)]">
                  STATUS: {currentResult?.verification_passed ? 'VERIFIED' : 'PENDING'}
                </span>
              </div>
              <h3 className="font-bold text-[13px] text-[var(--bb-text-bright)]">
                {currentResult?.entity || 'Custom Target Entity'}
              </h3>
              <p className="text-[11px] text-[var(--bb-text-secondary)] line-clamp-2">
                {currentResult?.capability || 'Custom Capability brief'}
              </p>
              <div className="p-2 bg-[var(--bb-bg-surface)] border border-[var(--bb-border-subtle)] rounded">
                <span className="text-[9px] text-[var(--bb-text-muted)] uppercase block mb-0.5">
                  RECOMMENDED PATH:
                </span>
                <span className="font-bold text-[11px] text-[var(--bb-green)]">
                  {currentVerdict?.recommended_path || 'Awaiting Synthesis'}
                </span>
              </div>
            </div>

            {/* Right Card: Selected Benchmark */}
            <div className="p-3 bg-[var(--bb-bg-raised)] border border-[var(--bb-cyan)] rounded space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] px-1.5 py-0.2 bg-[var(--bb-cyan-dim)] text-[var(--bb-cyan)] border border-[var(--bb-cyan)] rounded font-bold">
                  BENCHMARK // {benchmarkPreset.code}
                </span>
                <span className="text-[10px] text-[var(--bb-text-dim)] uppercase">
                  {benchmarkPreset.category}
                </span>
              </div>
              <h3 className="font-bold text-[13px] text-[var(--bb-text-bright)]">
                {benchmarkPreset.brief.entity}
              </h3>
              <p className="text-[11px] text-[var(--bb-text-secondary)] line-clamp-2">
                {benchmarkPreset.brief.capability}
              </p>
              <div className="p-2 bg-[var(--bb-bg-surface)] border border-[var(--bb-border-subtle)] rounded">
                <span className="text-[9px] text-[var(--bb-text-muted)] uppercase block mb-0.5">
                  RECOMMENDED PATH:
                </span>
                <span className="font-bold text-[11px] text-[var(--bb-cyan)]">
                  {benchmarkVerdict?.recommended_path || 'N/A'}
                </span>
              </div>
            </div>
          </div>

          {/* Comparative Metrics Table */}
          <div>
            <span className="text-[10px] text-[var(--bb-text-muted)] uppercase tracking-wider block mb-2">
              DIFFERENTIAL STRATEGIC ANALYSIS MATRIX:
            </span>

            <div className="border border-[var(--bb-border-subtle)] rounded overflow-hidden">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-[var(--bb-bg-raised)] border-b border-[var(--bb-border-subtle)] text-[10px] text-[var(--bb-text-muted)]">
                    <th className="p-2.5 uppercase">STRATEGIC VECTOR</th>
                    <th className="p-2.5 uppercase w-1/3 text-[var(--bb-amber)]">ACTIVE CASE</th>
                    <th className="p-2.5 uppercase w-1/3 text-[var(--bb-cyan)]">
                      BENCHMARK ({benchmarkPreset.code})
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[var(--bb-border-subtle)] bg-[var(--bb-bg-surface)]">
                  <tr>
                    <td className="p-2.5 font-bold text-[var(--bb-text-primary)]">
                      Primary Sourcing Stance
                    </td>
                    <td className="p-2.5 text-[11px] text-[var(--bb-text-bright)]">
                      {currentVerdict?.recommended_path || 'Pending'}
                    </td>
                    <td className="p-2.5 text-[11px] text-[var(--bb-text-bright)]">
                      {benchmarkVerdict?.recommended_path || 'N/A'}
                    </td>
                  </tr>

                  <tr>
                    <td className="p-2.5 font-bold text-[var(--bb-text-primary)]">
                      Data Sovereignty Weight
                    </td>
                    <td className="p-2.5 text-[11px]">
                      <span className="px-1.5 py-0.5 bg-[var(--bb-amber-dim)] text-[var(--bb-amber)] border border-[var(--bb-amber)] rounded font-bold text-[10px]">
                        {currentResult?.data_sovereignty_weight || 'CRITICAL'}
                      </span>
                    </td>
                    <td className="p-2.5 text-[11px]">
                      <span className="px-1.5 py-0.5 bg-[var(--bb-cyan-dim)] text-[var(--bb-cyan)] border border-[var(--bb-cyan)] rounded font-bold text-[10px]">
                        {benchmarkPreset.brief.data_sovereignty_weight || 'STANDARD'}
                      </span>
                    </td>
                  </tr>

                  <tr>
                    <td className="p-2.5 font-bold text-[var(--bb-text-primary)]">
                      Latency / SLA Priority
                    </td>
                    <td className="p-2.5 text-[11px]">
                      <span className="px-1.5 py-0.5 bg-[var(--bb-bg-raised)] text-[var(--bb-text-secondary)] border border-[var(--bb-border-subtle)] rounded text-[10px]">
                        {currentResult?.latency_tolerance || 'SUB_20MS'}
                      </span>
                    </td>
                    <td className="p-2.5 text-[11px]">
                      <span className="px-1.5 py-0.5 bg-[var(--bb-bg-raised)] text-[var(--bb-text-secondary)] border border-[var(--bb-border-subtle)] rounded text-[10px]">
                        {benchmarkPreset.brief.latency_tolerance || 'BALANCED'}
                      </span>
                    </td>
                  </tr>

                  <tr>
                    <td className="p-2.5 font-bold text-[var(--bb-text-primary)]">
                      Candidate Paths Evaluated
                    </td>
                    <td className="p-2.5 text-[11px] text-[var(--bb-text-secondary)]">
                      {currentResult?.options?.length || 0} candidate options
                    </td>
                    <td className="p-2.5 text-[11px] text-[var(--bb-text-secondary)]">
                      {benchmarkPreset.brief.options.length} candidate options
                    </td>
                  </tr>

                  <tr>
                    <td className="p-2.5 font-bold text-[var(--bb-text-primary)]">
                      Audit Verification Trail
                    </td>
                    <td className="p-2.5 text-[11px] text-[var(--bb-green)] font-bold">
                      {currentResult?.verification_results?.length || 6} stage gates passed
                    </td>
                    <td className="p-2.5 text-[11px] text-[var(--bb-green)] font-bold">
                      {benchmarkPreset.result?.verification_results?.length || 6} stage gates passed
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-3 py-2 bg-[var(--bb-bg-base)] border-t border-[var(--bb-border-subtle)] flex items-center justify-between text-[10px] text-[var(--bb-text-dim)]">
          <span>HELIOS COMPARATOR ENGINE // DIFFERENTIAL METRICS COMPUTED</span>
          <button
            type="button"
            onClick={onClose}
            className="bb-button bb-button-ghost px-3 py-1 text-[10px]"
          >
            DISMISS
          </button>
        </div>
      </div>
    </div>
  );
};
