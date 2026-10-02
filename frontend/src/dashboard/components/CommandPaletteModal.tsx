import React, { useState, useEffect, useRef } from 'react';
import {
  Terminal,
  Search,
  Sparkles,
  Zap,
  Globe,
  GitFork,
  Sliders,
  TrendingUp,
  Lock,
  ShieldCheck,
  Radio,
  FileText,
  Activity,
  Palette,
  X,
  Keyboard,
  Check,
} from 'lucide-react';
import { PRESET_SCENARIOS, type PresetScenario } from '../data/presetScenarios';
import { terminalAudio } from '../utils/terminalAudio';

export type TerminalTheme = 'amber' | 'emerald' | 'cyan' | 'gold' | 'monochrome';

interface CommandPaletteModalProps {
  isOpen: boolean;
  onClose: () => void;
  onExecuteCommand: (cmd: string) => void;
  onSelectPreset: (preset: PresetScenario) => void;
  currentTheme: TerminalTheme;
  onSelectTheme: (theme: TerminalTheme) => void;
}

export const CommandPaletteModal: React.FC<CommandPaletteModalProps> = ({
  isOpen,
  onClose,
  onExecuteCommand,
  onSelectPreset,
  currentTheme,
  onSelectTheme,
}) => {
  const [search, setSearch] = useState('');
  const [activeCategory, setActiveCategory] = useState<'all' | 'commands' | 'presets' | 'themes' | 'hotkeys'>('all');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const commandsList = [
    { cmd: 'QUAD', name: '4-Quadrant Launchpad Grid', icon: Activity, key: 'F1', cat: 'commands' },
    { cmd: 'EVAL', name: 'Decision Execution Console', icon: Sliders, key: 'F2', cat: 'commands' },
    { cmd: 'TRAJ', name: '5-Year Trajectory & TCO Simulator', icon: TrendingUp, key: 'F3', cat: 'commands' },
    { cmd: 'LOCKIN', name: 'Lock-In Multi-Vector Matrix', icon: Lock, key: 'F4', cat: 'commands' },
    { cmd: 'AUDIT', name: 'Grounded Verification Inspector', icon: ShieldCheck, key: 'F5', cat: 'commands' },
    { cmd: 'FEED', name: 'Live Intelligence Feed', icon: Radio, key: 'F6', cat: 'commands' },
    { cmd: 'DOSSIER', name: 'Printable Executive Briefing Memo', icon: FileText, key: 'F7', cat: 'commands' },
    { cmd: 'BMAP', name: 'Global AI Infrastructure & Sovereignty Map', icon: Globe, key: 'F8', cat: 'commands' },
    { cmd: 'SPLC', name: 'Multi-Tier AI Supply Chain Graph', icon: GitFork, key: 'F9', cat: 'commands' },
    { cmd: 'CLEAR', name: 'Reset Active Decision Context', icon: Zap, key: 'ESC', cat: 'commands' },
  ];

  const themesList: { id: TerminalTheme; name: string; color: string; desc: string }[] = [
    { id: 'amber', name: 'Bloomberg Classic Amber', color: '#FF9E00', desc: 'Standard high-contrast financial amber glow' },
    { id: 'emerald', name: 'Matrix Emerald Green', color: '#00FF66', desc: 'Sovereign defense & military tactical HUD' },
    { id: 'cyan', name: 'Cyberpunk Cyan Blue', color: '#00E5FF', desc: 'High-tech intelligence & analytical terminal' },
    { id: 'gold', name: 'Institutional Sovereign Gold', color: '#FFD700', desc: 'Central bank & high-assurance institutional' },
    { id: 'monochrome', name: 'Obsidian Pure White', color: '#E2E8F0', desc: 'Minimalist low-fatigue monochromatic canvas' },
  ];

  const hotkeysList = [
    { key: 'F1 – F9', desc: 'Instant switch between workstation views & tools' },
    { key: 'Cmd / Ctrl + K', desc: 'Open Command Palette & Global Search' },
    { key: '/', desc: 'Quick jump to Terminal Command input' },
    { key: 'Esc', desc: 'Close modals & dismiss active overlays' },
    { key: 'Enter', desc: 'Execute command or submit decision' },
  ];

  const filteredCommands = commandsList.filter(
    (c) =>
      c.cmd.toLowerCase().includes(search.toLowerCase()) ||
      c.name.toLowerCase().includes(search.toLowerCase())
  );

  const filteredPresets = PRESET_SCENARIOS.filter(
    (p) =>
      p.code.toLowerCase().includes(search.toLowerCase()) ||
      p.title.toLowerCase().includes(search.toLowerCase()) ||
      p.brief.entity.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4 backdrop-blur-sm select-none font-mono">
      <div className="bg-[var(--bb-bg-surface)] border border-[var(--bb-border-bright)] rounded max-w-2xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Search Header */}
        <div className="p-3 bg-[var(--bb-bg-base)] border-b border-[var(--bb-border-subtle)] flex items-center gap-2">
          <Terminal className="w-4 h-4 text-[var(--bb-amber)]" />
          <input
            ref={inputRef}
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Type command, preset (e.g. DEF, FIN, BMAP), or theme..."
            className="flex-1 bg-transparent text-xs text-[var(--bb-text-bright)] placeholder-[var(--bb-text-dim)] outline-none"
          />
          <Search className="w-3.5 h-3.5 text-[var(--bb-text-dim)]" />
          <button
            type="button"
            onClick={onClose}
            className="text-[var(--bb-text-muted)] hover:text-[var(--bb-text-bright)] p-1 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Category Tabs */}
        <div className="flex items-center gap-1 px-3 py-1.5 bg-[var(--bb-bg-raised)] border-b border-[var(--bb-border-subtle)] text-[10px]">
          {(['all', 'commands', 'presets', 'themes', 'hotkeys'] as const).map((cat) => (
            <button
              key={cat}
              type="button"
              onClick={() => {
                terminalAudio.playBlip();
                setActiveCategory(cat);
              }}
              className={`px-2.5 py-1 rounded uppercase font-bold transition-all ${
                activeCategory === cat
                  ? 'bg-[var(--bb-amber-dim)] text-[var(--bb-amber)] border border-[var(--bb-amber)]'
                  : 'text-[var(--bb-text-muted)] hover:text-[var(--bb-text-primary)]'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Content Body */}
        <div className="p-3 overflow-y-auto bb-scroll flex-1 space-y-4 text-xs">
          {/* COMMANDS SECTION */}
          {(activeCategory === 'all' || activeCategory === 'commands') && filteredCommands.length > 0 && (
            <div>
              <span className="text-[10px] text-[var(--bb-text-muted)] uppercase tracking-wider block mb-1.5 flex items-center gap-1">
                <Zap className="w-3 h-3 text-[var(--bb-amber)]" /> WORKSTATION FUNCTIONS:
              </span>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-1.5">
                {filteredCommands.map((c) => {
                  const Icon = c.icon;
                  return (
                    <button
                      key={c.cmd}
                      type="button"
                      onClick={() => {
                        terminalAudio.playGoCommand();
                        onExecuteCommand(c.cmd);
                        onClose();
                      }}
                      className="p-2 bg-[var(--bb-bg-raised)] hover:bg-[var(--bb-bg-elevated)] border border-[var(--bb-border-subtle)] hover:border-[var(--bb-amber)] rounded text-left transition-all flex items-center justify-between group"
                    >
                      <div className="flex items-center gap-2 min-w-0">
                        <Icon className="w-3.5 h-3.5 text-[var(--bb-text-secondary)] group-hover:text-[var(--bb-amber)]" />
                        <div className="truncate">
                          <span className="font-bold text-[11px] text-[var(--bb-text-bright)] block">
                            {c.cmd} &lt;GO&gt;
                          </span>
                          <span className="text-[10px] text-[var(--bb-text-dim)] truncate block">
                            {c.name}
                          </span>
                        </div>
                      </div>
                      <span className="text-[9px] px-1.5 py-0.5 bg-[var(--bb-bg-base)] text-[var(--bb-amber)] border border-[var(--bb-border-subtle)] rounded font-bold">
                        {c.key}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* PRESETS SECTION */}
          {(activeCategory === 'all' || activeCategory === 'presets') && filteredPresets.length > 0 && (
            <div>
              <span className="text-[10px] text-[var(--bb-text-muted)] uppercase tracking-wider block mb-1.5 flex items-center gap-1">
                <Sparkles className="w-3 h-3 text-[var(--bb-cyan)]" /> INSTITUTIONAL PRESETS:
              </span>
              <div className="space-y-1.5">
                {filteredPresets.map((p) => (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => {
                      terminalAudio.playGoCommand();
                      onSelectPreset(p);
                      onClose();
                    }}
                    className="w-full p-2.5 bg-[var(--bb-bg-raised)] hover:bg-[var(--bb-bg-elevated)] border border-[var(--bb-border-subtle)] hover:border-[var(--bb-cyan)] rounded text-left transition-all flex items-center justify-between group"
                  >
                    <div className="min-w-0 pr-2">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] px-1.5 py-0.2 bg-[var(--bb-cyan-dim)] text-[var(--bb-cyan)] border border-[var(--bb-cyan)] rounded font-bold">
                          {p.code}
                        </span>
                        <span className="font-bold text-[11px] text-[var(--bb-text-bright)] truncate">
                          {p.title}
                        </span>
                      </div>
                      <span className="text-[10px] text-[var(--bb-text-secondary)] line-clamp-1 mt-0.5 block">
                        {p.brief.entity} — {p.brief.capability}
                      </span>
                    </div>
                    <span className="text-[9px] text-[var(--bb-text-dim)] uppercase flex-shrink-0">
                      LOAD &gt;
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* THEMES SECTION */}
          {(activeCategory === 'all' || activeCategory === 'themes') && (
            <div>
              <span className="text-[10px] text-[var(--bb-text-muted)] uppercase tracking-wider block mb-1.5 flex items-center gap-1">
                <Palette className="w-3 h-3 text-[var(--bb-purple)]" /> TERMINAL ACCENT PALETTES:
              </span>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-1.5">
                {themesList.map((t) => {
                  const isCurrent = currentTheme === t.id;
                  return (
                    <button
                      key={t.id}
                      type="button"
                      onClick={() => {
                        terminalAudio.playBlip();
                        onSelectTheme(t.id);
                      }}
                      className={`p-2 rounded border text-left flex items-center justify-between transition-all ${
                        isCurrent
                          ? 'bg-[var(--bb-bg-elevated)] border-[var(--bb-amber)]'
                          : 'bg-[var(--bb-bg-raised)] border-[var(--bb-border-subtle)] hover:border-[var(--bb-border-mid)]'
                      }`}
                    >
                      <div className="flex items-center gap-2 min-w-0">
                        <span
                          className="w-3.5 h-3.5 rounded-full border border-white/20 flex-shrink-0"
                          style={{ backgroundColor: t.color }}
                        />
                        <div className="truncate">
                          <span className="font-bold text-[11px] text-[var(--bb-text-bright)] block">
                            {t.name}
                          </span>
                          <span className="text-[9px] text-[var(--bb-text-dim)] block truncate">
                            {t.desc}
                          </span>
                        </div>
                      </div>
                      {isCurrent && <Check className="w-3.5 h-3.5 text-[var(--bb-green)] flex-shrink-0 ml-1" />}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* HOTKEYS CHEATSHEET */}
          {(activeCategory === 'all' || activeCategory === 'hotkeys') && (
            <div>
              <span className="text-[10px] text-[var(--bb-text-muted)] uppercase tracking-wider block mb-1.5 flex items-center gap-1">
                <Keyboard className="w-3 h-3 text-[var(--bb-green)]" /> KEYBOARD SHORTCUTS:
              </span>
              <div className="space-y-1 bg-[var(--bb-bg-base)] p-2.5 rounded border border-[var(--bb-border-subtle)]">
                {hotkeysList.map((h, idx) => (
                  <div key={idx} className="flex items-center justify-between py-1 text-[11px]">
                    <span className="font-bold text-[var(--bb-amber)]">{h.key}</span>
                    <span className="text-[var(--bb-text-secondary)]">{h.desc}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer info */}
        <div className="px-3 py-2 bg-[var(--bb-bg-base)] border-t border-[var(--bb-border-subtle)] flex items-center justify-between text-[10px] text-[var(--bb-text-dim)]">
          <span>NAVIGATION: [TAB / ARROWS] // EXECUTE: [ENTER]</span>
          <span>DISMISS: [ESC]</span>
        </div>
      </div>
    </div>
  );
};
