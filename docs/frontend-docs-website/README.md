# frontend-docs-website

Documentation for the **marketing site** only: Home, Architecture, About, Team.
The Dashboard (the actual product) has its own dark terminal aesthetic and
will get a separate `frontend-docs-dashboard` set later — don't pull design
tokens or components from that effort into this one, they're deliberately
different visual languages connected by a single shared accent color.

## Files

| File | Covers |
| --- | --- |
| `01_FRONTEND_VISION.md` | Purpose, audience, tone, relationship to the Dashboard |
| `02_REQUIREMENTS_AND_FEATURES.md` | What each page must do, non-goals, responsiveness |
| `03_UX_FLOWS.md` | How different visitors move through the site |
| `04_SCREEN_INVENTORY.md` | Every page, section by section |
| `05_DESIGN_SYSTEM.md` | Colors, type, spacing, motion — the tokens |
| `06_COMPONENT_BREAKDOWN.md` | Reusable components and where each is used |
| `07_API_CONTRACT.md` | Deliberately thin — the site is static |
| `08_FRONTEND_ARCHITECTURE.md` | Folder structure, routing, how this coexists with the Dashboard build |

## Status

Written fresh following the frontend-reset and the website-architecture
discussion (light/warm site, contrast against a dark Dashboard, nav order
`Home · Architecture · About · Team` with Dashboard as a separated CTA,
Synopsis folded into About rather than its own page). Supersedes whatever
was in the old `frontend-docs/` set for the website portion — that set
covered a single unified dark app which is no longer the plan.
