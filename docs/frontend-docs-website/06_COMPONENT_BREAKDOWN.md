# 06 — Component breakdown (website)

| Component | Purpose | Variants | Used on |
| --- | --- | --- | --- |
| `SiteHeader` | Sticky nav + Dashboard CTA | Light (site) / dark-collapsed (Dashboard entry) | All |
| `SiteFooter` | GitHub, synopsis note, credit line | — | All |
| `Button` | CTA element | primary (filled), secondary (outline), ghost | All |
| `Hero` | Large headline block | with-CTAs (Home), typographic-only (About) | Home, About |
| `TwoColumnBlock` | Prose + small diagram | — | Home |
| `PipelineStrip` | Six connected nodes, mini preview | compact (Home) | Home |
| `PillarCard` | Icon + label + one-line description, 3-up grid | — | Home |
| `CTABand` | Full-width band with headline + button | with-gradient-sliver | Home |
| `PipelineDiagram` | Full six-stage diagram with forward + dashed backward edges | — | Architecture |
| `StepSequence` | Compact 3-step horizontal explainer | — | Architecture |
| `TechStackStrip` | Plain-text tech labels | — | Architecture |
| `NarrativeColumn` | Centered prose block, optional drop-cap | — | About |
| `PersonaList` | Minimal labeled list | — | About |
| `PullQuote` | Large centered italic serif line | — | About |
| `DownloadCard` | Bordered card with file info + download button | — | About |
| `TeamCard` | Avatar-initials + name + role + icon links | — | Team |
| `TeamGrid` | 4-up responsive grid of TeamCard | wraps 2x2 | Team |

Each component reads only from `05_DESIGN_SYSTEM.md` tokens — no
component should hardcode a color or font not listed there.
