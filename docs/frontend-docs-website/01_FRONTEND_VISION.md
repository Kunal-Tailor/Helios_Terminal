# 01 — Frontend vision (website & workstation)

## Purpose

The Helios Terminal frontend delivers a two-tier experience:
1. **The Editorial Marketing Website (`/`, `/architecture`, `/about`, `/team`):** Acts as the institutional credibility layer. It articulates the problem of latent AI dependency, explains the six-agent architecture, presents the project team, and delivers the research synopsis in under 30 seconds.
2. **The Terminal Workstation (`/dashboard`):** An operational, Bloomberg-inspired intelligence console where decision-makers run, analyze, and audit AI sourcing strategies in real time.

## Target Audience

- **Capstone Evaluators & Technical Reviewers:** Require rapid academic credibility: structured problem statement, verifiable stage-gated architecture, transparent evaluation criteria, and a downloadable synopsis.
- **Enterprise & Defense Leadership:** Sourcing decision-makers seeking defensible rationales to navigate the build vs buy vs outsource fork without getting locked into vendor traps.
- **Open-Source & AI Researchers:** Interested in multi-agent orchestration, cross-stage claim verification, and sovereign AI dependency modeling.

## Visual Identity: The Light-to-Dark Contrast

The relationship between the website and the dashboard is built on **intentional contrast rather than uniform consistency**:
- **Marketing Website:** Minimalist, warm bone/sand (`#F7F3EE`), generous whitespace, serif editorial typography (`Source Serif 4`), and hairline borders. Uncluttered, quiet, and reading-focused.
- **Terminal Workstation:** High-density, dark command center (`#0E1013`), monospace data matrices (`IBM Plex Mono`), real-time telemetry, interactive network graphs, and tactile audio feedback.
- **The Unifying Accent:** Both interfaces are anchored by the signature muted teal accent (`#3FA7B3`), ensuring a seamless identity transition when entering the product.

## Key Frontend Objectives

- **Fast Value Articulation:** A visitor understands what Helios Terminal achieves within 15 seconds of reading the Home hero.
- **Auditable & Verifiable:** Every claim made in the pipeline can be traced back to its underlying evidence in the audit inspector.
- **Instant Client Transitions:** Client-side SPA routing enables zero-latency transitions between public pages and the dashboard.
- **Graceful Resilience:** The dashboard seamlessly communicates with the live FastAPI backend when online, and activates a deterministic synthesis engine when offline.
