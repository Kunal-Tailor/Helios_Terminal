# 02_REQUIREMENTS_AND_FEATURES.md — Helios Terminal Frontend

## Purpose

Maps each backend-facing functional requirement from `PRD.md` §7 to what the frontend actually has to build, and separates that into MVP vs. stretch — the frontend equivalent of `FEATURES.md`'s MVP/Future split, scoped to what lives in the browser.

## Requirement → Frontend Mapping

| PRD ID | Requirement | Frontend Implication | Priority |
| --- | --- | --- | --- |
| FR-1 | User can submit a decision brief | `DecisionInput` screen: entity, capability, optional candidate options | Must |
| FR-2 | Pipeline runs end-to-end on submission | Pipeline status strip showing live stage progression during the call | Must |
| FR-3 | Side-by-side comparison of paths + verdicts | `Result View` (v1: stacked cards) → `Dashboard` (v2: multi-pane) | Must |
| FR-4 | Claims checked against source before downstream use | Not directly rendered in MVP UI — a stretch "reasoning trail" view surfaces this later (ties to FR-9) | Should (MVP), Could (v1 UI) |
| FR-5 | User can view lock-in risk + future failure mode per path | Dependency detail within each path card / dependency-graph node | Must |
| FR-6 | Multi-pane, command-driven layout | Dashboard shell + nav-only command bar | Should |
| FR-7 | Export/save a decision analysis | Not in MVP frontend scope | Should → Later |
| FR-8 | Revisit a past decision analysis | Not in MVP frontend scope | Could → Later |
| FR-9 | Retrieval/web-search grounding supports verification | Backend-only; frontend has no UI obligation beyond FR-4's stretch reasoning-trail view | Must (backend), N/A (MVP frontend) |

## MVP frontend scope (build this)

- Decision Input form (FR-1)
- Pipeline status strip during submission (FR-2, and directly addresses the "silent spinner" persona risk from `01_FRONTEND_VISION.md`)
- Basic Result View: verdict banner + per-path cards, each showing outcome, named dependency, and failure mode (FR-3, FR-5)
- Nav-only command bar (FR-6, scoped down — see `03_UX_FLOWS.md`)

## Stretch / explicitly deferred (do not build until MVP flow is proven)

- Full multi-pane dashboard assembly beyond the basic result cards
- Dependency-graph visualization (react-flow) — valuable, but the *text* verdict has to be trustworthy and legible before it's worth visualizing as a graph
- Export/save (FR-7), revisit history (FR-8)
- Reasoning-trail / source-grounding view (FR-4/FR-9 surfaced in UI)
- Command bar as a query/submission language (only nav in MVP, per the interaction-model decision in `03_UX_FLOWS.md`)

## Non-functional frontend requirements

- **Perceived latency:** the pipeline can take real time to run (six agents, verification gates). The UI's job is to make that legible, not fast — a visible per-stage status beats a spinner even if total time is unchanged. This is a frontend requirement in its own right, not just a nice-to-have.
- **Failure legibility:** if the pipeline halts on a verification failure (per `pipeline/graph.py`'s gating), the UI must say which stage failed and why in plain language — never a generic "something went wrong."
- **Desktop-only for MVP:** no responsive requirement below ~1280px. Stated explicitly here so it isn't quietly assumed and then treated as a bug later. See `05_DESIGN_SYSTEM.md`.
- **No client-side decision logic:** the frontend never scores, ranks, or interprets dependency severity itself — it renders what the Orchestrator Agent returns. Keeps the frontend a thin, honest presentation layer over the pipeline's verified output.
