import React, { useState } from 'react';
import {
  Globe,
  Layers,
  Server,
  Zap,
  Compass,
  Plus,
  Minus,
  RotateCcw,
  X,
} from 'lucide-react';
import { terminalAudio } from '../utils/terminalAudio';

export interface DatacenterCluster {
  id: string;
  name: string;
  code: string;
  region: string;
  lat: number;
  lng: number;
  type: 'SOVEREIGN_POD' | 'TIER_1_CLOUD' | 'FABRICATION_HUB' | 'SUBSEA_GATEWAY';
  h100Equiv: number;
  powerMw: number;
  pueScore: number;
  spotGpuHour: number;
  sovereigntyIndex: number; // 1-10
  exportControlRisk: 'LOW' | 'MEDIUM' | 'RESTRICTED';
  keyProviders: string[];
  description: string;
}

export const GLOBAL_CLUSTERS: DatacenterCluster[] = [
  {
    id: 'dc-mumbai',
    name: 'Mumbai Yotta NM1 Sovereign Cloud Pod',
    code: 'IN-BOM-01',
    region: 'India (Western Zone)',
    lat: 19.076,
    lng: 72.8777,
    type: 'SOVEREIGN_POD',
    h100Equiv: 16384,
    powerMw: 250,
    pueScore: 1.28,
    spotGpuHour: 2.15,
    sovereigntyIndex: 9.8,
    exportControlRisk: 'LOW',
    keyProviders: ['Yotta Enterprise', 'Indian Defense Air-Gap Grid', 'Sarvam Sovereign Node'],
    description: 'Indigenous sovereign GPU cluster certified under Indian Digital Personal Data Protection (DPDP) Act with zero overseas data transmission egress.',
  },
  {
    id: 'dc-frankfurt',
    name: 'Frankfurt EU AI Sovereign Core (Equinix FR5)',
    code: 'EU-FRA-01',
    region: 'European Union (Germany)',
    lat: 50.1109,
    lng: 8.6821,
    type: 'SOVEREIGN_POD',
    h100Equiv: 24500,
    powerMw: 180,
    pueScore: 1.19,
    spotGpuHour: 2.65,
    sovereigntyIndex: 9.2,
    exportControlRisk: 'LOW',
    keyProviders: ['Hetzner Sovereign', 'OVHcloud AI', 'Mistral Dedicated Enclave'],
    description: 'Strict GDPR & EU AI Act Tier-1 compliance zone with 100% renewable energy grid and zero US CLOUD Act warrantless disclosure exposure.',
  },
  {
    id: 'dc-us-east',
    name: 'Northern Virginia Hyperscale Nexus (Ashburn)',
    code: 'US-IAD-01',
    region: 'United States (East)',
    lat: 39.0438,
    lng: -77.4874,
    type: 'TIER_1_CLOUD',
    h100Equiv: 128000,
    powerMw: 1800,
    pueScore: 1.15,
    spotGpuHour: 2.85,
    sovereigntyIndex: 4.2,
    exportControlRisk: 'RESTRICTED',
    keyProviders: ['AWS us-east-1', 'Azure East US', 'OpenAI Hypercluster', 'Anthropic Core'],
    description: 'The global epicenter of LLM inference traffic handling 70% of world internet backbone. Subject to US EAR & CLOUD Act jurisdiction.',
  },
  {
    id: 'dc-taiwan',
    name: 'Hsinchu Science Park // TSMC Fab 18/20',
    code: 'TW-HSZ-01',
    region: 'East Asia (Taiwan)',
    lat: 24.7806,
    lng: 120.9972,
    type: 'FABRICATION_HUB',
    h100Equiv: 0,
    powerMw: 950,
    pueScore: 1.35,
    spotGpuHour: 0,
    sovereigntyIndex: 6.5,
    exportControlRisk: 'RESTRICTED',
    keyProviders: ['TSMC N3/N2 Node', 'ASML Twinscan High-NA', 'CoWoS Packaging Lines'],
    description: 'Single point of failure for 92% of global advanced semiconductor fabrication. Geopolitical chokepoint subject to Strait of Taiwan maritime tension.',
  },
  {
    id: 'dc-singapore',
    name: 'Singapore Jurong SEA Cloud Gateway',
    code: 'SG-SIN-01',
    region: 'Southeast Asia (Singapore)',
    lat: 1.3521,
    lng: 103.8198,
    type: 'SUBSEA_GATEWAY',
    h100Equiv: 32000,
    powerMw: 420,
    pueScore: 1.38,
    spotGpuHour: 2.45,
    sovereigntyIndex: 7.8,
    exportControlRisk: 'MEDIUM',
    keyProviders: ['Singtel AI Cloud', 'GCP Southeast Asia', 'SEA-ME-WE-6 Terminal'],
    description: 'Crucial ASEAN data transit hub bridging Indian Ocean subsea fiber corridors with Pacific gateways.',
  },
  {
    id: 'dc-tokyo',
    name: 'Tokyo Bay AI Supercluster (ABCI 3.0)',
    code: 'JP-TYO-01',
    region: 'East Asia (Japan)',
    lat: 35.6762,
    lng: 139.6503,
    type: 'SOVEREIGN_POD',
    h100Equiv: 42000,
    powerMw: 320,
    pueScore: 1.22,
    spotGpuHour: 2.50,
    sovereigntyIndex: 8.9,
    exportControlRisk: 'LOW',
    keyProviders: ['Sakura Internet', 'AIST ABCI 3.0', 'SoftBank Sovereign AI'],
    description: 'Japanese national sovereign AI infrastructure decoupled from US foreign cloud tenancy with indigenous LLM fine-tuning clusters.',
  },
  {
    id: 'dc-dublin',
    name: 'Dublin Silicon Docks Hyperscale Campus',
    code: 'IE-DUB-01',
    region: 'Western Europe (Ireland)',
    lat: 53.3498,
    lng: -6.2603,
    type: 'TIER_1_CLOUD',
    h100Equiv: 48000,
    powerMw: 540,
    pueScore: 1.24,
    spotGpuHour: 2.70,
    sovereigntyIndex: 6.8,
    exportControlRisk: 'LOW',
    keyProviders: ['AWS eu-west-1', 'Microsoft Ireland Central', 'Meta AI Datacenter'],
    description: 'Transatlantic subsea fiber landing zone with massive cloud hyperscaler density under Irish Data Protection Commission jurisdiction.',
  },
];

const SUBSEA_CABLES = [
  { name: 'SEA-ME-WE-6 (Bharat-Marseille)', from: [72.87, 19.07], to: [8.68, 50.11], latencyMs: 64, bandwidthTbps: 126 },
  { name: 'Transatlantic Dunant (Ashburn-Frankfurt)', from: [-77.48, 39.04], to: [8.68, 50.11], latencyMs: 58, bandwidthTbps: 250 },
  { name: 'Pacific Light Cable (Taiwan-Singapore)', from: [120.99, 24.78], to: [103.81, 1.35], latencyMs: 38, bandwidthTbps: 144 },
  { name: 'APCN-2 (Tokyo-Singapore)', from: [139.65, 35.67], to: [103.81, 1.35], latencyMs: 44, bandwidthTbps: 180 },
];

export const BloombergGlobalMap: React.FC = () => {
  const [selectedCluster, setSelectedCluster] = useState<DatacenterCluster | null>(GLOBAL_CLUSTERS[0]);
  const [activeLayers, setActiveLayers] = useState({
    gpuNodes: true,
    subseaCables: true,
    sanctionZones: true,
    energyPue: false,
  });
  const [zoomLevel, setZoomLevel] = useState(1);
  const [searchFilter, setSearchFilter] = useState('');

  // Map projection coordinates to SVG box (width: 900, height: 460)
  const projectCoords = (lng: number, lat: number): [number, number] => {
    const x = ((lng + 180) / 360) * 860 + 20;
    const y = ((90 - lat) / 180) * 420 + 20;
    return [x, y];
  };

  const toggleLayer = (key: keyof typeof activeLayers) => {
    terminalAudio.playBlip();
    setActiveLayers((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const filteredClusters = searchFilter
    ? GLOBAL_CLUSTERS.filter(
        (c) =>
          c.name.toLowerCase().includes(searchFilter.toLowerCase()) ||
          c.region.toLowerCase().includes(searchFilter.toLowerCase()) ||
          c.code.toLowerCase().includes(searchFilter.toLowerCase())
      )
    : GLOBAL_CLUSTERS;

  return (
    <div className="flex flex-col h-full bg-[var(--bb-bg-surface)] text-[var(--bb-text-primary)] font-mono">
      {/* Top Header Bar */}
      <div className="bb-panel-header">
        <div className="flex items-center gap-2">
          <Globe className="w-3.5 h-3.5 text-[var(--bb-cyan)]" />
          <span>BMAP &lt;GO&gt; // GLOBAL AI INFRASTRUCTURE & SOVEREIGNTY MAP</span>
          <span className="text-[10px] text-[var(--bb-text-muted)]">[FUNCTION 08]</span>
        </div>

        <div className="flex items-center gap-2">
          <span className="bb-badge bb-badge-cyan">TACTICAL GEOPOLITICAL RADAR</span>
        </div>
      </div>

      {/* Map Control Strip */}
      <div className="px-3 py-2 bg-[var(--bb-bg-raised)] border-b border-[var(--bb-border-subtle)] flex flex-wrap items-center justify-between gap-2 text-xs">
        {/* Layer Toggles */}
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-[var(--bb-text-muted)] uppercase flex items-center gap-1">
            <Layers className="w-3 h-3 text-[var(--bb-amber)]" />
            OVERLAYS:
          </span>

          <button
            type="button"
            onClick={() => toggleLayer('gpuNodes')}
            className={`px-2 py-0.5 text-[10px] rounded border ${
              activeLayers.gpuNodes
                ? 'bg-[var(--bb-green-dim)] text-[var(--bb-green)] border-[var(--bb-green)] font-bold'
                : 'bg-[var(--bb-bg-base)] text-[var(--bb-text-muted)] border-[var(--bb-border-subtle)]'
            }`}
          >
            [•] GPU CLUSTERS
          </button>

          <button
            type="button"
            onClick={() => toggleLayer('subseaCables')}
            className={`px-2 py-0.5 text-[10px] rounded border ${
              activeLayers.subseaCables
                ? 'bg-[var(--bb-cyan-dim)] text-[var(--bb-cyan)] border-[var(--bb-cyan)] font-bold'
                : 'bg-[var(--bb-bg-base)] text-[var(--bb-text-muted)] border-[var(--bb-border-subtle)]'
            }`}
          >
            [•] SUBSEA LATENCY CABLES
          </button>

          <button
            type="button"
            onClick={() => toggleLayer('sanctionZones')}
            className={`px-2 py-0.5 text-[10px] rounded border ${
              activeLayers.sanctionZones
                ? 'bg-[var(--bb-red-dim)] text-[var(--bb-red)] border-[var(--bb-red)] font-bold'
                : 'bg-[var(--bb-bg-base)] text-[var(--bb-text-muted)] border-[var(--bb-border-subtle)]'
            }`}
          >
            [•] BIS & EXPORT PERIMETERS
          </button>

          <button
            type="button"
            onClick={() => toggleLayer('energyPue')}
            className={`px-2 py-0.5 text-[10px] rounded border ${
              activeLayers.energyPue
                ? 'bg-[var(--bb-amber-dim)] text-[var(--bb-amber)] border-[var(--bb-amber)] font-bold'
                : 'bg-[var(--bb-bg-base)] text-[var(--bb-text-muted)] border-[var(--bb-border-subtle)]'
            }`}
          >
            [•] PUE / ENERGY EFFICIENCY
          </button>
        </div>

        {/* Zoom & Search */}
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            placeholder="Search cluster (e.g. Mumbai, TSMC)..."
            className="bg-[var(--bb-bg-input)] border border-[var(--bb-border-mid)] text-[var(--bb-text-bright)] px-2 py-0.5 text-[11px] rounded outline-none w-48"
          />

          <div className="flex items-center bg-[var(--bb-bg-base)] border border-[var(--bb-border-subtle)] rounded p-0.5">
            <button
              type="button"
              onClick={() => {
                terminalAudio.playBlip();
                setZoomLevel((z) => Math.min(2.5, z + 0.25));
              }}
              className="p-1 hover:text-[var(--bb-amber)] text-[var(--bb-text-secondary)]"
              title="Zoom In"
            >
              <Plus className="w-3 h-3" />
            </button>
            <span className="text-[10px] px-1 text-[var(--bb-text-muted)]">{(zoomLevel * 100).toFixed(0)}%</span>
            <button
              type="button"
              onClick={() => {
                terminalAudio.playBlip();
                setZoomLevel((z) => Math.max(0.75, z - 0.25));
              }}
              className="p-1 hover:text-[var(--bb-amber)] text-[var(--bb-text-secondary)]"
              title="Zoom Out"
            >
              <Minus className="w-3 h-3" />
            </button>
            <button
              type="button"
              onClick={() => {
                terminalAudio.playBlip();
                setZoomLevel(1);
              }}
              className="p-1 hover:text-[var(--bb-amber)] text-[var(--bb-text-secondary)]"
              title="Reset Zoom"
            >
              <RotateCcw className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Map Viewport & Drawer Area */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* SVG World Map Canvas */}
        <div className="flex-1 bg-[var(--bb-bg-base)] overflow-hidden relative flex items-center justify-center p-2">
          {/* Tactical Grid Background */}
          <div
            className="absolute inset-0 opacity-20 pointer-events-none"
            style={{
              backgroundImage: 'linear-gradient(#1E293B 1px, transparent 1px), linear-gradient(90deg, #1E293B 1px, transparent 1px)',
              backgroundSize: '40px 40px',
            }}
          />

          <svg
            viewBox="0 0 900 460"
            className="w-full h-full max-h-[580px] select-none transition-transform duration-200"
            style={{ transform: `scale(${zoomLevel})` }}
          >
            {/* World Continents Stylized Silhouette */}
            <g fill="#121824" stroke="#1E293B" strokeWidth="0.8">
              {/* North America */}
              <path d="M 120 70 L 250 65 L 290 110 L 250 190 L 190 230 L 160 170 L 110 130 Z" />
              {/* South America */}
              <path d="M 230 240 L 290 250 L 320 330 L 270 410 L 240 340 L 210 270 Z" />
              {/* Europe */}
              <path d="M 430 70 L 510 60 L 530 110 L 480 150 L 420 130 L 400 90 Z" />
              {/* Africa */}
              <path d="M 420 160 L 510 160 L 540 250 L 490 350 L 430 330 L 410 230 Z" />
              {/* Asia */}
              <path d="M 520 60 L 750 70 L 780 160 L 690 240 L 620 220 L 540 180 Z" />
              {/* India subcontinent */}
              <path d="M 590 170 L 650 180 L 630 260 L 600 240 Z" fill="#172233" stroke="#25354D" strokeWidth="1.2" />
              {/* Australia */}
              <path d="M 690 290 L 790 290 L 800 370 L 710 370 Z" />
            </g>

            {/* Geopolitical Sanction / Boundary Rings */}
            {activeLayers.sanctionZones && (
              <g>
                {/* Indian Sovereign Air-Gap Zone */}
                <circle cx={projectCoords(72.87, 19.07)[0]} cy={projectCoords(72.87, 19.07)[1]} r="42" fill="rgba(0, 255, 102, 0.05)" stroke="#00FF66" strokeWidth="1" strokeDasharray="3 3" />
                <text x={projectCoords(72.87, 19.07)[0] - 38} y={projectCoords(72.87, 19.07)[1] - 46} fill="#00FF66" fontSize="8" fontFamily="monospace">
                  [DPDP SOVEREIGN ENCLAVE]
                </text>

                {/* EU AI Act Boundary */}
                <circle cx={projectCoords(8.68, 50.11)[0]} cy={projectCoords(8.68, 50.11)[1]} r="48" fill="rgba(0, 229, 255, 0.05)" stroke="#00E5FF" strokeWidth="1" strokeDasharray="3 3" />
                <text x={projectCoords(8.68, 50.11)[0] - 40} y={projectCoords(8.68, 50.11)[1] - 52} fill="#00E5FF" fontSize="8" fontFamily="monospace">
                  [EU AI ACT COMPLIANCE ZONE]
                </text>

                {/* US Export Control Restriction Boundary */}
                <circle cx={projectCoords(-77.48, 39.04)[0]} cy={projectCoords(-77.48, 39.04)[1]} r="54" fill="rgba(255, 51, 102, 0.05)" stroke="#FF3366" strokeWidth="1" strokeDasharray="3 3" />
                <text x={projectCoords(-77.48, 39.04)[0] - 44} y={projectCoords(-77.48, 39.04)[1] - 58} fill="#FF3366" fontSize="8" fontFamily="monospace">
                  [US EAR & CLOUD ACT JURISDICTION]
                </text>

                {/* Taiwan Strait Chokepoint */}
                <circle cx={projectCoords(120.99, 24.78)[0]} cy={projectCoords(120.99, 24.78)[1]} r="32" fill="rgba(255, 158, 0, 0.08)" stroke="#FF9E00" strokeWidth="1.2" strokeDasharray="2 2" />
                <text x={projectCoords(120.99, 24.78)[0] - 32} y={projectCoords(120.99, 24.78)[1] + 40} fill="#FF9E00" fontSize="8" fontFamily="monospace">
                  [TSMC CHOKEPOINT]
                </text>
              </g>
            )}

            {/* Subsea Fiber Cables */}
            {activeLayers.subseaCables && (
              <g>
                {SUBSEA_CABLES.map((cable, idx) => {
                  const [x1, y1] = projectCoords(cable.from[0], cable.from[1]);
                  const [x2, y2] = projectCoords(cable.to[0], cable.to[1]);
                  const cx = (x1 + x2) / 2;
                  const cy = (y1 + y2) / 2 - 30;

                  return (
                    <g key={idx}>
                      <path
                        d={`M ${x1} ${y1} Q ${cx} ${cy} ${x2} ${y2}`}
                        fill="none"
                        stroke="#00E5FF"
                        strokeWidth="1.2"
                        strokeDasharray="4 2"
                        opacity="0.6"
                      />
                      <circle cx={cx} cy={cy} r="2" fill="#00E5FF" />
                      <text x={cx + 4} y={cy} fill="#94A3B8" fontSize="7" fontFamily="monospace">
                        {cable.name.split(' ')[0]} ({cable.latencyMs}ms)
                      </text>
                    </g>
                  );
                })}
              </g>
            )}

            {/* Datacenter Cluster Nodes */}
            {activeLayers.gpuNodes &&
              filteredClusters.map((cluster) => {
                const [cx, cy] = projectCoords(cluster.lng, cluster.lat);
                const isSelected = selectedCluster?.id === cluster.id;
                const isSovereign = cluster.type === 'SOVEREIGN_POD';
                const isFab = cluster.type === 'FABRICATION_HUB';

                return (
                  <g
                    key={cluster.id}
                    onClick={() => {
                      terminalAudio.playBlip();
                      setSelectedCluster(cluster);
                    }}
                    className="cursor-pointer group"
                  >
                    {/* Glowing Pulse */}
                    <circle
                      cx={cx}
                      cy={cy}
                      r={isSelected ? 10 : 6}
                      fill={isSovereign ? 'rgba(0, 255, 102, 0.2)' : isFab ? 'rgba(255, 158, 0, 0.2)' : 'rgba(0, 229, 255, 0.2)'}
                      stroke={isSovereign ? '#00FF66' : isFab ? '#FF9E00' : '#00E5FF'}
                      strokeWidth={isSelected ? 2 : 1.2}
                      className="animate-ping"
                      style={{ animationDuration: '3s' }}
                    />

                    {/* Center Pin */}
                    <circle
                      cx={cx}
                      cy={cy}
                      r={isSelected ? 5 : 3.5}
                      fill={isSovereign ? '#00FF66' : isFab ? '#FF9E00' : '#00E5FF'}
                    />

                    {/* Label Tag */}
                    <rect
                      x={cx + 7}
                      y={cy - 7}
                      width={cluster.code.length * 6 + 8}
                      height="14"
                      fill="#0D1117"
                      stroke={isSelected ? '#FF9E00' : '#252F42'}
                      strokeWidth="1"
                      rx="2"
                    />
                    <text
                      x={cx + 11}
                      y={cy + 3}
                      fill={isSelected ? '#FF9E00' : '#E2E8F0'}
                      fontSize="8"
                      fontFamily="monospace"
                      fontWeight="bold"
                    >
                      {cluster.code}
                    </text>
                  </g>
                );
              })}
          </svg>

          {/* Compass & Lat/Long HUD Overlay */}
          <div className="absolute bottom-3 left-3 bg-[var(--bb-bg-surface)]/90 border border-[var(--bb-border-subtle)] p-2 rounded text-[10px] flex items-center gap-3 backdrop-blur-sm">
            <div className="flex items-center gap-1 text-[var(--bb-amber)] font-bold">
              <Compass className="w-3.5 h-3.5 animate-spin" style={{ animationDuration: '20s' }} />
              <span>BMAP MERCATOR GRID</span>
            </div>
            <span className="text-[var(--bb-text-muted)]">|</span>
            <span className="text-[var(--bb-text-secondary)]">ACTIVE NODES: {GLOBAL_CLUSTERS.length}</span>
            <span className="text-[var(--bb-text-muted)]">|</span>
            <span className="text-[var(--bb-green)]">SOVEREIGN ENCLAVES: 3</span>
          </div>
        </div>

        {/* Right Node Inspector Drawer */}
        {selectedCluster && (
          <div className="w-80 bg-[var(--bb-bg-surface)] border-l border-[var(--bb-border-subtle)] flex flex-col overflow-y-auto bb-scroll">
            <div className="bb-panel-header">
              <div className="flex items-center gap-2 truncate pr-2">
                <Server className="w-3.5 h-3.5 text-[var(--bb-amber)] flex-shrink-0" />
                <span className="truncate">{selectedCluster.code}</span>
              </div>
              <button
                type="button"
                onClick={() => setSelectedCluster(null)}
                className="text-[var(--bb-text-dim)] hover:text-[var(--bb-text-bright)]"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="p-4 space-y-4 text-xs">
              {/* Cluster Title Banner */}
              <div>
                <span className="text-[9px] text-[var(--bb-text-dim)] uppercase block mb-0.5">
                  {selectedCluster.region}
                </span>
                <h3 className="text-sm font-bold text-[var(--bb-text-bright)] leading-snug">
                  {selectedCluster.name}
                </h3>
              </div>

              {/* Cluster Telemetry Stats */}
              <div className="grid grid-cols-2 gap-2">
                <div className="p-2 bg-[var(--bb-bg-raised)] border border-[var(--bb-border-subtle)] rounded">
                  <span className="text-[9px] text-[var(--bb-text-muted)] block mb-0.5">SOVEREIGNTY SCORE</span>
                  <span className="text-xs font-bold text-[var(--bb-green)] bb-tabular">
                    {selectedCluster.sovereigntyIndex.toFixed(1)} / 10.0
                  </span>
                </div>

                <div className="p-2 bg-[var(--bb-bg-raised)] border border-[var(--bb-border-subtle)] rounded">
                  <span className="text-[9px] text-[var(--bb-text-muted)] block mb-0.5">EXPORT RISK</span>
                  <span
                    className={`text-xs font-bold ${
                      selectedCluster.exportControlRisk === 'LOW'
                        ? 'text-[var(--bb-green)]'
                        : selectedCluster.exportControlRisk === 'MEDIUM'
                        ? 'text-[var(--bb-amber)]'
                        : 'text-[var(--bb-red)]'
                    }`}
                  >
                    {selectedCluster.exportControlRisk}
                  </span>
                </div>

                <div className="p-2 bg-[var(--bb-bg-raised)] border border-[var(--bb-border-subtle)] rounded">
                  <span className="text-[9px] text-[var(--bb-text-muted)] block mb-0.5">H100 COMPUTE</span>
                  <span className="text-xs font-bold text-[var(--bb-text-bright)] bb-tabular">
                    {selectedCluster.h100Equiv.toLocaleString()} GPUs
                  </span>
                </div>

                <div className="p-2 bg-[var(--bb-bg-raised)] border border-[var(--bb-border-subtle)] rounded">
                  <span className="text-[9px] text-[var(--bb-text-muted)] block mb-0.5">SPOT PRICE</span>
                  <span className="text-xs font-bold text-[var(--bb-amber)] bb-tabular">
                    {selectedCluster.spotGpuHour > 0 ? `$${selectedCluster.spotGpuHour.toFixed(2)}/hr` : 'N/A'}
                  </span>
                </div>
              </div>

              {/* Energy & Power Efficiency */}
              <div className="p-2.5 bg-[var(--bb-bg-base)] border border-[var(--bb-border-subtle)] rounded space-y-1">
                <div className="flex items-center justify-between text-[10px]">
                  <span className="text-[var(--bb-text-muted)] flex items-center gap-1">
                    <Zap className="w-3 h-3 text-[var(--bb-amber)]" />
                    POWER CAPACITY:
                  </span>
                  <span className="text-[var(--bb-text-bright)] font-bold">{selectedCluster.powerMw} MW</span>
                </div>
                <div className="flex items-center justify-between text-[10px]">
                  <span className="text-[var(--bb-text-muted)]">PUE EFFICIENCY:</span>
                  <span className="text-[var(--bb-green)] font-bold">{selectedCluster.pueScore}</span>
                </div>
              </div>

              {/* Description */}
              <div>
                <span className="text-[9px] text-[var(--bb-text-muted)] uppercase block mb-1">
                  STRATEGIC ASSESSMENT:
                </span>
                <p className="text-[11px] text-[var(--bb-text-secondary)] leading-relaxed bg-[var(--bb-bg-raised)] p-2.5 rounded border border-[var(--bb-border-subtle)]">
                  {selectedCluster.description}
                </p>
              </div>

              {/* Key Providers */}
              <div>
                <span className="text-[9px] text-[var(--bb-text-muted)] uppercase block mb-1.5">
                  CERTIFIED PROVIDERS & ENCLAVES:
                </span>
                <div className="space-y-1">
                  {selectedCluster.keyProviders.map((prov, idx) => (
                    <div
                      key={idx}
                      className="p-1.5 bg-[var(--bb-bg-base)] border border-[var(--bb-border-subtle)] rounded text-[10px] text-[var(--bb-text-bright)] flex items-center gap-1.5"
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-[var(--bb-cyan)]" />
                      <span>{prov}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
