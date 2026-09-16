# 07 — API contract (website)

Deliberately thin. The marketing site makes no calls to the Helios
Terminal backend (`POST /decisions` and friends belong entirely to the
Dashboard's contract, documented separately).

## What the website actually touches

| Interaction | Mechanism |
| --- | --- |
| "Dashboard" CTA | Client-side route change to `/dashboard`, no API call |
| Synopsis download | Static file link (served asset, e.g. `/assets/synopsis.pdf`), not an endpoint |
| Team GitHub/email links | Plain `<a href>`, external, no API |

## If this changes later

A contact form, newsletter signup, or analytics event would each need an
entry here with method, payload, and response shape before implementation
starts — none exist in the current scope. If one gets added, update this
file in the same commit as the feature, not after.
