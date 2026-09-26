# 01_DASHBOARD_VISION.md — Helios Terminal Dashboard

## Why this exists separately from `01_FRONTEND_VISION.md`

`01_FRONTEND_VISION.md` covers the marketing website's Hybrid Terminal philosophy — dense chrome, room where you decide. This document covers the dashboard's **operating philosophy**, which is a stricter, purer version of that: the dashboard *is* the instrument, not a wrapper around it. There's no editorial copy here, no hero sections — only the decision workstation.

## The core interface idea

> The Bloomberg Terminal for AI sovereign sourcing decisions.

The Helios dashboard takes Bloomberg's *posture* literally rather than metaphorically. Where the website *borrows* Bloomberg's density for contrast, the dashboard *is* Bloomberg — amber on black, function keys, a `<GO>` command bar, a scrolling market ticker, and a multi-pane grid. The reference is earned because the users (defense procurement officers, ministry analysts, enterprise leadership) operate Bloomberg terminals in their day jobs. The interface is immediately legible to them without training.

The key substitution: Bloomberg's tickers are replaced with AI model pricing, GPU spot rates, BIS entity watch counts, lock-in index scores, and EU AI Act risk tiers. The underlying *information density discipline* is preserved; only the domain changes.

## Design philosophy: Full Terminal

Unlike the website's Hybrid Terminal (dense chrome, spacious verdicts), the dashboard applies terminal density uniformly. This is intentional — the user has already decided to run a sourcing analysis. They are not being sold anything. Every pixel is operational:

- **Header strip:** live UTC/local clocks, backend connection beacon, pipeline status badge, mute toggle.
- **Command bar:** free-text `<GO>` input with autocomplete, identical in feel to Bloomberg's function bar.
- **Function key ribbon:** F1–F9 mapped to nine dedicated workstation views.
- **Ticker tape:** live-scrolling AI market data strip, 40-second animation cycle, pauses on hover.
- **Main viewport:** the active workstation view — either the 4-quadrant grid or a fullscreen panel.
- **Footer strip:** pipeline metadata, hotkey hint, verification gate status.

## User intent at dashboard load time

A user arriving at `/dashboard` has already read the architecture page or been referred by a colleague. They have a specific institutional brief in mind. They do not want onboarding — they want to run an analysis. The dashboard defaults to the quadrant view with the first preset already loaded (`PRESET_SCENARIOS[0]`, the Indian Army Signals Directorate SLM case) so there is always a fully populated, readable verdict on screen from first load. No empty states, no "get started" prompts.

## Three user archetypes in the workstation

| Archetype | Primary view | Secondary views |
|---|---|---|
| Procurement analyst running a live brief | F2 (Decision Console) → F1 (Quadrant) | F5 (Audit) to validate claims |
| Presenter showing stakeholders | F1 (Quadrant) with a preset loaded | F3 (Trajectory), F7 (Dossier) for print |
| Technical reviewer inspecting evidence | F5 (Audit Inspector) | F6 (Intel Feed) for source traceability |

## What the dashboard is explicitly not trying to be

- **Not a data dashboard for monitoring a running system.** There are no time-series charts of live system metrics. The "charts" here are TCO vs lock-in projections for institutional decision paths.
- **Not a chat interface.** There is no conversational LLM UX. Inputs are structured: entity, capability, sourcing options. Output is a structured verdict with grounded audit trail.
- **Not a mobile app.** Desktop-only, same as the website. The 4-quadrant grid requires a large viewport.
- **Not a literal Bloomberg clone.** The amber-on-black aesthetic, `<GO>` button, and function keys are real references to Bloomberg's UI language — but every component is purpose-built for AI sourcing decisions. Nothing is borrowed from Bloomberg's actual codebase.

## Where the rest of this lives

- Functional requirements → `02_REQUIREMENTS_AND_FEATURES.md`
- User flows step-by-step → `03_UX_FLOWS.md`
- Every view and its states → `04_SCREEN_INVENTORY.md`
- Design tokens and primitives → `05_DESIGN_SYSTEM.md`
- Per-component breakdown → `06_COMPONENT_BREAKDOWN.md`
- API shapes → `07_API_CONTRACT.md`
- State machine and architecture → `08_DASHBOARD_ARCHITECTURE.md`
