# 06_COMPONENT_BREAKDOWN.md — Helios Terminal Dashboard

All components live in `frontend/src/dashboard/components/`. This document covers props, internal state, and behavior for each. Components are listed in dependency order (leaf components first).

---

## `BloombergHeader.tsx`

**Type:** Navigation + Telemetry shell  
**Exported type:** `ActiveWorkstationTab` (union type)

### Props

```typescript
interface BloombergHeaderProps {
  activeTab: ActiveWorkstationTab;
  onSelectTab: (tab: ActiveWorkstationTab) => void;
  onExecuteCommand: (cmd: string) => void;
  status: 'idle' | 'submitting' | 'polling' | 'completed' | 'failed';
  isLiveServerConnected: boolean;
  selectedPresetCode?: string;
}
```

### `ActiveWorkstationTab` union

```typescript
type ActiveWorkstationTab =
  | 'quadrant' | 'decision' | 'trajectory' | 'lockin'
  | 'audit' | 'feed' | 'dossier' | 'bmap' | 'splc';
```

### Internal state

| State | Type | Purpose |
|---|---|---|
| `commandInput` | `string` | Controlled value for the command bar input |
| `timeUtc` | `string` | Live UTC time string, updated every 1000ms |
| `timeLocal` | `string` | Live local time string, updated every 1000ms |
| `isMuted` | `boolean` | Audio mute state, initialized from `terminalAudio.isMuted()` |
| `suggestionsOpen` | `boolean` | Whether the command autocomplete dropdown is visible |

### Behaviors

- **Clock:** `useEffect` sets a 1-second `setInterval` updating both `timeUtc` (via `.toUTCString().slice(17,25)`) and `timeLocal` (via `.toLocaleTimeString('en-US', { hour12: false })`). Cleared on unmount.
- **Global hotkeys:** `useEffect` attaches `window.keydown`. Intercepts `/`, `Cmd+K`/`Ctrl+K` (focuses input + plays blip), F1–F9 (calls `onSelectTab` + plays blip), and Escape (closes dropdown).
- **Command submit:** `handleCommandSubmit` normalizes to uppercase, calls `terminalAudio.playGoCommand()`, calls `onExecuteCommand`, clears input.
- **Sound toggle:** `handleToggleSound` calls `terminalAudio.toggleMute()`, updates `isMuted`.
- **Pipeline badge:** renders one of five `bb-badge` variants based on `status` prop. `polling` state applies `bb-live-indicator` pulsing animation.
- **Ticker tape:** renders `[...TICKER_ITEMS, ...TICKER_ITEMS]` (10 items doubled = 20) as a seamlessly looping scroll strip via `bb-ticker-track` animation.

### Ticker data

10 static entries in `TICKER_ITEMS`: AI model pricing (LLAMA-3.3-70B, GPT-4o-OMNI, CLAUDE-3.5-SONNET), GPU spot rates (H100-SXM5, A100-80GB), regulatory indices (BIS-ENTITY-WATCH, EU-AI-ACT-RISK-IDX), and sovereignty/security metrics.

---

## `BloombergDecisionConsole.tsx`

**Type:** Decision brief input form  
**Used in:** Quadrant Q1, fullscreen View 2

### Props

```typescript
interface BloombergDecisionConsoleProps {
  onSubmit: (brief: DecisionRequest) => void;
  onSelectPreset: (preset: PresetScenario) => void;
  isSubmitting: boolean;
  selectedPresetId?: string;
}
```

### Internal state

| State | Type | Initial value |
|---|---|---|
| `entity` | `string` | `'Indian Army Signals Directorate'` |
| `capability` | `string` | `'Tactical Small Language Model for Edge Comms & SIGINT'` |
| `options` | `string[]` | 3 default options from DEF-SLM preset |
| `newOption` | `string` | `''` |
| `sovereigntyWeight` | `'CRITICAL' \| 'STANDARD' \| 'LOW'` | `'CRITICAL'` |
| `latencyTolerance` | `'SUB_20MS' \| 'BALANCED' \| 'BATCH'` | `'SUB_20MS'` |

### Sections

1. **Institutional Presets (fast load):** 3×1 grid of preset buttons. Active preset highlighted with amber background + checkmark icon. Clicking calls `handlePresetClick` → updates form fields + calls `onSelectPreset`.
2. **Field 01 — Target Entity/Institution:** text input, controlled by `entity`.
3. **Field 02 — AI Capability/Technical Brief:** text input, controlled by `capability`.
4. **Field 03 — Sourcing Candidate Paths:** chip list with × remove button per chip. Add-option input + ADD ghost button (also triggered by Enter key on the add input).
5. **Field 04 — Strategic Constraints:** 2-column grid. Left: DATA SOVEREIGNTY toggle (CRITICAL/STANDARD/LOW). Right: LATENCY/SLA toggle (SUB_20MS/BALANCED/BATCH). Active button uses amber or cyan fill respectively.
6. **Submit:** `EXECUTE SOURCING VERDICT <GO>` button. Disabled if entity or capability is empty or `isSubmitting`. During submission shows spinning `Loader2` icon + "RUNNING 6-AGENT VERIFICATION PIPELINE...".

---

## `AgentPipelineTopology.tsx`

**Type:** Pipeline stage visualization  
**Used in:** Quadrant Q2, referenced in pipeline status

### Props

```typescript
interface AgentPipelineTopologyProps {
  status: 'queued' | 'processing' | 'completed' | 'failed';
  verificationResults?: VerificationResult[];
  recalibrationTrail?: RecalibrationTrailItem[];
  error?: string | null;
}
```

Note: `status` prop receives `state === 'idle' ? 'idle' : jobStatus` from the parent, effectively mapping `WorkstationState` to the job status enum.

### Behavior

Displays the six sequential pipeline stages: **Ingestion → Stack Mapping → Scenario Generation → Outcome Prediction → Dependency Diagnosis → Comparative Verdict**. Each stage is rendered as a node. Verification results from `verificationResults` prop are associated with their corresponding `agent_stage` field and rendered as pass/fail indicators. Recalibration trail items show loop-back arrows between stages when present.

---

## `InstitutionalVerdictPanel.tsx`

**Type:** Sovereign recommendation display  
**Used in:** Quadrant Q3

### Props

```typescript
interface InstitutionalVerdictPanelProps {
  verdict: OrchestratorVerdict | null;
  caveats?: string[];
  verificationPassed?: boolean;
}
```

### Empty state

When `verdict === null`: centered `Award` icon, "AWAITING SYNTHESIS EXECUTION" message, instruction copy. Returns early.

### Populated sections

1. **Recommended path banner** — green-tinted box with `verdict.recommended_path` as `<h2>`.
2. **Verdict summary** — `verdict.verdict_summary` in a raised-background paragraph.
3. **Path-by-path stances** — for each entry in `verdict.path_stances`, a card with:
   - Path name (bold, bright text).
   - Stance badge — green if contains `RECOMMENDED`/`OPTIMAL`/`ACCEPTABLE`, red if contains `CRITICAL`/`UNACCEPTABLE`/`HIGH RISK`, amber otherwise.
   - Stance description text after the `—` separator.
4. **Actionable directives** — `verdict.key_recommendations` as a bulleted list with amber arrow icon.
5. **Strategic caveats** — amber-tinted box if `caveats.length > 0`.
6. **Header badge** — `VERIFIED DECISION` (green) or `PARTIAL VERIFICATION` (amber) based on `verificationPassed`.

---

## `TrajectoryChartPanel.tsx`

**Type:** 5-year TCO and lock-in projection charts  
**Used in:** Quadrant Q4, fullscreen View 3  
**Library:** Recharts

### Props

```typescript
interface TrajectoryChartPanelProps {
  comparison?: CrossPathComparison | null;
  trajectoryData?: PresetScenario['trajectoryData'];
}
```

### Content

- **TCO line chart:** X-axis = year labels (Y0–Y5), Y-axis = cost in \$K. Three lines: `buildTco`, `buyTco`, `outsourceTco` in distinct colors.
- **Lock-In severity chart:** same X-axis. Three lines/bars: `buildLockIn`, `buyLockIn`, `outsourceLockIn` (scale 0–10).
- **Comparative narrative:** `comparison.comparative_narrative` displayed below the charts if present.
- **Path comparison cards:** `comparison.path_comparisons` rendered as per-path summary cards with `lock_in_count`, `max_severity_score`, and `key_tradeoffs`.

---

## `LockInMatrixView.tsx`

**Type:** Multi-layer lock-in severity heatmap  
**Used in:** Fullscreen View 4

### Props

```typescript
interface LockInMatrixViewProps {
  vectors?: PresetScenario['lockInVectors'];
}
```

### Content

Tabular display with rows for each of the five lock-in dimensions (from `selectedPreset.lockInVectors`):

| Dimension | Build score | Buy score | Outsource score | Critical notes |
|---|---|---|---|---|
| Data Sovereignty & Air-Gap... | 1–10 | 1–10 | 1–10 | text |

Scores rendered as color-coded severity bars or badges (green 1–3, amber 4–6, red 7–10). `criticalNotes` rendered below each row.

---

## `AuditInspector.tsx`

**Type:** Verification claim ledger  
**Used in:** Fullscreen View 5

### Props

```typescript
interface AuditInspectorProps {
  verificationResults: VerificationResult[];
  recalibrationTrail: RecalibrationTrailItem[];
  explanationTrail?: ExplanationTrail;
  verificationPassed: boolean;
  verificationFailedStage?: string | null;
}
```

### Sections

1. **Overall verification status banner** — green (VERIFICATION PASSED) or red (FAILED AT STAGE: `verificationFailedStage`).
2. **Verification results table** — one row per `VerificationResult`: `agent_stage`, `claim`, `confidence` (as percentage), pass/fail badge, `reason`.
3. **Explanation trail** — if `explanationTrail` present:
   - Summary paragraph.
   - Step-by-step table: `stage`, `claim`, `evidence` — each step with a grounded/inference badge based on evidence content.
   - Sources list as hyperlinks.
4. **Recalibration trail** — if `recalibrationTrail.length > 0`: per-item cards showing `from_stage → to_stage`, `reason`, `gap_description`, `iteration_count`.

---

## `AuditTrail.tsx`

**Type:** Standalone audit trail sub-component  
**Used in:** `AuditInspector.tsx` (as a composed sub-panel)

Renders the recalibration trail items in a timeline-style layout. Each item shows the stage loop-back with color-coded arrows.

---

## `IntelFeedPanel.tsx`

**Type:** Live intelligence feed display  
**Used in:** Fullscreen View 6

### Props

None.

### Content

Renders a structured feed of intelligence items organized by source type:
- **Tavily web search** — retrieved document titles, URLs, relevance scores.
- **HuggingFace Hub** — model cards, license metadata, architecture info.
- **BIS Entity Lists** — entity watch entries, jurisdiction flags.

The panel represents the retrieval sources used by the pipeline agents. In the current build, these are illustrative representations tied to the active preset's explanation trail sources.

---

## `BloombergGlobalMap.tsx`

**Type:** Interactive SVG global infrastructure map  
**Used in:** Fullscreen View 8 (BMAP)

### Props

None.

### Content

An SVG world map marking:
- **Data center regions:** cloud provider and sovereign data center locations.
- **Semiconductor origin points:** fab locations for GPUs and custom silicon.
- **Vendor corporate jurisdictions:** legal domicile of major AI vendors, color-coded by sovereignty risk.

Interactive: hovering nodes reveals tooltips with jurisdiction details. Clicking nodes may highlight dependent supply chain edges.

---

## `BloombergSupplyChainGraph.tsx`

**Type:** Vector supply chain dependency graph  
**Used in:** Fullscreen View 9 (SPLC)

### Props

None.

### Content

A directed graph (force-layout or SVG-based) mapping:
- **Model weight providers** → training compute → cloud inference providers.
- **Hardware suppliers** → GPU vendors → cloud providers → end-user API services.
- Node colors indicate sovereignty risk tier. Edge thickness indicates dependency weight.

---

## `ExecutiveDossierModal.tsx`

**Type:** Printable executive briefing modal  
**Used in:** Modal overlay (not a routed view)

### Props

```typescript
interface ExecutiveDossierModalProps {
  result: DecisionResponse | null;
  onClose: () => void;
}
```

### Content

Full-viewport overlay (`z-50`) with a printable memo layout:
- **Header:** HELIOS INTELLIGENCE // EXECUTIVE DECISION MEMO, entity name, capability brief, timestamp.
- **Recommended path** — prominently featured.
- **Verdict summary** — executive narrative paragraph.
- **Path stances table** — per-path recommendation and rationale.
- **Key recommendations** — numbered action items.
- **Caveats** — regulatory and assumption boundaries.
- **Verification status** — passed/partial with failed stage if applicable.
- **Close button** — calls `onClose()`.
- **Print-optimized:** suitable for browser print to PDF via `window.print()`.

---

## `TerminalToast.tsx`

**Type:** Notification context & toast alert overlay  
**Used in:** Application-wide notification viewport (`z-50`)

### Exports
- `ToastProvider`: Wraps workstation and manages queue of up to 5 concurrent toast notices.
- `useToast()`: Hook providing `showToast(type, title, message)` and `removeToast(id)`.

---

## `CommandPaletteModal.tsx`

**Type:** Modal overlay for universal search, quick functions, and themes  
**Used in:** Triggered via `Cmd+K`, `/`, `?`, or header action button

### Props

```typescript
interface CommandPaletteModalProps {
  isOpen: boolean;
  onClose: () => void;
  onExecuteCommand: (cmd: string) => void;
  onSelectPreset: (preset: PresetScenario) => void;
  currentTheme: TerminalTheme;
  onSelectTheme: (theme: TerminalTheme) => void;
}
```

### Features
- Real-time filtered search for terminal functions (`QUAD`, `EVAL`, `TRAJ`, `LOCKIN`, `AUDIT`, `BMAP`, `SPLC`, `DOSSIER`).
- Quick preset launcher for all institutional benchmarks.
- Accent palette switcher (Amber, Emerald, Cyan, Gold, Monochrome).
- Keyboard shortcut index.

---

## `ScenarioComparatorModal.tsx`

**Type:** Comparative decision diff modal  
**Used in:** Triggered via `COMPARE DIFF` button or `COMPARE <GO>` command

### Props

```typescript
interface ScenarioComparatorModalProps {
  currentResult: DecisionResponse | null;
  isOpen: boolean;
  onClose: () => void;
}
```

### Features
- Side-by-side comparative table against any selected institutional benchmark.
- Compares strategic sovereignty constraints, latency SLA budgets, candidate options count, and verification gate audit passes.

---

## `DeveloperConsoleModal.tsx`

**Type:** Developer & API Code Generator Modal  
**Used in:** Triggered via `DEV API </>` button, `DEV <GO>` command, or Decision Console action

### Props

```typescript
interface DeveloperConsoleModalProps {
  isOpen: boolean;
  onClose: () => void;
  activeBrief: DecisionRequest;
  currentResult: DecisionResponse | null;
  onSubmitJson: (brief: DecisionRequest) => void;
}
```

### Features
- Generates syntax-highlighted code snippets for cURL, Python (Async HTTPX), and TypeScript.
- Interactive raw JSON schema editor with syntax error validation and direct execution.
- Live AST response inspector.

---

## `GuidedDecisionWizardModal.tsx`

**Type:** 3-Step Guided Sourcing Decision Wizard  
**Used in:** Triggered via `WIZARD 🪄` button, `WIZARD <GO>` command, or Decision Console action

### Props

```typescript
interface GuidedDecisionWizardModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLaunchBrief: (brief: DecisionRequest) => void;
}
```

### Features
- 3-step visual cards for selecting Organization Profile, Capability Objectives, and Strategic Constraints.
- Auto-configures candidate paths and triggers execution with 1 click.

---

## `DecisionForm.tsx`, `PathCards.tsx`, `PipelineProgress.tsx`, `VerdictPanel.tsx`

These are additional component files present in the `components/` directory. They serve as sub-components or alternate renderings used within the primary components above. `PathCards.tsx` renders the per-path comparison cards used in `TrajectoryChartPanel`. `PipelineProgress.tsx` provides the inline progress representation embedded in `AgentPipelineTopology`. `VerdictPanel.tsx` and `DecisionForm.tsx` may serve as composable sub-panels within their respective parent components.
