# frontend-dashboard-architecture/ — Helios Terminal Dashboard

Dashboard-specific documentation for the Helios Terminal Bloomberg-style decision intelligence workstation (`/dashboard`). This folder is the parallel counterpart to `docs/frontend-website-architecure/` — the same structure and discipline, applied to the dark terminal application itself rather than the marketing website.

All files here describe what was **actually built** in Phase 9 by Kunal. They are accurate to the source code in `frontend/src/dashboard/`, not aspirational specs.

## Reading order

1. **`01_DASHBOARD_VISION.md`** — why the dashboard looks and operates the way it does; the Bloomberg Terminal philosophy and design decisions.
2. **`02_REQUIREMENTS_AND_FEATURES.md`** — functional requirements for the workstation; what each view must do.
3. **`03_UX_FLOWS.md`** — how a user moves through the dashboard, step by step, from load to verdict.
4. **`04_SCREEN_INVENTORY.md`** — every workstation view (tab), its state, its route, its keyboard shortcut.
5. **`05_DESIGN_SYSTEM.md`** — color tokens, typography, component primitives, animations, scrollbar conventions.
6. **`06_COMPONENT_BREAKDOWN.md`** — every component in `src/dashboard/components/`, its props, internal state, and behaviour.
7. **`07_API_CONTRACT.md`** — the actual request/response shapes used by `api.ts`, mirroring the live backend Pydantic schemas.
8. **`08_DASHBOARD_ARCHITECTURE.md`** — folder structure, state machine, data flow, offline fallback, audio engine.

## What this covers vs. the website docs

| Concern | `frontend-website-architecure/` | `frontend-dashboard-architecture/` |
|---|---|---|
| Route | `/`, `/architecture`, `/about`, `/team` | `/dashboard` |
| Stack | Marketing site Tailwind + React components | Bloomberg terminal CSS tokens + Recharts |
| State | None (static pages) | `WorkstationState` machine + polling loop |
| API | None | `POST /decisions/async` + `GET /decisions/jobs/{id}` |
| Offline | N/A | `presetScenarios.ts` client synthesis fallback |

## Build sequencing lives in TASKS.md, not here

Phase 9 task tracking (with per-commit granularity) is in the top-level `docs/TASKS.md` so there is one source of truth for build order. These docs describe *what* exists; `TASKS.md` describes *in what commit it was built*.

## Core decisions locked by this folder

- **Design language:** Bloomberg Terminal dark aesthetic — `--bb-bg-base: #07090D`, amber `#FF9E00` accent, JetBrains Mono. (`01`, `05`)
- **State machine:** five-state hook in `DashboardPlaceholder.tsx` — `idle → submitting → polling → completed / failed`. (`08`)
- **Offline synthesis:** client-side fallback using `presetScenarios.ts` — no degraded UI experience when backend is unreachable. (`08`)
- **Audio:** Web Audio API, no external files, mute preference persisted to `localStorage`. (`06`, `08`)
- **Desktop-only:** workstation is not responsive — same stance as the website for MVP. (`05`)
