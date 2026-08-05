# PRD.md — Helios Terminal

## 1. Overview

**Product name:** Helios Terminal
**One-line description:** An AI-powered multi-agent decision intelligence platform for AI sourcing strategy and dependency risk analysis.
**Type:** Capstone project (CSE-AIDS, Level 1) — in-house/independent research project.

## 2. Problem Statement

Organisations adopting AI capability must repeatedly choose between building, buying, or outsourcing. This choice is currently made without a structured way to forecast the long-term dependency risk each option creates. Helios Terminal provides that structure for a single, concretely scoped decision at a time.

## 3. Goals

- G1: Let a user describe a real AI sourcing decision (entity, capability, options) and receive a structured comparison of paths.
- G2: Surface the specific dependency/lock-in risk each path creates, not just cost or performance tradeoffs.
- G3: Ground every agent's output in verifiable source material via a cross-stage verification layer.
- G4: Present results in a dense, professional, command-driven interface suited to fast decision-making.

## 4. Non-Goals (for MVP)

- Continuous/real-time monitoring of an organisation's entire AI estate.
- Automated procurement or contract execution.
- Financial/legal advice — outputs are decision-support, not binding recommendations.
- Multi-decision portfolio optimisation (comparing many decisions against each other) — MVP is single-decision scoped.

## 5. User Personas

| Persona | Need |
| --- | --- |
| Defence procurement officer | Evaluate build/buy/outsource for a field-deployed model without long-term vendor lock-in |
| Government ministry analyst | Structured, defensible rationale for a sovereign AI capability decision |
| Enterprise/subsidiary decision-maker | Compare AI sourcing options against long-term dependency cost, not just sticker price |

## 6. Core User Flow

1. User enters a decision: the entity, the capability needed, and the candidate options (or asks Helios to infer the realistic option set).
2. Ingestion Agent gathers context relevant to that decision.
3. Stack-Mapping Agent identifies which layers of the AI stack the decision touches.
4. Scenario-Generation Agent lays out the realistic paths (e.g., build, buy, outsource).
5. Outcome-Prediction Agent projects where each path plausibly leads.
6. Dependency-Diagnosis Agent names the lock-in each outcome creates and what breaks later if unmanaged.
7. Orchestrator Agent combines the analyses into one comparative verdict.
8. Verification layer checks claims against sources at every stage before handoff.
9. User views the result on the Helios Terminal dashboard — paths, verdicts, and dependency risk side by side.

## 7. Functional Requirements

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-1 | User can submit a decision brief (entity, capability, candidate options) | Must |
| FR-2 | System runs the six-agent pipeline end-to-end on a submitted decision | Must |
| FR-3 | System displays a side-by-side comparison of paths with dependency verdicts | Must |
| FR-4 | Each agent's claims are checked against cited source material before being passed downstream | Must |
| FR-5 | User can view the specific lock-in risk and its future failure mode per path | Must |
| FR-6 | Dashboard UI follows a multi-pane, command-driven layout | Should |
| FR-7 | User can export/save a decision analysis | Should |
| FR-8 | User can revisit a past decision analysis | Could |
| FR-9 | System supports web-search/retrieval augmentation for grounding agent claims | Must |

## 8. Non-Functional Requirements

- **Explainability:** Every verdict must be traceable to the agent reasoning and sources that produced it.
- **Latency:** Full pipeline run should complete within a session-reasonable time (target: minutes, not hours) for MVP scale.
- **Extensibility:** Agent pipeline should be modular so agents can be added/modified without rearchitecting the system.
- **No GPU dependency for MVP:** inference via hosted LLM APIs.

## 9. Success Metrics

- Pipeline produces a coherent, source-grounded comparative verdict for a real test decision.
- Verification layer catches at least a defined percentage of unsupported claims in evaluation testing.
- A panel/evaluator judges the output as more structured and useful than an unaided vendor-pitch comparison.

## 10. Open Questions

- How is the "true option set" determined when the user doesn't specify all options themselves?
- What is the minimum context needed from the user before Ingestion Agent can proceed reliably?
- How are conflicting source claims resolved during verification?
