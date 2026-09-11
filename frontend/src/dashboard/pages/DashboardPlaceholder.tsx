import React from 'react';
import { SiteHeader } from '../../shared/SiteHeader';
import { Terminal, Shield, Cpu, Network, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';

export const DashboardPlaceholder: React.FC = () => {
  return (
    <div className="theme-dashboard min-h-screen bg-[#0E1013] text-[#E6EDF3] flex flex-col justify-between font-sans selection:bg-site-accent selection:text-black">
      <SiteHeader variant="dark-collapsed" />

      <main className="max-w-4xl mx-auto px-6 py-20 flex-1 flex flex-col justify-center">
        <div className="border border-[#23272F] bg-[#14171C] rounded-site p-8 max-w-2xl mx-auto shadow-2xl relative overflow-hidden">
          {/* Subtle top indicator bar */}
          <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-site-accent to-transparent opacity-80" />

          <div className="flex items-center gap-2 mb-4">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-mono uppercase tracking-widest bg-[#1A1F26] border border-[#2D333B] text-site-accent rounded">
              <Terminal className="w-3 h-3" />
              <span>DASHBOARD_GATE // PHASE_9_TARGET</span>
            </span>
          </div>

          <h1 className="text-3xl font-mono font-bold text-[#F0F6FC] mb-3 tracking-tight">
            Helios Strategic Engine Console
          </h1>

          <p className="text-sm font-sans text-[#8B949E] leading-relaxed mb-6">
            You have crossed into the sovereign decision terminal workspace. The light marketing site header has successfully collapsed into the dark command header.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-8">
            <div className="p-3 bg-[#0E1013] border border-[#23272F] rounded text-left">
              <div className="flex items-center gap-1.5 text-xs font-mono text-[#8B949E] mb-1">
                <Cpu className="w-3.5 h-3.5 text-site-accent" />
                <span>PIPELINE</span>
              </div>
              <p className="text-xs text-[#C9D1D9]">6 Verified Stages Ready</p>
            </div>

            <div className="p-3 bg-[#0E1013] border border-[#23272F] rounded text-left">
              <div className="flex items-center gap-1.5 text-xs font-mono text-[#8B949E] mb-1">
                <Network className="w-3.5 h-3.5 text-site-accent" />
                <span>RECALIBRATION</span>
              </div>
              <p className="text-xs text-[#C9D1D9]">Bounded LoopGuard</p>
            </div>

            <div className="p-3 bg-[#0E1013] border border-[#23272F] rounded text-left">
              <div className="flex items-center gap-1.5 text-xs font-mono text-[#8B949E] mb-1">
                <Shield className="w-3.5 h-3.5 text-site-accent" />
                <span>SOVEREIGNTY</span>
              </div>
              <p className="text-xs text-[#C9D1D9]">Lock-in Risk Audit</p>
            </div>
          </div>

          <div className="flex items-center justify-between pt-4 border-t border-[#23272F]">
            <span className="text-xs font-mono text-[#7D8590]">
              Phase 9 will connect live multi-pane terminal UI
            </span>

            <Link
              to="/"
              className="inline-flex items-center gap-1.5 text-xs font-mono text-site-accent hover:text-[#56D4DD] transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Return to Overview</span>
            </Link>
          </div>
        </div>
      </main>

      <footer className="border-t border-[#23272F] py-4 text-center text-xs font-mono text-[#7D8590]">
        HELIOS_TERMINAL // AIR-GAPPED & DUAL-THEME ENGINE
      </footer>
    </div>
  );
};