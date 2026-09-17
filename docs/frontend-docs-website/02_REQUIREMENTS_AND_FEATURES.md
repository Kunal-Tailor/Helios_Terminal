# 02 — Requirements and features (website)

## Pages in Scope

The marketing website consists of four public routes (`/`, `/architecture`, `/about`, `/team`), supported by a shared navigation header (`SiteHeader`) and footer (`SiteFooter`).

The decision intelligence terminal lives at `/dashboard` and is entered via persistent primary CTAs across all pages.

## Navigation Structure

- **Routes:**
  - `/` → Home (`Home.tsx`)
  - `/architecture` → Architecture (`Architecture.tsx`)
  - `/about` → About (`About.tsx`)
  - `/team` → Team (`Team.tsx`)
  - `/dashboard` → Terminal Dashboard (`DashboardPlaceholder.tsx` / `dashboard/`)
- **Primary CTA:** `Enter dashboard` is displayed as a prominent teal button separated from the standard link group.
- **Header Behavior:** Sticky on all pages with backdrop blur (`backdrop-blur-sm`), no drop shadows, hairline border (`border-site-border`).

## Synopsis Delivery

The project research synopsis (`Helios-Terminal-Synopsis.docx`) is bundled statically under `frontend/public/assets/`. It is accessible via the synopsis download card on the `/about` page using an HTML5 `download` attribute trigger.

## Functional Requirements & Live Implementation

| ID | Requirement | Implementation Status | Implementation Details |
| --- | --- | --- | --- |
| FR-W1 | Visible Dashboard CTA above the fold | Implemented | Sticky header button on all routes + large hero button on Home & Architecture. |
| FR-W2 | Six-agent pipeline preview links to Architecture | Implemented | Horizontal preview strip on Home links each stage into `/architecture`. |
| FR-W3 | Pipeline + recalibration diagram | Implemented | Runtime SVG rendering with `Mermaid.js` (`pipelineChart` and `recalibrationChart`), including `.sr-only` accessible text fallback. |
| FR-W4 | Synopsis file download | Implemented | `<Button href="/assets/Helios-Terminal-Synopsis.docx" download={true}>` delivers the DOCX file directly. |
| FR-W5 | Team member cards & roles | Implemented | 4 cards on `/team` with circular avatar initials, roles, and project GitHub links. |
| FR-W6 | Consistent footer | Implemented | Shared `SiteFooter.tsx` on all 4 marketing pages with repository and synopsis links. |
| FR-W7 | Scroll-triggered entrance animations | Implemented | `useScrollReveal` hook + `.hero-reveal` / `.scroll-reveal.visible` CSS classes with staggered delays. |

## Accessibility Baseline

- **Landmarks:** Structured semantic HTML (`header`, `nav`, `main`, `section`, `dl`, `dt`, `dd`, `footer`).
- **Screen Reader Support:** Complex diagrams (e.g. Mermaid pipeline graph) include hidden `.sr-only` descriptive descriptions.
- **Reduced Motion:** When `prefers-reduced-motion: reduce` is enabled, all animations, delays, and transitions are neutralized to instantaneous display.
- **Contrast & Legibility:** Charcoal text (`#2A2724`) and secondary text (`#6B645C`) exceed WCAG AA contrast against `#F7F3EE` canvas.
