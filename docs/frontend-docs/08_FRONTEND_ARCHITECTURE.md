# 08_FRONTEND_ARCHITECTURE.md — Helios Terminal Frontend

## Structure

Follows `FOLDER_STRUCTURE.md`'s `frontend/` layout as-is:

```
frontend/src/
├── main.tsx / App.tsx
├── components/
│   ├── decision-input/       # new, add in 9.1
│   ├── pipeline-status/      # new, add in 9.2
│   ├── dashboard/
│   ├── command-bar/
│   ├── dependency-graph/
│   └── verdict-panel/        # includes PathCard, VerdictBanner
├── pages/
│   ├── Home.tsx               # Decision Input screen
│   ├── DecisionInput.tsx      # (may fold into Home.tsx — decide at 9.1, don't pre-split)
│   └── DecisionResult.tsx     # Result View (v1), grows into Dashboard route later
├── hooks/
├── lib/                        # API client, formatting helpers
└── styles/
```

No new top-level folders needed — the two new component directories (`decision-input/`, `pipeline-status/`) slot into the existing tree per `06_COMPONENT_BREAKDOWN.md`.

## Routing

React Router, minimal:

- `/` — Decision Input (includes inline Pipeline Status state)
- `/result` — Result View (v1)
- `/dashboard` — v2 only, added when Phase 9.4/9.5 begin; do not scaffold the route before the components exist behind it.

No nested/dynamic routes needed for MVP (no `/decisions/:id` — that's history/revisit, out of scope per `02_REQUIREMENTS_AND_FEATURES.md`).

## State management

**Decision: TanStack Query (React Query) for server state, local component state for everything else. No Redux/Zustand for MVP.**

Rationale: the app has exactly one meaningful server interaction — submit a decision brief, get a verdict back (plus possibly poll a job status if Phase 7.3's async handling is live). That's a textbook fit for React Query's `useMutation`/`useQuery` primitives, and it gets loading/error/retry states for free, which directly serves the failure-legibility requirement in `02_REQUIREMENTS_AND_FEATURES.md`. A global store would be solving a problem this app doesn't have — there's no cross-cutting client state (no auth, no multi-entity cache, no offline sync) to justify one.

- `useMutation` — decision brief submission
- `useQuery` (polling, `refetchInterval`) — only if Phase 7.3's async job pattern is active; if `POST /decisions` is synchronous, skip polling entirely and treat the `PipelineStatusStrip` as a client-side simulated progression tied to the single request's lifecycle (see note below)
- Local `useState`/`useReducer` — form state (`DecisionInputForm`), command bar focus state, which pane is active

**Open question to resolve at 8.3, not before:** if `POST /decisions` is synchronous (blocks until the full pipeline finishes), the `PipelineStatusStrip`'s six-stage progression can't reflect real backend state — it would need either (a) a genuinely async/polling backend (Phase 7.3), or (b) an honest client-side approximation that says "running" rather than fabricating per-stage completion it can't actually verify. Do not silently fake stage-by-stage progress against a synchronous call — that would misrepresent the verification-gated pipeline the whole product is built around. Resolve this against the real Phase 7.3 status before building 9.2.

## Command bar state

Global, lightweight: a single `isFocused` boolean plus a command registry (`verdict`, `graph`, `new` per `03_UX_FLOWS.md`). Implemented as a small custom hook (`useCommandBar`) rather than pulled into the server-state layer — it's pure client UI state with no persistence requirement in MVP.

## Styling implementation

Tailwind CSS per `TECH_STACK.md`, with the tokens from `05_DESIGN_SYSTEM.md` defined as CSS custom properties (`--bg-base`, `--accent`, etc.) and referenced from `tailwind.config.js` rather than hardcoded hex values scattered through components — keeps the design system file the single source of truth if a token needs to change later.

## What's deliberately not architected yet

- No data-fetching layer for history/export (FR-7/FR-8) — don't build the query hooks for endpoints that don't exist yet.
- No `dependency-graph/` data transformation logic until `PathCard` data is proven correct in the Result View (v1) — building the graph's data shape against unproven verdict data risks having to redo it.
- No global theme-switching (light mode, etc.) — not a requirement anywhere in the product docs; don't add token-switching infrastructure speculatively.
