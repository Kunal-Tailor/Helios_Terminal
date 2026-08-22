# 01_FRONTEND_VISION.md — Helios Terminal Frontend

## Why this exists separately from PROJECT_VISION.md

`PROJECT_VISION.md` states the product's reason for existing. This document states what the **interface** has to be true to for that vision to land — the frontend is the only part of Helios a user ever actually touches, so it carries the entire first impression of "structured decision-support tool" vs. "another AI demo."

## The core interface idea

> The panes hold decision paths and dependency verdicts instead of market tickers.

Helios borrows the Bloomberg Terminal's *posture* — dense, professional, built for someone making a consequential call under time pressure — without borrowing its literal skin. A defence procurement officer or ministry analyst should recognize the register immediately (this is an instrument, not a marketing site) while the actual content reads like a briefing document, not a stock ticker.

## Design philosophy: Hybrid Terminal

Two things are true about a real Bloomberg Terminal at once: it's maximally dense, and it's built for people who've been trained to read it. Helios's users have not had that training — they're opening this tool to make one high-stakes decision, not running it all day. So density is earned selectively:

- **Chrome, navigation, metadata, status** → dense, monospace, terminal-native. This is where density signals competence and doesn't cost comprehension.
- **The verdict and the dependency diagnosis** → generous spacing, larger type, serif prose. This is the part a human is meant to slow down and actually think about. Cramming it into terminal density would optimize for the wrong thing — it's not a ticker, it's the answer to "should we do this."

This split *is* the frontend's signature idea, more than any single visual element: **density where you scan, room where you decide.**

## Frontend-specific persona notes

(Full persona definitions live in `PRD.md` §5 — these are the interface-relevant implications only.)

| Persona | What that means for the UI |
| --- | --- |
| Defence procurement officer | Needs to trust the verdict fast under time pressure — status of the pipeline run must always be visible, never a silent spinner. Low tolerance for ambiguous states. |
| Government ministry analyst | Will likely screenshot or export the verdict pane for a briefing document — the verdict/dependency view should look complete and presentable on its own, not require the surrounding chrome to make sense. |
| Enterprise/subsidiary decision-maker | Least familiar with "terminal" interfaces of the three — the hybrid approach (breathing room in the decision-critical panes) matters most for this persona specifically. |

## What the frontend is explicitly not trying to be

- Not a marketing site for Helios — no hero sections, no scroll-triggered reveals, no "convince the visitor" copy. Users arrive already needing to make a decision.
- Not a literal Bloomberg Terminal clone — no green-on-black CRT pastiche, no attempt to recreate specific Bloomberg widgets. The reference is a *feeling* (dense, instrument-like, professional), not a skin to copy.
- Not mobile-first, not even mobile-considered for MVP (see `05_DESIGN_SYSTEM.md` — Responsive Stance). This is a desk-bound decision-support instrument, matching its Bloomberg reference point.

## Where the rest of this lives

- What the interface must do → `02_REQUIREMENTS_AND_FEATURES.md`
- How a user actually moves through it → `03_UX_FLOWS.md`
- Concrete screens → `04_SCREEN_INVENTORY.md`
- Colors, type, tokens → `05_DESIGN_SYSTEM.md`
- Components → `06_COMPONENT_BREAKDOWN.md`
- Backend contract → `07_API_CONTRACT.md`
- Code structure and state → `08_FRONTEND_ARCHITECTURE.md`
