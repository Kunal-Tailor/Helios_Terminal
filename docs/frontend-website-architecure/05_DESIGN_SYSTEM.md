# 05_DESIGN_SYSTEM.md — Helios Terminal Frontend

## Design plan summary

Following the Hybrid Terminal direction from `01_FRONTEND_VISION.md`: dense terminal bones for chrome/navigation/data, generous room for the verdict and dependency panes. Two deliberate departures from the two most common "AI-generated dark UI" defaults — flat black-with-acid-green/vermilion, and warm-cream-with-terracotta — are made below and named explicitly so they don't drift back toward either during implementation.

## Color tokens

| Token | Hex | Use |
| --- | --- | --- |
| `--bg-base` | `#0B0E11` | App background — near-black with a cool undertone, not flat black |
| `--bg-surface` | `#12161B` | Panel/card backgrounds |
| `--bg-surface-raised` | `#171C22` | Hover/active surface state |
| `--border-hairline` | `#232931` | 1px pane and card dividers — borders over shadows, no blur/glow |
| `--text-primary` | `#E4E7EB` | Primary reading text |
| `--text-secondary` | `#8A94A0` | Metadata, labels, timestamps |
| `--text-tertiary` | `#5A6472` | Disabled, placeholder |
| `--accent` | `#3FA7B3` | Interactive elements, focus states, brand mark — a muted phosphor-teal, deliberately *not* acid-green or vermilion |
| `--risk-critical` | `#E5484D` | Dependency severity: critical, reserved for this meaning only |
| `--risk-elevated` | `#D89B3C` | Dependency severity: elevated |
| `--risk-low` | `#4C9F70` | Dependency severity: low |

**Why teal, not green/amber:** the two most common defaults for a dark data UI are acid-green-on-black (generic "hacker terminal") or the amber/green Bloomberg-literal palette. Both would either read as templated or as a direct skin-copy of Bloomberg, which `01_FRONTEND_VISION.md` explicitly avoids. Teal keeps the "phosphor display" heritage without either. Risk-severity colors are kept out of the accent's hue family on purpose, so a critical-risk badge is never visually confusable with an ordinary interactive element.

## Typography

| Role | Typeface | Where |
| --- | --- | --- |
| Structural / data / labels | IBM Plex Mono | Command bar, nav, table data, status strip, metadata, timestamps |
| Reading / prose | Source Serif 4 | Verdict banner, dependency descriptions, outcome/failure-mode text |
| UI labels (buttons, form labels) | Inter | Form fields, buttons — needs to be legible at small sizes, mono is worse for this than for data |

**Why mono + serif, not mono + sans:** the chrome already carries the "instrument" feeling in mono. Pairing the *reasoning content* with a serif — rather than a second sans — borrows from briefing-document and policy-memo typography instead of generic dashboard typography, which fits a tool aimed at defence/government/enterprise decision-makers reading an actual analytical verdict, not scanning a metric.

**Type scale (base 16px):** `12px` metadata / `14px` body-mono/UI labels / `16px` UI body / `19px` prose body (serif) / `24px` section headers / `32px` verdict banner headline.

## Density rule

- **Dense (mono, tight line-height ~1.3, minimal padding):** nav, command bar, status strip, decision-brief recap, table/metadata surfaces.
- **Roomy (serif, line-height ~1.6, generous padding ~24-32px):** verdict banner, per-path outcome/dependency/failure-mode text.

This is the one rule every component decision should be checked against — see `06_COMPONENT_BREAKDOWN.md`.

## Layout

- Hairline (`1px solid var(--border-hairline)`) between panes — no drop shadows, no blur. Cheaper to build and consistent with the terminal reference.
- Border-radius: `2px` on cards/inputs (barely-there, not the 0px broadsheet look and not a soft rounded-corner default) — a small, deliberate middle ground.
- Grid: CSS grid for the Dashboard's multi-pane layout (v2); flex/stack for the Input and Result screens (v1).

## Responsive stance

**Desktop-only for MVP.** Minimum supported width: `1280px`. This mirrors the real Bloomberg Terminal, which is not a responsive product either — Helios is a desk-bound decision instrument, not a marketing page. State this explicitly rather than leaving it an unstated assumption: no mobile breakpoints, no hamburger nav, no stacking-to-single-column fallback are in scope until there's an actual demand signal for it.

## Accessibility (kept honest, not exhaustive)

- All interactive elements keyboard-reachable; visible focus ring using `--accent` at 2px outset — required given the command bar is keyboard-first by design.
- Text contrast: `--text-primary` on `--bg-base`/`--bg-surface` meets WCAG AA; `--text-secondary` checked against AA for non-body text only (labels/metadata), not relied on for primary reading content.
- Risk-severity color tokens are never the *only* signal — always paired with a text label ("Critical", "Elevated", "Low"), so color-blind users aren't dependent on hue alone.
- `prefers-reduced-motion` respected — see Motion below.

## Motion

Terminal UIs use almost no motion by convention, and that convention is kept deliberately rather than added-to:

- Pipeline status stage transitions: instant state change, no easing flourish — the *information* (which stage is active) is the point, not the animation.
- Panel/route transitions: fast opacity fade only (~120ms), no slide/scale.
- No page-load sequences, no scroll-triggered reveals — these belong to marketing sites, not an instrument.
- Respect `prefers-reduced-motion: reduce` by disabling even the 120ms fade.

## Signature element

**The Dependency Thread.** A thin `--accent`-colored line that visually connects a path's outcome → named dependency → failure mode within its card, literalizing "lock-in" as something the eye can trace rather than just read. Used *only* in the Result View and Dashboard's verdict-adjacent panes — nowhere else — so it stays a signature, not a decoration repeated until it means nothing.
