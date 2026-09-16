# 03 — UX flows (website)

## Flow 1 — First-time visitor, evaluating the product

Home → skims hero + three pillars + pipeline strip → clicks through to
Architecture for technical credibility → clicks Dashboard CTA.

## Flow 2 — Evaluator / guide

Lands on Home or a direct link → goes to About for the problem/vision
framing → scrolls to the Synopsis download card → downloads.
Alternative: goes to Architecture first if they want the technical case
before the narrative one — both paths should reach Synopsis in ≤2 clicks
from wherever they land.

## Flow 3 — Portfolio / recruiter viewer

Home → Team → clicks a GitHub or email link on a team card. Doesn't
necessarily touch Architecture or About.

## Flow 4 — Returning user who already knows the product

Lands anywhere → goes straight to the Dashboard CTA, ignores marketing
content entirely. This is why the CTA must be reachable without scrolling
on every page, not just Home.

## Transition into the Dashboard

Clicking Dashboard is a route change, not a modal or overlay. On arrival:
header flips from light/full-nav to dark/collapsed (logo + a small
"← Helios" back-link, full nav links dropped since the Dashboard's own
command bar takes over navigation). This transition is documented fully
in `frontend-docs-dashboard` once that set exists — this doc only defines
the trigger point (the CTA) and the fact that the site's nav does not
persist into the Dashboard unchanged.
