# Helios Terminal

An AI-powered multi-agent decision intelligence platform for **AI sourcing strategy and dependency risk analysis** — it takes one concrete build/buy/outsource decision and returns a side-by-side comparison of the long-term dependency risk each path creates.

## The problem

Every organisation adopting AI faces the same fork in the road: build the capability in-house, buy a ready-made model, or hand it to an outside vendor. Each path quietly locks the organisation into a different kind of dependency — one that may only surface years later, when a vendor changes terms, a licence expires, or a partner disappears. Today that call is made on instinct and vendor pitches, with no structured way to see what each option costs down the line.

## What Helios Terminal does

Helios focuses on **one sourcing decision at a time** and answers a single question: *of the available options, which creates the least dangerous long-term dependency?*

A user describes the decision — entity, capability needed, candidate options (or leave them blank and let Helios infer a realistic set). A six-agent pipeline takes it from there and ends in a comparative verdict: every path, the lock-in it creates, and what breaks later if unmanaged — delivered ahead of the decision, not after it.

## How it works

```
Decision brief ─▶ Ingestion ─▶ Stack-Mapping ─▶ Scenario-Generation
                                                      │
Comparative verdict ◀─ Orchestrator ◀─ Dependency-Diagnosis ◀─ Outcome-Prediction
```

| Stage | Role |
| --- | --- |
| **Ingestion** | Gathers context relevant to this specific decision (web search + structured sources such as HF Hub, BIS Entity List) |
| **Stack-Mapping** | Narrows to the AI-stack layers the decision actually touches |
| **Scenario-Generation** | Lays out realistic paths (build / buy / outsource, or the true option set) |
| **Outcome-Prediction** | Projects where each path plausibly leads |
| **Dependency-Diagnosis** | Names the lock-in each outcome creates and what breaks if unmanaged |
| **Orchestrator** | Combines the analyses into one comparative verdict |

Each top-level agent orchestrates 2–3 sub-agents (18 LLM-calling components in total). Between every stage, a **cross-stage verification layer** checks the agent's claims against its cited sources before handing off — each agent's claims are registered as `grounded_in` a retrieved source or flagged as `inference`, so downstream agents never build on unverified upstream claims, and a failed gate halts the pipeline rather than propagating bad output.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full component breakdown and rationale.

## Tech stack

| Layer | Technology |
| --- | --- |
| Frontend | React 18 + Vite, TypeScript, Tailwind CSS, TanStack Query, React Router, react-flow (`@xyflow/react`) |
| Backend | Python 3.11, FastAPI, Pydantic v2 |
| Multi-agent pipeline | Hand-rolled stage-gated orchestration in `backend/app/pipeline/graph.py` (sequential agents + parallel sub-agents; no agent framework dependency) |
| LLM layer | Provider-agnostic client (`backend/app/llm/client.py`) — DeepSeek V4 Flash pinned by default; OpenRouter / Anthropic / OpenAI switchable via env vars |
| Grounding | Tavily web-search retrieval |

## Project structure

```
helios-terminal/
├── backend/        FastAPI API + six-agent pipeline + verification layer + tests (pytest)
├── frontend/       React terminal UI: input form, pipeline status, result view, dashboard
├── docs/           Product & architecture docs (PRD, vision, architecture, TASKS plan)
│   └── frontend-docs/   Interface-specific docs (UX flows, design system, components)
├── infra/          Docker & deployment configs (Phase 11 — pending)
└── .github/        CI workflows (pending)
```

Full layout: [docs/FOLDER_STRUCTURE.md](docs/FOLDER_STRUCTURE.md).

## Getting started

Prerequisites: **Python 3.11**, **Node.js 18+**, and API keys (an LLM provider plus [Tavily](https://app.tavily.com)).

### Backend

```bash
cd backend
pip install -r requirements.txt
copy .env.example .env        # then fill in your keys (see below)
uvicorn app.main:app --reload
```

The API serves at `http://127.0.0.1:8000` (health check: `GET /health`).

Required environment variables (see `backend/.env.example`):

- `LLM_PROVIDER` — `deepseek` (default) or `openrouter`
- `DEEPSEEK_API_KEY` or `OPENROUTER_API_KEY` — matching the provider above
- `TAVILY_API_KEY` — retrieval augmentation used by the ingestion and verification layers
- Optional: `DEFAULT_MODEL`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`

Run the backend test suite (350 tests, fully mocked — no network calls):

```bash
cd backend
python -m pytest
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. It expects the backend at `http://localhost:8000`; to point elsewhere, set `VITE_API_BASE_URL` in `frontend/.env.local`:

```
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Usage

Through the UI: enter an entity and capability, optionally add candidate option chips (leave blank and Helios infers the option set), submit, watch the six-stage status strip, and read the verdict — path cards, severity bands, and a dependency graph in the dashboard view.

Via the API directly:

```bash
curl -X POST http://127.0.0.1:8000/decisions \
  -H "Content-Type: application/json" \
  -d '{
    "entity": "Indian Army signals division",
    "capability": "small language model for edge inference",
    "options": ["build in-house", "license open-weight"]
  }'
```

Omitting `options` (or sending `[]`) triggers system inference of the option set. A full run takes minutes — the response includes the comparative `verdict` (`recommended_path`, `verdict_summary`, per-path comparisons with numeric severity scores) and the flat `verification_passed` / `verification_failed_stage` audit fields. Response shapes are documented in [docs/frontend-docs/07_API_CONTRACT.md](docs/frontend-docs/07_API_CONTRACT.md), synced against the live Pydantic schemas in `backend/app/api/schemas/`.

## Current status

Built and working (per [docs/TASKS.md](docs/TASKS.md), Phases 1–9):

- Full six-agent backend pipeline with stage-gated verification, sync + async endpoints, and 350 passing mocked tests
- Complete frontend flow: decision input → inline pipeline status → result view → multi-pane dashboard with dependency graph and command bar, styled with the design-system tokens

Not yet done:

- Phase 10 — end-to-end manual verification pass (including deliberate verification-failure cases), accessibility/motion pass, final aesthetic review
- Phase 11 — Dockerfiles, docker-compose, Render/Vercel deployment configs, CI workflows

Known MVP limitations: no persistence or decision history (in-memory async job store), verification is a keyword-presence heuristic rather than semantic checking, and the UI is desktop-only by design.

## Team

Capstone project (CSE-AIDS, Level 1), Department of Computer Engineering & Technology, MIT-WPU — in-house research project, Panel B:

- Rishav Singh
- Kunal Tailor
- Prakash
- Neeraj Gupta
