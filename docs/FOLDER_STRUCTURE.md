# FOLDER_STRUCTURE.md — Helios Terminal

Proposed repository layout for a React (Vite) frontend + FastAPI backend with a LangGraph/CrewAI-based multi-agent pipeline.

```
helios-terminal/
├── README.md
├── docs/
│   ├── PROJECT_VISION.md
│   ├── PRD.md
│   ├── FEATURES.md
│   ├── TECH_STACK.md
│   ├── ARCHITECTURE.md
│   └── FOLDER_STRUCTURE.md
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── dashboard/          # multi-pane terminal-style layout
│   │   │   ├── command-bar/        # command-driven input UI
│   │   │   ├── dependency-graph/   # react-flow / D3.js visualisation
│   │   │   └── verdict-panel/      # comparative verdict side-by-side view
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── DecisionInput.tsx
│   │   │   └── DecisionResult.tsx
│   │   ├── hooks/
│   │   ├── lib/                    # API client, formatting helpers
│   │   └── styles/
│   └── public/
│
├── backend/
│   ├── pyproject.toml / requirements.txt
│   ├── app/
│   │   ├── main.py                 # FastAPI entrypoint
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── decisions.py    # submit/retrieve decision briefs & results
│   │   │   │   └── health.py
│   │   │   └── schemas/            # pydantic request/response models
│   │   ├── agents/
│   │   │   ├── ingestion_agent.py
│   │   │   ├── stack_mapping_agent.py
│   │   │   ├── scenario_generation_agent.py
│   │   │   ├── outcome_prediction_agent.py
│   │   │   ├── dependency_diagnosis_agent.py
│   │   │   └── orchestrator_agent.py
│   │   ├── verification/
│   │   │   ├── verifier.py         # cross-stage claim verification logic (grounded vs. inference)
│   │   │   ├── source_store.py     # tracks cited sources per claim
│   │   │   └── recalibration.py    # sufficiency checks + RecalibrationRequest + loop-guard (Phase 7.5)
│   │   ├── pipeline/
│   │   │   └── graph.py            # LangGraph/CrewAI pipeline definition & stage gating
│   │   ├── llm/
│   │   │   └── client.py           # Claude / GPT API client wrapper
│   │   ├── retrieval/
│   │   │   └── web_search.py       # retrieval augmentation for grounding
│   │   ├── models/                 # DB models, if persistence is added
│   │   └── core/
│   │       ├── config.py
│   │       └── logging.py
│   └── tests/
│       ├── test_agents/
│       ├── test_verification/
│       └── test_api/
│
├── infra/
│   ├── docker/
│   │   ├── frontend.Dockerfile
│   │   └── backend.Dockerfile
│   ├── docker-compose.yml
│   └── deploy/
│       ├── vercel.json             # frontend deployment config
│       └── render.yaml             # backend deployment config
│
└── .github/
    └── workflows/
        ├── frontend-ci.yml
        └── backend-ci.yml
```

## Notes

- `agents/` maps 1:1 to the six agents in ARCHITECTURE.md — keeps the pipeline auditable and each agent independently testable.
- `verification/` is intentionally separate from `agents/` since it is a cross-cutting layer used at every stage boundary, not a pipeline stage itself.
- `pipeline/graph.py` is where the stage-gated flow (agent → verify → next agent) is actually wired together — as of Phase 7.5 this also includes the conditional backward edges (agent → sufficiency check → recalibrate-or-continue).
- `verification/recalibration.py` is deliberately kept separate from `verifier.py` rather than folded into it: verification checks *correctness* of a claim against its source, recalibration checks *sufficiency* of an upstream stage's output. Same cross-cutting placement as verification, different question being asked.
- `models/` under backend is left minimal for MVP since persistence (saved decision history) is a "Should/Could" feature, not required for the core pipeline.
