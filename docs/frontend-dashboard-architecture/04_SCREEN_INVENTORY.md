# 04_SCREEN_INVENTORY.md — Helios Terminal Dashboard

## Route

**`/dashboard`** — single route, no sub-routes. All nine views are rendered by swapping the `activeTab` state in `DashboardPlaceholder.tsx`. The URL does not change between tabs — this is intentional to avoid the user bookmarking a specific view and expecting its state to be restored.

---

## Layout skeleton

Every view shares the same outer shell. Only the `<main>` viewport content changes.

```
┌─────────────────────────────────────────────────────────────────────┐
│  BloombergHeader                                                     │
│  ├── Telemetry strip (brand, health beacon, pipeline badge, clocks) │
│  ├── Command bar (COMMAND: input <GO>)                              │
│  ├── Function key ribbon ([F1] through [F9])                        │
│  └── Ticker tape (AI market data, 40s scroll)                       │
├─────────────────────────────────────────────────────────────────────┤
│  <main> — active workstation view (flex-1, p-2, overflow-hidden)    │
│  [renders one of nine views based on activeTab]                     │
├─────────────────────────────────────────────────────────────────────┤
│  Footer strip (HELIOS_WORKSTATION v2.4, pipeline count, hotkeys)    │
└─────────────────────────────────────────────────────────────────────┘
```

If `dossierModalOpen === true`, `ExecutiveDossierModal` renders as an overlay on top of this entire shell.

---

## View 1 — Quadrant Grid (`quadrant`)

**Hotkey:** F1 / QUAD / GRID  
**Command alias:** `QUAD`, `GRID`, `F1`  
**Layout:** 2×2 grid (`grid-cols-1 lg:grid-cols-2 grid-rows-2`) with 4 equal `.bb-panel` panes.

| Quadrant | Component | Data source |
|---|---|---|
| Q1 (top-left) | `BloombergDecisionConsole` | Local form state + `selectedPreset.id` |
| Q2 (top-right) | `AgentPipelineTopology` | `result.verification_results`, `result.recalibration_trail`, `error`, `jobStatus` |
| Q3 (bottom-left) | `InstitutionalVerdictPanel` | `result.verdict`, `result.partial_verdict_caveats`, `result.verification_passed` |
| Q4 (bottom-right) | `TrajectoryChartPanel` | `result.verdict.cross_path_comparison`, `selectedPreset.trajectoryData` |

Each quadrant can potentially expand to full-screen via `focusedQuadrant` state (the expansion CSS is wired with `col-span-2 row-span-2 z-20` classes), though the UI control to trigger this is not exposed in the current build.

**States:**
- All four panes render simultaneously regardless of `state`.
- Q2 and Q3 render empty states if `result === null`.
- Q1 always renders (it's the input form).

---

## View 2 — Decision Console (`decision`)

**Hotkey:** F2 / EVAL / RUN  
**Command alias:** `EVAL`, `RUN`, `F2`  
**Layout:** Single `.bb-panel` filling the entire main viewport.

Fullscreen `BloombergDecisionConsole`. Same component as Q1 in the quadrant view, but without the adjacent panels — used when the analyst wants to focus entirely on building the brief. After submitting, most analysts switch back to `quadrant` (F1) to see the full result.

**States:**
- `isSubmitting` prop is `true` when `state === 'submitting' || state === 'polling'`.
- Submit button is disabled and shows a spinning loader during submission.

---

## View 3 — Trajectory Simulator (`trajectory`)

**Hotkey:** F3 / TRAJ / CHART  
**Command alias:** `TRAJ`, `CHART`, `F3`  
**Layout:** Single `.bb-panel` filling the entire main viewport.

Fullscreen `TrajectoryChartPanel`. Year-by-year TCO and lock-in severity projections for all three sourcing paths using Recharts `LineChart` / `BarChart`. Data comes from `selectedPreset.trajectoryData` (always available, from preset) and comparative narrative from `result.verdict.cross_path_comparison`.

**States:**
- If `result === null`, the Recharts chart renders with preset trajectory data but no comparative narrative.

---

## View 4 — Lock-In Matrix (`lockin`)

**Hotkey:** F4 / LOCKIN / MATRIX  
**Command alias:** `LOCKIN`, `MATRIX`, `F4`  
**Layout:** Single `.bb-panel` filling the entire main viewport.

Fullscreen `LockInMatrixView`. Layer-by-layer exposure heatmap. Data comes from `selectedPreset.lockInVectors` — five dimensions across three paths (Build / Buy / Outsource) with per-dimension critical notes.

**States:**
- Data is always available from `selectedPreset` (no network dependency). Even on `idle` state, this view renders meaningfully.

---

## View 5 — Audit Inspector (`audit`)

**Hotkey:** F5 / AUDIT / VERIFY  
**Command alias:** `AUDIT`, `VERIFY`, `F5`  
**Layout:** Single `.bb-panel` filling the entire main viewport.

Fullscreen `AuditInspector`. Cross-stage verification claim ledger showing:
- `result.verification_results` — per-stage pass/fail with confidence scores.
- `result.recalibration_trail` — any recalibration loops that occurred between pipeline stages.
- `result.verdict.explanation_trail` — the explanation chain: summary, step-by-step stage claims with evidence, and cited sources.
- `result.verification_passed` and `result.verification_failed_stage` — overall verification status.

**States:**
- Empty arrays render as empty tables with appropriate empty-state messaging.
- The `verificationFailedStage` prop highlights which stage caused a pipeline failure.

---

## View 6 — Intel Feed (`feed`)

**Hotkey:** F6 / FEED / STREAM  
**Command alias:** `FEED`, `STREAM`, `F6`  
**Layout:** Single `.bb-panel` filling the entire main viewport.

Fullscreen `IntelFeedPanel`. Live intelligence feed showing sources retrieved during the pipeline run: Tavily web search results, HuggingFace Hub entries, and BIS Entity List entries. This component has no props — it renders a representation of the intelligence sources associated with the current workstation state.

---

## View 7 — Executive Dossier (`dossier`)

**Hotkey:** F7 / DOSSIER / PRINT  
**Command alias:** `DOSSIER`, `PRINT`, `F7`  
**Layout:** Full-viewport modal overlay (`z-50`) on top of the current active view.

`ExecutiveDossierModal`. A printable executive briefing memo. Unlike the other tabs, selecting `dossier` does not change `activeTab` — it sets `dossierModalOpen = true`. The underlying view remains mounted. Close button sets `dossierModalOpen = false`.

**Props received:** `result: DecisionResponse | null`, `onClose: () => void`

---

## View 8 — Bloomberg Global Map (`bmap`)

**Hotkey:** F8 / BMAP / MAP / INFRA  
**Command alias:** `BMAP`, `MAP`, `INFRA`, `F8`  
**Layout:** Single `.bb-panel` filling the entire main viewport.

Fullscreen `BloombergGlobalMap`. Interactive SVG global AI infrastructure map showing data center locations, semiconductor origins, and vendor corporate jurisdictions. No props — the map renders static infrastructure intelligence.

---

## View 9 — Supply Chain Graph (`splc`)

**Hotkey:** F9 / SPLC / CHAIN / SUPPLY  
**Command alias:** `SPLC`, `CHAIN`, `SUPPLY`, `F9`  
**Layout:** Single `.bb-panel` filling the entire main viewport.

Fullscreen `BloombergSupplyChainGraph`. Vector supply chain dependency graph mapping model weight origins, compute dependencies, and vendor relationships. No props — renders static supply chain intelligence.

---

## Footer strip (persistent across all views)

Always visible at the bottom of the viewport. Content:

| Left cluster | Right cluster |
|---|---|
| `HELIOS_WORKSTATION // v2.4` (amber) | `PIPELINE: 6 AGENTS // 18 SUB-AGENTS` |
| `TERMINAL MODE: LAUNCHPAD_GRID` | `VERIFICATION GATE: ENFORCED` (green) |
| `HOTKEYS: [F1-F9] OR [/] FOR COMMAND BAR` | |
