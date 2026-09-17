# 08 — Frontend architecture (website)

## Stack

- **Framework:** React 18 (`react: ^18.3.1`, `react-dom: ^18.3.1`)
- **Bundler & Tooling:** Vite 5 (`vite: ^5.4.11`), TypeScript (`typescript: ^5.6.3`)
- **Styling:** Tailwind CSS 3 (`tailwindcss: ^3.4.17`, `postcss`, `autoprefixer`)
- **Diagramming & Flowcharts:** Mermaid 11 (`mermaid: ^11.x`) for dynamic pipeline graphs
- **Routing:** React Router v7 (`react-router-dom: ^7.18.3`)
- **Icons:** Lucide React (`lucide-react: ^1.45.0`)
- **Data Visualization (Dashboard):** Recharts (`recharts: ^3.10.1`)

The marketing website and the decision terminal dashboard are unified in a single Vite project, split cleanly by route and theme scope (`.theme-site` vs `.theme-dashboard`).

## Directory Structure

```
frontend/
├── public/
│   └── assets/
│       └── Helios-Terminal-Synopsis.docx   # Bundled downloadable project synopsis
├── src/
│   ├── shared/
│   │   ├── Button.tsx                      # Unified button: Link (`to`), Anchor (`href` + `download`), button
│   │   ├── Mermaid.tsx                     # Dynamic SVG diagram component styled to site theme
│   │   ├── useScrollReveal.tsx             # IntersectionObserver hook for `.scroll-reveal` elements
│   │   ├── SiteHeader.tsx                  # Sticky site navigation with logo and "Enter dashboard" CTA
│   │   └── SiteFooter.tsx                  # Editorial footer with repo link, synopsis, and institution note
│   ├── site/
│   │   ├── pages/
│   │   │   ├── Home.tsx                    # Value proposition, sourcing fork teaser, pillars, CTA band
│   │   │   ├── Architecture.tsx            # 6-agent conditional graph, Mermaid diagram, recalibration loop
│   │   │   ├── About.tsx                   # Typographic hero, drop-cap narrative, persona list, synopsis card
│   │   │   └── Team.tsx                    # Capstone contributors, agent responsibilities, GitHub links
│   │   └── site-theme.css                  # Light-theme tokens, `.hero-reveal`, `.scroll-reveal`, `.drop-cap`
│   ├── dashboard/                          # Decision terminal (FastAPI backend consumer)
│   │   ├── api.ts                          # REST / SSE client connecting to http://127.0.0.1:8000
│   │   ├── components/                     # BloombergSupplyChainGraph, MatrixView, TraceFeed, VerdictPanel
│   │   ├── pages/                          # Dashboard pages and views
│   │   └── styles/
│   │       └── terminal.css                # Dark terminal theme tokens
│   ├── App.tsx                             # Client-side routing (`BrowserRouter`) + `SiteMotion` trigger
│   ├── index.css                           # Root styles, Tailwind directives, font family bindings
│   └── main.tsx                            # React root bootstrap
├── package.json
└── vite.config.ts
```

## Theme Scoping

The project enforces strict separation between the light marketing site and the dark terminal dashboard:
- **Website theme (`.theme-site` / `:root`):** Defined in `src/site/site-theme.css` (`--site-bg: #F7F3EE`, `--site-surface: #EDE6DC`, `--site-text-primary: #2A2724`, `--site-border: #DDD5C9`, `--site-accent: #3FA7B3`).
- **Dashboard theme (`.theme-dashboard`):** Defined in `src/dashboard/styles/terminal.css` (`--dash-bg: #0E1013`, `--dash-surface: #14171C`, `--dash-border: #23272F`).
- **Shared accent:** Both environments share the teal accent color (`#3FA7B3`) to create a cohesive brand continuity when transitioning from marketing to the product.

## Motion & Scroll Animation Architecture

1. **Global Route Transitions (`SiteMotion` in `App.tsx`):**
   - Automatically detects route changes via `useLocation`.
   - Attaches `site-reveal` class to top-level sections in `.theme-site` and animates them as they scroll into view.
2. **Component & Section Reveal (`useScrollReveal.tsx`):**
   - Headless hook leveraging `IntersectionObserver`.
   - Observes elements matching `.scroll-reveal` and assigns `.visible` upon entry.
   - Respects `--reveal-delay` inline styles for staggered sequences.
3. **Typographic Hero Animations (`.hero-reveal`):**
   - CSS `@keyframes hero-fade-up` with customized easing (`cubic-bezier(0.16, 1, 0.3, 1)`).
4. **Accessibility:**
   - Full `@media (prefers-reduced-motion: reduce)` support: disables transitions, delays, and transforms across all reveal utilities.

## Mermaid Flowchart Integration

Architecture diagrams are rendered at runtime via `src/shared/Mermaid.tsx`:
- Initialized with custom theme variables matching `--site-bg`, `--site-surface`, and `--site-accent`.
- Dynamic rendering via `mermaid.render()` ensures high DPI vector scaling without pixelation.
- Supports both the 6-agent conditional graph (forward handoffs and backward dashed recalibration loops) and the 3-step recalibration sequence.

## Single App Architecture Rationale

- **Instant Transitions:** Navigating from the marketing site into the dashboard (`/dashboard`) is an instantaneous client-side SPA transition, reinforcing the feel of entering an active operational terminal.
- **Shared Type Definitions & UI Components:** Common elements like `Button.tsx` and SVGs are reused without cross-package duplication.
- **Unified Build:** Built and deployed as a single production artifact via `vite build`.
