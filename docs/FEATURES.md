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

## Cross-Cutting Feature: Recalibration & Fallback Layer

- A second gate, distinct from verification: checks whether an upstream stage's output was *sufficient* to work with, not whether a claim is *correct*.
- On an insufficient result, the stage does not regenerate blindly — it emits a specific, named gap and routes backward to the stage best positioned to fill it (e.g. Stack-Mapping asks Ingestion for targeted data on licensing terms, rather than re-running the whole pipeline).
- Scenario-Generation is the one stage with a genuine routing decision: it can fall back to Stack-Mapping (scope too narrow) or Ingestion (missing concrete option data), depending on the nature of the gap.
- Orchestrator fallback is **path-scoped** — if one of three paths has a thin diagnosis, only that path's Dependency-Diagnosis re-runs, not the full stage.
- Bounded by a loop-guard (max 2 retries per stage-pair) and accumulates context across retries rather than discarding it, keeping added latency bounded.
- On exceeding the retry cap, the system does not fail or hang — it returns a partial verdict with explicit per-path caveat flags, surfaced to the user via a `recalibration_trail` in the API response.
- Purpose: turns the pipeline from a fixed sequence into a conditional, self-correcting graph — this is what supports the platform's claim to being a decision-*intelligence* system rather than a fixed six-step script.

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
- Recalibration & fallback layer active at every stage (added post-Level-1-review; see Phase 7.5 in `TASKS.md`).
- Dashboard rendering of the comparative verdict, including recalibration-trail caveats where applicable.

**Future / stretch (not MVP):**
- Saved decision history and revisit/export.
- Portfolio-level view comparing multiple past decisions.
- Continuous monitoring mode for an organisation's broader AI footprint.
- Collaborative/multi-user review of a single decision brief.
