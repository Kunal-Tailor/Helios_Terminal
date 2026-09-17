import React, { useState, useEffect } from 'react';
import {
  Radio,
} from 'lucide-react';

interface FeedItem {
  id: string;
  time: string;
  source: 'BIS_ENTITY' | 'HF_HUB' | 'WEB_SEARCH' | 'TENSOR_RT' | 'VERIFIER';
  tag: string;
  message: string;
  meta?: string;
}

const DEFAULT_FEED: FeedItem[] = [
  {
    id: 'f-1',
    time: '15:38:02.114',
    source: 'BIS_ENTITY',
    tag: 'REGULATORY',
    message: 'Queried US Dept of Commerce EAR Entity Watchlist for targeted vendor subsidiaries.',
    meta: 'MATCH_COUNT: 0 (CLEAR)',
  },
  {
    id: 'f-2',
    time: '15:38:02.482',
    source: 'HF_HUB',
    tag: 'MODEL_REGISTRY',
    message: 'Retrieved Hugging Face model card & commit sha for "sarvamai/sarvam-2b-v0.5".',
    meta: 'LICENSE: Apache 2.0 | WEIGHTS: 4.8GB SafeTensors',
  },
  {
    id: 'f-3',
    time: '15:38:03.018',
    source: 'WEB_SEARCH',
    tag: 'MARKET_INTEL',
    message: 'Ingested 18 technical reports regarding defense air-gapped SLM deployment.',
    meta: 'HTTP_STATUS: 200 OK | SNIPPETS: 42',
  },
  {
    id: 'f-4',
    time: '15:38:03.621',
    source: 'TENSOR_RT',
    tag: 'COMPUTE_STACK',
    message: 'Benchmarked FP16 vs AWQ 4-bit edge memory bandwidth on Jetson AGX Orin.',
    meta: 'LATENCY: 14.2ms/tok | VRAM: 3.8GB',
  },
  {
    id: 'f-5',
    time: '15:38:04.102',
    source: 'VERIFIER',
    tag: 'GATE_AUDIT',
    message: 'Stage 01 -> 02 verification check passed with 0.98 grounded confidence rating.',
    meta: 'GROUNDINGS: 14/14 CITED',
  },
];

export const IntelFeedPanel: React.FC = () => {
  const [feedItems, setFeedItems] = useState<FeedItem[]>(DEFAULT_FEED);
  const [isStreaming, setIsStreaming] = useState(true);

  useEffect(() => {
    if (!isStreaming) return;
    const interval = setInterval(() => {
      const now = new Date();
      const timeStr = now.toTimeString().split(' ')[0] + '.' + String(now.getMilliseconds()).padStart(3, '0');
      const sources: FeedItem['source'][] = ['BIS_ENTITY', 'HF_HUB', 'WEB_SEARCH', 'TENSOR_RT', 'VERIFIER'];
      const pickSource = sources[Math.floor(Math.random() * sources.length)];
      
      const newEntry: FeedItem = {
        id: 'f-' + Date.now(),
        time: timeStr,
        source: pickSource,
        tag: 'LIVE_STREAM',
        message:
          pickSource === 'HF_HUB'
            ? 'Monitored model repository updates & GGUF quantization branches.'
            : pickSource === 'BIS_ENTITY'
            ? 'Refreshed export control compliance status against Bureau of Industry and Security.'
            : pickSource === 'WEB_SEARCH'
            ? 'Scraped sovereign cloud token pricing updates and latency telemetry.'
            : 'Validated cross-agent premise verification consistency matrix.',
        meta: `STATUS: VERIFIED // LATENCY: ${(Math.random() * 20 + 5).toFixed(1)}ms`,
      };

      setFeedItems((prev) => [newEntry, ...prev.slice(0, 30)]);
    }, 6000);

    return () => clearInterval(interval);
  }, [isStreaming]);

  const getSourceBadge = (source: FeedItem['source']) => {
    switch (source) {
      case 'BIS_ENTITY':
        return <span className="bb-badge bb-badge-red">BIS_WATCH</span>;
      case 'HF_HUB':
        return <span className="bb-badge bb-badge-amber">HF_HUB</span>;
      case 'WEB_SEARCH':
        return <span className="bb-badge bb-badge-cyan">SCRAPER</span>;
      case 'TENSOR_RT':
        return <span className="bb-badge bb-badge-dim">RUNTIME</span>;
      case 'VERIFIER':
        return <span className="bb-badge bb-badge-green">VERIFIER</span>;
    }
  };

  return (
    <div className="flex flex-col h-full bg-[var(--bb-bg-surface)] text-[var(--bb-text-primary)]">
      {/* Panel Header */}
      <div className="bb-panel-header">
        <div className="flex items-center gap-2">
          <Radio className="w-3.5 h-3.5 text-[var(--bb-purple)]" />
          <span>LIVE INTELLIGENCE STREAM & SOURCE MONITOR</span>
          <span className="text-[10px] text-[var(--bb-text-muted)]">[FUNCTION 06]</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setIsStreaming(!isStreaming)}
            className={`text-[9px] px-2 py-0.5 rounded border font-bold ${
              isStreaming
                ? 'bg-[var(--bb-green-dim)] text-[var(--bb-green)] border-[var(--bb-green)]'
                : 'bg-[var(--bb-bg-base)] text-[var(--bb-text-muted)] border-[var(--bb-border-subtle)]'
            }`}
          >
            {isStreaming ? '● STREAMING LIVE' : '|| PAUSED'}
          </button>
        </div>
      </div>

      <div className="p-3 space-y-2 overflow-y-auto bb-scroll flex-1 text-xs font-mono">
        <div className="divide-y divide-[var(--bb-border-subtle)]">
          {feedItems.map((item) => (
            <div key={item.id} className="py-2.5 flex items-start gap-3 hover:bg-[var(--bb-bg-raised)] px-2 rounded transition-colors">
              <span className="text-[10px] text-[var(--bb-text-dim)] bb-tabular whitespace-nowrap mt-0.5">
                {item.time}
              </span>
              <div className="flex-shrink-0 mt-0.5">
                {getSourceBadge(item.source)}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-[11px] text-[var(--bb-text-primary)] leading-snug">
                  {item.message}
                </p>
                {item.meta && (
                  <span className="text-[10px] text-[var(--bb-text-dim)] block mt-0.5 font-mono">
                    {item.meta}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
