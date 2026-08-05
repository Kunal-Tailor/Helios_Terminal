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

### 3.2 Stack-Mapping Agent
- **Input:** Decision context from Ingestion Agent
- **Output:** The specific AI-stack layers implicated (e.g., model weights, training data, inference infra, fine-tuning pipeline, licensing terms)
- **Notes:** Prevents the system from defaulting to a full-footprint audit.

### 3.3 Scenario-Generation Agent
- **Input:** Mapped stack layers + decision brief
- **Output:** The realistic option set (build / buy / outsource, or the true set applicable to this decision)

### 3.4 Outcome-Prediction Agent
- **Input:** Scenario set
- **Output:** Plausible future trajectory for each path

### 3.5 Dependency-Diagnosis Agent
- **Input:** Predicted outcomes per path
- **Output:** The specific lock-in/dependency each outcome creates, and what breaks later if left unmanaged

### 3.6 Orchestrator Agent
- **Input:** All three (or n) path diagnoses
- **Output:** Single comparative verdict combining paths side by side

### 3.7 Verification Layer (cross-cutting)
- **Function:** Validates each agent's claims against its underlying source before allowing handoff to the next stage
- **Placement:** Runs at every stage boundary, not as a final review step

## 4. Data Flow Summary

Decision Brief → Context → Stack Scope → Scenario Set → Predicted Outcomes → Dependency Diagnoses → Comparative Verdict → Dashboard Render

Each arrow is gated by the verification layer.

## 5. Presentation Layer

- Rendered on the Helios Terminal dashboard.
- Styled after the Bloomberg Terminal's multi-pane, command-driven interface.
- Panes hold decision paths and dependency verdicts instead of market instruments.

## 6. Architectural Rationale

- **Stage-gated verification** (rather than end-of-pipeline fact-checking) prevents error compounding — a hallucinated claim from the Ingestion Agent would otherwise propagate uncorrected through five more agents.
- **Decision-scoped design** keeps the system fast and specific; it is explicitly not designed to be a continuous full-footprint monitor (see Non-Goals in PRD.md).
- **Orchestrator as a separate final agent** (rather than each agent writing directly to the dashboard) keeps the comparative verdict as a distinct, auditable synthesis step.
