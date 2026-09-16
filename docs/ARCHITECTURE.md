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

**Recalibration layer (conditional backward edges):** the diagram above shows the forward path only. In addition to the `✓ verified` gate, each analytical stage also runs a **sufficiency** check — not "is this claim true" but "was I given enough to work with." On failure, the stage does not regenerate blindly; it emits a `RecalibrationRequest` naming the specific gap and routes backward to the stage best positioned to fill it:

```
Stack-Mapping   --insufficient layers-->        Ingestion (scoped re-query)
Scenario-Gen.   --infeasible/generic options-->  Stack-Mapping  OR  Ingestion (routing decision, see §3.8)
Outcome-Pred.   --ungrounded/undifferentiated--> Scenario-Generation (invokes scenario_refinement_sub_agent)
Dependency-Diag.--non-specific lock-in-->        Outcome-Prediction (invokes timeline_projection_sub_agent)
Orchestrator    --asymmetric path completeness-->Dependency-Diagnosis, scoped to the deficient path only
```

Each backward edge carries the accumulated context forward (append, not replace) and is capped at 2 retries per `(from, to)` pair. If the cap is hit, the pipeline does not fail or loop indefinitely — it returns a verdict with explicit per-path caveat flags. See §3.8 for the component breakdown and §6 for why this replaces the sequential-only design.

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

### 3.8 Recalibration Layer (cross-cutting, conditional)
- **Function:** A second, distinct gate from 3.7 — checks *sufficiency* of upstream input rather than *correctness* of the current claim. Verification asks "is this grounded"; recalibration asks "was I given enough to work with."
- **Trigger conditions (per stage):**
  - Stack-Mapping: 0–1 surviving AI-stack layers after relevance filtering
  - Scenario-Generation: fewer than 2 viable options after feasibility filtering, or options not concretely tied to the mapped stack layers
  - Outcome-Prediction: repeated grounding failures, or projected paths too similar to differentiate later
  - Dependency-Diagnosis: lock-in description falls back to generic language because the outcome lacked a timeline
  - Orchestrator: diagnoses across paths are asymmetrically complete (one path analyzed in depth, another thin)
- **Routing:** Each trigger names a specific upstream target and a `gap_description` (not a blind "try again"). Scenario-Generation is the one stage with a genuine routing decision — it can fall back to either Stack-Mapping or Ingestion depending on the nature of the gap.
- **Bounding:** Loop-guard caps retries at 2 per `(from_stage, to_stage)` pair. Context accumulates across retries rather than resetting, which keeps the added latency bounded.
- **Terminal state:** If the cap is exceeded, the pipeline does not hard-fail — it returns a partial verdict with explicit per-path caveat flags, and the caveat is surfaced in the API response's `recalibration_trail` (see PRD.md FR-4/FR-5).
- **Data structure:** `RecalibrationRequest` — lives in `verification/recalibration.py`, alongside `verifier.py`, since both are cross-cutting checks rather than pipeline stages themselves.

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
- **Conditional recalibration over pure sequential flow:** a strictly linear pipeline has no way to recover from a genuinely thin upstream result other than producing a genuinely thin downstream one. Adding a sufficiency gate (§3.8) alongside the verification gate (§3.7) turns the pipeline from a fixed DAG into a stage-gated *conditional* graph — each stage can diagnose its own input as insufficient and route backward with a bounded, targeted request, rather than silently propagating a weak analysis forward. This is a direct response to the Level 1 feedback that the sequential-only design read as simplistic; it also maps cleanly onto LangGraph's conditional-edge model, so it extends the existing tech-stack choice rather than replacing it.
