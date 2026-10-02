import React, { useState } from 'react';
import {
  TrendingUp,
  ChevronRight,
  Sliders,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  LineChart,
  Line,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import type { CrossPathComparison } from '../api';
import { terminalAudio } from '../utils/terminalAudio';

interface TrajectoryDataPoint {
  year: string;
  buildTco: number;
  buyTco: number;
  outsourceTco: number;
  buildLockIn: number;
  buyLockIn: number;
  outsourceLockIn: number;
}

interface TrajectoryChartPanelProps {
  comparison?: CrossPathComparison | null;
  trajectoryData?: TrajectoryDataPoint[];
}

const DEFAULT_TRAJECTORY: TrajectoryDataPoint[] = [
  { year: 'Y0 (Deploy)', buildTco: 450, buyTco: 200, outsourceTco: 280, buildLockIn: 1.5, buyLockIn: 4.8, outsourceLockIn: 6.2 },
  { year: 'Y1', buildTco: 540, buyTco: 360, outsourceTco: 460, buildLockIn: 1.8, buyLockIn: 5.9, outsourceLockIn: 7.1 },
  { year: 'Y2', buildTco: 610, buyTco: 550, outsourceTco: 690, buildLockIn: 2.1, buyLockIn: 6.8, outsourceLockIn: 8.0 },
  { year: 'Y3', buildTco: 670, buyTco: 790, outsourceTco: 980, buildLockIn: 2.4, buyLockIn: 7.8, outsourceLockIn: 8.9 },
  { year: 'Y4', buildTco: 720, buyTco: 1060, outsourceTco: 1310, buildLockIn: 2.5, buyLockIn: 8.5, outsourceLockIn: 9.4 },
  { year: 'Y5 (EOL)', buildTco: 760, buyTco: 1380, outsourceTco: 1720, buildLockIn: 2.6, buyLockIn: 9.1, outsourceLockIn: 9.8 },
];

const RADAR_DATA = [
  { subject: 'Data Sovereignty', build: 9.5, buy: 4.5, outsource: 2.0 },
  { subject: 'Model Portability', build: 9.0, buy: 3.5, outsource: 1.5 },
  { subject: 'Air-Gap Feasibility', build: 9.8, buy: 2.0, outsource: 1.0 },
  { subject: 'Predictable TCO', build: 8.5, buy: 5.0, outsource: 3.0 },
  { subject: 'Talent Autonomy', build: 5.5, buy: 8.0, outsource: 9.0 },
  { subject: 'Sanction Immunity', build: 9.2, buy: 3.0, outsource: 2.5 },
];

export const TrajectoryChartPanel: React.FC<TrajectoryChartPanelProps> = ({
  comparison,
  trajectoryData = DEFAULT_TRAJECTORY,
}) => {
  const [metricMode, setMetricMode] = useState<'TCO' | 'LOCKIN' | 'RADAR'>('TCO');
  const [volumeScale, setVolumeScale] = useState<number>(1.0);

  const handleMetricToggle = (mode: 'TCO' | 'LOCKIN' | 'RADAR') => {
    terminalAudio.playBlip();
    setMetricMode(mode);
  };

  // Dynamically scale trajectory data based on simulated query volume
  const scaledData = trajectoryData.map((d, idx) => {
    if (idx === 0) return d;
    return {
      ...d,
      buildTco: Math.round(d.buildTco + (volumeScale - 1) * 60 * idx),
      buyTco: Math.round(d.buyTco * volumeScale),
      outsourceTco: Math.round(d.outsourceTco * (volumeScale * 1.25)),
    };
  });

  return (
    <div className="flex flex-col h-full bg-[var(--bb-bg-surface)] text-[var(--bb-text-primary)]">
      {/* Panel Header */}
      <div className="bb-panel-header">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-3.5 h-3.5 text-[var(--bb-cyan)]" />
          <span>5-YEAR SOURCING TRAJECTORY & TCO SIMULATOR</span>
          <span className="text-[10px] text-[var(--bb-text-muted)]">[FUNCTION 03]</span>
        </div>

        {/* Metric Mode Switcher */}
        <div className="flex items-center gap-1 bg-[var(--bb-bg-base)] p-0.5 rounded border border-[var(--bb-border-subtle)]">
          <button
            type="button"
            onClick={() => handleMetricToggle('TCO')}
            className={`px-2 py-0.5 text-[9px] font-bold rounded ${
              metricMode === 'TCO'
                ? 'bg-[var(--bb-amber)] text-black'
                : 'text-[var(--bb-text-muted)] hover:text-[var(--bb-text-primary)]'
            }`}
          >
            TCO ($k)
          </button>
          <button
            type="button"
            onClick={() => handleMetricToggle('LOCKIN')}
            className={`px-2 py-0.5 text-[9px] font-bold rounded ${
              metricMode === 'LOCKIN'
                ? 'bg-[var(--bb-cyan)] text-black'
                : 'text-[var(--bb-text-muted)] hover:text-[var(--bb-text-primary)]'
            }`}
          >
            LOCK-IN (1-10)
          </button>
          <button
            type="button"
            onClick={() => handleMetricToggle('RADAR')}
            className={`px-2 py-0.5 text-[9px] font-bold rounded ${
              metricMode === 'RADAR'
                ? 'bg-[var(--bb-green)] text-black'
                : 'text-[var(--bb-text-muted)] hover:text-[var(--bb-text-primary)]'
            }`}
          >
            RADAR PROFILE
          </button>
        </div>
      </div>

      <div className="p-3 space-y-3 overflow-y-auto bb-scroll flex-1 text-xs font-mono">
        {/* Interactive Volume Scaling Simulator Bar */}
        {metricMode === 'TCO' && (
          <div className="flex items-center justify-between p-2 bg-[var(--bb-bg-raised)] border border-[var(--bb-border-subtle)] rounded text-[10px]">
            <div className="flex items-center gap-2">
              <Sliders className="w-3.5 h-3.5 text-[var(--bb-amber)]" />
              <span className="text-[var(--bb-text-secondary)] font-bold">
                SIMULATE AI QUERY SCALE:
              </span>
              <span className="text-[var(--bb-amber)] font-bold">{volumeScale.toFixed(1)}x LOAD</span>
            </div>
            <div className="flex items-center gap-1.5">
              {[1.0, 1.5, 2.5, 5.0].map((scale) => (
                <button
                  key={scale}
                  type="button"
                  onClick={() => {
                    terminalAudio.playBlip();
                    setVolumeScale(scale);
                  }}
                  className={`px-2 py-0.5 text-[9px] font-bold rounded border ${
                    volumeScale === scale
                      ? 'bg-[var(--bb-amber)] text-black border-[var(--bb-amber)]'
                      : 'bg-[var(--bb-bg-surface)] text-[var(--bb-text-muted)] border-[var(--bb-border-subtle)] hover:text-[var(--bb-text-primary)]'
                  }`}
                >
                  {scale.toFixed(1)}x
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Interactive Chart Container */}
        <div className="h-56 w-full bg-[var(--bb-bg-base)] p-2 rounded border border-[var(--bb-border-subtle)] relative">
          <ResponsiveContainer width="100%" height="100%">
            {metricMode === 'TCO' ? (
              <AreaChart data={scaledData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                <defs>
                  <linearGradient id="buildGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00FF66" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#00FF66" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="buyGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#FF9E00" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#FF9E00" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="outsourceGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#FF3366" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#FF3366" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="2 2" stroke="#1F2937" vertical={false} />
                <XAxis dataKey="year" stroke="#64748B" tick={{ fontSize: 10 }} tickLine={false} />
                <YAxis stroke="#64748B" tick={{ fontSize: 10 }} tickLine={false} unit="k" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0F131A',
                    borderColor: '#374151',
                    borderRadius: '4px',
                    fontSize: '11px',
                    fontFamily: 'monospace',
                  }}
                  formatter={(val: any) => [`$${val ?? 0}k USD`, '']}
                />
                <Legend
                  wrapperStyle={{ fontSize: '10px', paddingTop: '4px' }}
                  iconSize={8}
                />
                <Area
                  type="monotone"
                  dataKey="buildTco"
                  name="Build (Self-Hosted Open Weights)"
                  stroke="#00FF66"
                  fillOpacity={1}
                  fill="url(#buildGrad)"
                  strokeWidth={2}
                />
                <Area
                  type="monotone"
                  dataKey="buyTco"
                  name="Buy (Sovereign Cloud API)"
                  stroke="#FF9E00"
                  fillOpacity={1}
                  fill="url(#buyGrad)"
                  strokeWidth={2}
                />
                <Area
                  type="monotone"
                  dataKey="outsourceTco"
                  name="Outsource (Turnkey SaaS)"
                  stroke="#FF3366"
                  fillOpacity={1}
                  fill="url(#outsourceGrad)"
                  strokeWidth={2}
                />
              </AreaChart>
            ) : metricMode === 'LOCKIN' ? (
              <LineChart data={trajectoryData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                <CartesianGrid strokeDasharray="2 2" stroke="#1F2937" vertical={false} />
                <XAxis dataKey="year" stroke="#64748B" tick={{ fontSize: 10 }} tickLine={false} />
                <YAxis stroke="#64748B" tick={{ fontSize: 10 }} tickLine={false} domain={[0, 10]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0F131A',
                    borderColor: '#374151',
                    borderRadius: '4px',
                    fontSize: '11px',
                    fontFamily: 'monospace',
                  }}
                  formatter={(val: any) => [`${val ?? 0}/10.0`, 'Lock-In Severity']}
                />
                <Legend
                  wrapperStyle={{ fontSize: '10px', paddingTop: '4px' }}
                  iconSize={8}
                />
                <Line
                  type="monotone"
                  dataKey="buildLockIn"
                  name="Build (Self-Hosted)"
                  stroke="#00FF66"
                  strokeWidth={2.5}
                  dot={{ r: 3 }}
                />
                <Line
                  type="monotone"
                  dataKey="buyLockIn"
                  name="Buy (Cloud API)"
                  stroke="#FF9E00"
                  strokeWidth={2.5}
                  dot={{ r: 3 }}
                />
                <Line
                  type="monotone"
                  dataKey="outsourceLockIn"
                  name="Outsource (SaaS)"
                  stroke="#FF3366"
                  strokeWidth={2.5}
                  dot={{ r: 3 }}
                />
              </LineChart>
            ) : (
              <RadarChart data={RADAR_DATA} margin={{ top: 10, right: 20, left: 20, bottom: 10 }}>
                <PolarGrid stroke="#252F42" />
                <PolarAngleAxis dataKey="subject" stroke="#94A3B8" tick={{ fontSize: 9 }} />
                <PolarRadiusAxis angle={30} domain={[0, 10]} stroke="#475569" tick={{ fontSize: 8 }} />
                <Radar name="Build (Self-Hosted)" dataKey="build" stroke="#00FF66" fill="#00FF66" fillOpacity={0.3} />
                <Radar name="Buy (Cloud API)" dataKey="buy" stroke="#FF9E00" fill="#FF9E00" fillOpacity={0.2} />
                <Radar name="Outsource (SaaS)" dataKey="outsource" stroke="#FF3366" fill="#FF3366" fillOpacity={0.2} />
                <Legend wrapperStyle={{ fontSize: '10px' }} iconSize={8} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0F131A',
                    borderColor: '#374151',
                    borderRadius: '4px',
                    fontSize: '11px',
                    fontFamily: 'monospace',
                  }}
                />
              </RadarChart>
            )}
          </ResponsiveContainer>
        </div>

        {/* Cross Path Comparison Breakdown */}
        {comparison && (
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] text-[var(--bb-text-muted)] uppercase tracking-wider">
                CROSS-PATH METRICS BREAKDOWN ({comparison.path_comparisons.length} PATHS)
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
              {comparison.path_comparisons.map((path, idx) => {
                const isLow = path.max_severity_score <= 3.5;
                const isHigh = path.max_severity_score >= 7.0;

                return (
                  <div
                    key={idx}
                    className="p-2.5 bg-[var(--bb-bg-raised)] border border-[var(--bb-border-subtle)] rounded flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-bold text-[10px] text-[var(--bb-text-bright)] truncate pr-1">
                          {path.scenario_name}
                        </span>
                        <span
                          className={`text-[9px] px-1.5 py-0.5 rounded font-bold ${
                            isLow
                              ? 'bg-[var(--bb-green-dim)] text-[var(--bb-green)] border border-[var(--bb-green)]'
                              : isHigh
                              ? 'bg-[var(--bb-red-dim)] text-[var(--bb-red)] border border-[var(--bb-red)]'
                              : 'bg-[var(--bb-amber-dim)] text-[var(--bb-amber)] border border-[var(--bb-amber)]'
                          }`}
                        >
                          LOCKIN {path.max_severity_score.toFixed(1)}/10
                        </span>
                      </div>
                      <p className="text-[10px] text-[var(--bb-text-secondary)] line-clamp-2 leading-relaxed mb-2">
                        {path.path_summary}
                      </p>
                    </div>

                    <div className="border-t border-[var(--bb-border-subtle)] pt-1.5 space-y-1">
                      {path.key_tradeoffs.slice(0, 2).map((tradeoff, tIdx) => (
                        <div
                          key={tIdx}
                          className="flex items-center gap-1 text-[9px] text-[var(--bb-text-muted)]"
                        >
                          <ChevronRight className="w-2.5 h-2.5 text-[var(--bb-amber)]" />
                          <span className="truncate">{tradeoff}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
