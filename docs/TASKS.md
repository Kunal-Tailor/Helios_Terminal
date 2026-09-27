# TASKS.md — Helios Terminal Implementation Plan

## How to use this file

- Work **one task at a time**, top to bottom, phase by phase.
- Each task below is sized to be **one commit** — not a batch of commits, not a partial commit.
- Do not start a task until the previous one is committed and (where applicable) passes its check.
- Do not jump ahead to a later phase "while you're at it" — if a task in a later phase seems easier to do while working on the current one, note it here as a future task instead and stay on the current one.
- Backend is built fully before frontend work begins (Phases 1–7.5 before Phase 8).
- Frontend is now split into two parts, built in order: Website Architecture (Phase 8) fully complete before Dashboard Architecture (Phase 9) begins, and Integration (Phase 10) only after both exist.
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

- [x] 7.5.1 — `backend/app/verification/recalibration.py` — `RecalibrationRequest` data structure: `from_stage`, `to_stage`, `reason` (`insufficient` | `unverified`), `gap_description`, `iteration_count`; unit test for construction/serialization
  Commit: `Update - 7.5.1 - RecalibrationRequest data structure`
- [x] 7.5.2 — Sufficiency-check function (in `recalibration.py`, reusing `verifier.py`'s pattern) — per-stage threshold checks: e.g. Stack-Mapping has 0–1 surviving layers, Scenario-Generation has <2 viable options after feasibility filtering; unit tests with a known-sufficient and known-insufficient case per stage
  Commit: `Update - 7.5.2 - sufficiency-check function per stage`
- [x] 7.5.3 — Loop-guard: per-`(from_stage, to_stage)` iteration counter carried in pipeline state, capped at 2 retries; unit test confirming the cap is enforced and does not reset across unrelated stage pairs
  Commit: `Update - 7.5.3 - loop-guard iteration tracking`
- [x] 7.5.4 — Context accumulation helper — recalibration appends targeted new data to the existing context object rather than discarding/replacing it; unit test confirming prior context survives a re-ingestion pass
  Commit: `Update - 7.5.4 - context accumulation on re-ingestion`
- [x] 7.5.5 — Wire Stack-Mapping → Ingestion fallback in `pipeline/graph.py`: on insufficient layer mapping, re-invoke Ingestion scoped to the `gap_description` only; integration test (mocked LLM) confirming the loop-back fires and the pipeline continues after
  Commit: `Update - 7.5.5 - stack-mapping to ingestion fallback wiring`
- [x] 7.5.6 — Wire Scenario-Generation fallback routing: on insufficient/generic scenarios, decide target (Stack-Mapping if layer scope too narrow, Ingestion if missing concrete option data e.g. no known vendors) and route accordingly; integration test covering both target branches
  Commit: `Update - 7.5.6 - scenario-generation fallback routing (dual target)`
- [x] 7.5.7 — Wire Outcome-Prediction → Scenario-Generation fallback: on repeated grounded_in failures or low path differentiation, invoke `scenario_refinement_sub_agent` (5.11, previously optional/unused) instead of a blind Scenario-Generation re-run; integration test
  Commit: `Update - 7.5.7 - outcome-prediction fallback invokes scenario refinement`
- [x] 7.5.8 — Wire Dependency-Diagnosis → Outcome-Prediction fallback: on generic/non-specific lock-in output, invoke `timeline_projection_sub_agent` (5.15, previously optional/unused) if it was skipped; integration test
  Commit: `Update - 7.5.8 - dependency-diagnosis fallback invokes timeline projection`
- [x] 7.5.9 — Wire Orchestrator → Dependency-Diagnosis fallback, **path-scoped**: when `cross_path_comparison_sub_agent` finds asymmetric completeness across paths, re-run Dependency-Diagnosis for only the deficient path, not the full stage; integration test confirming the other paths are untouched
  Commit: `Update - 7.5.9 - orchestrator path-scoped fallback`
- [x] 7.5.10 — Partial-verdict terminal state: when the loop-guard cap is hit before a stage becomes sufficient, the pipeline returns a verdict with explicit per-path caveat flags instead of hard-failing or looping indefinitely; unit + integration test forcing the cap and asserting a caveat-flagged (not null) verdict
  Commit: `Update - 7.5.10 - partial-verdict terminal state on loop-guard exceeded`
- [x] 7.5.11 — Extend API response schema (`api/schemas/`) to include a `recalibration_trail`: which stages looped back, why, and how many iterations — supports FR-4/FR-5 explainability; update `POST /decisions` integration test to assert the trail is present and empty for a clean run
  Commit: `Update - 7.5.11 - recalibration trail in API response`
- [x] 7.5.12 — Full end-to-end verification pass: one real (non-mocked) decision brief run through the pipeline confirming at least one deliberate insufficient-input scenario triggers a fallback, resolves within the retry cap, and produces a fully populated verdict
  Commit: `Update - 7.5.12 - end-to-end recalibration verification pass`

**Checkpoint:** Pipeline is a conditional, stage-gated graph — not a straight sequence — with bounded, targeted backward recalibration and a documented terminal state. This is the checkpoint to demo to the guide before frontend work resumes.

---

## Frontend, Part 1 — Website Architecture (Phase 8)

Context: the original unified dark-terminal frontend (old Phases 8–10 above) was reset — see `Update - 8.0 - reset frontend directory for full restart`. The frontend is now split into two builds sharing one Vite/React app: a light, static **marketing site** (this phase) and a dark, dense **Dashboard** (Phase 9, detailed later). Full spec lives in `docs/frontend-website-architecure/` (all 9 files) and `docs/frontend-website-architecure/Helios-Terminal-Marketing-Site-Design-Spec.md` (via `frontend-docs-website` at the time of commit `Update - 8.1 - frontend-docs-website addition`, now superseded). Read the relevant `frontend-website-architecure` file before implementing each task below.

Each page is built in one pass rather than component-by-component — an IDE agent can assemble a full page from the screen inventory + design system docs in one go. Iteration on a page (if a first pass doesn't land right) gets added as its own follow-up task under that page's section once reviewed, rather than pre-planned here.

### 8A — Setup & Shared Components

- [x] 8.2 — Vite + React 18 scaffold, Tailwind config, `site-theme.css` design tokens per `05_DESIGN_SYSTEM.md`; confirm `npm run dev` runs
  Commit: `Update - 8.2 - Vite scaffold, Tailwind, and site design tokens`
- [x] 8.3 — Routing skeleton (`/`, `/architecture`, `/about`, `/team`, placeholder `/dashboard`) + shared `SiteHeader`, `SiteFooter`, and `Button` components per `06_COMPONENT_BREAKDOWN.md`
  Commit: `Update - 8.3 - routing and shared header/footer/button`

### 8B — Home Page

- [x] 8.4 — Build the full Home page in one pass — hero, problem teaser, pipeline strip, three pillars, Dashboard CTA band, wired to header/footer — per `04_SCREEN_INVENTORY.md`
  Commit: `Update - 8.4 - home page`

### 8C — Architecture Page

- [x] 8.5 — Build the full Architecture page in one pass — intro, pipeline diagram (forward + dashed recalibration edges), recalibration step sequence, tech stack strip, CTA
  Commit: `Update - 8.5 - architecture page`

### 8D — About Page

- [x] 8.6 — Build the full About page in one pass — editorial hero, narrative column, persona list, pull-quote, synopsis download card
  Commit: `Update - 8.6 - about page`

### 8E — Team Page

- [x] 8.7 — Build the full Team page in one pass — intro, four-card team grid, contribution note
  Commit: `Update - 8.7 - team page`

### 8F — Cross-Page Pass

- [x] 8.8 — Responsive, accessibility, and motion consistency pass across all four pages in one commit
  Commit: `Update - 8.8 - website responsive, accessibility, and motion pass`

**Checkpoint:** Website Architecture (Home, Architecture, About, Team) is complete, responsive, and accessible, with the Dashboard CTA wired to a placeholder route. This is the checkpoint before Dashboard Architecture work begins.

---

## Frontend, Part 2 — Dashboard Architecture (Phase 9)

Context: the Bloomberg-style decision intelligence workstation at `/dashboard`. Full spec lives in `docs/frontend-dashboard-architecture/` (all 9 files). Read the relevant doc before reviewing any task below. All tasks in this phase are complete — Kunal built the entire dashboard.

### 9A — Foundation: Design Tokens + Folder Structure

- [x] 9.1 — Create `frontend/src/dashboard/` folder structure (pages/, components/, api.ts, data/, utils/, styles/); add `terminal.css` with all `--bb-*` CSS custom property design tokens — backgrounds, borders, accent colors (amber `#FF9E00`, cyan `#00E5FF`, green `#00FF66`, red `#FF3366`, purple `#B388FF`), typography tokens, and component primitives (`.bloomberg-terminal`, `.bb-panel`, `.bb-panel-header`, `.bb-badge`, `.bb-button`, `.bb-scroll`, `.bb-ticker-track`, `.bb-live-indicator`, `.bb-scanline`); import in dashboard entry point
  Commit: `Update - 9.1 - dashboard folder structure and terminal.css design tokens`

### 9B — Navigation Shell

- [x] 9.2 — Build `BloombergHeader.tsx` — top telemetry strip (brand link, health beacon using `isLiveServerConnected`, active preset badge, pipeline status badge with 5 states, sound toggle, dual UTC/local clock); `<GO>` command bar with autocomplete dropdown (13 command suggestions, filtered on input, dismissed by Escape, triggered by `/` or `Cmd+K` global hotkey); F1–F9 function key ribbon with per-tab color accents (amber/cyan/red/green/purple/amber/amber); live AI market ticker tape (`bb-ticker-track` 40s loop, pauses on hover); export `ActiveWorkstationTab` union type
  Commit: `Update - 9.2 - BloombergHeader command bar, telemetry, and function key ribbon`

### 9C — Decision Console

- [x] 9.3 — Build `BloombergDecisionConsole.tsx` — institutional preset grid (3 presets, selected state with amber highlight + checkmark); entity input (field 01); capability input (field 02); sourcing paths chip list with add/remove (field 03, Enter key on add field); strategic constraints matrix — DATA SOVEREIGNTY toggle (CRITICAL/STANDARD/LOW, amber fill on active) and LATENCY/SLA toggle (SUB_20MS/BALANCED/BATCH, cyan fill on active); `EXECUTE SOURCING VERDICT <GO>` primary button with spinner during submission
  Commit: `Update - 9.3 - BloombergDecisionConsole decision brief input form`

### 9D — Agent Pipeline Topology

- [x] 9.4 — Build `AgentPipelineTopology.tsx` — 6-stage sequential pipeline visualization: Ingestion → Stack Mapping → Scenario Generation → Outcome Prediction → Dependency Diagnosis → Comparative Verdict; per-stage verification result badges (pass/fail, confidence score) mapped from `verificationResults` prop by `agent_stage` field; recalibration loop-back arrows from `recalibrationTrail` prop; idle/processing/completed/failed state rendering
  Commit: `Update - 9.4 - AgentPipelineTopology 6-stage visualization`

### 9E — Institutional Verdict Panel

- [x] 9.5 — Build `InstitutionalVerdictPanel.tsx` — empty state (Award icon, awaiting copy) when `verdict === null`; recommended path green-tinted banner; verdict summary narrative; path-by-path stances matrix (stance badge color: green for RECOMMENDED/OPTIMAL/ACCEPTABLE, red for CRITICAL/UNACCEPTABLE/HIGH RISK, amber otherwise); actionable implementation directives list; strategic caveats amber-tinted box; VERIFIED DECISION / PARTIAL VERIFICATION header badge based on `verificationPassed` prop
  Commit: `Update - 9.5 - InstitutionalVerdictPanel sovereign recommendation display`

### 9F — Trajectory Chart Panel

- [x] 9.6 — Build `TrajectoryChartPanel.tsx` using Recharts — year-by-year (Y0–Y5) TCO line chart (three series: buildTco, buyTco, outsourceTco) and lock-in severity chart (three series: buildLockIn, buyLockIn, outsourceLockIn on 0–10 scale); comparative narrative from `cross_path_comparison.comparative_narrative`; per-path comparison summary cards from `cross_path_comparison.path_comparisons` (lock_in_count, max_severity_score, key_tradeoffs)
  Commit: `Update - 9.6 - TrajectoryChartPanel Recharts 5-year TCO and lock-in charts`

### 9G — Lock-In Matrix View

- [x] 9.7 — Build `LockInMatrixView.tsx` — tabular heatmap of `lockInVectors` data; five lock-in dimensions as rows (e.g. Data Sovereignty, Model Weights Portability, Export Control, TCO Scalability, Talent Ownership); three sourcing path columns (Build, Buy, Outsource); per-cell severity score rendered as color-coded bar/badge (green 1–3, amber 4–6, red 7–10); criticalNotes rendered below each dimension row
  Commit: `Update - 9.7 - LockInMatrixView layer-by-layer exposure heatmap`

### 9H — Audit Inspector

- [x] 9.8 — Build `AuditInspector.tsx` and `AuditTrail.tsx` — overall verification status banner (green PASSED / red FAILED AT STAGE); verification results table (per-stage: stage name, claim, confidence %, pass/fail badge, reason); explanation trail section (summary, step-by-step table with stage/claim/evidence and grounded/inference badge, sources list as links); recalibration trail cards (from_stage → to_stage, reason, gap_description, iteration_count)
  Commit: `Update - 9.8 - AuditInspector and AuditTrail verification claim ledger`

### 9I — Intel Feed Panel

- [x] 9.9 — Build `IntelFeedPanel.tsx` — live intelligence feed panel rendering retrieved source items by type: Tavily web search (titles, URLs, relevance), HuggingFace Hub (model cards, license metadata), BIS Entity Lists (entity watch entries, jurisdiction flags); structured feed layout with source-type headers and item cards
  Commit: `Update - 9.9 - IntelFeedPanel live intelligence source stream`

### 9J — Global Map + Supply Chain Graph

- [x] 9.10 — Build `BloombergGlobalMap.tsx` (interactive SVG world map — data center locations, semiconductor origins, vendor corporate jurisdictions, hover tooltips with jurisdiction details) and `BloombergSupplyChainGraph.tsx` (directed dependency graph — model weight providers, compute dependencies, vendor relationships; node colors by sovereignty risk tier; edge thickness by dependency weight)
  Commit: `Update - 9.10 - BloombergGlobalMap and BloombergSupplyChainGraph`

### 9K — Executive Dossier Modal

- [x] 9.11 — Build `ExecutiveDossierModal.tsx` — full-viewport overlay (`z-50`); printable memo layout: HELIOS INTELLIGENCE // EXECUTIVE DECISION MEMO header, entity/capability/timestamp; recommended path; verdict summary; path stances table; key recommendations numbered list; caveats; verification status; close button (`onClose` prop); print-optimized layout suitable for browser print-to-PDF
  Commit: `Update - 9.11 - ExecutiveDossierModal printable executive briefing`

### 9L — API Client

- [x] 9.12 — Build `frontend/src/dashboard/api.ts` — `API_BASE` from `import.meta.env.VITE_API_BASE_URL` with fallback to `http://127.0.0.1:8000`; full TypeScript interface suite mirroring live backend Pydantic schemas (`DecisionRequest`, `DecisionResponse`, `OrchestratorVerdict`, `CrossPathComparison`, `PathComparison`, `ExplanationTrail`, `AuditStep`, `VerificationResult`, `RecalibrationTrailItem`, `JobStatusResponse`); `submitDecision()` — `POST /decisions/async`; `pollJobStatus()` — `GET /decisions/jobs/{job_id}`; `submitDecisionSync()` — `POST /decisions` (test/fallback utility)
  Commit: `Update - 9.12 - dashboard API client with typed async submit and polling`

### 9M — Preset Scenarios + Offline Synthesis

- [x] 9.13 — Build `frontend/src/dashboard/data/presetScenarios.ts` — `PresetScenario` interface (id, code, title, category, description, brief, result, trajectoryData, lockInVectors); three full institutional presets: DEF-SLM (Indian Army Signals Directorate — tactical edge SLM with 6-year trajectory data and 5 lock-in vectors), FIN-RAG (Global Tier-1 Investment Bank AMR Capital — financial RAG), MED-AI (MetroHealth Regional Hospital System — HIPAA clinical copilot); each preset has a complete pre-computed `DecisionResponse` with verdict, verification_results, explanation_trail, and recalibration_trail
  Commit: `Update - 9.13 - preset scenarios data and offline synthesis fallback`

### 9N — Dashboard Main Page (State Machine Wiring)

- [x] 9.14 — Build `frontend/src/dashboard/pages/DashboardPlaceholder.tsx` — `WorkstationState` type; all state variables (activeTab, state, jobStatus, selectedPreset, result, error, isLiveServerConnected, dossierModalOpen, focusedQuadrant); mount health-check `useEffect` (`GET /health`); polling loop via `useRef<setInterval>` at `POLL_INTERVAL_MS = 2500` with cleanup; `handleSubmit` (submit → polling → completed/failed, offline fallback with 1200ms simulated delay and entity fuzzy-match); `handleSelectPreset`; `handleExecuteCommand` (full command routing for all 9 tabs + DEMO DEF/FIN/MED + CLEAR/RESET + HELP alert); render: `BloombergHeader`, 9 conditional views in `<main>`, footer strip, `ExecutiveDossierModal` overlay
  Commit: `Update - 9.14 - DashboardPlaceholder state machine and full workstation wiring`

### 9O — Terminal Audio Engine

- [x] 9.15 — Build `frontend/src/dashboard/utils/terminalAudio.ts` — `TerminalAudioEngine` class with lazy `AudioContext` initialization (with `webkitAudioContext` Safari fallback and suspended-context resume); mute state loaded/persisted to `localStorage` key `helios_terminal_sound_muted`; four synthesized sounds: `playBlip()` (sine 880Hz→1200Hz, 40ms — focus/click/tab), `playGoCommand()` (square 520→780→1040Hz steps, 90ms — command submit), `playSuccessChime()` (sine D5/A5/D6 staggered 70ms, 180ms each — job completed), `playWarning()` (sawtooth 220→180Hz, 160ms — job failed); `toggleMute()` plays confirmation blip on unmute; exported singleton `terminalAudio`
  Commit: `Update - 9.15 - terminalAudio Web Audio API sound effects engine`

**Checkpoint:** Dashboard Architecture is complete — Bloomberg-style dark workstation at `/dashboard` with 9 workstation views (F1–F9), a `<GO>` command bar, 5-state async pipeline state machine, offline synthesis fallback, Recharts trajectory charts, lock-in matrix, grounded audit inspector, global infrastructure map, supply chain graph, executive dossier modal, and Web Audio API sound engine. All views are populated from preset data on first load. Full spec documented in `docs/frontend-dashboard-architecture/`.

---

## Integration (Phase 10)

Context: wiring the completed Dashboard (Phase 9) to the live backend, multi-provider LLM reliability, end-to-end testing, and cross-cutting polish. The fallback chain (10.3) was moved ahead of the E2E test (10.5) and polish pass (10.6) because both of those tasks require a backend that can actually complete a pipeline run — production testing showed the single-provider setup (Gemini free tier, 5 RPM) stalls mid-run on rate limits, which would make 10.4/10.5 as originally ordered untestable in practice.

- [x] 10.1 — Replace the Phase 8.3 placeholder `/dashboard` route with the real `Dashboard` component from `DashboardPlaceholder.tsx`; confirm the full site routes work together (`/`, `/architecture`, `/about`, `/team`, `/dashboard`)
  Commit: `Update - 10.1 - wire live Dashboard component to /dashboard route`

- [x] 10.2 — Wire `VITE_API_BASE_URL` environment variable — create `.env.example` for frontend with `VITE_API_BASE_URL=http://127.0.0.1:8000`; confirm the dashboard uses the env var in both dev and production builds
  Commit: `Update - 10.2 - VITE_API_BASE_URL env var wiring`

### 10.3 — Multi-Provider LLM Fallback Chain (moved ahead of E2E/polish — see context above)

CONSTRAINT for all of 10.3: every existing test currently passing must keep passing, unmodified. The existing call_llm-equivalent function signature in `backend/app/llm/client.py` must not change. `LLM_PROVIDER_MODE=manual` must reproduce the exact current single-provider behavior with zero fallback logic invoked — byte-for-byte the same code path as today.

- [x] 10.3.1 — Replace `.env.example` (backend) with the 4-provider structure: `LLM_PROVIDER_MODE` (manual|auto), `LLM_PROVIDER_CHAIN` (comma-separated), `LLM_PROVIDER_COOLDOWN_SEC`, `LLM_PROVIDER_MAX_RETRIES_PER_CALL`, and per-provider key/base_url/model triplets for `nvidia_nim`, `openrouter`, `gemini`, `deepseek_direct`. Config file only, no code changes.
  Commit: `Update - 10.3.1 - redesign env for multi-provider fallback chain`

- [x] 10.3.2 — Extend `backend/app/core/config.py` to parse the new env vars and build a per-provider config object (api_key, base_url, model) for each of the four providers. Unit test for valid and malformed `LLM_PROVIDER_CHAIN` values.
  Commit: `Update - 10.3.2 - parse multi-provider config`

- [x] 10.3.3 — Add `backend/app/llm/errors.py` defining `RateLimitError`, `AuthError`, `ServerError`, plus a mapper from HTTP status / provider SDK exception to the right type — reuse existing status-code mapping logic in `client.py` rather than duplicating it. Unit test covering 429, 401/403, 5xx, and the Gemini-specific 503 "UNAVAILABLE" case seen in production logs.
  Commit: `Update - 10.3.3 - provider error taxonomy`

- [x] 10.3.4 — Add one adapter function per provider (`nvidia_nim`, `openrouter`, `gemini`, `deepseek_direct`) taking (prompt, config) and returning text, raising `errors.py` exception types on failure. Extract from the provider logic already inside `client.py`'s single call function — don't duplicate. Unit test per adapter with a mocked response.
  Commit: `Update - 10.3.4 - per-provider adapter functions`

- [x] 10.3.5 — Add an in-memory cooldown tracker (dict of provider name → cooldown-until timestamp) and a `call_llm_with_fallback()` wrapper: if `LLM_PROVIDER_MODE=manual`, calls the single configured provider directly, no fallback logic; if `auto`, iterates `LLM_PROVIDER_CHAIN`, skips providers in cooldown, on `RateLimitError`/`AuthError`/`ServerError` sets cooldown and tries the next provider for the SAME call, returns on first success, raises `AllProvidersExhaustedError` if the chain is exhausted. Wraps the existing single-provider function — doesn't replace its signature.
  Commit: `Update - 10.3.5 - cooldown tracker and fallback wrapper`

- [x] 10.3.6 — Wire `call_llm_with_fallback()` into the six agents' call sites, replacing direct calls to the old single-provider function. Confirm every existing unit/integration test still passes unmodified; only touch a test file if it called the old function by name and needs an import path update (note explicitly in commit message).
  Commit: `Update - 10.3.6 - wire fallback wrapper into agent call sites`

- [ ] 10.3.7 — Add fallback-specific tests: (a) forced `RateLimitError` on provider 1 falls through to provider 2, (b) all providers exhausted raises `AllProvidersExhaustedError`, (c) a provider within cooldown is skipped without being called again, (d) `LLM_PROVIDER_MODE=manual` never invokes chain/cooldown logic.
  Commit: `Update - 10.3.7 - fallback and cooldown test coverage`

- [ ] 10.3.8 — Record which provider served each call into the structure backing `recalibration_trail`/verification metadata (Phase 7.5.11), so the API response shows which provider answered each pipeline stage. Update response schema and its test if the shape changes.
  Commit: `Update - 10.3.8 - log serving provider per call`

- [ ] 10.3.9 — Full manual verification: set `LLM_PROVIDER_CHAIN` to `nvidia_nim,gemini` only, run one real decision brief, then forcibly exhaust `nvidia_nim` and confirm automatic failover to `gemini` mid-run, no manual intervention, no broken endpoint behavior.
  Commit: `Update - 10.3.9 - end-to-end fallback verification pass`

**Checkpoint:** fallback chain proven under real rate-limit exhaustion, all pre-existing tests still green, `LLM_PROVIDER_MODE=manual` behavior unchanged. This is the checkpoint before 10.4.

---

- [ ] 10.4 — Serialize strategic constraints (Data Sovereignty weight, Latency/SLA tolerance) from `BloombergDecisionConsole` into the `DecisionRequest` body sent to `POST /decisions/async` — requires backend schema update if fields are not yet accepted
  Commit: `Update - 10.4 - serialize strategic constraints into API request`

- [ ] 10.5 — End-to-end integration test: submit a live brief from the Decision Console (F2) with the real backend running (multi-provider fallback active), verify the polling loop completes, the verdict populates all four quadrants, the audit trail shows real grounded verification results, and the response includes which provider served each stage (from 10.3.8)
  Commit: `Update - 10.5 - E2E integration test: dashboard to live backend`

- [ ] 10.6 — Cross-cutting polish pass: verify the backend health beacon correctly reflects ONLINE/STANDALONE across different network states — and, now that fallback exists, that a mid-chain provider failover does NOT falsely trigger the offline/STANDALONE state; confirm the offline fallback fires correctly only when the backend itself is genuinely unreachable (not merely rate-limited on one provider); verify the Dossier modal prints cleanly in Chrome and Firefox
  Commit: `Update - 10.6 - integration polish and offline fallback verification`

**Checkpoint:** Integration (Phase 10) is complete — Dashboard wired to a reliability-hardened backend, verified end-to-end, before Deployment (Phase 11) begins.

---

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
- The frontend restart follows the same discipline in three ordered parts: Website Architecture (Phase 8, detailed above) → Dashboard Architecture (Phase 9, documented in `docs/frontend-dashboard-architecture/`) → Integration (Phase 10, tasks listed above). Each part gets its own checkpoint before the next begins, same pattern as Phase 7.5's checkpoint before Phase 8.
