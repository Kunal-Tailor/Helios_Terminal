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

## Phase 1 — Repo Scaffolding (no logic yet)

- [x] 1.1 — Initialise git repo, add `.gitignore` (Python + Node)
  Commit: `Update - 1.1 - initial repo scaffolding`
- [x] 1.2 — Add `README.md` with project name + one-line description only
  Commit: `Update - 1.2 - add README`
- [x] 1.3 — Create empty folder structure per `FOLDER_STRUCTURE.md` (folders + placeholder `.gitkeep` or empty `__init__.py` only — no code)
  Commit: `Update - 1.3 - create folder structure`
- [x] 1.4 — Copy `docs/` (the seven files already created) into the repo
  Commit: `Update - 1.4 - add project docs`

## Phase 2 — Backend Skeleton (no agents yet)

- [x] 2.1 — `backend/requirements.txt` or `pyproject.toml` with FastAPI, uvicorn only
  Commit: `Update - 2.1 - backend dependencies`
- [x] 2.2 — `backend/app/main.py` — FastAPI app that starts and returns a health check
  Commit: `Update - 2.2 - minimal FastAPI app`
- [x] 2.3 — `backend/app/api/routes/health.py` — `GET /health` returns `{"status": "ok"}`; confirm `uvicorn app.main:app` runs locally and `/health` responds
  Commit: `Update - 2.3 - health check endpoint`
- [x] 2.4 — `backend/app/core/config.py` — environment/config loading (API keys via env vars, not hardcoded)
  Commit: `Update - 2.4 - config loading via environment variables`
- [x] 2.5 — `backend/tests/test_api/test_health.py` — one test for the health endpoint
  Commit: `Update - 2.5 - health check test`

## Phase 3 — LLM Client Wrapper (shared dependency for all agents)

- [x] 3.1 — `backend/app/llm/client.py` — thin wrapper around Claude/GPT API call (single function: prompt in, text out); unit test with a mocked API response (no live call in CI)
  Commit: `Update - 3.1 - LLM client wrapper`
- [x] 3.2 — `backend/app/retrieval/web_search.py` — thin wrapper for retrieval/web-search augmentation
  Commit: `Update - 3.2 - web search retrieval wrapper`
- [x] 3.3 — Pin DeepSeek V4 Flash as the default model: set it in `backend/app/core/config.py` (env var default) and `.env.example`. No changes to the client wrapper's interface — this only sets which model it points to by default.
  Commit: `Update - 3.3 - pin DeepSeek V4 Flash as default LLM`

## Phase 4 — Verification Layer (build before agents depend on it)

- [x] 4.1 — `backend/app/verification/source_store.py` — data structure to hold a claim + its cited source
  Commit: `Update - 4.1 - source store structure`
- [x] 4.2 — `backend/app/verification/verifier.py` — function that checks a claim against a source (start simple: presence/consistency check, not full semantic verification); unit tests for verifier with a known-good and known-bad claim/source pair
  Commit: `Update - 4.2 - verification layer (claim-source checking)`

## Phase 5 — Agents, One Sub-Agent at a Time

Each of the six top-level agents is a **parent that orchestrates 2-3 sub-agents**, all running on DeepSeek V4 Flash via the Phase 3 client wrapper. Build sub-agents first, one at a time, then the parent that wires them together. Do not write two sub-agents (or a sub-agent + its parent) in the same commit, even if it feels efficient. The third sub-agent in each group is optional/stretch — skip it if you're short on time and let the parent do that step's work directly; note the skip in the parent's commit message if so.

### 5A — Ingestion Agent

- [x] 5.1 — `agents/ingestion/sub_agents/web_scraping_sub_agent.py` — pulls public info on entity/capability via web search; unit test (mocked search)
  Commit: `Update - 5.1 - ingestion sub-agent: web scraping`
- [x] 5.2 — `agents/ingestion/sub_agents/structured_source_sub_agent.py` — pulls from known structured sources (HF Hub, BIS Entity List, TPDi, market-share reports); unit test
  Commit: `Update - 5.2 - ingestion sub-agent: structured source`
- [x] 5.3 — (optional) `agents/ingestion/sub_agents/context_synthesis_sub_agent.py` — merges 5.1 + 5.2 outputs into structured context; unit test
  Commit: `Update - 5.3 - ingestion sub-agent: context synthesis`
- [x] 5.4 — `agents/ingestion/ingestion_agent.py` — parent: calls sub-agents above (parallel where independent), merges/returns structured context; unit + integration test
  Commit: `Update - 5.4 - ingestion agent (parent)`

### 5B — Stack-Mapping Agent

- [x] 5.5 — `agents/stack_mapping/sub_agents/layer_identification_sub_agent.py` — proposes candidate AI-stack layers from context; unit test
  Commit: `Update - 5.5 - stack-mapping sub-agent: layer identification`
- [x] 5.6 — `agents/stack_mapping/sub_agents/relevance_filter_sub_agent.py` — narrows candidates to layers this decision touches; unit test
  Commit: `Update - 5.6 - stack-mapping sub-agent: relevance filter`
- [x] 5.7 — (optional) `agents/stack_mapping/sub_agents/dependency_linkage_sub_agent.py` — maps how surviving layers interconnect; unit test
  Commit: `Update - 5.7 - stack-mapping sub-agent: dependency linkage`
- [x] 5.8 — `agents/stack_mapping/stack_mapping_agent.py` — parent: orchestrates 5.5-5.7, returns stack scope; unit + integration test
  Commit: `Update - 5.8 - stack-mapping agent (parent)`

### 5C — Scenario-Generation Agent

- [x] 5.9 — `agents/scenario_generation/sub_agents/option_enumeration_sub_agent.py` — generates raw candidate option set; unit test
  Commit: `Update - 5.9 - scenario-generation sub-agent: option enumeration`
- [x] 5.10 — `agents/scenario_generation/sub_agents/feasibility_check_sub_agent.py` — filters out unrealistic options (depends on 5.9's output); unit test
  Commit: `Update - 5.10 - scenario-generation sub-agent: feasibility check`
- [x] 5.11 — (optional) `agents/scenario_generation/sub_agents/scenario_refinement_sub_agent.py` — sharpens surviving options into full scenarios; unit test
  Commit: `Update - 5.11 - scenario-generation sub-agent: scenario refinement`
- [x] 5.12 — `agents/scenario_generation/scenario_generation_agent.py` — parent: orchestrates 5.9-5.11, returns option set; unit + integration test
  Commit: `Update - 5.12 - scenario-generation agent (parent)`

### 5D — Outcome-Prediction Agent

- [x] 5.13 — `agents/outcome_prediction/sub_agents/trajectory_modeling_sub_agent.py` — projects forward path for each scenario; unit test
  Commit: `Update - 5.13 - outcome-prediction sub-agent: trajectory modeling`
- [x] 5.14 — `agents/outcome_prediction/sub_agents/risk_factor_sub_agent.py` — identifies events/conditions that could alter the trajectory; unit test
  Commit: `Update - 5.14 - outcome-prediction sub-agent: risk factor`
- [x] 5.15 — (optional) `agents/outcome_prediction/sub_agents/timeline_projection_sub_agent.py` — attaches time horizons to outcomes; unit test
  Commit: `Update - 5.15 - outcome-prediction sub-agent: timeline projection`
- [x] 5.16 — `agents/outcome_prediction/outcome_prediction_agent.py` — parent: orchestrates 5.13-5.15, returns projected outcomes; unit + integration test
  Commit: `Update - 5.16 - outcome-prediction agent (parent)`

### 5E — Dependency-Diagnosis Agent

- [x] 5.17 — `agents/dependency_diagnosis/sub_agents/lock_in_identification_sub_agent.py` — names the specific dependency per outcome; unit test
  Commit: `Update - 5.17 - dependency-diagnosis sub-agent: lock-in identification`
- [x] 5.18 — `agents/dependency_diagnosis/sub_agents/failure_mode_sub_agent.py` — explains what breaks later if unmanaged; unit test
  Commit: `Update - 5.18 - dependency-diagnosis sub-agent: failure mode`
- [x] 5.19 — (optional) `agents/dependency_diagnosis/sub_agents/severity_scoring_sub_agent.py` — scores severity/urgency per dependency; unit test
  Commit: `Update - 5.19 - dependency-diagnosis sub-agent: severity scoring`
- [x] 5.20 — `agents/dependency_diagnosis/dependency_diagnosis_agent.py` — parent: orchestrates 5.17-5.19, returns diagnoses; unit + integration test
  Commit: `Update - 5.20 - dependency-diagnosis agent (parent)`

### 5F — Orchestrator Agent

- [x] 5.21 — `agents/orchestrator/sub_agents/cross_path_comparison_sub_agent.py` — compares diagnoses across all paths; unit test
  Commit: `Update - 5.21 - orchestrator sub-agent: cross-path comparison`
- [x] 5.22 — `agents/orchestrator/sub_agents/verdict_synthesis_sub_agent.py` — produces final comparative verdict text; unit test
  Commit: `Update - 5.22 - orchestrator sub-agent: verdict synthesis`
- [x] 5.23 — (optional) `agents/orchestrator/sub_agents/explanation_trail_sub_agent.py` — assembles source-grounded reasoning trail; unit test
  Commit: `Update - 5.23 - orchestrator sub-agent: explanation trail`
- [x] 5.24 — `agents/orchestrator/orchestrator_agent.py` — parent: orchestrates 5.21-5.23, returns comparative verdict; unit + integration test
  Commit: `Update - 5.24 - orchestrator agent (parent)`

## Phase 6 — Pipeline Wiring

- [x] 6.1 — `pipeline/graph.py` — wire agents together in sequence WITHOUT verification gating first (get the happy path working end-to-end); integration test on one sample decision brief, mocked LLM responses
  Commit: `Update - 6.1 - wire agents into sequential pipeline (no gating yet)`
- [x] 6.2 — Add verification gate between each agent handoff (reuse Phase 4 verifier); update integration test to confirm a bad/unverified claim halts or flags the pipeline
  Commit: `Update - 6.2 - add stage-gated verification between agents`

## Phase 7 — API Layer & Pipeline Verification Hardening (expose the pipeline)

- [x] 7.1 — `api/schemas/` — pydantic models for decision brief request + verdict response
  Commit: `Update - 7.1 - request/response schemas`
- [x] 7.2 — `api/routes/decisions.py` — `POST /decisions` accepts a brief, runs pipeline synchronously, returns verdict; integration test hitting the endpoint end-to-end (mocked LLM)
  Commit: `Update - 7.2 - decisions endpoint wired to pipeline`
- [x] 7.3 — (Optional, only if needed) add async/background job handling if pipeline runtime is too long for a synchronous request
  Commit: `Update - 7.3 - async decision processing`
- [x] 7.4 — Verification hardening: chained grounded vs. inference claim registration across all 6 stages, verifier matching normalizations (hyphens, commas, Indian number terms), and incomplete run reporting; full backend end-to-end verification
  Commit: `Update - 7.4 - backend verification and chained pipeline hardening`

**Checkpoint:** Backend is functionally complete and testable via curl/Postman before any frontend work starts.

---

## Phase 7.5 — Recalibration & Fallback Layer (turns the pipeline from a sequential chain into a conditional, self-correcting graph)

Context: Phases 1–7 gave every stage a **verification** gate (is this claim grounded in its source). This phase adds a second, distinct gate — a **sufficiency** check (did the upstream stage give me enough to work with at all) — and the backward routing that fires when it fails. A stage that detects insufficient input doesn't regenerate blindly; it emits a `RecalibrationRequest` naming exactly what's missing and which upstream stage should re-run. This is the mechanism that replaces "simple stepwise" with "stage-gated conditional graph" in the synopsis language.

- [ ] 7.5.1 — `backend/app/verification/recalibration.py` — `RecalibrationRequest` data structure: `from_stage`, `to_stage`, `reason` (`insufficient` | `unverified`), `gap_description`, `iteration_count`; unit test for construction/serialization
  Commit: `Update - 7.5.1 - RecalibrationRequest data structure`
- [ ] 7.5.2 — Sufficiency-check function (in `recalibration.py`, reusing `verifier.py`'s pattern) — per-stage threshold checks: e.g. Stack-Mapping has 0–1 surviving layers, Scenario-Generation has <2 viable options after feasibility filtering; unit tests with a known-sufficient and known-insufficient case per stage
  Commit: `Update - 7.5.2 - sufficiency-check function per stage`
- [ ] 7.5.3 — Loop-guard: per-`(from_stage, to_stage)` iteration counter carried in pipeline state, capped at 2 retries; unit test confirming the cap is enforced and does not reset across unrelated stage pairs
  Commit: `Update - 7.5.3 - loop-guard iteration tracking`
- [ ] 7.5.4 — Context accumulation helper — recalibration appends targeted new data to the existing context object rather than discarding/replacing it; unit test confirming prior context survives a re-ingestion pass
  Commit: `Update - 7.5.4 - context accumulation on re-ingestion`
- [ ] 7.5.5 — Wire Stack-Mapping → Ingestion fallback in `pipeline/graph.py`: on insufficient layer mapping, re-invoke Ingestion scoped to the `gap_description` only; integration test (mocked LLM) confirming the loop-back fires and the pipeline continues after
  Commit: `Update - 7.5.5 - stack-mapping to ingestion fallback wiring`
- [ ] 7.5.6 — Wire Scenario-Generation fallback routing: on insufficient/generic scenarios, decide target (Stack-Mapping if layer scope too narrow, Ingestion if missing concrete option data e.g. no known vendors) and route accordingly; integration test covering both target branches
  Commit: `Update - 7.5.6 - scenario-generation fallback routing (dual target)`
- [ ] 7.5.7 — Wire Outcome-Prediction → Scenario-Generation fallback: on repeated grounded_in failures or low path differentiation, invoke `scenario_refinement_sub_agent` (5.11, previously optional/unused) instead of a blind Scenario-Generation re-run; integration test
  Commit: `Update - 7.5.7 - outcome-prediction fallback invokes scenario refinement`
- [ ] 7.5.8 — Wire Dependency-Diagnosis → Outcome-Prediction fallback: on generic/non-specific lock-in output, invoke `timeline_projection_sub_agent` (5.15, previously optional/unused) if it was skipped; integration test
  Commit: `Update - 7.5.8 - dependency-diagnosis fallback invokes timeline projection`
- [ ] 7.5.9 — Wire Orchestrator → Dependency-Diagnosis fallback, **path-scoped**: when `cross_path_comparison_sub_agent` finds asymmetric completeness across paths, re-run Dependency-Diagnosis for only the deficient path, not the full stage; integration test confirming the other paths are untouched
  Commit: `Update - 7.5.9 - orchestrator path-scoped fallback`
- [ ] 7.5.10 — Partial-verdict terminal state: when the loop-guard cap is hit before a stage becomes sufficient, the pipeline returns a verdict with explicit per-path caveat flags instead of hard-failing or looping indefinitely; unit + integration test forcing the cap and asserting a caveat-flagged (not null) verdict
  Commit: `Update - 7.5.10 - partial-verdict terminal state on loop-guard exceeded`
- [ ] 7.5.11 — Extend API response schema (`api/schemas/`) to include a `recalibration_trail`: which stages looped back, why, and how many iterations — supports FR-4/FR-5 explainability; update `POST /decisions` integration test to assert the trail is present and empty for a clean run
  Commit: `Update - 7.5.11 - recalibration trail in API response`
- [ ] 7.5.12 — Full end-to-end verification pass: one real (non-mocked) decision brief run through the pipeline confirming at least one deliberate insufficient-input scenario triggers a fallback, resolves within the retry cap, and produces a fully populated verdict
  Commit: `Update - 7.5.12 - end-to-end recalibration verification pass`

**Checkpoint:** Pipeline is a conditional, stage-gated graph — not a straight sequence — with bounded, targeted backward recalibration and a documented terminal state. This is the checkpoint to demo to the guide before frontend work resumes.

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
- Backend (Phases 1–7.5) is a hard gate before Phase 8 begins. Phase 7.5 was added after the Level 1 synopsis review to replace the sequential-only pipeline with a conditional, self-correcting one — see `ARCHITECTURE.md` §3.8 and §6.