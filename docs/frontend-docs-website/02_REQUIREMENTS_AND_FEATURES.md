# 02 — Requirements and features (website)

## Pages in scope

Home, Architecture, About, Team — four pages, plus a shared Header and
Footer. Dashboard is a fifth destination but is out of scope for this doc
(it's a route the site links to, not a page this doc designs).

## Navigation

- Order: `Home · Architecture · About · Team`
- `Dashboard` is a separated, visually distinct CTA button — never inside
  the nav link list.
- Header is sticky on all four pages, no shadow on scroll, hairline
  border-bottom only.

## Synopsis

Not a standalone page. Lives as a download card at the end of the About
page. Optionally cross-linked (a small text link, not a duplicate card)
from the end of the Architecture page.

## Functional requirements

| ID | Requirement | Page |
| --- | --- | --- |
| FR-W1 | Visible Dashboard CTA above the fold | All |
| FR-W2 | Six-agent pipeline preview links through to Architecture | Home |
| FR-W3 | Full pipeline + recalibration diagram | Architecture |
| FR-W4 | Synopsis download (file link, opens/downloads the doc) | About |
| FR-W5 | Four team member cards with role/contribution + GitHub or email link | Team |
| FR-W6 | Footer present on every page with GitHub, institution line | All |

## Non-goals (for this build)

- No authentication, no user accounts on the marketing site.
- No forms, no lead capture, no analytics dashboard.
- No CMS — page content is static/hardcoded, edited in source.
- No live backend calls from the website itself. The only backend contact
  anywhere in this experience is inside the Dashboard, documented
  separately.

## Responsiveness

The website is responsive (mobile, tablet, desktop) — unlike the
Dashboard, which is desktop-only by design (a dense terminal layout
doesn't compress well). This is a deliberate difference: the site needs
to work for someone opening a shared link on a phone; the Dashboard
assumes someone sitting down to do analysis work.

## Accessibility baseline

- Semantic HTML landmarks (`header`, `nav`, `main`, `footer`).
- Nav and CTAs fully keyboard-navigable, visible focus states.
- Any diagram (pipeline strip, architecture flow) has an accessible text
  equivalent, not just a visual.
- Text contrast meets WCAG AA against the `#F7F3EE` base.
