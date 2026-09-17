import React, { useState } from 'react';
import {
  Send,
  Plus,
  X,
  Sparkles,
  SlidersHorizontal,
  Shield,
  Clock,
  Check,
  Loader2,
} from 'lucide-react';
import type { DecisionRequest } from '../api';
import { PRESET_SCENARIOS, type PresetScenario } from '../data/presetScenarios';
import { terminalAudio } from '../utils/terminalAudio';

interface BloombergDecisionConsoleProps {
  onSubmit: (brief: DecisionRequest) => void;
  onSelectPreset: (preset: PresetScenario) => void;
  isSubmitting: boolean;
  selectedPresetId?: string;
}

export const BloombergDecisionConsole: React.FC<BloombergDecisionConsoleProps> = ({
  onSubmit,
  onSelectPreset,
  isSubmitting,
  selectedPresetId,
}) => {
  const [entity, setEntity] = useState('Indian Army Signals Directorate');
  const [capability, setCapability] = useState('Tactical Small Language Model for Edge Comms & SIGINT');
  const [options, setOptions] = useState<string[]>([
    'Self-hosted Fine-tuned Open Weights (Llama 3.3 / Sarvam)',
    'Licensed Closed-Weights via Sovereign Cloud',
    'Outsourced Defense System Integrator Turnkey SLM',
  ]);
  const [newOption, setNewOption] = useState('');
  const [sovereigntyWeight, setSovereigntyWeight] = useState<'CRITICAL' | 'STANDARD' | 'LOW'>('CRITICAL');
  const [latencyTolerance, setLatencyTolerance] = useState<'SUB_20MS' | 'BALANCED' | 'BATCH'>('SUB_20MS');

  const handleAddOption = () => {
    const trimmed = newOption.trim();
    if (trimmed && !options.includes(trimmed)) {
      setOptions((prev) => [...prev, trimmed]);
      setNewOption('');
      terminalAudio.playBlip();
    }
  };

  const handleRemoveOption = (idx: number) => {
    setOptions((prev) => prev.filter((_, i) => i !== idx));
    terminalAudio.playBlip();
  };

  const handlePresetClick = (preset: PresetScenario) => {
    terminalAudio.playBlip();
    setEntity(preset.brief.entity);
    setCapability(preset.brief.capability);
    setOptions(preset.brief.options);
    onSelectPreset(preset);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!entity.trim() || !capability.trim() || isSubmitting) return;
    terminalAudio.playGoCommand();
    onSubmit({
      entity: entity.trim(),
      capability: capability.trim(),
      options: options.length > 0 ? options : [],
    });
  };

  return (
    <div className="flex flex-col h-full bg-[var(--bb-bg-surface)] text-[var(--bb-text-primary)]">
      {/* Panel Header */}
      <div className="bb-panel-header">
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="w-3.5 h-3.5 text-[var(--bb-amber)]" />
          <span>DECISION EXECUTION CONSOLE</span>
          <span className="text-[10px] text-[var(--bb-text-muted)]">[FUNCTION 01]</span>
        </div>
        <span className="bb-badge bb-badge-amber">SYNTHESIS_ENGINE</span>
      </div>

      <div className="p-4 space-y-4 overflow-y-auto bb-scroll flex-1 text-xs font-mono">
        {/* Institutional Presets Selector */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] text-[var(--bb-text-muted)] uppercase tracking-wider flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-[var(--bb-cyan)]" />
              INSTITUTIONAL PRESETS (FAST LOAD):
            </span>
            <span className="text-[10px] text-[var(--bb-text-dim)]">SELECT TO LOAD</span>
          </div>

          <div className="grid grid-cols-3 gap-2">
            {PRESET_SCENARIOS.map((preset) => {
              const isSelected = selectedPresetId === preset.id;
              return (
                <button
                  key={preset.id}
                  type="button"
                  onClick={() => handlePresetClick(preset)}
                  className={`p-2 rounded text-left border transition-all flex flex-col justify-between ${
                    isSelected
                      ? 'bg-[var(--bb-amber-dim)] border-[var(--bb-amber)] text-[var(--bb-text-bright)] shadow-md'
                      : 'bg-[var(--bb-bg-raised)] border-[var(--bb-border-subtle)] text-[var(--bb-text-secondary)] hover:border-[var(--bb-border-mid)] hover:text-[var(--bb-text-primary)]'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold text-[10px] text-[var(--bb-amber)]">
                      {preset.code}
                    </span>
                    {isSelected && <Check className="w-3 h-3 text-[var(--bb-amber)]" />}
                  </div>
                  <span className="text-[11px] font-medium line-clamp-1 leading-tight text-[var(--bb-text-primary)]">
                    {preset.title.split('//')[1] || preset.title}
                  </span>
                  <span className="text-[9px] text-[var(--bb-text-dim)] mt-1 uppercase">
                    {preset.category}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="space-y-3">
          {/* Target Entity */}
          <div>
            <label className="block text-[10px] text-[var(--bb-text-muted)] uppercase tracking-wider mb-1">
              01 // TARGET ENTITY / INSTITUTION
            </label>
            <input
              type="text"
              value={entity}
              onChange={(e) => setEntity(e.target.value)}
              disabled={isSubmitting}
              placeholder="e.g. Ministry of Defense, Tier-1 Bank, Autonomous Logistics Group"
              className="w-full bg-[var(--bb-bg-input)] border border-[var(--bb-border-mid)] focus:border-[var(--bb-amber)] text-[var(--bb-text-bright)] px-3 py-2 text-xs font-mono rounded outline-none"
            />
          </div>

          {/* AI Capability Required */}
          <div>
            <label className="block text-[10px] text-[var(--bb-text-muted)] uppercase tracking-wider mb-1">
              02 // AI CAPABILITY / TECHNICAL BRIEF
            </label>
            <input
              type="text"
              value={capability}
              onChange={(e) => setCapability(e.target.value)}
              disabled={isSubmitting}
              placeholder="e.g. Edge SLM for tactical SIGINT, Financial RAG for algorithmic advisory"
              className="w-full bg-[var(--bb-bg-input)] border border-[var(--bb-border-mid)] focus:border-[var(--bb-amber)] text-[var(--bb-text-bright)] px-3 py-2 text-xs font-mono rounded outline-none"
            />
          </div>

          {/* Sourcing Candidate Options */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-[10px] text-[var(--bb-text-muted)] uppercase tracking-wider">
                03 // SOURCING CANDIDATE PATHS ({options.length})
              </label>
              <span className="text-[9px] text-[var(--bb-text-dim)]">AUTO-INFERRED IF EMPTY</span>
            </div>

            {/* Chips */}
            <div className="space-y-1.5 mb-2">
              {options.map((opt, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between px-2.5 py-1.5 bg-[var(--bb-bg-raised)] border border-[var(--bb-border-subtle)] rounded text-xs text-[var(--bb-text-primary)]"
                >
                  <span className="truncate pr-2">
                    <span className="text-[var(--bb-amber)] font-bold mr-1.5">[{i + 1}]</span>
                    {opt}
                  </span>
                  <button
                    type="button"
                    onClick={() => handleRemoveOption(i)}
                    disabled={isSubmitting}
                    className="text-[var(--bb-text-dim)] hover:text-[var(--bb-red)] transition-colors"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>

            {/* Add Option Input */}
            <div className="flex gap-2">
              <input
                type="text"
                value={newOption}
                onChange={(e) => setNewOption(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddOption();
                  }
                }}
                disabled={isSubmitting}
                placeholder="Add custom candidate path..."
                className="flex-1 bg-[var(--bb-bg-input)] border border-[var(--bb-border-mid)] focus:border-[var(--bb-amber)] text-[var(--bb-text-bright)] px-3 py-1.5 text-xs font-mono rounded outline-none"
              />
              <button
                type="button"
                onClick={handleAddOption}
                disabled={isSubmitting || !newOption.trim()}
                className="bb-button bb-button-ghost px-3 py-1.5 text-[11px]"
              >
                <Plus className="w-3 h-3" /> ADD
              </button>
            </div>
          </div>

          {/* Strategic Constraints Matrix */}
          <div className="pt-2 border-t border-[var(--bb-border-subtle)]">
            <span className="text-[10px] text-[var(--bb-text-muted)] uppercase tracking-wider block mb-2">
              04 // STRATEGIC CONSTRAINTS & RISK WEIGHTS
            </span>
            <div className="grid grid-cols-2 gap-2">
              {/* Sovereignty Priority */}
              <div className="bg-[var(--bb-bg-raised)] p-2 rounded border border-[var(--bb-border-subtle)]">
                <div className="flex items-center gap-1.5 mb-1.5 text-[10px] text-[var(--bb-text-secondary)]">
                  <Shield className="w-3 h-3 text-[var(--bb-amber)]" />
                  <span>DATA SOVEREIGNTY:</span>
                </div>
                <div className="flex gap-1">
                  {(['CRITICAL', 'STANDARD', 'LOW'] as const).map((lvl) => (
                    <button
                      key={lvl}
                      type="button"
                      onClick={() => {
                        terminalAudio.playBlip();
                        setSovereigntyWeight(lvl);
                      }}
                      className={`flex-1 py-1 text-[9px] font-bold rounded border ${
                        sovereigntyWeight === lvl
                          ? 'bg-[var(--bb-amber)] text-black border-[var(--bb-amber)]'
                          : 'bg-[var(--bb-bg-surface)] text-[var(--bb-text-muted)] border-[var(--bb-border-subtle)]'
                      }`}
                    >
                      {lvl}
                    </button>
                  ))}
                </div>
              </div>

              {/* Latency / SLA */}
              <div className="bg-[var(--bb-bg-raised)] p-2 rounded border border-[var(--bb-border-subtle)]">
                <div className="flex items-center gap-1.5 mb-1.5 text-[10px] text-[var(--bb-text-secondary)]">
                  <Clock className="w-3 h-3 text-[var(--bb-cyan)]" />
                  <span>LATENCY / SLA:</span>
                </div>
                <div className="flex gap-1">
                  {(['SUB_20MS', 'BALANCED', 'BATCH'] as const).map((lat) => (
                    <button
                      key={lat}
                      type="button"
                      onClick={() => {
                        terminalAudio.playBlip();
                        setLatencyTolerance(lat);
                      }}
                      className={`flex-1 py-1 text-[9px] font-bold rounded border ${
                        latencyTolerance === lat
                          ? 'bg-[var(--bb-cyan)] text-black border-[var(--bb-cyan)]'
                          : 'bg-[var(--bb-bg-surface)] text-[var(--bb-text-muted)] border-[var(--bb-border-subtle)]'
                      }`}
                    >
                      {lat.replace('_', ' ')}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Submit Action Button */}
          <button
            type="submit"
            disabled={!entity.trim() || !capability.trim() || isSubmitting}
            className="w-full bb-button bb-button-go py-3 text-xs justify-center font-bold tracking-wider mt-2 shadow-lg"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>RUNNING 6-AGENT VERIFICATION PIPELINE...</span>
              </>
            ) : (
              <>
                <Send className="w-3.5 h-3.5" />
                <span>EXECUTE SOURCING VERDICT &lt;GO&gt;</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};
