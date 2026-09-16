# 08 — Frontend architecture (website)

## Stack

React 18 + Vite, Tailwind CSS — same as `TECH_STACK.md` establishes for
the frontend overall. The website and Dashboard are one build, split by
route and by theme scope, not two separate apps.

## Proposed structure

```
frontend/src/
├── site/                  # this doc's scope
│   ├── pages/
│   │   ├── Home.tsx
│   │   ├── Architecture.tsx
│   │   ├── About.tsx
│   │   └── Team.tsx
│   ├── components/        # components from 06_COMPONENT_BREAKDOWN.md
│   └── site-theme.css     # tokens from 05_DESIGN_SYSTEM.md
├── dashboard/              # out of scope here — see frontend-docs-dashboard later
│   └── ...
├── shared/
│   ├── SiteHeader.tsx      # theme-aware: light on /, dark-collapsed on /dashboard/*
│   └── SiteFooter.tsx
└── App.tsx                 # router: "/" family → site/, "/dashboard" family → dashboard/
```

## Theme scoping

Two CSS variable sets (`site-theme.css`, `dashboard-theme.css`), never
merged into one global palette. The router decides which theme class
wraps the current route (`<div class="theme-site">` vs `<div
class="theme-dashboard">`), so a component can't accidentally pull the
wrong palette just because it's mounted in the wrong tree.

## Why one app, not two

Keeps the Dashboard CTA a normal client-side route transition (instant,
no full page reload) rather than a link to a separate deployed site —
this matters for the "reveal" feel described in `01_FRONTEND_VISION.md`.
Deployment (Vercel, per `TECH_STACK.md`) still serves it as a single
static build.
