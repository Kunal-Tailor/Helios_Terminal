# frontend-docs-website

Comprehensive documentation for the **Helios Terminal frontend application**, spanning the editorial marketing website (`/`, `/architecture`, `/about`, `/team`) and the Bloomberg-style sovereign intelligence dashboard (`/dashboard`).

---

## Documentation Index

| File | Primary Coverage |
| --- | --- |
| [`01_FRONTEND_VISION.md`](./01_FRONTEND_VISION.md) | Product purpose, target personas, tone, and the light-to-dark contrast philosophy |
| [`02_REQUIREMENTS_AND_FEATURES.md`](./02_REQUIREMENTS_AND_FEATURES.md) | Functional requirements, live implementation status (FR-W1 to FR-W7), and accessibility |
| [`03_UX_FLOWS.md`](./03_UX_FLOWS.md) | User journeys: marketing visitor flows and workstation operational workflows |
| [`04_SCREEN_INVENTORY.md`](./04_SCREEN_INVENTORY.md) | Detailed section-by-section breakdown of all 4 marketing pages |
| [`05_DESIGN_SYSTEM.md`](./05_DESIGN_SYSTEM.md) | Light theme tokens, typography, drop-cap rules, Mermaid theming, and reveal animations |
| [`06_COMPONENT_BREAKDOWN.md`](./06_COMPONENT_BREAKDOWN.md) | Shared UI components (`SiteHeader`, `SiteFooter`, `Button`, `Mermaid`, `useScrollReveal`) and page structures |
| [`07_API_CONTRACT.md`](./07_API_CONTRACT.md) | Full API contract: static assets plus live FastAPI endpoints (`/health`, `/decisions/async`, polling) |
| [`08_FRONTEND_ARCHITECTURE.md`](./08_FRONTEND_ARCHITECTURE.md) | SPA architecture, directory tree, routing (`App.tsx`), theme scoping, and runtime diagram rendering |
| [`09_DASHBOARD_WORKSTATION.md`](./09_DASHBOARD_WORKSTATION.md) | Complete guide to the Bloomberg-style decision workstation (`/dashboard`), components, views, audio, and fallback engine |

---

## Current Implementation Summary

1. **Unified Application Architecture:** Single Page App built using React 18, Vite 5, TypeScript 5, Tailwind CSS 3, and React Router v7.
2. **Dual Theme Scoping:**
   - `.theme-site` (`#F7F3EE` bone/sand) for public marketing and academic evaluation.
   - `.theme-dashboard` (`#0E1013` charcoal/black) for the operational decision terminal.
   - Connected by the signature `#3FA7B3` teal accent.
3. **Dynamic Flowchart Generation:** Interactive runtime SVG diagrams powered by `Mermaid.js` with site-themed styling.
4. **Motion & Accessibility:** Coordinated scroll reveals (`useScrollReveal`, `.hero-reveal`, `.scroll-reveal`) with full `@media (prefers-reduced-motion: reduce)` support.
5. **Static Asset Distribution:** Direct download for `Helios-Terminal-Synopsis.docx` bundled under `frontend/public/assets/`.
6. **Backend Integration & Resilience:** Full typed integration with FastAPI backend (`submitDecision`, `pollJobStatus`), reinforced by an offline client synthesis engine.
