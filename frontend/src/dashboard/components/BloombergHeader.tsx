import React, { useState, useEffect, useRef } from 'react';
import {
  Terminal,
  Volume2,
  VolumeX,
  Radio,
  Search,
  Zap,
  TrendingUp,
  Lock,
  ShieldCheck,
  FileText,
  Sliders,
  Grid,
  Globe,
  GitFork,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { terminalAudio } from '../utils/terminalAudio';

export type ActiveWorkstationTab =
  | 'quadrant'
  | 'decision'
  | 'trajectory'
  | 'lockin'
  | 'audit'
  | 'feed'
  | 'dossier'
  | 'bmap'
  | 'splc';

interface BloombergHeaderProps {
  activeTab: ActiveWorkstationTab;
  onSelectTab: (tab: ActiveWorkstationTab) => void;
  onExecuteCommand: (cmd: string) => void;
  status: 'idle' | 'submitting' | 'polling' | 'completed' | 'failed';
  isLiveServerConnected: boolean;
  selectedPresetCode?: string;
}

const TICKER_ITEMS = [
  { symbol: 'LLAMA-3.3-70B', val: '$0.12/MTok', change: '+1.4%', up: true, tag: 'OPEN-W' },
  { symbol: 'GPT-4o-OMNI', val: '$2.50/MTok', change: '-0.8%', up: false, tag: 'API' },
  { symbol: 'CLAUDE-3.5-SONNET', val: '$3.00/MTok', change: '+0.0%', up: true, tag: 'API' },
  { symbol: 'H100-SXM5-SPOT', val: '$2.84/GPU-hr', change: '-4.2%', up: false, tag: 'COMPUTE' },
  { symbol: 'A100-80GB-SX', val: '$1.42/GPU-hr', change: '+0.5%', up: true, tag: 'COMPUTE' },
  { symbol: 'BIS-ENTITY-WATCH', val: '2,419 Entities', change: '+12 new', up: false, tag: 'REG' },
  { symbol: 'TITAN-CLOUD-LOCKIN', val: 'IDX 7.8/10', change: '+0.3', up: false, tag: 'RISK' },
  { symbol: 'AIR-GAP-SOVEREIGN', val: '99.98% SLA', change: '+0.01%', up: true, tag: 'SEC' },
  { symbol: 'SARVAM-2B-INDIC', val: 'Apache 2.0', change: 'VERIFIED', up: true, tag: 'MODEL' },
  { symbol: 'EU-AI-ACT-RISK-IDX', val: 'Tier-1 High', change: '+8.4%', up: false, tag: 'LEGAL' },
];

export const BloombergHeader: React.FC<BloombergHeaderProps> = ({
  activeTab,
  onSelectTab,
  onExecuteCommand,
  status,
  isLiveServerConnected,
  selectedPresetCode,
}) => {
  const [commandInput, setCommandInput] = useState('');
  const [timeUtc, setTimeUtc] = useState('');
  const [timeLocal, setTimeLocal] = useState('');
  const [isMuted, setIsMuted] = useState(terminalAudio.isMuted());
  const [suggestionsOpen, setSuggestionsOpen] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Clock updater
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeUtc(now.toUTCString().slice(17, 25) + ' UTC');
      setTimeLocal(now.toLocaleTimeString('en-US', { hour12: false }));
    };
    updateTime();
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, []);

  // Global hotkey listener for "/" or "Cmd+K" or F1-F9
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
        terminalAudio.playBlip();
      } else if (e.key === '/' && document.activeElement?.tagName !== 'INPUT' && document.activeElement?.tagName !== 'TEXTAREA') {
        e.preventDefault();
        inputRef.current?.focus();
        terminalAudio.playBlip();
      } else if (e.key === 'F1') {
        e.preventDefault();
        onSelectTab('quadrant');
        terminalAudio.playBlip();
      } else if (e.key === 'F2') {
        e.preventDefault();
        onSelectTab('decision');
        terminalAudio.playBlip();
      } else if (e.key === 'F3') {
        e.preventDefault();
        onSelectTab('trajectory');
        terminalAudio.playBlip();
      } else if (e.key === 'F4') {
        e.preventDefault();
        onSelectTab('lockin');
        terminalAudio.playBlip();
      } else if (e.key === 'F5') {
        e.preventDefault();
        onSelectTab('audit');
        terminalAudio.playBlip();
      } else if (e.key === 'F6') {
        e.preventDefault();
        onSelectTab('feed');
        terminalAudio.playBlip();
      } else if (e.key === 'F7') {
        e.preventDefault();
        onSelectTab('dossier');
        terminalAudio.playBlip();
      } else if (e.key === 'F8') {
        e.preventDefault();
        onSelectTab('bmap');
        terminalAudio.playBlip();
      } else if (e.key === 'F9') {
        e.preventDefault();
        onSelectTab('splc');
        terminalAudio.playBlip();
      } else if (e.key === 'Escape') {
        setSuggestionsOpen(false);
        inputRef.current?.blur();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onSelectTab]);

  const handleCommandSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const cleanCmd = commandInput.trim().toUpperCase();
    if (!cleanCmd) return;
    terminalAudio.playGoCommand();
    onExecuteCommand(cleanCmd);
    setCommandInput('');
    setSuggestionsOpen(false);
  };

  const handleToggleSound = () => {
    const nextMute = terminalAudio.toggleMute();
    setIsMuted(nextMute);
  };

  const quickCommands = [
    { cmd: 'BMAP', desc: 'Global AI Infrastructure & Sovereignty Map' },
    { cmd: 'SPLC', desc: 'Multi-Tier AI Supply Chain & Dependency Graph' },
    { cmd: 'EVAL', desc: 'Launch Decision Execution Console' },
    { cmd: 'QUAD', desc: 'Switch to 4-Quadrant Launchpad Grid' },
    { cmd: 'TRAJ', desc: '5-Year TCO & Lock-In Trajectory Simulator' },
    { cmd: 'LOCKIN', desc: 'Lock-In Multi-Vector Matrix Heatmap' },
    { cmd: 'AUDIT', desc: 'Grounded Verification Inspector & Citations' },
    { cmd: 'FEED', desc: 'Live Ingestion & Intelligence Stream' },
    { cmd: 'DOSSIER', desc: 'Printable Executive Briefing Memo' },
    { cmd: 'DEMO DEF', desc: 'Load Indian Army Signals SLM Case' },
    { cmd: 'DEMO FIN', desc: 'Load Tier-1 Investment Bank Case' },
    { cmd: 'DEMO MED', desc: 'Load Regional Healthcare AI Case' },
    { cmd: 'CLEAR', desc: 'Reset Active Decision Context' },
  ];

  const filteredCommands = commandInput
    ? quickCommands.filter((c) => c.cmd.includes(commandInput.toUpperCase()) || c.desc.toUpperCase().includes(commandInput.toUpperCase()))
    : quickCommands.slice(0, 6);

  return (
    <header className="bb-panel border-b border-[var(--bb-border-subtle)] bg-[var(--bb-bg-surface)] text-[var(--bb-text-primary)]">
      {/* Top Telemetry Strip */}
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-[var(--bb-border-subtle)] text-[11px] font-mono select-none">
        {/* Left: Brand & Status */}
        <div className="flex items-center gap-3">
          <Link
            to="/"
            className="flex items-center gap-1.5 text-[var(--bb-amber)] hover:text-[var(--bb-amber-bright)] transition-colors font-bold tracking-wider"
          >
            <Terminal className="w-3.5 h-3.5" />
            <span>HELIOS_TERMINAL</span>
            <span className="text-[9px] px-1 py-0.2 bg-[var(--bb-amber-dim)] border border-[var(--bb-amber)] text-[var(--bb-amber)] rounded">
              v2.4 PRO
            </span>
          </Link>

          <span className="text-[var(--bb-border-mid)]">|</span>

          {/* Connection Status */}
          <div className="flex items-center gap-1.5">
            <span
              className={`w-2 h-2 rounded-full ${
                isLiveServerConnected ? 'bg-[var(--bb-green)] bb-live-indicator' : 'bg-[var(--bb-amber)]'
              }`}
            />
            <span className="text-[var(--bb-text-secondary)] text-[10px]">
              {isLiveServerConnected ? 'HOST: 127.0.0.1:8000 [ONLINE]' : 'STANDALONE / CLIENT MODE'}
            </span>
          </div>

          {selectedPresetCode && (
            <span className="text-[10px] px-1.5 py-0.5 bg-[var(--bb-cyan-dim)] text-[var(--bb-cyan)] border border-[var(--bb-cyan)] rounded">
              ACTIVE: {selectedPresetCode}
            </span>
          )}
        </div>

        {/* Right: Pipeline State, Sound Toggle, Clocks */}
        <div className="flex items-center gap-3">
          {/* Pipeline Badge */}
          <div className="flex items-center gap-1.5">
            <span className="text-[10px] text-[var(--bb-text-muted)]">PIPELINE:</span>
            {status === 'idle' && <span className="bb-badge bb-badge-dim">READY</span>}
            {status === 'submitting' && <span className="bb-badge bb-badge-amber">SUBMITTING...</span>}
            {status === 'polling' && <span className="bb-badge bb-badge-amber bb-live-indicator">SYNTHESIZING (6 AGENTS)</span>}
            {status === 'completed' && <span className="bb-badge bb-badge-green">VERIFIED VERDICT</span>}
            {status === 'failed' && <span className="bb-badge bb-badge-red">EXECUTION FAILED</span>}
          </div>

          <span className="text-[var(--bb-border-mid)]">|</span>

          {/* Sound Toggle */}
          <button
            type="button"
            onClick={handleToggleSound}
            className="flex items-center gap-1 text-[10px] text-[var(--bb-text-secondary)] hover:text-[var(--bb-amber)] transition-colors"
            title={isMuted ? 'Unmute Terminal Audio' : 'Mute Terminal Audio'}
          >
            {isMuted ? <VolumeX className="w-3.5 h-3.5" /> : <Volume2 className="w-3.5 h-3.5 text-[var(--bb-green)]" />}
            <span>{isMuted ? 'MUTE' : 'AUDIO ON'}</span>
          </button>

          <span className="text-[var(--bb-border-mid)]">|</span>

          {/* Clocks */}
          <div className="flex items-center gap-2 text-[10px] text-[var(--bb-text-secondary)] bb-tabular">
            <span>{timeUtc}</span>
            <span className="text-[var(--bb-text-muted)]">({timeLocal} LOC)</span>
          </div>
        </div>
      </div>

      {/* Main Command Line Bar (<GO> Input Bar) */}
      <div className="px-3 py-2 flex items-center gap-2 border-b border-[var(--bb-border-subtle)] bg-[var(--bb-bg-base)]">
        <div className="flex items-center gap-1.5 text-[var(--bb-amber)] font-bold text-xs">
          <Zap className="w-3.5 h-3.5" />
          <span>COMMAND:</span>
        </div>

        {/* Input box with autocomplete */}
        <div className="relative flex-1">
          <form onSubmit={handleCommandSubmit} className="flex items-center gap-2">
            <div className="relative flex-1">
              <input
                ref={inputRef}
                type="text"
                value={commandInput}
                onChange={(e) => {
                  setCommandInput(e.target.value);
                  setSuggestionsOpen(true);
                }}
                onFocus={() => {
                  setSuggestionsOpen(true);
                  terminalAudio.playBlip();
                }}
                placeholder="Type function or command (e.g. EVAL, TRAJ, LOCKIN, DEMO DEF, HELP)... Press / or Cmd+K"
                className="w-full bg-[var(--bb-bg-input)] border border-[var(--bb-border-mid)] focus:border-[var(--bb-amber)] text-[var(--bb-amber-bright)] placeholder-[var(--bb-text-dim)] px-3 py-1.5 text-xs font-mono rounded outline-none bb-tabular"
              />
              <Search className="w-3.5 h-3.5 absolute right-2.5 top-2.5 text-[var(--bb-text-dim)]" />
            </div>

            {/* Bloomberg <GO> Button */}
            <button
              type="submit"
              className="bb-button bb-button-go px-4 py-1.5 text-xs font-mono font-bold tracking-wider"
            >
              EXEC &lt;GO&gt;
            </button>
          </form>

          {/* Autocomplete Dropdown */}
          {suggestionsOpen && (
            <div
              className="absolute left-0 right-0 top-full mt-1 bg-[var(--bb-bg-raised)] border border-[var(--bb-border-bright)] shadow-2xl z-50 rounded overflow-hidden max-h-64 bb-scroll"
              onMouseLeave={() => setSuggestionsOpen(false)}
            >
              <div className="px-3 py-1.5 bg-[var(--bb-bg-surface)] border-b border-[var(--bb-border-subtle)] text-[10px] text-[var(--bb-text-muted)] flex justify-between font-mono">
                <span>BLOOMBERG FUNCTION SUGGESTIONS</span>
                <span>ESC to close</span>
              </div>
              <div className="divide-y divide-[var(--bb-border-subtle)]">
                {filteredCommands.map((item) => (
                  <button
                    key={item.cmd}
                    type="button"
                    onClick={() => {
                      terminalAudio.playGoCommand();
                      onExecuteCommand(item.cmd);
                      setCommandInput('');
                      setSuggestionsOpen(false);
                    }}
                    className="w-full text-left px-3 py-2 hover:bg-[var(--bb-bg-elevated)] flex items-center justify-between text-xs font-mono transition-colors"
                  >
                    <span className="text-[var(--bb-amber)] font-bold">{item.cmd} &lt;GO&gt;</span>
                    <span className="text-[var(--bb-text-secondary)] text-[11px]">{item.desc}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Function Key Ribbon (F1-F7 navigation) */}
      <div className="flex items-center gap-1 px-3 py-1.5 bg-[var(--bb-bg-surface)] border-b border-[var(--bb-border-subtle)] overflow-x-auto bb-scroll text-[11px] font-mono">
        <span className="text-[10px] text-[var(--bb-text-muted)] mr-1 uppercase">FUNCTIONS:</span>

        <button
          type="button"
          onClick={() => {
            terminalAudio.playBlip();
            onSelectTab('quadrant');
          }}
          className={`px-2.5 py-1 rounded flex items-center gap-1.5 border transition-all ${
            activeTab === 'quadrant'
              ? 'bg-[var(--bb-amber-dim)] border-[var(--bb-amber)] text-[var(--bb-amber)] font-bold'
              : 'bg-[var(--bb-bg-raised)] border-[var(--bb-border-subtle)] text-[var(--bb-text-secondary)] hover:text-[var(--bb-text-primary)]'
          }`}
        >
          <Grid className="w-3 h-3" />
          <span>[F1] QUADRANT GRID</span>
        </button>

        <button
          type="button"
          onClick={() => {
            terminalAudio.playBlip();
            onSelectTab('decision');
          }}
          className={`px-2.5 py-1 rounded flex items-center gap-1.5 border transition-all ${
            activeTab === 'decision'
              ? 'bg-[var(--bb-amber-dim)] border-[var(--bb-amber)] text-[var(--bb-amber)] font-bold'
              : 'bg-[var(--bb-bg-raised)] border-[var(--bb-border-subtle)] text-[var(--bb-text-secondary)] hover:text-[var(--bb-text-primary)]'
          }`}
        >
          <Sliders className="w-3 h-3" />
          <span>[F2] DECISION EXEC</span>
        </button>

        <button
          type="button"
          onClick={() => {
            terminalAudio.playBlip();
            onSelectTab('trajectory');
          }}
          className={`px-2.5 py-1 rounded flex items-center gap-1.5 border transition-all ${
            activeTab === 'trajectory'
              ? 'bg-[var(--bb-cyan-dim)] border-[var(--bb-cyan)] text-[var(--bb-cyan)] font-bold'
              : 'bg-[var(--bb-bg-raised)] border-[var(--bb-border-subtle)] text-[var(--bb-text-secondary)] hover:text-[var(--bb-text-primary)]'
          }`}
        >
          <TrendingUp className="w-3 h-3" />
          <span>[F3] TRAJECTORY SIM</span>
        </button>

        <button
          type="button"
          onClick={() => {
            terminalAudio.playBlip();
            onSelectTab('lockin');
          }}
          className={`px-2.5 py-1 rounded flex items-center gap-1.5 border transition-all ${
            activeTab === 'lockin'
              ? 'bg-[var(--bb-red-dim)] border-[var(--bb-red)] text-[var(--bb-red)] font-bold'
              : 'bg-[var(--bb-bg-raised)] border-[var(--bb-border-subtle)] text-[var(--bb-text-secondary)] hover:text-[var(--bb-text-primary)]'
          }`}
        >
          <Lock className="w-3 h-3" />
          <span>[F4] LOCK-IN MATRIX</span>
        </button>

        <button
          type="button"
          onClick={() => {
            terminalAudio.playBlip();
            onSelectTab('audit');
          }}
          className={`px-2.5 py-1 rounded flex items-center gap-1.5 border transition-all ${
            activeTab === 'audit'
              ? 'bg-[var(--bb-green-dim)] border-[var(--bb-green)] text-[var(--bb-green)] font-bold'
              : 'bg-[var(--bb-bg-raised)] border-[var(--bb-border-subtle)] text-[var(--bb-text-secondary)] hover:text-[var(--bb-text-primary)]'
          }`}
        >
          <ShieldCheck className="w-3 h-3" />
          <span>[F5] AUDIT INSPECTOR</span>
        </button>

        <button
          type="button"
          onClick={() => {
            terminalAudio.playBlip();
            onSelectTab('feed');
          }}
          className={`px-2.5 py-1 rounded flex items-center gap-1.5 border transition-all ${
            activeTab === 'feed'
              ? 'bg-[var(--bb-purple-dim)] border-[var(--bb-purple)] text-[var(--bb-purple)] font-bold'
              : 'bg-[var(--bb-bg-raised)] border-[var(--bb-border-subtle)] text-[var(--bb-text-secondary)] hover:text-[var(--bb-text-primary)]'
          }`}
        >
          <Radio className="w-3 h-3" />
          <span>[F6] INTEL FEED</span>
        </button>

        <button
          type="button"
          onClick={() => {
            terminalAudio.playBlip();
            onSelectTab('dossier');
          }}
          className={`px-2.5 py-1 rounded flex items-center gap-1.5 border transition-all ${
            activeTab === 'dossier'
              ? 'bg-[var(--bb-amber-dim)] border-[var(--bb-amber)] text-[var(--bb-amber)] font-bold'
              : 'bg-[var(--bb-bg-raised)] border-[var(--bb-border-subtle)] text-[var(--bb-text-secondary)] hover:text-[var(--bb-text-primary)]'
          }`}
        >
          <FileText className="w-3 h-3" />
          <span>[F7] DOSSIER</span>
        </button>

        <button
          type="button"
          onClick={() => {
            terminalAudio.playBlip();
            onSelectTab('bmap');
          }}
          className={`px-2.5 py-1 rounded flex items-center gap-1.5 border transition-all ${
            activeTab === 'bmap'
              ? 'bg-[var(--bb-cyan-dim)] border-[var(--bb-cyan)] text-[var(--bb-cyan)] font-bold'
              : 'bg-[var(--bb-bg-raised)] border-[var(--bb-border-subtle)] text-[var(--bb-text-secondary)] hover:text-[var(--bb-text-primary)]'
          }`}
        >
          <Globe className="w-3 h-3" />
          <span>[F8] BMAP INFRA</span>
        </button>

        <button
          type="button"
          onClick={() => {
            terminalAudio.playBlip();
            onSelectTab('splc');
          }}
          className={`px-2.5 py-1 rounded flex items-center gap-1.5 border transition-all ${
            activeTab === 'splc'
              ? 'bg-[var(--bb-amber-dim)] border-[var(--bb-amber)] text-[var(--bb-amber)] font-bold'
              : 'bg-[var(--bb-bg-raised)] border-[var(--bb-border-subtle)] text-[var(--bb-text-secondary)] hover:text-[var(--bb-text-primary)]'
          }`}
        >
          <GitFork className="w-3 h-3" />
          <span>[F9] SPLC CHAIN</span>
        </button>
      </div>

      {/* Live AI Market Ticker Tape */}
      <div className="relative overflow-hidden bg-[var(--bb-bg-base)] border-t border-[var(--bb-border-subtle)] py-1 select-none">
        <div className="bb-ticker-track text-[10px] font-mono flex items-center gap-6">
          {[...TICKER_ITEMS, ...TICKER_ITEMS].map((item, idx) => (
            <div key={idx} className="flex items-center gap-1.5 whitespace-nowrap">
              <span className="text-[var(--bb-text-dim)] font-bold">[{item.tag}]</span>
              <span className="text-[var(--bb-text-primary)] font-bold">{item.symbol}</span>
              <span className="text-[var(--bb-text-secondary)] bb-tabular">{item.val}</span>
              <span className={item.up ? 'text-[var(--bb-green)]' : 'text-[var(--bb-red)]'}>
                {item.change}
              </span>
              <span className="text-[var(--bb-border-mid)] ml-2">/</span>
            </div>
          ))}
        </div>
      </div>
    </header>
  );
};
