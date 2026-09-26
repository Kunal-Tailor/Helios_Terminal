# 04_SCREEN_INVENTORY.md — Helios Terminal Frontend

Each entry below is both the screen inventory entry and its page-level spec — at this project's scale (4 screens for MVP) a separate page-specifications file would just repeat this table.

## Screen 1 — Decision Input

- **Route:** `/`
- **Phase:** 9.1
- **Purpose:** Entry point. Single-column, centered — not multi-pane. This is the one screen that deliberately breaks from terminal density, because it's a one-time form, not a data surface.
- **Key elements:**
  - Entity field (text — name/type of organization)
  - Capability field (text — what AI capability is needed)
  - Candidate options input (chip-style add field, optional, with inference hint per `03_UX_FLOWS.md`)
  - Submit action
- **States:** empty (default) · filled · submitting (locks form, reveals status strip) · submission error (inline, form re-enabled)

## Screen 2 — Pipeline Status (inline state, not a route)

- **Route:** none — rendered in place of the submit button area on `/`
- **Phase:** 9.2
- **Purpose:** Make pipeline latency and stage-gated verification visible instead of a blank wait.
- **Key elements:** six-stage strip (Ingestion → Stack-Mapping → Scenario-Generation → Outcome-Prediction → Dependency-Diagnosis → Orchestrator), current-stage highlight, completed-stage checkmarks.
- **States:** in-progress (stage N active) · stage failed (halts, shows reason + retry) · complete (transitions to Screen 3)

## Screen 3 — Result View (v1)

- **Route:** `/result` (or client-side state transition from `/` — decide during 8.3/9.2 based on whether deep-linking a result matters for MVP; default to no deep-link needed since there's no saved history yet)
- **Phase:** 9.3
- **Purpose:** Prove the verdict and per-path data round-trip cleanly and read well, before any graph/dashboard visualization is layered on.
- **Key elements:**
  - Verdict banner (Orchestrator's comparative summary, prose, serif per design system)
  - Decision brief recap (collapsed/small — entity, capability, options used)
  - One `PathCard` per candidate path: outcome, named dependency, failure mode
  - "New decision" action
- **States:** populated (normal) · partial (fewer than 3 paths, e.g. only build/buy) · empty dependency (rare — a path with no meaningful lock-in identified, should read as a genuine finding, not a broken card)

## Screen 4 — Dashboard (v2, later — Phase 9.4/9.5)

- **Route:** `/dashboard` (or replaces `/result` once built — decide when reached; do not scaffold this route in Phase 9.1–9.3)
- **Phase:** 9.4–9.5
- **Purpose:** Full multi-pane assembly once the underlying data/verdict is trusted.
- **Key elements:** verdict pane, dependency-graph pane (react-flow), command bar, path comparison pane.
- **States:** same data-states as Screen 3, plus graph-specific states (node selected, node hover detail).
- **Note:** this screen is explicitly *not* where MVP development starts (per the "one flow deep first" decision) — it's what Screen 3 grows into once proven.

## Deferred screens (not built for MVP — noted here so they aren't forgotten, not so they're started early)

- Decision history / list view (FR-8)
- Saved/exported decision view (FR-7)
- Reasoning-trail / source-grounding detail view (FR-4/FR-9 surfaced in UI)

## Navigation summary

```
/  (Decision Input, includes inline Pipeline Status)
 └── on completion → Result View (Screen 3)
                        └── "New decision" → back to /
                        └── (v2) → Dashboard (Screen 4), command-bar-navigable panes
```
