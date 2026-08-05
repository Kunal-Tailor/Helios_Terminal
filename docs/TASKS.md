# TASKS.md — Helios Terminal Implementation Plan

## How to use this file

- Work **one task at a time**, top to bottom, phase by phase.
- Each task below is sized to be **one commit** — not a batch of commits, not a partial commit.
- Do not start a task until the previous one is committed and (where applicable) passes its check.
- Do not jump ahead to a later phase "while you're at it" — if a task in a later phase seems easier to do while working on the current one, note it here as a future task instead and stay on the current one.
- Backend is built fully before frontend work begins (Phases 1–7 before Phase 8).
- Check off tasks as `[x]` as you complete them so progress is resumable in a new session.

**Commit message format:** `Update - <Phase>.<Task> - <description>`
Example: `Update - 1.1 - initial repo scaffolding`

---

## Phase 1 — Repo Scaffolding (no logic yet)

- [ ] 1.1 — Initialise git repo, add `.gitignore` (Python + Node)
  Commit: `Update - 1.1 - initial repo scaffolding`
- [ ] 1.2 — Add `README.md` with project name + one-line description only
  Commit: `Update - 1.2 - add README`
- [ ] 1.3 — Create empty folder structure per `FOLDER_STRUCTURE.md` (folders + placeholder `.gitkeep` or empty `__init__.py` only — no code)
  Commit: `Update - 1.3 - create folder structure`
- [ ] 1.4 — Copy `docs/` (the seven files already created) into the repo
  Commit: `Update - 1.4 - add project docs`

## Phase 2 — Backend Skeleton (no agents yet)

- [ ] 2.1 — `backend/requirements.txt` or `pyproject.toml` with FastAPI, uvicorn only
  Commit: `Update - 2.1 - backend dependencies`
- [ ] 2.2 — `backend/app/main.py` — FastAPI app that starts and returns a health check
  Commit: `Update - 2.2 - minimal FastAPI app`
- [ ] 2.3 — `backend/app/api/routes/health.py` — `GET /health` returns `{"status": "ok"}`; confirm `uvicorn app.main:app` runs locally and `/health` responds
  Commit: `Update - 2.3 - health check endpoint`
- [ ] 2.4 — `backend/app/core/config.py` — environment/config loading (API keys via env vars, not hardcoded)
  Commit: `Update - 2.4 - config loading via environment variables`
- [ ] 2.5 — `backend/tests/test_api/test_health.py` — one test for the health endpoint
  Commit: `Update - 2.5 - health check test`

## Phase 3 — LLM Client Wrapper (shared dependency for all agents)

- [ ] 3.1 — `backend/app/llm/client.py` — thin wrapper around Claude/GPT API call (single function: prompt in, text out); unit test with a mocked API response (no live call in CI)
  Commit: `Update - 3.1 - LLM client wrapper`
- [ ] 3.2 — `backend/app/retrieval/web_search.py` — thin wrapper for retrieval/web-search augmentation
  Commit: `Update - 3.2 - web search retrieval wrapper`

## Phase 4 — Verification Layer (build before agents depend on it)

- [ ] 4.1 — `backend/app/verification/source_store.py` — data structure to hold a claim + its cited source
  Commit: `Update - 4.1 - source store structure`
- [ ] 4.2 — `backend/app/verification/verifier.py` — function that checks a claim against a source (start simple: presence/consistency check, not full semantic verification); unit tests for verifier with a known-good and known-bad claim/source pair
  Commit: `Update - 4.2 - verification layer (claim-source checking)`

## Phase 5 — Agents, One at a Time

Build and commit each agent **separately**. Do not write two agents in the same commit, even if it feels efficient.

- [ ] 5.1 — `agents/ingestion_agent.py` — takes a decision brief, returns structured context (start with a stub/mock LLM call if needed); unit test
  Commit: `Update - 5.1 - ingestion agent`
- [ ] 5.2 — `agents/stack_mapping_agent.py` — takes context, returns stack layers touched; unit test
  Commit: `Update - 5.2 - stack-mapping agent`
- [ ] 5.3 — `agents/scenario_generation_agent.py` — takes stack scope, returns realistic option set; unit test
  Commit: `Update - 5.3 - scenario-generation agent`
- [ ] 5.4 — `agents/outcome_prediction_agent.py` — takes scenarios, returns projected outcomes; unit test
  Commit: `Update - 5.4 - outcome-prediction agent`
- [ ] 5.5 — `agents/dependency_diagnosis_agent.py` — takes outcomes, returns dependency/lock-in diagnosis; unit test
  Commit: `Update - 5.5 - dependency-diagnosis agent`
- [ ] 5.6 — `agents/orchestrator_agent.py` — takes all diagnoses, returns comparative verdict; unit test
  Commit: `Update - 5.6 - orchestrator agent`

## Phase 6 — Pipeline Wiring

- [ ] 6.1 — `pipeline/graph.py` — wire agents together in sequence WITHOUT verification gating first (get the happy path working end-to-end); integration test on one sample decision brief, mocked LLM responses
  Commit: `Update - 6.1 - wire agents into sequential pipeline (no gating yet)`
- [ ] 6.2 — Add verification gate between each agent handoff (reuse Phase 4 verifier); update integration test to confirm a bad/unverified claim halts or flags the pipeline
  Commit: `Update - 6.2 - add stage-gated verification between agents`

## Phase 7 — API Layer (expose the pipeline)

- [ ] 7.1 — `api/schemas/` — pydantic models for decision brief request + verdict response
  Commit: `Update - 7.1 - request/response schemas`
- [ ] 7.2 — `api/routes/decisions.py` — `POST /decisions` accepts a brief, runs pipeline synchronously, returns verdict; integration test hitting the endpoint end-to-end (mocked LLM)
  Commit: `Update - 7.2 - decisions endpoint wired to pipeline`
- [ ] 7.3 — (Optional, only if needed) add async/background job handling if pipeline runtime is too long for a synchronous request
  Commit: `Update - 7.3 - async decision processing` (only if this task is needed)

**Checkpoint:** Backend is functionally complete and testable via curl/Postman before any frontend work starts.

---

## Phase 8 — Frontend Skeleton

- [ ] 8.1 — `frontend/` — Vite + React 18 app, default starter page only; confirm `npm run dev` runs
  Commit: `Update - 8.1 - Vite + React scaffold`
- [ ] 8.2 — Add Tailwind CSS config
  Commit: `Update - 8.2 - Tailwind setup`
- [ ] 8.3 — `lib/` — API client function to call the backend `/decisions` endpoint
  Commit: `Update - 8.3 - API client for decisions endpoint`

## Phase 9 — Frontend, One Component at a Time

- [ ] 9.1 — `pages/DecisionInput.tsx` — form to submit entity/capability/options (plain form, no styling polish yet)
  Commit: `Update - 9.1 - decision input form`
- [ ] 9.2 — Wire form submit to backend API client, show raw JSON response
  Commit: `Update - 9.2 - wire input form to backend`
- [ ] 9.3 — `components/verdict-panel/` — render the comparative verdict as a simple side-by-side layout
  Commit: `Update - 9.3 - verdict panel component`
- [ ] 9.4 — `components/dependency-graph/` — react-flow/D3 visualisation of dependency relationships
  Commit: `Update - 9.4 - dependency graph visualisation`
- [ ] 9.5 — `components/dashboard/` — assemble multi-pane terminal-style layout using the above components
  Commit: `Update - 9.5 - multi-pane dashboard layout`
- [ ] 9.6 — `components/command-bar/` — command-driven input UI (can be a stretch/polish task)
  Commit: `Update - 9.6 - command bar UI`

## Phase 10 — Integration & Polish

- [ ] 10.1 — End-to-end manual test: real decision brief through frontend → backend → verdict rendered; commit any fixes found, described individually
  Commit: `Update - 10.1 - end-to-end manual verification pass`
- [ ] 10.2 — Styling pass to match Bloomberg-Terminal aesthetic (colors, density, typography)
  Commit: `Update - 10.2 - terminal aesthetic pass`

## Phase 11 — Deployment (last, not in parallel with feature work)

- [ ] 11.1 — `infra/docker/backend.Dockerfile`
  Commit: `Update - 11.1 - backend Dockerfile`
- [ ] 11.2 — `infra/docker/frontend.Dockerfile`
  Commit: `Update - 11.2 - frontend Dockerfile`
- [ ] 11.3 — `infra/docker-compose.yml` for local full-stack run
  Commit: `Update - 11.3 - docker-compose for local dev`
- [ ] 11.4 — Deploy backend to Render (or chosen VM)
  Commit: `Update - 11.4 - backend deploy config`
- [ ] 11.5 — Deploy frontend to Vercel
  Commit: `Update - 11.5 - frontend deploy config`

---

## Notes on Pace

- Given the target of 50+ commits, most tasks above should map to **one commit each**, not be batched further — the list is already sized for that.
- If a task still feels too large when you get to it, split it further in this file (e.g. `5.1a`, `5.1b`) before starting, rather than writing a large commit and describing it as several things at once.
- Backend (Phases 1–7) is a hard gate before Phase 8 begins.
