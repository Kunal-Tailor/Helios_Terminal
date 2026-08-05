# FEATURES.md — Helios Terminal

## Core Feature: Six-Agent Decision Pipeline

| Agent | Role |
| --- | --- |
| **Ingestion Agent** | Pulls in the context relevant to the specific decision submitted by the user (entity, capability, options). |
| **Stack-Mapping Agent** | Identifies which parts of the AI stack the decision actually touches, rather than scoring an organisation's entire footprint by default. |
| **Scenario-Generation Agent** | Lays out the realistic paths available — build, buy, outsource, or whatever the true option set is for this decision. |
| **Outcome-Prediction Agent** | Projects where each path plausibly leads over time. |
| **Dependency-Diagnosis Agent** | Names the specific lock-in each projected outcome creates and explains what breaks in the future if that dependency goes unmanaged. |
| **Orchestrator Agent** | Combines the three path analyses into a single comparative verdict for side-by-side viewing. |

## Cross-Cutting Feature: Verification Layer

- Runs across every stage of the pipeline, not just at the end.
- Checks each agent's claims against its underlying source before the output is allowed to reach the next agent.
- Purpose: prevent downstream agents from building conclusions on unverified upstream claims.

## Dashboard / Interface Features

- **Bloomberg-Terminal-style UI:** dense, command-driven, multi-pane screen designed for fast professional decisions.
- **Comparative verdict pane:** side-by-side view of all candidate paths and their long-term costs.
- **Dependency graph view:** visual representation of lock-in relationships (react-flow / D3.js).
- **Command bar:** fast, keyboard-driven interaction pattern consistent with the terminal aesthetic.

## Input Features

- Structured decision brief entry: entity, capability needed, candidate sourcing options.
- Support for user-specified option sets *or* system-inferred realistic options via the Scenario-Generation Agent.

## Output Features

- Side-by-side comparison of build/buy/outsource (or equivalent) paths.
- Per-path dependency risk verdict with explanation of what breaks later if unmanaged.
- Source-grounded reasoning trail per agent stage (supports explainability/auditability).

## MVP vs. Future Scope

**MVP (in scope):**
- Single-decision analysis end-to-end through all six agents.
- Verification layer active at every stage.
- Dashboard rendering of the comparative verdict.

**Future / stretch (not MVP):**
- Saved decision history and revisit/export.
- Portfolio-level view comparing multiple past decisions.
- Continuous monitoring mode for an organisation's broader AI footprint.
- Collaborative/multi-user review of a single decision brief.
