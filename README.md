<div align="center">

# Helios Terminal

**AI-Powered Multi-Agent Decision Intelligence Platform**

*AI sourcing strategy and dependency risk analysis*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![React 18](https://img.shields.io/badge/react-18.0-cyan.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.104-green.svg)](https://fastapi.tiangolo.com/)

</div>

---

## 🎯 Overview

Helios Terminal is a sophisticated decision intelligence platform that analyzes AI sourcing decisions (build/buy/outsource) and their long-term dependency risks. It takes a concrete decision brief and returns a comparative analysis of each path's hidden costs and lock-in risks.

**🔍 One Decision at a Time** — Focuses on single sourcing decisions with deep analysis rather than broad, shallow recommendations.

**🔗 Dependency Risk Mapping** — Identifies lock-in mechanisms, failure modes, and long-term consequences of each sourcing option.

**✅ Verification-Gated Pipeline** — Six-agent pipeline with cross-stage verification ensuring claims are grounded in sources before propagation.

---

## 🚀 Problem Statement

Every organization adopting AI faces the same critical decision: build capability in-house, license a model, or outsource to vendors. Each path creates different dependency structures that may only surface years later through:

- Vendor term changes and pricing shifts
- License expirations and compliance risks  
- Partner acquisition or discontinuation
- Technical debt and migration costs

Today these decisions are made on instinct and vendor pitches without structured visibility into long-term dependency risks.

---

## 💡 Solution

Helios answers one fundamental question: **Which sourcing option creates the least dangerous long-term dependency?**

**Input:** Entity, capability needed, candidate options (or auto-inferred)
**Process:** Six-agent analysis pipeline with verification gates
**Output:** Comparative verdict with lock-in analysis, severity scoring, and dependency graph

### Pipeline Architecture

```
Decision Brief
       │
       ▼
┌──────────────┐
│  Ingestion   │ ← Context gathering (web search + structured sources)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│Stack-Mapping │ ← AI-stack layer identification
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│Scenario-Generation│ ← Realistic path enumeration
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│Outcome-Prediction│ ← Future trajectory projection
└──────┬───────────┘
       │
       ▼
┌─────────────────────┐
│Dependency-Diagnosis │ ← Lock-in identification & failure modes
└──────┬──────────────┘
       │
       ▼
┌──────────────┐
│ Orchestrator │ ← Comparative verdict synthesis
└──────┬───────┘
       │
       ▼
 Comparative Verdict
```

### Agent Capabilities

| Agent | Function |
|-------|----------|
| **Ingestion** | Gathers decision-specific context via web search + structured sources (HF Hub, BIS Entity List) |
| **Stack-Mapping** | Identifies relevant AI-stack layers for the decision |
| **Scenario-Generation** | Enumerates realistic sourcing paths (build/buy/outsource variants) |
| **Outcome-Prediction** | Projects plausible future trajectories for each path |
| **Dependency-Diagnosis** | Identifies lock-in mechanisms and failure modes per outcome |
| **Orchestrator** | Synthesizes comparative verdict with severity scoring |

Each top-level agent orchestrates 2–3 sub-agents (18 LLM-calling components total). Between stages, a **cross-stage verification layer** validates claims against cited sources, registering each as `grounded_in` sources or `inference`.

---

## 🛠️ Tech Stack

### Frontend
- **Framework:** React 18 + Vite
- **Language:** TypeScript
- **Styling:** Tailwind CSS with custom design tokens
- **State Management:** TanStack Query
- **Routing:** React Router
- **Visualization:** react-flow (`@xyflow/react`)

### Backend
- **Framework:** FastAPI (Python 3.11)
- **Validation:** Pydantic v2
- **Testing:** pytest (350+ tests, fully mocked)

### Multi-Agent Pipeline
- **Architecture:** Hand-rolled stage-gated orchestration
- **Pattern:** Sequential agents with parallel sub-agents
- **Design:** No external agent framework dependency

### LLM Integration
- **Client:** Provider-agnostic wrapper (`backend/app/llm/client.py`)
- **Default:** DeepSeek V4 Flash
- **Alternatives:** OpenRouter, Anthropic, OpenAI (switchable via env vars)

### Grounding & Retrieval
- **Web Search:** Tavily API for context augmentation
- **Verification:** Cross-stage claim validation against sources

---

## 📁 Project Structure

```
helios-terminal/
├── backend/              # FastAPI API + multi-agent pipeline
│   ├── app/
│   │   ├── agents/      # Six parent agents + 18 sub-agents
│   │   ├── api/         # REST endpoints + schemas
│   │   ├── llm/         # LLM client wrapper
│   │   ├── pipeline/    # Stage-gated orchestration
│   │   ├── retrieval/   # Web search retrieval
│   │   └── verification/ # Claim validation layer
│   └── tests/           # 350+ pytest tests
├── frontend/             # React terminal UI
│   ├── src/
│   │   ├── components/  # Decision input, status, verdict, graph
│   │   ├── pages/       # Route components
│   │   └── lib/         # API client + utilities
├── docs/                 # Product & architecture documentation
│   ├── frontend-docs/   # Interface-specific docs
│   └── *.md             # PRD, vision, architecture, TASKS
├── infra/                # Docker & deployment configs
└── .github/              # CI workflows
```

---

## 🚦 Getting Started

### Prerequisites
- **Python 3.11+**
- **Node.js 18+**
- **API Keys:** LLM provider + [Tavily](https://app.tavily.com)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env          # Configure your API keys
uvicorn app.main:app --reload
```

**Environment Variables** (`.env`):
```env
LLM_PROVIDER=deepseek         # or openrouter
DEEPSEEK_API_KEY=your_key     # or OPENROUTER_API_KEY
TAVILY_API_KEY=your_key
```

**Run Tests:**
```bash
cd backend
python -m pytest              # 350+ tests, fully mocked
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` — expects backend at `http://localhost:8000`

**Custom Backend URL:**
```env
# frontend/.env.local
VITE_API_BASE_URL=http://127.0.0.1:8000
```

---

## 📊 Usage

### Web Interface
1. Enter entity and capability
2. Add candidate options (optional — Helios can infer)
3. Submit and watch the six-stage pipeline progress
4. Review comparative verdict with path cards and dependency graph

### API Usage

```bash
curl -X POST http://127.0.0.1:8000/decisions \
  -H "Content-Type: application/json" \
  -d '{
    "entity": "Indian Army signals division",
    "capability": "small language model for edge inference",
    "options": ["build in-house", "license open-weight"]
  }'
```

**Response includes:**
- `verdict.recommended_path` — Optimal sourcing choice
- `verdict.verdict_summary` — High-level analysis
- `verdict.cross_path_comparison.path_comparisons[]` — Per-path analysis with severity scores
- `verification_passed` / `verification_failed_stage` — Audit trail

See [docs/frontend-docs/07_API_CONTRACT.md](docs/frontend-docs/07_API_CONTRACT.md) for full API specification.

---

## ✨ Current Status

### ✅ Completed (Phases 1–9)
- Full six-agent backend pipeline with stage-gated verification
- Synchronous + asynchronous decision endpoints
- 350+ passing mocked tests
- Complete frontend flow: input → pipeline status → result view → dashboard
- Multi-pane dashboard with dependency graph visualization
- Command bar navigation
- Design system implementation with terminal aesthetic

### 🚧 In Progress (Phase 10)
- End-to-end manual verification testing
- Accessibility and motion refinement
- Final aesthetic review

### 📋 Planned (Phase 11)
- Docker containerization
- docker-compose for local development
- Render/Vercel deployment configs
- CI/CD workflows

### ⚠️ Known Limitations
- In-memory job store (no persistence)
- Verification uses keyword-presence heuristic (not semantic)
- Desktop-only UI (1280px+ minimum width)

---

## 📚 Documentation

- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — System architecture and rationale
- **[docs/TASKS.md](docs/TASKS.md)** — Implementation plan and progress tracking
- **[docs/frontend-docs/](docs/frontend-docs/)** — Interface specifications and design system
- **[docs/FOLDER_STRUCTURE.md](docs/FOLDER_STRUCTURE.md)** — Complete project layout

---

## 👥 Team

**Capstone Project (CSE-AIDS, Level 1)**  
Department of Computer Engineering & Technology, MIT-WPU  
*In-house research project — Panel B*

- **Rishav Singh**
- **Kunal Tailor**  
- **Prakash**
- **Neeraj Gupta**

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ for better AI sourcing decisions**

</div>
