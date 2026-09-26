# frontend-docs/ — Helios Terminal

Frontend-specific documentation, parallel to the top-level `docs/` folder (`PROJECT_VISION.md`, `PRD.md`, `FEATURES.md`, `TECH_STACK.md`, `ARCHITECTURE.md`, `FOLDER_STRUCTURE.md`), which stays the source of truth for product-level and backend decisions. This folder covers everything specific to *how the interface is built*, not re-litigated product scope.

## Reading order

1. **`01_FRONTEND_VISION.md`** — why the interface looks and feels the way it does; the Hybrid Terminal philosophy.
2. **`02_REQUIREMENTS_AND_FEATURES.md`** — PRD functional requirements mapped to frontend obligations; MVP vs. stretch.
3. **`03_UX_FLOWS.md`** — how a user actually moves through the product, step by step.
4. **`04_SCREEN_INVENTORY.md`** — every screen, its route, its states.
5. **`05_DESIGN_SYSTEM.md`** — color/type tokens, density rules, responsive stance, accessibility, motion.
6. **`06_COMPONENT_BREAKDOWN.md`** — every component, its data, its states — maps to `FOLDER_STRUCTURE.md`'s `components/` tree.
7. **`07_API_CONTRACT.md`** — draft request/response shapes for `POST /decisions`; **must be synced against real backend schemas before Phase 8.3**.
8. **`08_FRONTEND_ARCHITECTURE.md`** — folder structure, routing, state management (React Query, no Redux), styling implementation.

## Build sequencing lives in TASKS.md, not here

Commit-by-commit sequencing for the frontend (Phase 8 onward) is kept in the top-level `TASKS.md`, alongside the backend phases, so there's one source of truth for build order across the whole project rather than two task lists that can drift out of sync. These docs describe *what* to build; `TASKS.md` describes *when*, in what commit.

## Core decisions locked by this folder (don't re-litigate without updating the doc)

- **Aesthetic:** Hybrid Terminal — dense chrome, roomy verdict/dependency panes. (`01`, `05`)
- **Build order:** one flow deep first — Decision Input → basic Result View — before the full multi-pane Dashboard or dependency graph. (`03`, `04`)
- **Command bar:** navigation only for MVP, not a query/submission interface. (`03`, `06`)
- **State management:** TanStack Query for server state, local state for the rest — no global store. (`08`)
- **Responsive:** desktop-only for MVP, no mobile breakpoints. (`05`)

## Known open items

- `07_API_CONTRACT.md` is a draft and needs to be checked against the real backend Pydantic schemas.
- `08_FRONTEND_ARCHITECTURE.md` flags an open question on whether `PipelineStatusStrip` needs Phase 7.3's async/polling backend or an honest single-request "running" state — resolve before building 9.2.
