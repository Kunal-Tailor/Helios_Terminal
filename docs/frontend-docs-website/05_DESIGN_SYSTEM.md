# 05 — Design system (website)

Scoped to the website only. The Dashboard has its own dark token set,
defined separately, sharing only the accent color.

## Color

| Token | Value | Use |
| --- | --- | --- |
| `--site-bg` | `#F7F3EE` | Page background (warm bone/sand, not yellow) |
| `--site-surface` | `#EDE6DC` | Cards, deeper bands |
| `--site-text-primary` | `#2A2724` | Body/headline text (warm charcoal) |
| `--site-text-secondary` | `#6B645C` | Supporting text |
| `--site-border` | `#DDD5C9` | Hairline borders |
| `--site-accent` | `#3FA7B3` | Single accent — CTAs, links, connecting lines. Shared with the Dashboard's accent. |

One accent only. No secondary accent color — restraint is the design
language here, not a second hue.

## Typography

| Role | Font | Used for |
| --- | --- | --- |
| Headline / editorial | Source Serif 4 | Hero headlines, About narrative, pull-quotes |
| UI / body | Inter | Nav, buttons, body copy, cards |
| Technical accent | IBM Plex Mono | Small tags/labels only — sparing, foreshadows the Dashboard |

## Spacing & shape

- Borders: `0.5px solid var(--site-border)` everywhere — no drop shadows.
- Radius: 8px on cards/buttons, no pill shapes.
- Whitespace does the "premium" work — err toward more, not less.

## Motion

- Scroll-triggered fade-up on section entry, ~300ms, fires once.
- Hover: 2–4px lift or a border/color shift only.
- Exception: the Architecture pipeline diagram may trace its connecting
  lines in on scroll-into-view, once, non-looping.
- No parallax, no autoplay animation, no looping motion anywhere.

## Buttons

- **Primary** — solid `--site-accent` fill, used once per view max
  (the Dashboard CTA). Never for secondary actions.
- **Secondary** — outline, `--site-border` or accent-tinted border,
  transparent fill.
- **Ghost** — text-only, underline on hover.

## What not to do

No gradients (except the single dark sliver at the bottom of the Home
Dashboard-CTA band, which is intentional and singular), no glow/neon, no
stock photography, no corporate blue, no more than one filled-accent
button visible per screen.
