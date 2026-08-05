# TECH_STACK.md — Helios Terminal

## Frontend

- **Framework:** React 18 + Vite
- **Styling:** Tailwind CSS
- **Visualisation:** react-flow / D3.js — used for the dependency-graph view and command-bar UI

## Backend / Orchestration

- **Language:** Python 3.11
- **API framework:** FastAPI
- **Multi-agent orchestration:** LangGraph / CrewAI-based orchestration for the six-agent pipeline

## LLM Layer

- **Models:** Claude / GPT API for the reasoning agents (Ingestion, Stack-Mapping, Scenario-Generation, Outcome-Prediction, Dependency-Diagnosis, Orchestrator)
- **Grounding:** Web-search / retrieval augmentation to support the verification layer

## Scenario Engine

- Python-based scenario modelling for build vs. buy vs. outsource branching and outcome projection

## Deployment

- **Containerisation:** Docker
- **Frontend hosting:** Vercel
- **Backend hosting:** Small VM / Render instance

## Hardware (Development)

- Standard development laptop, 8GB+ RAM
- No GPU required for MVP (inference is API-based, not locally hosted)

## Version Control / Project Management

- **VCS:** Git & GitHub
- **PM tooling:** Notion / Jira for sprint tracking

## Rationale Notes

- API-based inference (rather than locally hosted models) keeps hardware requirements low and is appropriate for an MVP where reasoning quality matters more than inference cost control.
- LangGraph/CrewAI is used specifically because the pipeline is a *directed, stage-gated* flow (each agent's output must pass verification before the next agent proceeds) rather than a loose swarm of agents — this favours frameworks with explicit graph/state control.
- react-flow/D3.js is chosen over a simpler charting library because dependency relationships are graph-structured, not just tabular/time-series data.
