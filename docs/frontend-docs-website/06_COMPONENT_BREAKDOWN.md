# 06 — Component breakdown (website)

## Shared Components & Utilities (`frontend/src/shared/`)

| Component / Utility | File | Purpose | Props / Options | Used on |
| --- | --- | --- | --- | --- |
| `SiteHeader` | `SiteHeader.tsx` | Sticky header with logo, navigation links, and "Enter dashboard" CTA | `className?: string` | All site pages (`/`, `/architecture`, `/about`, `/team`) |
| `SiteFooter` | `SiteFooter.tsx` | Slim footer with project repository link, synopsis note, and academic credits | — | All site pages |
| `Button` | `Button.tsx` | Unified action component rendering `<button>`, `<Link>`, or `<a download>` | `variant?: 'primary' \| 'secondary' \| 'ghost'`, `size?: 'sm' \| 'md' \| 'lg'`, `to?: string`, `href?: string`, `download?: boolean \| string` | All pages |
| `Mermaid` | `Mermaid.tsx` | High-fidelity vector flowchart renderer powered by Mermaid.js with theme variables | `chart: string`, `className?: string` | `Architecture` |
| `useScrollReveal` | `useScrollReveal.tsx` | Custom IntersectionObserver hook that attaches `.visible` to observed `.scroll-reveal` elements | `options?: IntersectionObserverInit` | `Architecture`, `About` |

## Page Breakdown & Section Structure

### 1. Home (`src/site/pages/Home.tsx`)
- **Hero Section:** Tag badge (`[ strategic autonomy / decision engine ]`), serif headline, subhead, primary CTA to `/dashboard` and secondary CTA to `/architecture`.
- **Strategic Sourcing Fork Teaser:** Editorial prose side-by-side with line-art decision fork diagram.
- **Pipeline Strip:** Six-stage interactive preview (`Ingest` → `Map stack` → `Generate` → `Predict` → `Diagnose` → `Verdict`) with links to Architecture.
- **Three Pillars:** Decision-scoped, Verified, Self-correcting cards with Lucide icons (`GitFork`, `ShieldCheck`, `RefreshCw`).
- **Dashboard CTA Band:** Full-width band with gradient edge transitioning toward the terminal.

### 2. Architecture (`src/site/pages/Architecture.tsx`)
- **Header & Intro:** Centered title and description with staggered `.hero-reveal`.
- **Pipeline Flow Diagram:** Runtime-rendered `Mermaid` conditional graph featuring 6 forward stages and dashed backward recalibration loops.
- **Stage Cards Grid:** 6 cards with stage numbering, title, description, and Lucide icons (`Database`, `Layers3`, `Route`, `ChartNoAxesCombined`, `Link2`, `Scale`).
- **Recalibration Explainer:** `Mermaid` 3-step sequence flowchart alongside 3 explanatory step cards (`Sufficiency check`, `Gap payload`, `Bounded retry`).
- **Tech Stack Strip:** Monochrome badges for `React`, `FastAPI`, `LangGraph`, `DeepSeek V4 Flash`.
- **CTA:** Direct launch into `/dashboard`.

### 3. About (`src/site/pages/About.tsx`)
- **Editorial Hero:** Typographic hero with `.hero-reveal` animation.
- **Narrative Column:** Centered 680px editorial column with `.drop-cap` serif typography.
- **Persona List ("Who it's for"):** 4 target groups (Ministries, Defence, Enterprises, Procurement) with subtle left-rail accent hover highlight.
- **Pull-Quote Card:** Centered serif italic quote with decorative watermark quotation marks.
- **Synopsis Download Card:** Hairline-bordered card featuring `FileText` icon, document metadata, and a direct `<Button href="..." download={true}>` trigger for `Helios-Terminal-Synopsis.docx`.

### 4. Team (`src/site/pages/Team.tsx`)
- **Header & Context:** Capstone panel metadata and intro headline.
- **Team Grid:** 4 member cards with circular avatar initials, roles, and project GitHub links.
- **Shared System Note:** Card clarifying how individual responsibilities tie into the multi-agent pipeline.
