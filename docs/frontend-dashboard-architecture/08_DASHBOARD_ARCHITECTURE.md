# 08_DASHBOARD_ARCHITECTURE.md — Helios Terminal Dashboard

## Folder structure

```
frontend/src/dashboard/
├── pages/
│   └── DashboardPlaceholder.tsx    # Root page component, state machine owner
├── components/
│   ├── BloombergHeader.tsx         # Navigation, command bar, telemetry strip, ticker
│   ├── BloombergDecisionConsole.tsx# Decision brief input form
│   ├── AgentPipelineTopology.tsx   # 6-stage pipeline visualization
│   ├── InstitutionalVerdictPanel.tsx # Sovereign recommendation display
│   ├── TrajectoryChartPanel.tsx    # Recharts 5-year TCO & lock-in charts
│   ├── LockInMatrixView.tsx        # Layer-by-layer lock-in heatmap
│   ├── AuditInspector.tsx          # Verification claim ledger
│   ├── AuditTrail.tsx              # Recalibration trail sub-component
│   ├── IntelFeedPanel.tsx          # Live intelligence feed
│   ├── BloombergGlobalMap.tsx      # SVG global infrastructure map
│   ├── BloombergSupplyChainGraph.tsx # Supply chain dependency graph
│   ├── ExecutiveDossierModal.tsx   # Printable executive memo modal
│   ├── DecisionForm.tsx            # Sub-form component
│   ├── PathCards.tsx               # Per-path comparison cards
│   ├── PipelineProgress.tsx        # Inline pipeline progress indicator
│   └── VerdictPanel.tsx            # Composable verdict sub-panel
├── api.ts                          # Typed fetch wrapper (async submit + polling)
├── data/
│   └── presetScenarios.ts          # 3 pre-computed institutional scenarios
├── utils/
│   └── terminalAudio.ts            # Web Audio API sound engine
└── styles/
    └── terminal.css                # CSS custom property tokens + component primitives
```

---

## State machine

Managed by `useState` hooks in `DashboardPlaceholder.tsx`. No external state management library (no Redux, no Zustand, no TanStack Query).

```
idle ─────────────────► submitting ──────────────────► polling
 ▲                           │                             │
 │                           │ (offline fallback:          │ (every 2500ms)
 │                           │  1200ms setTimeout)         │
 │                           ▼                             ▼
 └── CLEAR/RESET ──── completed ◄──────────────────── failed
```

### State variable: `WorkstationState`

```typescript
type WorkstationState = 'idle' | 'submitting' | 'polling' | 'completed' | 'failed';
```

### Full state inventory (`DashboardPlaceholder.tsx`)

| State variable | Type | Initial value | Purpose |
|---|---|---|---|
| `activeTab` | `ActiveWorkstationTab` | `'quadrant'` | Which workstation view is rendered |
| `state` | `WorkstationState` | `'completed'` | Pipeline execution state |
| `jobStatus` | `JobStatusResponse['status']` | `'completed'` | Backend job status (used by `AgentPipelineTopology`) |
| `selectedPreset` | `PresetScenario` | `PRESET_SCENARIOS[0]` | Active preset for trajectory/lockin data |
| `result` | `DecisionResponse \| null` | `PRESET_SCENARIOS[0].result` | Current verdict data |
| `error` | `string \| null` | `null` | Error message on pipeline failure |
| `isLiveServerConnected` | `boolean` | `true` | Backend health beacon state |
| `dossierModalOpen` | `boolean` | `false` | Whether the dossier modal is open |
| `focusedQuadrant` | `number \| null` | `null` | Which quadrant (1–4) is focused/expanded |

---

## Data flow

```
PRESET_SCENARIOS[0]
        │
        ▼
DashboardPlaceholder (state owner)
        │
        ├── BloombergHeader
        │     ├── status → pipeline badge
        │     ├── isLiveServerConnected → health beacon
        │     ├── selectedPresetCode → active preset badge
        │     ├── onSelectTab → setActiveTab
        │     └── onExecuteCommand → handleExecuteCommand
        │
        └── <main> (conditional on activeTab)
              ├── quadrant → 4 child components in grid
              │     ├── Q1: BloombergDecisionConsole
              │     │     ├── onSubmit → handleSubmit
              │     │     └── onSelectPreset → handleSelectPreset
              │     ├── Q2: AgentPipelineTopology
              │     │     └── verification/recalibration from result
              │     ├── Q3: InstitutionalVerdictPanel
              │     │     └── verdict from result
              │     └── Q4: TrajectoryChartPanel
              │           └── comparison from result + trajectoryData from selectedPreset
              ├── decision → BloombergDecisionConsole (fullscreen)
              ├── trajectory → TrajectoryChartPanel (fullscreen)
              ├── lockin → LockInMatrixView(vectors=selectedPreset.lockInVectors)
              ├── audit → AuditInspector (from result)
              ├── feed → IntelFeedPanel (no props)
              ├── bmap → BloombergGlobalMap (no props)
              └── splc → BloombergSupplyChainGraph (no props)
```

---

## Polling loop

Implemented via `useRef<ReturnType<typeof setInterval>>` (`pollTimerRef`).

```typescript
const POLL_INTERVAL_MS = 2500;

const startPolling = useCallback((jobId: string) => {
  if (pollTimerRef.current) clearInterval(pollTimerRef.current);

  pollTimerRef.current = setInterval(async () => {
    const status = await pollJobStatus(jobId);
    setJobStatus(status.status);

    if (status.status === 'completed') {
      clearInterval(pollTimerRef.current!);
      setResult(status.result);
      setState('completed');
      terminalAudio.playSuccessChime();
    } else if (status.status === 'failed') {
      clearInterval(pollTimerRef.current!);
      setError(status.error || '...');
      setState('failed');
      terminalAudio.playWarning();
    }
  }, POLL_INTERVAL_MS);
}, []);
```

Interval is cleared on component unmount via a cleanup `useEffect`. Errors during individual poll calls are caught and logged — transient network errors do not kill the polling loop.

---

## Offline synthesis fallback

Activated when `submitDecision()` throws (no live backend). The catch block runs a fuzzy entity match:

```typescript
const match = PRESET_SCENARIOS.find(
  (p) =>
    p.brief.entity.toLowerCase().includes(brief.entity.toLowerCase()) ||
    brief.entity.toLowerCase().includes(p.brief.entity.toLowerCase())
) || PRESET_SCENARIOS[0];

const clientResult: DecisionResponse = {
  ...match.result,
  entity: brief.entity,
  capability: brief.capability,
  options: brief.options.length > 0 ? brief.options : match.result.options,
};
```

A 1200ms `setTimeout` simulates synthesis latency before result delivery. The UI transitions through `submitting` → 1200ms delay → `completed` (skipping `polling`).

---

## Audio engine (`terminalAudio.ts`)

Singleton `TerminalAudioEngine` class, exported as `terminalAudio`.

### Initialization

- `AudioContext` created lazily on first audio call (`initCtx()`).
- Falls back to `webkitAudioContext` for Safari.
- Resumes suspended context automatically.
- Mute preference loaded from `localStorage.getItem('helios_terminal_sound_muted')` on construction.

### Sound effects

| Method | Waveform | Frequency | Duration | Trigger |
|---|---|---|---|---|
| `playBlip()` | sine | 880Hz → 1200Hz ramp | 40ms | Focus, click, tab switch, hotkey |
| `playGoCommand()` | square | 520 → 780 → 1040Hz steps | 90ms | Command submit, form submit |
| `playSuccessChime()` | sine | D5 (587Hz), A5 (880Hz), D6 (1175Hz) staggered 70ms | 180ms each | Job completed |
| `playWarning()` | sawtooth | 220Hz → 180Hz | 160ms | Job failed |

### Mute persistence

```typescript
toggleMute(): boolean {
  this.muted = !this.muted;
  localStorage.setItem('helios_terminal_sound_muted', String(this.muted));
  if (!this.muted) this.playBlip(); // confirmation blip on unmute
  return this.muted;
}
```

---

## Routing integration

The dashboard is registered as a route in the frontend router (React Router v6). The route is `/dashboard`. The `Dashboard` component (named export from `DashboardPlaceholder.tsx`) is the route element. No sub-routes exist within the dashboard — all nine views are rendered via state, not URL changes.

The `BloombergHeader` contains a `<Link to="/">` back to the marketing home page, using React Router's `Link` component.

---

## Styling approach

- **`terminal.css`** provides the CSS custom property token foundation (`--bb-*`).
- **Tailwind CSS** provides utility classes for layout, spacing, and sizing.
- All color values in Tailwind classes use arbitrary value syntax referencing tokens: `bg-[var(--bb-bg-surface)]`, `text-[var(--bb-amber)]`, `border-[var(--bb-border-subtle)]`.
- Component-specific layout is handled with Tailwind flex/grid utilities.
- No CSS Modules, no styled-components — flat class-based approach throughout.

---

## External dependencies (dashboard-specific)

| Package | Purpose |
|---|---|
| `recharts` | `TrajectoryChartPanel` line/bar charts |
| `lucide-react` | All icons across all dashboard components |
| `react-router-dom` | `<Link>` in `BloombergHeader`, routing in app |
| Web Audio API | `terminalAudio.ts` — browser-native, no package |

---

## Known limitations and open items

- **Strategic constraints not serialized:** the Sovereignty and Latency toggles in `BloombergDecisionConsole` update local state but the values are not included in the `DecisionRequest` sent to the backend. This is a known open item for Phase 10.
- **`focusedQuadrant` expansion:** the CSS wiring for expanding individual quadrants to full-screen is present (`col-span-2 row-span-2 z-20` classes are conditional), but no UI control to trigger it is wired in the current build.
- **`IntelFeedPanel` static:** the panel renders intelligence source representations based on preset explanation trail sources rather than live retrieval data.
- **Polling error recovery:** transient polling errors are logged but the loop continues. If the backend permanently fails mid-poll (not at the initial submit), the state will remain stuck in `polling`. A polling timeout/max-retry mechanism is not implemented.
