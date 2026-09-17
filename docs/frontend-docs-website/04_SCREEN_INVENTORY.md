# 04 — Screen inventory (website)

Inventory of pages, components, and section implementations across the marketing website.

## Shared Elements

- **Header (`SiteHeader.tsx`):**
  - Sticky at page top (`backdrop-blur-sm`, `bg-site-bg/95`, hairline border).
  - Left: Helios sunburst SVG mark + serif wordmark `Helios Terminal`.
  - Center/Right: Navigation links (`Home`, `Architecture`, `About`, `Team`).
  - Far Right: Separated primary CTA button (`Enter dashboard` → `/dashboard`).
- **Footer (`SiteFooter.tsx`):**
  - Hairline top border (`border-site-border`).
  - GitHub repository link with external link icon.
  - Synopsis note linking to synopsis download.
  - Academic capstone attribution line (`CSE-AIDS Capstone 2026`).

---

## 1. Home (`/`) — 7 Sections

1. **Header:** Sticky site navigation.
2. **Hero:**
   - Tag: `[ strategic autonomy / decision engine ]`.
   - Serif headline: `Build, buy, or outsource—choose with the full picture.`
   - Subhead: Narrative on avoiding long-term dependency.
   - Dual CTAs: Primary `Enter dashboard`, Secondary `See the architecture`.
3. **Problem Teaser:** Two-column split with editorial prose explaining latent dependency emergence alongside an SVG line-art sourcing fork.
4. **Pipeline Strip:** Horizontal preview of 6 pipeline nodes (`Ingest`, `Map stack`, `Generate`, `Predict`, `Diagnose`, `Verdict`) linked directly to the Architecture page.
5. **Three Pillars:** 3-column grid highlighting `Decision-scoped`, `Verified`, and `Self-correcting` principles with Lucide icons.
6. **Dashboard CTA Band:** Full-width container with dark gradient edge foreshadowing the terminal workspace.
7. **Footer:** Bottom navigation and project links.

---

## 2. Architecture (`/architecture`) — 7 Sections

1. **Header:** Sticky site navigation.
2. **Intro:**
   - Tag: `Architecture / conditional graph`.
   - Serif headline: `How Helios thinks through a sourcing decision.`
   - Intro paragraph explaining the six-agent verification and recalibration loops.
3. **Pipeline Flow Diagram (Mermaid.js):**
   - Dynamic SVG flowchart rendered via `Mermaid.tsx` (`pipelineChart`).
   - Solid lines (`-->`) for forward verified handoffs (`01 Ingestion` through `06 Comparative verdict`).
   - Dashed curved lines (`-.->`) representing backward conditional recalibration requests.
4. **Stage Cards Grid:**
   - 6 responsive cards (wrapping 1 / 2 / 3 / 6 columns) detailing the role of each agent:
     - `01 Ingestion` (`Database`)
     - `02 Stack mapping` (`Layers3`)
     - `03 Scenario generation` (`Route`)
     - `04 Outcome prediction` (`ChartNoAxesCombined`)
     - `05 Dependency diagnosis` (`Link2`)
     - `06 Comparative verdict` (`Scale`)
   - Dashed line legend explaining loop recovery.
5. **Recalibration Explainer Sequence:**
   - Subsection header: `The recalibration sequence`.
   - 3-step sequence flowchart rendered via Mermaid (`recalibrationChart`).
   - 3 cards detailing:
     - `Step 01: Sufficiency check`
     - `Step 02: Gap payload`
     - `Step 03: Bounded retry` (max 2 retries)
6. **Tech Stack Strip:**
   - Clean horizontal row showcasing core technologies: `React`, `FastAPI`, `LangGraph`, `DeepSeek V4 Flash` with checkmarks.
7. **CTA & Footer:**
   - "See it in action" CTA prompting users to enter the dashboard.
   - Sticky footer.

---

## 3. About (`/about`) — 6 Sections

1. **Header:** Sticky site navigation.
2. **Editorial Hero:**
   - Tag: `The premise`.
   - High-impact serif headline: `Every organisation adopting AI eventually faces a sourcing fork.`
   - Staggered entrance via `.hero-reveal`.
3. **Narrative Column:**
   - Max-width 680px reading column.
   - Lead paragraph with decorative serif drop cap (`.drop-cap`).
   - Deep dive into hidden lock-ins, contract terms, and why Helios Terminal exists.
4. **Who It's For (Interactive Persona List):**
   - 4 target audiences:
     - `Government ministries`
     - `Defence units`
     - `Companies and subsidiaries`
     - `Procurement and policy teams`
   - Clean responsive dl grid with animated teal left-indicator on hover.
5. **Pull-Quote Section:**
   - Centered large italic serif quote highlighting twofold contribution: usable tool + repeatable forecasting method.
   - Decorative watermark quotation marks in background.
6. **Synopsis Download Card & Footer:**
   - Card featuring `FileText` icon, document title `Helios Terminal Synopsis`, and file metadata (`Project document / DOCX`).
   - Action: `<Button href="/assets/Helios-Terminal-Synopsis.docx" download={true}>` with download icon.
   - Footer.

---

## 4. Team (`/team`) — 5 Sections

1. **Header:** Sticky site navigation.
2. **Intro:** `CSE-AIDS capstone / panel B` tag, serif headline `The team.`, and mission statement.
3. **Team Grid:**
   - 4 contributor cards (2x2 on mobile/tablet, 4-across on wide desktop):
     - `Rishav Singh` (RS) — System architecture & full-stack engineering
     - `Kunal Tailor` (KT) — AI pipeline & agent design
     - `Prakash` (P) — Research, verification & evaluation
     - `Neeraj Gupta` (NG) — Product strategy & decision analysis
   - Monospace circular initials avatar and direct repository link.
4. **Shared System Note:**
   - Explains how engineering, agent design, verification, and decision theory converge into the six-stage pipeline.
5. **Footer.**
