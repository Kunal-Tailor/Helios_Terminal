# Helios Terminal — Marketing Site Design Spec

Four pages: Home, Architecture, About, Team. Dashboard is out of scope here (separate dark terminal aesthetic, designed later). This doc covers the theoretical layout for each page, then a ready-to-use prompt for an image generator at the end of each section.

---

## Global design tokens (shared across all four pages)

**Palette — warm, premium, restrained. Not yellow-warm, closer to bone/sand.**
- Base background: `#F7F3EE` (warm off-white, sand)
- Secondary surface / cards: `#EDE6DC` (slightly deeper warm neutral)
- Text primary: `#2A2724` (warm charcoal, not pure black)
- Text secondary: `#6B645C` (warm gray)
- Borders / hairlines: `#DDD5C9`
- Accent (single accent, used sparingly): `#3FA7B3` (muted phosphor-teal — same accent as the Dashboard, this is the thread connecting the two worlds)

**Typography**
- Headlines / editorial voice: Source Serif 4
- Nav, buttons, UI chrome, body copy: Inter
- Occasional technical/label accents only (small tags, stats): IBM Plex Mono — used sparingly, foreshadows the terminal without making the site feel technical

**Motion**
- Scroll-triggered fade-up on section entry, ~300ms, one-time only — no looping, no parallax
- Hover states: 2–4px lift or a border/color shift only — never a drop shadow
- One exception: the Architecture page's pipeline diagram may "trace in" its connecting lines on scroll-into-view

**Overall tone:** restraint over decoration. Whitespace and hairline borders do the "premium" work — no gradients, no heavy shadows, no stock photography anywhere on the site.

---

## Page 1 — Home

**Sections (7, in order):**

1. **Header** — sticky, warm off-white bg, logo + "Helios Terminal" wordmark left, nav right (`Home · Architecture · About · Team`), `Dashboard` as a distinct filled teal button, not a nav link. Hairline border-bottom, no shadow even on scroll.
2. **Hero** — ~80vh, centered column, max-width ~760px. Small monospace tag above the headline (e.g. a bracketed label). Large serif headline stating the build/buy/outsource fork. Inter subhead below, one sentence. Two CTAs: primary filled teal ("Enter dashboard"), secondary ghost/outline ("See the architecture").
3. **Problem teaser** — two-column: left is 2–3 sentences of prose (from the project's problem statement), right is a small restrained line-art diagram of a fork/three-paths shape. No photography, no color fill — thin teal lines only.
4. **Pipeline strip** — a single horizontal row of six small labeled nodes connected by thin lines, monospace labels, teal connecting line. A simplified static preview of the six-agent flow. Clicking through leads to Architecture.
5. **Three pillars** — three equal columns, hairline-bordered (no shadow), each with a small line-icon, one-word or short label, one line of description. (Decision-scoped / Verified at every stage / Self-correcting.)
6. **Dashboard CTA band** — full-width section, background one shade deeper than base. Centered short headline + the Dashboard button again. A thin dark gradient sliver at the very bottom edge of this band, foreshadowing the dark terminal the user is about to enter.
7. **Footer** — one row: GitHub link, synopsis note, team credit line, institution line.

**Image-gen prompt:**
```
A minimalist, premium website homepage design mockup, desktop resolution 1440x1024,
Figma-style UI design (not a photo). Warm sand/bone background (#F7F3EE), warm
charcoal text (#2A2724), single muted teal accent color (#3FA7B3) used sparingly.
Typography: an elegant serif for the large headline, clean sans-serif for body
and navigation, a small monospace label above the headline.

Layout top to bottom:
1. Sticky header: logo + wordmark "Helios Terminal" top-left, navigation links
   "Home / Architecture / About / Team" top-right, and a solid teal filled
   button labeled "Enter dashboard" separated from the nav links.
2. Large centered hero section: small bracketed monospace tag, a large serif
   headline about choosing between building, buying, or outsourcing AI
   capability, one line of smaller sans-serif subtext, two buttons (one solid
   teal, one outlined).
3. A two-column section: short paragraph of text on the left, a simple thin
   teal line-art diagram of a forking path on the right.
4. A horizontal row of six small connected nodes/boxes with short labels and
   thin teal connecting lines, representing a six-step process flow.
5. Three equal-width bordered cards in a row, each with a small minimal line
   icon, a short bold label, and one line of description underneath.
6. A full-width darker sand-colored band with a centered short headline and
   another teal button, with a subtle dark gradient sliver along its bottom edge.
7. A slim footer with small text links.

Style: generous whitespace, hairline 1px borders (no drop shadows, no
gradients except the one noted), flat and clean, luxurious and restrained,
editorial and professional — not flashy, not corporate-blue, not stock-photo.
```

---

## Page 2 — Architecture

**Sections (7, in order):**

1. **Header** — identical to Home.
2. **Intro** — short serif headline framing this as "how Helios thinks," one paragraph in plain language below, centered, max-width ~700px.
3. **Pipeline flow diagram (centerpiece)** — six stage-cards laid out left to right (or wrapped 3+3 on smaller widths), each with a name and a one-line role. Thin teal lines connect them forward. Separately, dashed teal lines curve backward beneath the row, representing the conditional recalibration loops — visually distinct from the forward flow (dashed vs solid).
4. **Recalibration explainer** — a compact 3-step horizontal sequence just below the diagram: "sufficiency check → gap payload → bounded retry," each step a short label with a one-line caption underneath.
5. **Tech stack strip** — a slim row of plain-text/monospace labels (React, FastAPI, LangGraph, DeepSeek), minimal, functioning as a quiet credibility strip, not logo badges.
6. **CTA** — centered, "See it in action," teal Dashboard button.
7. **Footer** — identical to Home.

**Image-gen prompt:**
```
A minimalist, premium technical architecture page design mockup, desktop
resolution 1440x1400, Figma-style UI design (not a photo). Warm sand/bone
background (#F7F3EE), warm charcoal text (#2A2724), single muted teal accent
(#3FA7B3). Serif headline font, clean sans-serif body, occasional small
monospace labels.

Layout top to bottom:
1. Sticky header identical to a homepage: logo left, nav links and a teal
   "Enter dashboard" button right.
2. Centered intro: short serif headline about how the system reasons, one
   paragraph of smaller sans-serif text below it.
3. The visual centerpiece: six small rectangular stage-cards arranged in a
   horizontal row, each with a bold short title and a one-line description,
   connected left to right by thin solid teal lines with arrowheads. Below
   this row, add a few dashed teal curved lines looping backward from later
   cards to earlier ones, clearly distinct from the solid forward lines,
   representing feedback loops.
4. A compact three-step horizontal sequence below the diagram: three short
   labeled steps connected by thin arrows, each with a one-line caption.
5. A slim horizontal row of plain monospace technology names, minimal,
   no logos, just clean text labels evenly spaced.
6. A centered call-to-action: short headline and a solid teal button.
7. A slim footer with small text links.

Style: technical but calm, generous whitespace, hairline 1px borders, flat
and clean, no drop shadows, no gradients, no glow effects, precise and
engineering-credible while still feeling premium and uncluttered.
```

---

## Page 3 — About

**Sections (6, in order):**

1. **Header** — identical to Home.
2. **Editorial hero** — pure typographic hero, no imagery. Large serif headline (the project's opening framing line about organizations facing a sourcing fork), generous surrounding whitespace, nothing else in this section.
3. **Narrative** — single centered column, max-width ~680px (magazine-style reading width), 2–3 paragraphs of prose. Optional serif drop-cap on the first paragraph for a premium editorial touch.
4. **Who it's for** — 3–4 short persona lines (government ministry, defence unit, enterprise/subsidiary), presented as a minimal list, not heavy cards — just a label and one line each.
5. **Pull-quote** — a large centered serif italic line highlighting the project's twofold contribution (usable tool + research contribution), set apart with generous whitespace above and below.
6. **Synopsis card + footer** — a single clean hairline-bordered card near the page end: title, one-line description, file type, a download button. Footer follows directly beneath.

**Image-gen prompt:**
```
A minimalist, premium editorial "about" page design mockup, desktop
resolution 1440x1600, Figma-style UI design (not a photo). Warm sand/bone
background (#F7F3EE), warm charcoal text (#2A2724), single muted teal accent
(#3FA7B3) used only for one download button and small link underlines.
Elegant serif font for headline and pull-quote, clean sans-serif for body text.

Layout top to bottom:
1. Sticky header identical to a homepage: logo left, nav links and a teal
   "Enter dashboard" button right.
2. A large, purely typographic hero section with no images: a big serif
   headline sentence centered on the page with generous empty space around it.
3. A single centered narrow column of body text (like a magazine article),
   two to three paragraphs, with a large decorative serif drop-cap on the
   first letter of the first paragraph.
4. A short minimal list of three or four lines, each a bold short label
   followed by a brief description, no cards or boxes, just clean vertical
   spacing.
5. A large centered italic serif pull-quote sentence, set apart with wide
   margins above and below.
6. A single bordered card near the bottom containing a document title, one
   line of description, and a solid teal "Download" button, followed by a
   slim footer with small text links.

Style: calm, reading-focused, generous whitespace, hairline 1px borders, no
drop shadows, no gradients, elegant and quiet — the most text-forward and
least "app-like" page on the site.
```

---

## Page 4 — Team

**Sections (5, in order):**

1. **Header** — identical to Home.
2. **Intro** — short headline ("The team"), one line of context underneath (capstone project, institution, panel).
3. **Team grid** — four cards in a row (wraps to 2x2 on narrower widths). Each card: a warm-toned initials circle (no real photos), name, role/contribution area in one short line, small GitHub/email icon links at the bottom of the card.
4. **Contribution note** — a small text block beneath the grid clarifying how each member's area ties to the six-agent pipeline, optionally cross-linking to the Architecture page.
5. **Footer** — identical to Home.

**Image-gen prompt:**
```
A minimalist, premium team page design mockup, desktop resolution 1440x900,
Figma-style UI design (not a photo). Warm sand/bone background (#F7F3EE),
warm charcoal text (#2A2724), single muted teal accent (#3FA7B3). Serif
headline font, clean sans-serif body.

Layout top to bottom:
1. Sticky header identical to a homepage: logo left, nav links and a teal
   "Enter dashboard" button right.
2. A short centered intro: one serif headline word or short phrase, one line
   of smaller sans-serif context text beneath it.
3. A row of four equal-width minimal cards with hairline borders (2x2 grid
   on smaller widths). Each card has a small circular avatar filled with a
   warm neutral tone containing initials, a bold name, a short one-line role
   description below it, and two tiny icon links at the bottom of the card.
4. A short paragraph of small text below the grid.
5. A slim footer with small text links.

Style: clean, restrained, generous whitespace, hairline 1px borders, no drop
shadows, no gradients, no real photography — abstract initials only, quiet
and professional.
```
