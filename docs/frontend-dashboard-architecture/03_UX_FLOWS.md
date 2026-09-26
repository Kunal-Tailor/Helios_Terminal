# 03_UX_FLOWS.md — Helios Terminal Dashboard

## How to read this file

Each flow is a numbered step sequence reflecting what the user actually experiences in the built dashboard. State machine transitions (`idle`, `submitting`, `polling`, `completed`, `failed`) are noted inline.

---

## Flow 1 — Default load (preset already populated)

This is what happens when a user navigates to `/dashboard` for the first time.

1. React mounts `Dashboard` component in `DashboardPlaceholder.tsx`.
2. Initial state: `state = 'completed'`, `activeTab = 'quadrant'`, `selectedPreset = PRESET_SCENARIOS[0]` (DEF-SLM), `result = PRESET_SCENARIOS[0].result`.
3. A background `useEffect` fires `GET /health` to probe the FastAPI backend. The header beacon updates from STANDALONE to ONLINE (or remains STANDALONE if backend is unreachable).
4. The 4-Quadrant view renders immediately with real verdict data — no empty states, no loading spinner.
5. The Bloomberg ticker tape scrolls across the bottom of the header at 40s cycle.
6. **User is immediately operational.** No onboarding prompt, no "click start," no empty panes.

---

## Flow 2 — Running a custom brief (live backend path)

1. User presses `F2` or clicks `[F2] DECISION EXEC` in the ribbon → `activeTab` → `'decision'` → fullscreen `BloombergDecisionConsole` renders.
2. User types an entity name (e.g. "UK Ministry of Defence") and capability brief (e.g. "Sovereign LLM for classified document summarisation").
3. User optionally edits sourcing paths via chips (add / remove). Optionally sets Sovereignty and Latency toggles.
4. User clicks `EXECUTE SOURCING VERDICT <GO>` (or presses Enter on the form).
5. `handleSubmit` fires → `terminalAudio.playGoCommand()` → `setState('submitting')` → calls `submitDecision(brief)`.
6. Header pipeline badge updates: **SUBMITTING…** (amber badge, no animation).
7. Backend returns `{ job_id, status: 'queued' }`. State → `'polling'`. `startPolling(job_id)` begins a 2500ms interval.
8. Header pipeline badge updates: **SYNTHESIZING (6 AGENTS)** (amber badge, pulsing `bb-live-indicator` animation).
9. Every 2500ms: `pollJobStatus(job_id)` fires. `jobStatus` state updates to `queued → processing → completed`.
10. When `status === 'completed'`: interval cleared, `result` set to `status.result`, state → `'completed'`, `terminalAudio.playSuccessChime()`.
11. Header badge updates: **VERIFIED VERDICT** (green badge).
12. If user is still on the `decision` tab, they can switch to `quadrant` (F1) to see the full 4-pane result, or drill into any other view.

---

## Flow 3 — Running a custom brief (offline / fallback path)

1. Steps 1–5 same as Flow 2.
2. `submitDecision()` throws (network error, CORS block, backend not running).
3. `console.warn` fires. A `setTimeout(fn, 1200)` creates a simulated synthesis delay.
4. The entity string is fuzzy-matched against `PRESET_SCENARIOS` by `entity.toLowerCase().includes()` — bidirectional substring match. If no match, falls back to `PRESET_SCENARIOS[0]`.
5. `clientResult` is assembled: matched preset's `result` with the user's `entity`, `capability`, and `options` overlaid.
6. State → `'completed'`, result set, `terminalAudio.playSuccessChime()`.
7. The user sees a fully populated verdict in under 2 seconds. No error message, no degraded UI. The header beacon will be showing STANDALONE mode, indicating the offline path was used.

---

## Flow 4 — Loading a preset via the command bar

1. User focuses the command bar by pressing `/` or `Cmd+K`. `terminalAudio.playBlip()` plays.
2. User types `DEMO DEF` (or `DEMO FIN`, `DEMO MED`).
3. The autocomplete dropdown shows the matching command: `DEMO DEF <GO> — Load Indian Army Signals SLM Case`.
4. User clicks the suggestion or presses Enter.
5. `terminalAudio.playGoCommand()` plays → `handleExecuteCommand('DEMO DEF')` → `handleSelectPreset(PRESET_SCENARIOS[0])`.
6. `selectedPreset` and `result` both update immediately. State stays `'completed'`. No network call.
7. All open views instantly reflect the new preset data.

---

## Flow 5 — Switching workstation views

**Via function key ribbon:**
1. User clicks `[F3] TRAJECTORY SIM` in the ribbon.
2. `terminalAudio.playBlip()` plays. `activeTab` → `'trajectory'`.
3. Fullscreen `TrajectoryChartPanel` renders with `selectedPreset.trajectoryData` and `result.verdict.cross_path_comparison`.

**Via keyboard:**
1. User presses `F4` anywhere in the document (the global `keydown` listener in `BloombergHeader.tsx` intercepts).
2. `onSelectTab('lockin')` fires. `activeTab` → `'lockin'`. Fullscreen `LockInMatrixView` renders.

**Via command bar:**
1. User types `AUDIT <GO>`.
2. `handleExecuteCommand('AUDIT')` → `activeTab` → `'audit'`.

---

## Flow 6 — Opening the Executive Dossier

1. User presses `F7` or types `DOSSIER <GO>` or clicks `[F7] DOSSIER` in the ribbon.
2. `onSelectTab('dossier')` fires → in `DashboardPlaceholder`, the dossier tab case sets `dossierModalOpen = true` instead of changing `activeTab`.
3. `ExecutiveDossierModal` renders as a portal/overlay on top of the current view.
4. User reads, prints, or exports the executive memo.
5. User clicks close → `setDossierModalOpen(false)` → modal disappears, underlying view is unchanged.

---

## Flow 7 — Pipeline failure

1. Live pipeline run encounters a fatal verification exception (backend returns `status: 'failed'`).
2. Poll interval detects the failure. `setError(status.error)`. State → `'failed'`. `terminalAudio.playWarning()` plays.
3. Header badge updates: **EXECUTION FAILED** (red badge).
4. `AgentPipelineTopology` reflects the failed status — the failed stage is highlighted.
5. User can inspect `AuditInspector` (F5) to see `verification_failed_stage` and any partial claims.
6. User can hit `CLEAR` command to reset to `idle` and start a new brief.

---

## Flow 8 — Resetting the workstation

1. User types `CLEAR` or `RESET` in the command bar.
2. `handleExecuteCommand('CLEAR')` → `setResult(null)`, `setState('idle')`, `setJobStatus('queued')`, `setError(null)`.
3. All result-dependent panels show their empty/awaiting states.
4. The form in the Decision Console retains its last input values (form state is local to `BloombergDecisionConsole`).

---

## Empty states

Every result-dependent panel handles `result === null` gracefully:

| Panel | Empty state copy |
|---|---|
| `InstitutionalVerdictPanel` | "AWAITING SYNTHESIS EXECUTION — Submit a decision brief or load an institutional preset from Console [F2] to synthesize comparative verdict." |
| `TrajectoryChartPanel` | Recharts renders with no data series; placeholder label shown |
| `AgentPipelineTopology` | Pipeline stages shown in idle/grey state |
| `AuditInspector` | Empty verification table, empty recalibration trail |
