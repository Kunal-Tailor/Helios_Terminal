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
│   │   │   ├── ingestion/
│   │   │   │   ├── ingestion_agent.py         # parent — orchestrates sub-agents below
│   │   │   │   └── sub_agents/
│   │   │   │       ├── web_scraping_sub_agent.py
│   │   │   │       ├── structured_source_sub_agent.py
│   │   │   │       └── context_synthesis_sub_agent.py   # optional
│   │   │   ├── stack_mapping/
│   │   │   │   ├── stack_mapping_agent.py
│   │   │   │   └── sub_agents/
│   │   │   │       ├── layer_identification_sub_agent.py
│   │   │   │       ├── relevance_filter_sub_agent.py
│   │   │   │       └── dependency_linkage_sub_agent.py  # optional
│   │   │   ├── scenario_generation/
│   │   │   │   ├── scenario_generation_agent.py
│   │   │   │   └── sub_agents/
│   │   │   │       ├── option_enumeration_sub_agent.py
│   │   │   │       ├── feasibility_check_sub_agent.py
│   │   │   │       └── scenario_refinement_sub_agent.py  # optional
│   │   │   ├── outcome_prediction/
│   │   │   │   ├── outcome_prediction_agent.py
│   │   │   │   └── sub_agents/
│   │   │   │       ├── trajectory_modeling_sub_agent.py
│   │   │   │       ├── risk_factor_sub_agent.py
│   │   │   │       └── timeline_projection_sub_agent.py  # optional
│   │   │   ├── dependency_diagnosis/
│   │   │   │   ├── dependency_diagnosis_agent.py
│   │   │   │   └── sub_agents/
│   │   │   │       ├── lock_in_identification_sub_agent.py
│   │   │   │       ├── failure_mode_sub_agent.py
│   │   │   │       └── severity_scoring_sub_agent.py  # optional
│   │   │   └── orchestrator/
│   │   │       ├── orchestrator_agent.py
│   │   │       └── sub_agents/
│   │   │           ├── cross_path_comparison_sub_agent.py
│   │   │           ├── verdict_synthesis_sub_agent.py
│   │   │           └── explanation_trail_sub_agent.py  # optional
│   │   ├── verification/
│   │   │   ├── verifier.py         # cross-stage claim verification logic
│   │   │   └── source_store.py     # tracks cited sources per claim
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

- `agents/` has one subfolder per top-level agent (matching ARCHITECTURE.md §3.1-3.6), each containing the parent agent file plus a `sub_agents/` folder for its 2-3 sub-agents. `backend/tests/test_agents/` mirrors this same nesting (e.g. `test_agents/ingestion/test_web_scraping_sub_agent.py`) so each sub-agent stays independently testable.
- `verification/` is intentionally separate from `agents/` since it is a cross-cutting layer used at every stage boundary, not a pipeline stage itself.
- `pipeline/graph.py` is where the stage-gated flow (agent → verify → next agent) is actually wired together.
- `models/` under backend is left minimal for MVP since persistence (saved decision history) is a "Should/Could" feature, not required for the core pipeline.