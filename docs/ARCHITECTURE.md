# ARCHITECTURE.md — Helios Terminal

## 1. Design Principle

The system takes a **specific sourcing decision** as its starting input, rather than an open-ended entity to monitor. Every downstream agent is scoped by that decision — this is what keeps the pipeline fast and its outputs specific, instead of producing generic organisation-wide AI audits.

## 2. Pipeline Flow

```
User Decision Brief (entity, capability, candidate options)
        │
        ▼
 ┌────────────────────┐
 │  Ingestion Agent    │  gathers context relevant to this decision
 └─────────┬──────────┘
           │  ✓ verified
           ▼
 ┌────────────────────┐
 │ Stack-Mapping Agent │  narrows to the AI stack layers this decision touches
 └─────────┬──────────┘
           │  ✓ verified
           ▼
 ┌─────────────────────────┐
 │ Scenario-Generation Agent│  lays out realistic paths (build / buy / outsource)
 └─────────┬────────────────┘
           │  ✓ verified
           ▼
 ┌─────────────────────────┐
 │ Outcome-Prediction Agent │  projects where each path plausibly leads
 └─────────┬────────────────┘
           │  ✓ verified
           ▼
 ┌───────────────────────────┐
 │ Dependency-Diagnosis Agent │  names the lock-in each outcome creates
 └─────────┬───────────────────┘
           │  ✓ verified
           ▼
 ┌────────────────────┐
 │  Orchestrator Agent │  combines analyses into one comparative verdict
 └─────────┬──────────┘
           │
           ▼
 Helios Terminal Dashboard (multi-pane, comparative verdict view)
```

**Verification layer:** runs across every stage (not only at the end). Before any agent's output is handed to the next agent, its claims are checked against its underlying cited source. This is a cross-cutting layer, not a single pipeline step — shown here as the `✓ verified` gate at each stage.

## 3. Component Breakdown

### 3.1 Ingestion Agent
- **Input:** Decision brief (entity, capability, candidate options)
- **Output:** Structured, decision-relevant context
- **Notes:** Scoped retrieval — does not attempt to gather everything about the entity, only what's relevant to this decision.
- **Sub-agents:**
  - *Web-Scraping Sub-Agent* — pulls public information on the entity/capability from live web search
  - *Structured-Source Sub-Agent* — pulls from known structured sources (Hugging Face Hub, BIS Entity List, TPDi assessments, cloud market-share reports)
  - *Context-Synthesis Sub-Agent (optional)* — merges the two raw pulls above into the final structured context; if omitted, the parent agent performs this merge itself

### 3.2 Stack-Mapping Agent
- **Input:** Decision context from Ingestion Agent
- **Output:** The specific AI-stack layers implicated (e.g., model weights, training data, inference infra, fine-tuning pipeline, licensing terms)
- **Notes:** Prevents the system from defaulting to a full-footprint audit.
- **Sub-agents:**
  - *Layer-Identification Sub-Agent* — proposes candidate AI-stack layers from the ingested context
  - *Relevance-Filter Sub-Agent* — narrows candidates to only the layers this specific decision touches
  - *Dependency-Linkage Sub-Agent (optional)* — maps how the surviving layers interconnect (e.g., fine-tuning pipeline depends on training data licensing)

### 3.3 Scenario-Generation Agent
- **Input:** Mapped stack layers + decision brief
- **Output:** The realistic option set (build / buy / outsource, or the true set applicable to this decision)
- **Sub-agents:**
  - *Option-Enumeration Sub-Agent* — generates the raw candidate option set
  - *Feasibility-Check Sub-Agent* — filters out options that aren't realistic for this entity/capability
  - *Scenario-Refinement Sub-Agent (optional)* — sharpens each surviving option into a fully specified scenario

### 3.4 Outcome-Prediction Agent
- **Input:** Scenario set
- **Output:** Plausible future trajectory for each path
- **Sub-agents:**
  - *Trajectory-Modeling Sub-Agent* — projects the plausible forward path for each scenario
  - *Risk-Factor Sub-Agent* — identifies events/conditions that could alter that trajectory
  - *Timeline-Projection Sub-Agent (optional)* — attaches rough time horizons to each projected outcome

### 3.5 Dependency-Diagnosis Agent
- **Input:** Predicted outcomes per path
- **Output:** The specific lock-in/dependency each outcome creates, and what breaks later if left unmanaged
- **Sub-agents:**
  - *Lock-in Identification Sub-Agent* — names the specific dependency each outcome creates
  - *Failure-Mode Sub-Agent* — explains what breaks later if that dependency goes unmanaged
  - *Severity-Scoring Sub-Agent (optional)* — scores each identified dependency's severity/urgency

### 3.6 Orchestrator Agent
- **Input:** All three (or n) path diagnoses
- **Output:** Single comparative verdict combining paths side by side
- **Sub-agents:**
  - *Cross-Path Comparison Sub-Agent* — compares diagnoses across all paths side by side
  - *Verdict-Synthesis Sub-Agent* — produces the final comparative verdict text
  - *Explanation-Trail Sub-Agent (optional)* — assembles the source-grounded reasoning trail for explainability/audit

### 3.7 Verification Layer (cross-cutting)
- **Function:** Validates each agent's claims against its underlying source before allowing handoff to the next stage
- **Placement:** Runs at every top-level agent stage boundary (Ingestion → Stack-Mapping → … → Orchestrator), not as a final review step
- **Scope note (MVP):** Verification gates the *combined output* of each top-level agent, after its sub-agents have run and been merged. Sub-agent outputs are not individually gated in MVP — this is a deliberate scope limit, noted as a possible future extension in PRD.md's Open Questions.

### 3.8 Sub-Agent Model
- **Model:** All top-level agents and all sub-agents run on the same LLM — DeepSeek V4 Flash — via the shared LLM client wrapper (see TECH_STACK.md). A single model keeps cost predictable across ~18-24 LLM-calling components and avoids inconsistent reasoning styles between agents.
- **Pattern:** Each top-level agent is a thin orchestrator: it calls its 2-3 sub-agents (in parallel where they don't depend on each other, e.g. Web-Scraping and Structured-Source; sequentially where one needs another's output, e.g. Feasibility-Check needs Option-Enumeration's output), merges their outputs, and returns one structured result to the pipeline.

## 4. Data Flow Summary

Decision Brief → Context → Stack Scope → Scenario Set → Predicted Outcomes → Dependency Diagnoses → Comparative Verdict → Dashboard Render

Each arrow is gated by the verification layer.

## 5. Presentation Layer

- Rendered on the Helios Terminal dashboard.
- Styled after the Bloomberg Terminal's multi-pane, command-driven interface.
- Panes hold decision paths and dependency verdicts instead of market instruments.

## 6. Sub-Agent Diagram (per top-level agent, e.g. Ingestion)

```
        Decision Brief
              │
              ▼
   ┌─────────────────────┐
   │   Ingestion Agent    │  (parent — orchestrates below, returns one context object)
   └───────────┬──────────┘
     ┌─────────┼─────────────┐
     ▼         ▼              ▼
┌─────────┐ ┌──────────────┐ ┌────────────────────┐
│Web-Scrape│ │Structured-   │ │Context-Synthesis    │
│Sub-Agent │ │Source        │ │Sub-Agent (optional) │
│          │ │Sub-Agent     │ │                     │
└─────────┘ └──────────────┘ └────────────────────┘
```

The same pattern (parent + 2-3 sub-agents) repeats for all six top-level agents — see 3.1-3.6 for each agent's specific sub-agent roles.

## 7. Architectural Rationale

- **Stage-gated verification** (rather than end-of-pipeline fact-checking) prevents error compounding — a hallucinated claim from the Ingestion Agent would otherwise propagate uncorrected through five more agents.
- **Decision-scoped design** keeps the system fast and specific; it is explicitly not designed to be a continuous full-footprint monitor (see Non-Goals in PRD.md).
- **Orchestrator as a separate final agent** (rather than each agent writing directly to the dashboard) keeps the comparative verdict as a distinct, auditable synthesis step.