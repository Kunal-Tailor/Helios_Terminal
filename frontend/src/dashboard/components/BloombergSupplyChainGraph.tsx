import React, { useState } from 'react';
import {
  GitFork,
  AlertTriangle,
  ShieldAlert,
  RefreshCw,
} from 'lucide-react';
import { terminalAudio } from '../utils/terminalAudio';

export interface SupplyChainNode {
  id: string;
  tier: 0 | 1 | 2 | 3 | 4 | 5;
  tierName: string;
  name: string;
  supplier: string;
  country: string;
  dependencySharePct: number;
  switchingFrictionScore: number; // 1-10
  spofRisk: 'CRITICAL' | 'HIGH' | 'MODERATE' | 'LOW';
  alternativeOption: string;
  impactOnFailure: string;
  status: 'ACTIVE' | 'SEVERED';
}

export const SUPPLY_CHAIN_NODES: SupplyChainNode[] = [
  // Tier 0: Silicon & Lithography
  {
    id: 'node-tsmc',
    tier: 0,
    tierName: 'Tier 0: Advanced Silicon Fabrication',
    name: 'TSMC 3nm & 4nm High-Density Wafers',
    supplier: 'Taiwan Semiconductor Manufacturing Co.',
    country: 'Taiwan (ROC)',
    dependencySharePct: 88,
    switchingFrictionScore: 9.9,
    spofRisk: 'CRITICAL',
    alternativeOption: 'Intel 18A Sovereign Foundry / Samsung Foundry',
    impactOnFailure: 'Complete halt in global GPU supply for 18-24 months.',
    status: 'ACTIVE',
  },
  {
    id: 'node-asml',
    tier: 0,
    tierName: 'Tier 0: Lithography Equipment',
    name: 'Twinscan EXE High-NA EUV Scanners',
    supplier: 'ASML Holding N.V.',
    country: 'Netherlands',
    dependencySharePct: 95,
    switchingFrictionScore: 10.0,
    spofRisk: 'CRITICAL',
    alternativeOption: 'None (Global monopoly on sub-5nm lithography)',
    impactOnFailure: 'Zero capacity expansion for leading-edge semiconductors globally.',
    status: 'ACTIVE',
  },
  // Tier 1: Cloud & Datacenter
  {
    id: 'node-cloud',
    tier: 1,
    tierName: 'Tier 1: Cloud Compute Infrastructure',
    name: 'Hyperscale GPU Cluster Orchestration',
    supplier: 'AWS / Azure / Yotta NM1 Sovereign Pod',
    country: 'US / India',
    dependencySharePct: 65,
    switchingFrictionScore: 7.5,
    spofRisk: 'HIGH',
    alternativeOption: 'Bare-Metal On-Premise Air-Gapped Datacenter',
    impactOnFailure: 'Service degradation, latency spikes, and WAN egress fees.',
    status: 'ACTIVE',
  },
  // Tier 2: Foundation Model Weights
  {
    id: 'node-weights',
    tier: 2,
    tierName: 'Tier 2: Foundation Model Weights',
    name: 'Llama-3.3 70B / Sarvam Indic Open Weights',
    supplier: 'Meta AI / Sarvam AI Labs',
    country: 'US / India',
    dependencySharePct: 74,
    switchingFrictionScore: 3.2,
    spofRisk: 'LOW',
    alternativeOption: 'Mistral Large / Qwen-2.5 / DeepSeek-V3',
    impactOnFailure: 'Re-prompting & fine-tuning dataset migration required (2-3 weeks).',
    status: 'ACTIVE',
  },
  // Tier 3: Tensor Runtimes & Inference
  {
    id: 'node-runtime',
    tier: 3,
    tierName: 'Tier 3: Tensor Inference Runtime',
    name: 'vLLM / llama.cpp GGML Quantization Engine',
    supplier: 'Open Source Community / UC Berkeley',
    country: 'Decentralized',
    dependencySharePct: 82,
    switchingFrictionScore: 2.1,
    spofRisk: 'LOW',
    alternativeOption: 'TensorRT-LLM / Triton Inference Server / ONNX',
    impactOnFailure: 'Zero supply disruption; code is permanently forked in-house.',
    status: 'ACTIVE',
  },
  // Tier 4: Vector Storage & Memory
  {
    id: 'node-vector',
    tier: 4,
    tierName: 'Tier 4: Vector Retrieval & Embeddings',
    name: 'Qdrant HNSW Private Cluster + BGE Embeddings',
    supplier: 'Qdrant Solutions GmbH / BAAI',
    country: 'Germany / Open',
    dependencySharePct: 70,
    switchingFrictionScore: 4.8,
    spofRisk: 'MODERATE',
    alternativeOption: 'pgvector on PostgreSQL / Milvus / Chroma',
    impactOnFailure: 'Index recalculation & vector space re-indexing needed.',
    status: 'ACTIVE',
  },
  // Tier 5: Enterprise Application
  {
    id: 'node-app',
    tier: 5,
    tierName: 'Tier 5: Decision Intelligence & Copilot Apps',
    name: 'Helios Multi-Agent Sourcing Pipeline',
    supplier: 'Helios Terminal Core',
    country: 'Sovereign Institutional Perimeter',
    dependencySharePct: 100,
    switchingFrictionScore: 1.0,
    spofRisk: 'LOW',
    alternativeOption: 'Internal manual strategic committee',
    impactOnFailure: 'Mission-critical automated sourcing analysis offline.',
    status: 'ACTIVE',
  },
];

export const BloombergSupplyChainGraph: React.FC = () => {
  const [nodes, setNodes] = useState<SupplyChainNode[]>(SUPPLY_CHAIN_NODES);
  const [selectedNode, setSelectedNode] = useState<SupplyChainNode>(SUPPLY_CHAIN_NODES[0]);
  const [severedNodeId, setSeveredNodeId] = useState<string | null>(null);

  const handleSimulateOutage = (nodeId: string) => {
    terminalAudio.playWarning();
    if (severedNodeId === nodeId) {
      // Restore
      setSeveredNodeId(null);
      setNodes((prev) => prev.map((n) => ({ ...n, status: 'ACTIVE' })));
    } else {
      // Sever
      setSeveredNodeId(nodeId);
      const target = nodes.find((n) => n.id === nodeId);
      if (target) {
        setNodes((prev) =>
          prev.map((n) => (n.tier >= target.tier ? { ...n, status: 'SEVERED' } : { ...n, status: 'ACTIVE' }))
        );
      }
    }
  };

  const handleResetOutage = () => {
    terminalAudio.playBlip();
    setSeveredNodeId(null);
    setNodes((prev) => prev.map((n) => ({ ...n, status: 'ACTIVE' })));
  };

  return (
    <div className="flex flex-col h-full bg-[var(--bb-bg-surface)] text-[var(--bb-text-primary)] font-mono">
      {/* Panel Header */}
      <div className="bb-panel-header">
        <div className="flex items-center gap-2">
          <GitFork className="w-3.5 h-3.5 text-[var(--bb-amber)]" />
          <span>SPLC &lt;GO&gt; // MULTI-TIER AI SUPPLY CHAIN & DEPENDENCY GRAPH</span>
          <span className="text-[10px] text-[var(--bb-text-muted)]">[FUNCTION 09]</span>
        </div>

        <div className="flex items-center gap-2">
          {severedNodeId && (
            <button
              type="button"
              onClick={handleResetOutage}
              className="bb-badge bb-badge-amber hover:bg-[var(--bb-amber)] hover:text-black transition-colors"
            >
              <RefreshCw className="w-3 h-3" /> RESET BLAST SIMULATION
            </button>
          )}
          <span className="bb-badge bb-badge-amber">6-TIER DEPENDENCY TREE</span>
        </div>
      </div>

      {/* Control Banner */}
      <div className="px-3 py-2 bg-[var(--bb-bg-raised)] border-b border-[var(--bb-border-subtle)] flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-[var(--bb-text-muted)] uppercase">
            BLAST RADIUS SIMULATION:
          </span>
          <span className="text-[11px] text-[var(--bb-text-secondary)]">
            Click any supplier node below to simulate a single-point-of-failure (SPOF) embargo or blackout.
          </span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[10px] px-2 py-0.5 rounded bg-[var(--bb-red-dim)] text-[var(--bb-red)] border border-[var(--bb-red)] font-bold">
            CRITICAL SPOF: TSMC & ASML
          </span>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Interactive Multi-Tier Visual Graph */}
        <div className="flex-1 p-4 overflow-y-auto bb-scroll space-y-3">
          {nodes.map((node, idx) => {
            const isSelected = selectedNode.id === node.id;
            const isSevered = node.status === 'SEVERED';

            return (
              <div
                key={node.id}
                onClick={() => {
                  terminalAudio.playBlip();
                  setSelectedNode(node);
                }}
                className={`p-3 rounded border transition-all cursor-pointer relative ${
                  isSevered
                    ? 'bg-red-950/20 border-[var(--bb-red)] shadow-lg'
                    : isSelected
                    ? 'bg-[var(--bb-bg-raised)] border-[var(--bb-amber)] shadow-md'
                    : 'bg-[var(--bb-bg-base)] border-[var(--bb-border-subtle)] hover:border-[var(--bb-border-mid)]'
                }`}
              >
                {/* Connecting Line to next tier */}
                {idx < nodes.length - 1 && (
                  <div className="absolute left-6 -bottom-3 w-0.5 h-3 bg-[var(--bb-border-mid)] z-0" />
                )}

                <div className="flex items-center justify-between mb-1.5 relative z-10">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold text-[var(--bb-amber)]">
                      TIER {node.tier}
                    </span>
                    <span className="text-[var(--bb-border-mid)]">/</span>
                    <span className="font-bold text-[12px] text-[var(--bb-text-bright)]">
                      {node.name}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    {/* SPOF Badge */}
                    <span
                      className={`text-[9px] px-1.5 py-0.5 rounded font-bold ${
                        node.spofRisk === 'CRITICAL'
                          ? 'bg-[var(--bb-red-dim)] text-[var(--bb-red)] border border-[var(--bb-red)]'
                          : node.spofRisk === 'HIGH'
                          ? 'bg-[var(--bb-amber-dim)] text-[var(--bb-amber)] border border-[var(--bb-amber)]'
                          : 'bg-[var(--bb-green-dim)] text-[var(--bb-green)] border border-[var(--bb-green)]'
                      }`}
                    >
                      SPOF: {node.spofRisk}
                    </span>

                    {/* Status Badge */}
                    <span
                      className={`text-[9px] px-1.5 py-0.5 rounded font-bold ${
                        isSevered
                          ? 'bg-[var(--bb-red)] text-black'
                          : 'bg-[var(--bb-green-dim)] text-[var(--bb-green)]'
                      }`}
                    >
                      {isSevered ? 'CASCADE BLACKOUT' : 'OPERATIONAL'}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2 text-[10px] text-[var(--bb-text-secondary)] mt-2">
                  <div>
                    <span className="text-[var(--bb-text-dim)] block">PRIMARY SUPPLIER:</span>
                    <span className="text-[var(--bb-text-primary)] font-bold">{node.supplier}</span>
                  </div>
                  <div>
                    <span className="text-[var(--bb-text-dim)] block">JURISDICTION:</span>
                    <span className="text-[var(--bb-text-primary)]">{node.country}</span>
                  </div>
                  <div>
                    <span className="text-[var(--bb-text-dim)] block">DEPENDENCY SHARE:</span>
                    <span className="text-[var(--bb-amber)] font-bold">{node.dependencySharePct}%</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right: Supplier Deep-Dive Inspector */}
        <div className="w-80 bg-[var(--bb-bg-surface)] border-l border-[var(--bb-border-subtle)] p-4 flex flex-col overflow-y-auto bb-scroll text-xs">
          <div className="bb-panel-header -mx-4 -mt-4 mb-4">
            <div className="flex items-center gap-2">
              <ShieldAlert className="w-3.5 h-3.5 text-[var(--bb-red)]" />
              <span>SUPPLIER RISK DOSSIER</span>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <span className="text-[9px] text-[var(--bb-text-dim)] uppercase block mb-0.5">
                {selectedNode.tierName}
              </span>
              <h3 className="text-sm font-bold text-[var(--bb-text-bright)]">
                {selectedNode.name}
              </h3>
            </div>

            {/* Metrics */}
            <div className="grid grid-cols-2 gap-2">
              <div className="p-2 bg-[var(--bb-bg-raised)] border border-[var(--bb-border-subtle)] rounded">
                <span className="text-[9px] text-[var(--bb-text-muted)] block mb-0.5">SWITCHING FRICTION</span>
                <span className="text-xs font-bold text-[var(--bb-red)] bb-tabular">
                  {selectedNode.switchingFrictionScore.toFixed(1)} / 10.0
                </span>
              </div>

              <div className="p-2 bg-[var(--bb-bg-raised)] border border-[var(--bb-border-subtle)] rounded">
                <span className="text-[9px] text-[var(--bb-text-muted)] block mb-0.5">MARKET MONOPOLY</span>
                <span className="text-xs font-bold text-[var(--bb-amber)] bb-tabular">
                  {selectedNode.dependencySharePct}% SHARE
                </span>
              </div>
            </div>

            {/* Impact On Failure */}
            <div>
              <span className="text-[9px] text-[var(--bb-text-muted)] uppercase block mb-1">
                OUTAGE / EMBARGO BLAST RADIUS:
              </span>
              <p className="text-[11px] text-[var(--bb-red-bright)] leading-relaxed bg-[var(--bb-red-dim)] p-2.5 rounded border border-[var(--bb-red)]">
                {selectedNode.impactOnFailure}
              </p>
            </div>

            {/* Alternative Sovereign Path */}
            <div>
              <span className="text-[9px] text-[var(--bb-text-muted)] uppercase block mb-1">
                RECOMMENDED SOVEREIGN ALTERNATIVE:
              </span>
              <p className="text-[11px] text-[var(--bb-green)] leading-relaxed bg-[var(--bb-green-dim)] p-2.5 rounded border border-[var(--bb-green)]">
                {selectedNode.alternativeOption}
              </p>
            </div>

            {/* Simulate Outage Trigger */}
            <button
              type="button"
              onClick={() => handleSimulateOutage(selectedNode.id)}
              className={`w-full bb-button py-2.5 text-xs justify-center font-bold tracking-wider ${
                severedNodeId === selectedNode.id
                  ? 'bg-[var(--bb-green)] text-black border-[var(--bb-green)]'
                  : 'bg-[var(--bb-red)] text-white border-[var(--bb-red-bright)]'
              }`}
            >
              {severedNodeId === selectedNode.id ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5" /> RESTORE SUPPLIER LINK
                </>
              ) : (
                <>
                  <AlertTriangle className="w-3.5 h-3.5" /> SIMULATE EMBARGO / OUTAGE
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
