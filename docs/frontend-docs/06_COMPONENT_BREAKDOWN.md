# 06_COMPONENT_BREAKDOWN.md — Helios Terminal Frontend

Maps 1:1 to `FOLDER_STRUCTURE.md`'s `frontend/src/components/` directories, extended with the components the "one flow deep first" plan actually needs. Each entry includes its states — folded in here rather than a separate states file, since at this component count a per-component states table is enough.

## `decision-input/` (new — not in original FOLDER_STRUCTURE.md, add during 9.1)

### `DecisionInputForm`
- **Purpose:** Screen 1's form — entity, capability, candidate options.
- **Data in:** none (fresh form)
- **Data out:** decision brief payload matching `07_API_CONTRACT.md`'s request shape
- **States:** empty · partially filled · valid/submittable · submitting (disabled) · submission error (re-enabled, inline message)

### `OptionChipInput`
- **Purpose:** Add/remove candidate option chips; empty is valid (triggers system inference).
- **States:** empty (shows inference hint) · has-chips · max-reached (soft cap, e.g. 6, to keep Result View cards readable)

## `pipeline-status/` (new — add during 9.2)

### `PipelineStatusStrip`
- **Purpose:** Screen 2's inline six-stage progress indicator.
- **Data in:** current stage index, per-stage status (pending/active/complete/failed)
- **States:** stage 1-6 active (one at a time) · complete (all six ✓, transitions to Result View) · failed-at-stage-N (halts, shows plain-language reason + retry action) — this is the state most worth getting right per `02_REQUIREMENTS_AND_FEATURES.md`'s failure-legibility requirement.

## `verdict-panel/` (existing in FOLDER_STRUCTURE.md)

### `VerdictBanner`
- **Purpose:** Renders the Orchestrator Agent's comparative verdict summary. Serif, roomy, per density rule in `05_DESIGN_SYSTEM.md`.
- **Data in:** verdict text, decision brief recap
- **States:** populated · loading (skeleton, brief) · missing (should not normally occur post-pipeline-success; render as an explicit "verdict unavailable" state rather than blank, since a blank verdict banner reads as broken, not empty)

### `PathCard` (new sub-component under verdict-panel/, add during 9.3)
- **Purpose:** One path's outcome / dependency / failure-mode, connected by the Dependency Thread signature element.
- **Data in:** path name (build/buy/outsource/other), outcome text, dependency name, failure-mode text, severity token
- **States:** populated · no-meaningful-dependency-found (a genuine finding — render distinctly from an error, not as an empty card) · long-content overflow (verdict text can run long; card should expand, not truncate silently — truncating a dependency-risk explanation is the one place brevity actively works against the product's purpose)

## `dependency-graph/` (existing in FOLDER_STRUCTURE.md — v2, Phase 9.4)

### `DependencyGraph`
- **Purpose:** react-flow visualization of lock-in relationships, built only after `PathCard` data is proven correct in Screen 3.
- **Data in:** nodes (paths, dependencies), edges (path → dependency → failure mode)
- **States:** populated · node-selected (detail panel opens) · node-hover · empty-graph (falls back to a message, not a blank canvas)

## `command-bar/` (existing in FOLDER_STRUCTURE.md — nav-only scope per `03_UX_FLOWS.md`)

### `CommandBar`
- **Purpose:** Keyboard-first navigation between panes/sections. Not a query or submission interface for MVP.
- **States:** unfocused (dormant, minimal) · focused (input active, command hints visible) · command-recognized vs. command-unrecognized (unrecognized should suggest the valid command set, not fail silently)

## `dashboard/` (existing in FOLDER_STRUCTURE.md — v2, Phase 9.5)

### `DashboardShell`
- **Purpose:** Multi-pane grid assembling `VerdictBanner`, `DependencyGraph`, and pane navigation via `CommandBar`, once Screen 3's flow is proven.
- **States:** standard responsive-to-panes states only (no mobile states, per Responsive Stance in `05_DESIGN_SYSTEM.md`) — pane focused/unfocused via command bar.

## Shared/utility components (add as needed, not pre-built)

- `StatusBadge` — small severity-token badge (critical/elevated/low), always paired with text label per accessibility notes in `05_DESIGN_SYSTEM.md`.
- `HairlineDivider` — the pane/card border primitive, single source so the `--border-hairline` token isn't hand-applied inconsistently.

## Explicit non-components for MVP

No `HistoryList`, `ExportButton`, or `ReasoningTrailPanel` components until FR-7/FR-8/FR-4-in-UI are actually scheduled — building these early risks scaffolding UI for data the backend doesn't expose yet.
