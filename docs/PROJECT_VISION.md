# PROJECT_VISION.md — Helios Terminal

## The Problem

Every organisation that adopts AI eventually faces the same fork in the road: build a capability in-house, buy a ready-made model, or hand it to an outside vendor to develop. A defence unit that wants a small language model running locally on a drone could train it privately, license an existing one, or contract a third party. Each of these three roads quietly locks the unit into a different kind of dependency — one that may only surface years later, when a vendor changes terms, a licence expires, or an outside partner disappears.

Today this decision is made on instinct and vendor pitches. There is no structured way to see what each path actually costs an organisation down the line.

## The Vision

Helios Terminal closes that gap. Instead of monitoring an organisation's entire AI footprint in the abstract, it focuses on **one concrete sourcing decision at a time** and answers a single question:

> Of the options available, which one creates the least dangerous long-term dependency?

A user describes the decision at hand — the entity, the capability needed, and the choices on the table — and a six-agent pipeline takes it from there, ending in a side-by-side comparison of paths and the dependency risk each one carries, delivered **ahead of** the decision rather than after it.

## Who It's For

- Government ministries evaluating sovereign AI capability decisions
- Defence units sourcing AI for sensitive or field-deployed systems
- Companies and subsidiaries making build/buy/outsource calls on AI capability
- Procurement and policy teams who need a defensible, repeatable rationale — not a vendor pitch deck

## Why It's Different

- **Decision-scoped, not footprint-scoped.** Helios doesn't try to audit an entire AI estate; it narrows to the layers of the stack a specific decision actually touches.
- **Forecasts lock-in before it happens.** Existing tooling (if any) tends to audit dependencies that already exist. Helios projects the dependency a *not-yet-made* decision would create.
- **Verified at every stage.** A verification layer checks each agent's claims against its underlying source before the next agent can act on them, rather than fact-checking only the final output.
- **Familiar interface for an unfamiliar problem.** The interface borrows its feel from the Bloomberg Terminal — dense, command-driven, multi-pane — but the panes hold decision paths and dependency verdicts instead of market tickers.

## The Twofold Contribution

1. **A usable decision-support tool** with direct relevance to defence, policy, and enterprise procurement.
2. **A research contribution in its own right** — a structured, repeatable method for forecasting AI dependency risk before it is locked in, an area with no established prior tooling.

## Definition of Success

A decision-maker can enter a real sourcing decision (entity, capability, options on the table) and receive, within one session, a side-by-side comparison of realistic paths (build/buy/outsource or the true option set) along with the specific dependency each path creates and what breaks later if that dependency goes unmanaged.
