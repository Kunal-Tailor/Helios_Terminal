# 02_REQUIREMENTS_AND_FEATURES.md — Helios Terminal Dashboard

## Scope

This file maps the dashboard's functional requirements to the components and behaviors that implement them. All requirements listed here are **implemented and verified** in the Phase 9 source code.

---

## FR-D1: Decision brief submission

- User can enter a free-text **target entity** (institution name) and **AI capability brief** (what they need AI to do).
- User can specify 1–N **sourcing candidate paths** as labelled chips, or leave the list empty (the backend infers paths from the brief).
- User can add a custom candidate path via a text field + ADD button; can remove any path via the × button on its chip.
- User can configure two **strategic constraints**: Data Sovereignty priority (CRITICAL / STANDARD / LOW) and Latency/SLA tolerance (SUB_20MS / BALANCED / BATCH). These are UI-only controls in the current build — informational context for the analyst, not yet serialized into the API request.
- Submission triggers the `handleSubmit` handler in `DashboardPlaceholder.tsx` → calls `submitDecision()` → transitions state machine to `submitting`.

**Implemented by:** `BloombergDecisionConsole.tsx`, `api.ts#submitDecision`

---

## FR-D2: Institutional preset loading

- Three institutional presets are available at all times via the preset grid in the Decision Console and via command bar (`DEMO DEF`, `DEMO FIN`, `DEMO MED`).
- Selecting a preset populates the form fields, sets `selectedPreset`, and immediately shows the preset's pre-computed result without making a network call.
- Presets are defined in `presetScenarios.ts` with full `DecisionResponse`, `trajectoryData`, and `lockInVectors` — giving every view instant data even offline.

| Code | ID | Entity |
|---|---|---|
| `DEF-SLM` | `defense-tactical-slm` | Indian Army Signals Directorate |
| `FIN-RAG` | `fintech-tier1-rag` | Global Tier-1 Investment Bank (AMR Capital) |
| `MED-AI` | `healthcare-clinical-copilot` | MetroHealth Regional Hospital System |

**Implemented by:** `presetScenarios.ts`, `BloombergDecisionConsole.tsx#handlePresetClick`, `DashboardPlaceholder.tsx#handleSelectPreset`

---

## FR-D3: Async pipeline execution + polling

- On submit, the frontend calls `POST /decisions/async` (not the synchronous `/decisions`) to avoid blocking the browser tab during a 1–3 minute pipeline run.
- The backend immediately returns a `job_id`. The frontend transitions to `polling` state and starts a `setInterval` at `POLL_INTERVAL_MS = 2500` calling `GET /decisions/jobs/{job_id}`.
- When status reaches `completed`, polling stops, result is stored, state transitions to `completed`, and the success chime plays.
- When status reaches `failed`, polling stops, the error message is stored, state transitions to `failed`, and the warning tone plays.

**Implemented by:** `api.ts#submitDecision`, `api.ts#pollJobStatus`, `DashboardPlaceholder.tsx#startPolling`

---

## FR-D4: Offline client synthesis fallback

- If `submitDecision()` throws (network error, backend offline, CORS error), the catch block activates.
- A 1200ms simulated delay fires, then the entity string is fuzzy-matched against `PRESET_SCENARIOS` by entity name substring. If no match, `PRESET_SCENARIOS[0]` is used.
- The result object is assembled with the user's actual `entity`, `capability`, and `options` fields overlaid on the matched preset's result data — maintaining field consistency.
- State transitions to `completed` as normal; the UI is fully populated with no degradation.

**Implemented by:** `DashboardPlaceholder.tsx#handleSubmit` catch block

---

## FR-D5: Nine workstation views

The dashboard renders exactly one active view at a time based on `activeTab: ActiveWorkstationTab`. Nine views exist:

| Tab ID | Hotkey | Label |
|---|---|---|
| `quadrant` | F1 / QUAD | 4-Quadrant Launchpad Grid |
| `decision` | F2 / EVAL | Decision Execution Console (fullscreen) |
| `trajectory` | F3 / TRAJ | 5-Year Trajectory Simulator (fullscreen) |
| `lockin` | F4 / LOCKIN | Lock-In Severity Matrix (fullscreen) |
| `audit` | F5 / AUDIT | Grounded Verification Inspector (fullscreen) |
| `feed` | F6 / FEED | Live Intelligence Stream (fullscreen) |
| `dossier` | F7 / DOSSIER | Executive Dossier (modal overlay, not a tab) |
| `bmap` | F8 / BMAP | Global AI Infrastructure Map (fullscreen) |
| `splc` | F9 / SPLC | Supply Chain Dependency Graph (fullscreen) |

**Implemented by:** `DashboardPlaceholder.tsx` tab switch logic, `BloombergHeader.tsx` function key ribbon

---

## FR-D6: Command bar

- A free-text `<GO>` input in the header accepts Bloomberg-style commands.
- Pressing `/` or `Cmd+K` (or `Ctrl+K`) from anywhere in the workstation focuses the command bar.
- Pressing Enter or clicking `EXEC <GO>` dispatches the command to `handleExecuteCommand()`.
- Supported commands: `EVAL`, `RUN`, `F2`, `QUAD`, `GRID`, `F1`, `TRAJ`, `CHART`, `F3`, `LOCKIN`, `MATRIX`, `F4`, `AUDIT`, `VERIFY`, `F5`, `FEED`, `STREAM`, `F6`, `DOSSIER`, `PRINT`, `F7`, `BMAP`, `MAP`, `INFRA`, `F8`, `SPLC`, `CHAIN`, `SUPPLY`, `F9`, `DEMO DEF`, `DEMO FIN`, `DEMO MED`, `CLEAR`, `RESET`, `HELP`.
- An autocomplete dropdown shows function suggestions on focus; filtered by typed text; dismissed with Escape.

**Implemented by:** `BloombergHeader.tsx`, `DashboardPlaceholder.tsx#handleExecuteCommand`

---

## FR-D7: Backend health beacon

- On mount, `DashboardPlaceholder.tsx` fires one `GET http://127.0.0.1:8000/health` request.
- `isLiveServerConnected` is set to `true` if the response is OK, `false` otherwise.
- The header displays a pulsing green dot ("HOST: 127.0.0.1:8000 [ONLINE]") or a static amber dot ("STANDALONE / CLIENT MODE") accordingly.

**Implemented by:** `DashboardPlaceholder.tsx` mount `useEffect`, `BloombergHeader.tsx` connection beacon

---

## FR-D8: Terminal audio engine

- All interactive events play synthesized audio feedback with no external asset files.
- Events: key blip (focus, clicks), `<GO>` chime (command submit), success three-tone chime (job completed), warning buzz (job failed).
- Mute state is persisted to `localStorage` key `helios_terminal_sound_muted`.
- Toggle button in the header switches mute state; plays a blip on unmute to confirm audio is working.

**Implemented by:** `terminalAudio.ts`, `BloombergHeader.tsx` mute toggle

---

## FR-D9: Executive Dossier modal

- Accessible via F7 / DOSSIER command / header tab button.
- Opens as a full-viewport overlay on top of the active workstation view.
- Renders a printable executive briefing memo from the current `result` state.
- Dismissed via the modal's close button; returns to the previously active view.

**Implemented by:** `ExecutiveDossierModal.tsx`, `DashboardPlaceholder.tsx#dossierModalOpen`

---

## Non-requirements (explicit exclusions for MVP)

- **No authentication:** the dashboard is accessible at `/dashboard` without login.
- **No persistence:** results are held in React state only; page refresh resets to the first preset.
- **No mobile layout:** desktop-only; no responsive breakpoints in the dashboard CSS.
- **No WebSocket:** polling via `setInterval` is used rather than a persistent WebSocket connection.
- **Strategic constraints UI:** the Sovereignty / Latency toggles in the Decision Console are rendered but not serialized into the API request body in the current build.
