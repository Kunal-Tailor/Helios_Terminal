import React, { useState } from 'react';
import {
  Sparkles,
  Shield,
  Building2,
  Cpu,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  X,
  Play,
} from 'lucide-react';
import type { DecisionRequest } from '../api';
import { terminalAudio } from '../utils/terminalAudio';

interface GuidedDecisionWizardModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLaunchBrief: (brief: DecisionRequest) => void;
}

const ORG_TEMPLATES = [
  {
    id: 'defense',
    name: 'Defense & National Security',
    icon: Shield,
    defaultEntity: 'Directorate of Defense Intelligence & Communications',
    tag: 'MAX SOVEREIGNTY',
    desc: 'Strict air-gap, zero foreign telemetry egress, Level-5 military perimeter.',
  },
  {
    id: 'fintech',
    name: 'Banking & Capital Markets',
    icon: Building2,
    defaultEntity: 'Global Institutional Asset Management & Prime Brokerage',
    tag: 'LOW LATENCY / SEC',
    desc: 'FINRA / SEC compliance, proprietary algorithmic alpha protection.',
  },
  {
    id: 'healthcare',
    name: 'Healthcare & Clinical Systems',
    icon: Cpu,
    defaultEntity: 'National Regional Hospital & Oncology Center',
    tag: 'HIPAA COMPLIANT',
    desc: 'Patient PII isolation, zero third-party diagnostic data leakage.',
  },
  {
    id: 'gov',
    name: 'Public Sector & Government',
    icon: Building2,
    defaultEntity: 'Federal Revenue & Tax Compliance Authority',
    tag: 'DATA CITIZENSHIP',
    desc: 'Citizen privacy protection, public procurement audit trails.',
  },
];

const CAPABILITY_TEMPLATES = [
  {
    title: 'Tactical Small Language Model for Edge Comms',
    defaultOptions: [
      'Self-hosted Fine-tuned Open Weights (Llama 3.3 / Sarvam 2B)',
      'Licensed Closed-Weights via Sovereign Private Cloud',
      'Outsourced Turnkey Managed SaaS Platform',
    ],
    sovereignty: 'CRITICAL',
    latency: 'SUB_20MS',
  },
  {
    title: 'Multi-Asset Financial Document Intelligence & RAG',
    defaultOptions: [
      'Internal Air-Gapped Financial RAG Cluster (vLLM + TensorRT)',
      'Tier-1 Hyperscaler Cloud Private Endpoint (OpenAI on Azure)',
      'Fintech Specialist Turnkey Financial Analytics API',
    ],
    sovereignty: 'STANDARD',
    latency: 'BALANCED',
  },
  {
    title: 'Clinical Co-Pilot & Medical Record Synthesizer',
    defaultOptions: [
      'On-Premise Medical Foundation Model (BioMistral / Meditron)',
      'HIPAA-Compliant Sovereign Healthcare Cloud Enclave',
      'Proprietary Medical Intelligence API SaaS',
    ],
    sovereignty: 'CRITICAL',
    latency: 'BALANCED',
  },
];

export const GuidedDecisionWizardModal: React.FC<GuidedDecisionWizardModalProps> = ({
  isOpen,
  onClose,
  onLaunchBrief,
}) => {
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [selectedOrg, setSelectedOrg] = useState(ORG_TEMPLATES[0]);
  const [customEntity, setCustomEntity] = useState(ORG_TEMPLATES[0].defaultEntity);
  const [selectedCap, setSelectedCap] = useState(CAPABILITY_TEMPLATES[0]);
  const [customCapability, setCustomCapability] = useState(CAPABILITY_TEMPLATES[0].title);
  const [options, setOptions] = useState<string[]>(CAPABILITY_TEMPLATES[0].defaultOptions);
  const [sovereignty, setSovereignty] = useState<'CRITICAL' | 'STANDARD' | 'LOW'>('CRITICAL');
  const [latency, setLatency] = useState<'SUB_20MS' | 'BALANCED' | 'BATCH'>('SUB_20MS');

  if (!isOpen) return null;

  const handleNext = () => {
    terminalAudio.playBlip();
    if (step === 1) setStep(2);
    else if (step === 2) setStep(3);
  };

  const handleBack = () => {
    terminalAudio.playBlip();
    if (step === 3) setStep(2);
    else if (step === 2) setStep(1);
  };

  const handleOrgSelect = (org: typeof ORG_TEMPLATES[0]) => {
    terminalAudio.playBlip();
    setSelectedOrg(org);
    setCustomEntity(org.defaultEntity);
  };

  const handleCapSelect = (cap: typeof CAPABILITY_TEMPLATES[0]) => {
    terminalAudio.playBlip();
    setSelectedCap(cap);
    setCustomCapability(cap.title);
    setOptions(cap.defaultOptions);
    setSovereignty(cap.sovereignty as 'CRITICAL' | 'STANDARD' | 'LOW');
    setLatency(cap.latency as 'SUB_20MS' | 'BALANCED' | 'BATCH');
  };

  const handleFinish = () => {
    terminalAudio.playGoCommand();
    onLaunchBrief({
      entity: customEntity.trim() || selectedOrg.defaultEntity,
      capability: customCapability.trim() || selectedCap.title,
      options: options.length > 0 ? options : selectedCap.defaultOptions,
      data_sovereignty_weight: sovereignty,
      latency_tolerance: latency,
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/85 flex items-center justify-center p-4 backdrop-blur-sm select-none font-mono">
      <div className="bg-[var(--bb-bg-surface)] border border-[var(--bb-border-bright)] rounded max-w-3xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="bb-panel-header">
          <div className="flex items-center gap-2">
            <Sparkles className="w-3.5 h-3.5 text-[var(--bb-amber)]" />
            <span>GUIDED SOURCING DECISION ASSISTANT // STEP {step} OF 3</span>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="text-[var(--bb-text-muted)] hover:text-[var(--bb-text-bright)] p-1 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-[var(--bb-bg-base)] h-1 border-b border-[var(--bb-border-subtle)]">
          <div
            className="bg-[var(--bb-amber)] h-full transition-all duration-300"
            style={{ width: `${(step / 3) * 100}%` }}
          />
        </div>

        {/* Wizard Content Body */}
        <div className="p-5 overflow-y-auto bb-scroll flex-1 space-y-4 text-xs">
          {/* STEP 1: ORGANIZATION SELECTION */}
          {step === 1 && (
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-bold text-[var(--bb-text-bright)] mb-1">
                  01 // Select Your Institutional Profile
                </h3>
                <p className="text-[11px] text-[var(--bb-text-secondary)]">
                  Choose the archetype that best matches your organization&apos;s regulatory and security boundaries.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                {ORG_TEMPLATES.map((org) => {
                  const isSelected = selectedOrg.id === org.id;
                  const Icon = org.icon;

                  return (
                    <button
                      key={org.id}
                      type="button"
                      onClick={() => handleOrgSelect(org)}
                      className={`p-3 rounded border text-left transition-all flex flex-col justify-between ${
                        isSelected
                          ? 'bg-[var(--bb-amber-dim)] border-[var(--bb-amber)] shadow-md'
                          : 'bg-[var(--bb-bg-raised)] border-[var(--bb-border-subtle)] hover:border-[var(--bb-border-mid)]'
                      }`}
                    >
                      <div>
                        <div className="flex items-center justify-between mb-1.5">
                          <div className="flex items-center gap-1.5 font-bold text-[11px] text-[var(--bb-text-bright)]">
                            <Icon className="w-3.5 h-3.5 text-[var(--bb-amber)]" />
                            <span>{org.name}</span>
                          </div>
                          <span className="text-[9px] px-1.5 py-0.2 bg-[var(--bb-bg-base)] text-[var(--bb-amber)] border border-[var(--bb-border-subtle)] rounded font-bold">
                            {org.tag}
                          </span>
                        </div>
                        <p className="text-[10px] text-[var(--bb-text-secondary)] leading-relaxed">
                          {org.desc}
                        </p>
                      </div>

                      {isSelected && (
                        <span className="text-[10px] text-[var(--bb-green)] font-bold mt-2 flex items-center gap-1">
                          <CheckCircle2 className="w-3 h-3" /> SELECTED ARCHETYPE
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>

              <div className="pt-2">
                <label className="block text-[10px] text-[var(--bb-text-muted)] uppercase tracking-wider mb-1">
                  CUSTOMIZE ENTITY NAME (OPTIONAL):
                </label>
                <input
                  type="text"
                  value={customEntity}
                  onChange={(e) => setCustomEntity(e.target.value)}
                  className="w-full bg-[var(--bb-bg-input)] border border-[var(--bb-border-mid)] focus:border-[var(--bb-amber)] text-[var(--bb-text-bright)] px-3 py-2 text-xs font-mono rounded outline-none"
                />
              </div>
            </div>
          )}

          {/* STEP 2: CAPABILITY & SOURCING PATHS */}
          {step === 2 && (
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-bold text-[var(--bb-text-bright)] mb-1">
                  02 // What AI Capability Do You Need To Deploy?
                </h3>
                <p className="text-[11px] text-[var(--bb-text-secondary)]">
                  Pick a standardized use-case or customize your exact technical requirements.
                </p>
              </div>

              <div className="space-y-2">
                {CAPABILITY_TEMPLATES.map((cap, idx) => {
                  const isSelected = selectedCap.title === cap.title;

                  return (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => handleCapSelect(cap)}
                      className={`w-full p-3 rounded border text-left transition-all ${
                        isSelected
                          ? 'bg-[var(--bb-cyan-dim)] border-[var(--bb-cyan)] shadow-md'
                          : 'bg-[var(--bb-bg-raised)] border-[var(--bb-border-subtle)] hover:border-[var(--bb-border-mid)]'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-bold text-[11px] text-[var(--bb-text-bright)]">
                          {cap.title}
                        </span>
                        {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-[var(--bb-cyan)]" />}
                      </div>
                      <div className="flex flex-wrap gap-1 mt-2">
                        {cap.defaultOptions.map((opt, oIdx) => (
                          <span
                            key={oIdx}
                            className="text-[9px] px-1.5 py-0.5 bg-[var(--bb-bg-surface)] text-[var(--bb-text-secondary)] border border-[var(--bb-border-subtle)] rounded"
                          >
                            [{oIdx + 1}] {opt.split('(')[0]}
                          </span>
                        ))}
                      </div>
                    </button>
                  );
                })}
              </div>

              <div className="pt-2">
                <label className="block text-[10px] text-[var(--bb-text-muted)] uppercase tracking-wider mb-1">
                  CUSTOMIZE TECHNICAL BRIEF:
                </label>
                <input
                  type="text"
                  value={customCapability}
                  onChange={(e) => setCustomCapability(e.target.value)}
                  className="w-full bg-[var(--bb-bg-input)] border border-[var(--bb-border-mid)] focus:border-[var(--bb-cyan)] text-[var(--bb-text-bright)] px-3 py-2 text-xs font-mono rounded outline-none"
                />
              </div>
            </div>
          )}

          {/* STEP 3: STRATEGIC PRIORITIES & REVIEW */}
          {step === 3 && (
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-bold text-[var(--bb-text-bright)] mb-1">
                  03 // Review & Enforce Strategic Constraints
                </h3>
                <p className="text-[11px] text-[var(--bb-text-secondary)]">
                  Confirm the evaluation boundaries before launching the 6-agent verification pipeline.
                </p>
              </div>

              {/* Summary Review Card */}
              <div className="p-3 bg-[var(--bb-bg-raised)] border border-[var(--bb-border-subtle)] rounded space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-[var(--bb-amber)] font-bold uppercase">
                    TARGET: {customEntity}
                  </span>
                  <span className="text-[9px] px-1.5 py-0.2 bg-[var(--bb-green-dim)] text-[var(--bb-green)] border border-[var(--bb-green)] rounded font-bold">
                    READY FOR PIPELINE
                  </span>
                </div>
                <p className="font-bold text-[12px] text-[var(--bb-text-bright)]">
                  {customCapability}
                </p>
                <div className="border-t border-[var(--bb-border-subtle)] pt-2 space-y-1">
                  <span className="text-[9px] text-[var(--bb-text-muted)] uppercase block">
                    CANDIDATE SOURCING PATHS:
                  </span>
                  {options.map((opt, i) => (
                    <div key={i} className="text-[10px] text-[var(--bb-text-secondary)]">
                      • {opt}
                    </div>
                  ))}
                </div>
              </div>

              {/* Quick Constraints Toggles */}
              <div className="grid grid-cols-2 gap-2">
                <div className="p-2.5 bg-[var(--bb-bg-surface)] border border-[var(--bb-border-subtle)] rounded">
                  <span className="text-[10px] font-bold text-[var(--bb-text-secondary)] block mb-1.5">
                    DATA SOVEREIGNTY PRIORITY:
                  </span>
                  <div className="flex gap-1">
                    {(['CRITICAL', 'STANDARD', 'LOW'] as const).map((lvl) => (
                      <button
                        key={lvl}
                        type="button"
                        onClick={() => {
                          terminalAudio.playBlip();
                          setSovereignty(lvl);
                        }}
                        className={`flex-1 py-1 text-[9px] font-bold rounded border ${
                          sovereignty === lvl
                            ? 'bg-[var(--bb-amber)] text-black border-[var(--bb-amber)]'
                            : 'bg-[var(--bb-bg-raised)] text-[var(--bb-text-muted)] border-[var(--bb-border-subtle)]'
                        }`}
                      >
                        {lvl}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="p-2.5 bg-[var(--bb-bg-surface)] border border-[var(--bb-border-subtle)] rounded">
                  <span className="text-[10px] font-bold text-[var(--bb-text-secondary)] block mb-1.5">
                    LATENCY / SLA TOLERANCE:
                  </span>
                  <div className="flex gap-1">
                    {(['SUB_20MS', 'BALANCED', 'BATCH'] as const).map((lat) => (
                      <button
                        key={lat}
                        type="button"
                        onClick={() => {
                          terminalAudio.playBlip();
                          setLatency(lat);
                        }}
                        className={`flex-1 py-1 text-[9px] font-bold rounded border ${
                          latency === lat
                            ? 'bg-[var(--bb-cyan)] text-black border-[var(--bb-cyan)]'
                            : 'bg-[var(--bb-bg-raised)] text-[var(--bb-text-muted)] border-[var(--bb-border-subtle)]'
                        }`}
                      >
                        {lat.replace('_', ' ')}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Wizard Footer Controls */}
        <div className="px-4 py-3 bg-[var(--bb-bg-raised)] border-t border-[var(--bb-border-subtle)] flex items-center justify-between">
          <div>
            {step > 1 ? (
              <button
                type="button"
                onClick={handleBack}
                className="bb-button bb-button-ghost px-3 py-1.5 text-xs"
              >
                <ArrowLeft className="w-3.5 h-3.5" /> BACK
              </button>
            ) : (
              <button
                type="button"
                onClick={onClose}
                className="bb-button bb-button-ghost px-3 py-1.5 text-xs"
              >
                CANCEL
              </button>
            )}
          </div>

          <div>
            {step < 3 ? (
              <button
                type="button"
                onClick={handleNext}
                className="bb-button bb-button-go px-4 py-1.5 text-xs font-bold"
              >
                NEXT STEP <ArrowRight className="w-3.5 h-3.5" />
              </button>
            ) : (
              <button
                type="button"
                onClick={handleFinish}
                className="bb-button bb-button-go px-5 py-1.5 text-xs font-bold shadow-lg"
              >
                <Play className="w-3.5 h-3.5" /> SYNTHESIZE SOURCING VERDICT &lt;GO&gt;
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
