# 03_UX_FLOWS.md — Helios Terminal Frontend

## Flow A — Primary flow (build this first, per Phase 9 in TASKS.md)

```
[Decision Input]
      │  user fills entity, capability, (optional) candidate options
      │  submits
      ▼
[Pipeline Status]  ── shown inline, not a separate route ──
      │  Ingestion → Stack-Mapping → Scenario-Generation →
      │  Outcome-Prediction → Dependency-Diagnosis → Orchestrator
      │  current stage highlighted; each completed stage marked ✓
      ▼
[Result View — v1]
      │  verdict banner (Orchestrator's comparative summary)
      │  + one card per path: outcome / dependency / failure mode
      ▼
[Dashboard — v2, later]
      multi-pane assembly: verdict pane + dependency-graph pane
      + command bar for pane navigation
```

**Why Pipeline Status is inline, not a route:** the user has already committed to one decision brief; sending them to a separate "loading page" route adds a navigation event with no destination of its own. An inline status strip on the same screen (replacing the submit button's area) keeps the flow to two conceptual screens for v1: Input, then Result.

### Step-by-step

1. **Decision Input.** User enters entity + capability. Candidate options field is optional with a visible note: *"Leave blank and Helios will infer the realistic option set"* — this directly answers PRD.md's open question #1 in the UI itself rather than hiding the ambiguity.
2. **Submit.** Form locks (no double-submit), status strip appears in place of the form.
3. **Pipeline Status.** Each of the six stages lights up as its verification gate passes. If a stage fails verification, the strip stops there and shows which stage failed — no silent fallback to a generic error.
4. **Result View.** Verdict banner at top (Orchestrator's synthesis, 2-3 sentences). Below it, one card per candidate path in the order the Scenario-Generation Agent produced them — each card shows the projected outcome, the named dependency, and what breaks later if unmanaged (FR-5).
5. **From here:** "New decision" returns to a blank Input screen. (No history/revisit in MVP — see `02_REQUIREMENTS_AND_FEATURES.md`.)

## Flow B — Command bar navigation (nav-only, MVP scope)

Per the interaction-model decision: the command bar **navigates, it does not submit or query.** Scope is deliberately narrow for MVP:

```
/ or :  → focuses the command bar
verdict → jump to verdict banner / pane
graph   → jump to dependency-graph pane (once it exists, v2)
new     → start a new decision (clears current result, returns to Input)
esc     → unfocus / close
```

No natural-language parsing, no decision submission through it, no history/search command in MVP. This keeps FR-6 satisfied at "Should" priority without pulling command-parsing complexity into the MVP timeline. Extending the command bar toward query/submission is an explicit *future* item, not a phase-9 task.

## Flow C — Error and empty states (part of the primary flow, not separate screens)

- **Verification halt mid-pipeline:** status strip shows the failed stage in the risk-red token (see `05_DESIGN_SYSTEM.md`), with a one-line plain-language reason and a "try again" action — not a raw error dump.
- **Network/API failure:** same treatment, distinguished only by copy ("Couldn't reach Helios" vs. "Stage failed verification") so the user isn't left guessing whether it's their decision or the connection.
- **Empty candidate options + system-inferred set:** Result View should visibly label which options were user-specified vs. system-inferred, so the verdict doesn't read as more prescriptive than it is.

## Explicitly out of scope for MVP flows

- Multi-decision comparison / portfolio view (Non-Goal in PRD.md §4)
- Saved history browsing (FR-8, stretch)
- Any flow that lets the frontend itself alter or re-rank the verdict — the frontend only ever displays what the Orchestrator Agent returned.
