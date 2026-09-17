import React, { useState } from 'react';
import { Plus, X, Send, Loader2 } from 'lucide-react';
import type { DecisionRequest } from '../api';

interface DecisionFormProps {
  onSubmit: (brief: DecisionRequest) => void;
  isSubmitting: boolean;
}

export const DecisionForm: React.FC<DecisionFormProps> = ({ onSubmit, isSubmitting }) => {
  const [entity, setEntity] = useState('');
  const [capability, setCapability] = useState('');
  const [options, setOptions] = useState<string[]>([]);
  const [optionInput, setOptionInput] = useState('');

  const addOption = () => {
    const trimmed = optionInput.trim();
    if (trimmed && !options.includes(trimmed)) {
      setOptions((prev) => [...prev, trimmed]);
      setOptionInput('');
    }
  };

  const removeOption = (index: number) => {
    setOptions((prev) => prev.filter((_, i) => i !== index));
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addOption();
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!entity.trim() || !capability.trim()) return;
    onSubmit({
      entity: entity.trim(),
      capability: capability.trim(),
      options,
    });
  };

  const isValid = entity.trim().length > 0 && capability.trim().length > 0;

  return (
    <form onSubmit={handleSubmit} className="dash-animate-in">
      {/* Header */}
      <div className="flex items-center gap-2 mb-6">
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-mono uppercase tracking-widest"
              style={{ background: 'var(--dash-surface-raised)', border: '1px solid var(--dash-border-strong)', color: 'var(--dash-accent)', borderRadius: '4px' }}>
          DECISION_BRIEF
        </span>
      </div>

      {/* Entity */}
      <div className="mb-5">
        <label htmlFor="dash-entity" className="block text-xs font-mono uppercase tracking-wider mb-2"
               style={{ color: 'var(--dash-text-muted)' }}>
          Entity / Organisation
        </label>
        <input
          id="dash-entity"
          type="text"
          value={entity}
          onChange={(e) => setEntity(e.target.value)}
          placeholder="e.g. Indian Army signals division"
          disabled={isSubmitting}
          className="w-full px-3 py-2.5 text-sm font-sans rounded"
          style={{
            background: 'var(--dash-bg)',
            border: '1px solid var(--dash-border)',
            color: 'var(--dash-text-primary)',
            outline: 'none',
          }}
          onFocus={(e) => e.target.style.borderColor = 'var(--dash-accent)'}
          onBlur={(e) => e.target.style.borderColor = 'var(--dash-border)'}
        />
      </div>

      {/* Capability */}
      <div className="mb-5">
        <label htmlFor="dash-capability" className="block text-xs font-mono uppercase tracking-wider mb-2"
               style={{ color: 'var(--dash-text-muted)' }}>
          AI Capability Needed
        </label>
        <input
          id="dash-capability"
          type="text"
          value={capability}
          onChange={(e) => setCapability(e.target.value)}
          placeholder="e.g. small language model for edge inference"
          disabled={isSubmitting}
          className="w-full px-3 py-2.5 text-sm font-sans rounded"
          style={{
            background: 'var(--dash-bg)',
            border: '1px solid var(--dash-border)',
            color: 'var(--dash-text-primary)',
            outline: 'none',
          }}
          onFocus={(e) => e.target.style.borderColor = 'var(--dash-accent)'}
          onBlur={(e) => e.target.style.borderColor = 'var(--dash-border)'}
        />
      </div>

      {/* Options */}
      <div className="mb-6">
        <label htmlFor="dash-option-input" className="block text-xs font-mono uppercase tracking-wider mb-2"
               style={{ color: 'var(--dash-text-muted)' }}>
          Candidate Options <span className="normal-case tracking-normal text-[10px]">(optional — Helios can infer)</span>
        </label>

        {/* Option chips */}
        {options.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {options.map((opt, i) => (
              <span
                key={i}
                className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-mono rounded"
                style={{ background: 'var(--dash-surface-raised)', border: '1px solid var(--dash-border-strong)', color: 'var(--dash-text-primary)' }}
              >
                {opt}
                <button
                  type="button"
                  onClick={() => removeOption(i)}
                  disabled={isSubmitting}
                  className="hover:opacity-70 transition-opacity"
                  style={{ color: 'var(--dash-text-muted)' }}
                  aria-label={`Remove option: ${opt}`}
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
        )}

        {/* Add option input */}
        <div className="flex gap-2">
          <input
            id="dash-option-input"
            type="text"
            value={optionInput}
            onChange={(e) => setOptionInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="e.g. build in-house"
            disabled={isSubmitting}
            className="flex-1 px-3 py-2 text-sm font-sans rounded"
            style={{
              background: 'var(--dash-bg)',
              border: '1px solid var(--dash-border)',
              color: 'var(--dash-text-primary)',
              outline: 'none',
            }}
            onFocus={(e) => e.target.style.borderColor = 'var(--dash-accent)'}
            onBlur={(e) => e.target.style.borderColor = 'var(--dash-border)'}
          />
          <button
            type="button"
            onClick={addOption}
            disabled={isSubmitting || !optionInput.trim()}
            className="px-3 py-2 text-xs font-mono rounded transition-colors flex items-center gap-1.5"
            style={{
              background: 'var(--dash-surface-raised)',
              border: '1px solid var(--dash-border-strong)',
              color: optionInput.trim() ? 'var(--dash-accent)' : 'var(--dash-text-muted)',
              cursor: optionInput.trim() ? 'pointer' : 'default',
            }}
          >
            <Plus className="w-3.5 h-3.5" /> Add
          </button>
        </div>
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={!isValid || isSubmitting}
        className="w-full flex items-center justify-center gap-2 px-4 py-3 text-sm font-mono font-medium rounded transition-all duration-150"
        style={{
          background: isValid && !isSubmitting ? 'var(--dash-accent)' : 'var(--dash-surface-raised)',
          color: isValid && !isSubmitting ? '#fff' : 'var(--dash-text-muted)',
          border: '1px solid transparent',
          cursor: isValid && !isSubmitting ? 'pointer' : 'not-allowed',
          opacity: isSubmitting ? 0.7 : 1,
        }}
      >
        {isSubmitting ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            SUBMITTING...
          </>
        ) : (
          <>
            <Send className="w-4 h-4" />
            EXECUTE PIPELINE
          </>
        )}
      </button>
    </form>
  );
};
