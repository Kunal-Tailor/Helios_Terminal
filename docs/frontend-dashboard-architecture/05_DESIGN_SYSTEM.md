# 05_DESIGN_SYSTEM.md — Helios Terminal Dashboard

## Source file

`frontend/src/dashboard/styles/terminal.css` — all tokens defined as CSS custom properties on `:root`. Imported globally in the dashboard entry point. Components reference tokens via `var(--bb-*)` in Tailwind arbitrary-value classes (e.g. `bg-[var(--bb-bg-surface)]`).

---

## Color palette

### Background layers (depth system)

| Token | Value | Usage |
|---|---|---|
| `--bb-bg-base` | `#07090D` | Outermost terminal container, command bar input, footer |
| `--bb-bg-surface` | `#0D1117` | Panel backgrounds, header |
| `--bb-bg-raised` | `#131821` | Cards, panel headers (gradient end), option chips |
| `--bb-bg-elevated` | `#1A202C` | Hover states for autocomplete rows |
| `--bb-bg-input` | `#090C10` | All text input fields |

### Border hierarchy

| Token | Value | Usage |
|---|---|---|
| `--bb-border-subtle` | `#1B2230` | Default panel borders, section dividers |
| `--bb-border-mid` | `#252F42` | Hover borders, autocomplete container |
| `--bb-border-bright` | `#384661` | Active/focused panel containers |
| `--bb-border-active` | `#FF9E00` | Focused panels (`.bb-focused` class), active tab ribbon |

### Accent colors

| Token | Value | Hex | Role |
|---|---|---|---|
| `--bb-amber` | `#FF9E00` | Bloomberg amber | Primary brand accent, active tabs, `<GO>` button, command bar |
| `--bb-amber-bright` | `#FFB733` | Lighter amber | Hover states for amber elements |
| `--bb-amber-dim` | `rgba(255,158,0,0.12)` | Amber tint | Active tab backgrounds, badge backgrounds |
| `--bb-cyan` | `#00E5FF` | Cyan | Trajectory tab accent, latency toggle active |
| `--bb-cyan-bright` | `#33EBFF` | Lighter cyan | — |
| `--bb-cyan-dim` | `rgba(0,229,255,0.12)` | Cyan tint | BMAP tab background, cyan badge fill |
| `--bb-green` | `#00FF66` | Terminal green | Success state, verified verdict badge, live indicator |
| `--bb-green-bright` | `#33FF85` | Lighter green | — |
| `--bb-green-dim` | `rgba(0,255,102,0.12)` | Green tint | Audit tab, success badge backgrounds |
| `--bb-red` | `#FF3366` | Terminal red | Failure state, danger badges |
| `--bb-red-bright` | `#FF5C85` | Lighter red | — |
| `--bb-red-dim` | `rgba(255,51,102,0.12)` | Red tint | Lock-In matrix tab, failure badge backgrounds |
| `--bb-purple` | `#B388FF` | Purple | Intel Feed tab accent |
| `--bb-purple-dim` | `rgba(179,136,255,0.12)` | Purple tint | Feed tab background |
| `--bb-gold` | `#FFD700` | Gold | Special callout indicators |

> **Note on brand continuity:** The teal `#3FA7B3` used on the marketing website is replaced in the dashboard by Bloomberg amber `#FF9E00`. The dashboard operates on its own color grammar.

### Status color semantics

| Purpose | Token | Value |
|---|---|---|
| Success / verified | `--bb-green` | `#00FF66` |
| Warning / caution | `--bb-amber` | `#FF9E00` |
| Danger / failed | `--bb-red` | `#FF3366` |
| Neutral / muted | `--bb-text-muted` | `#64748B` |

---

## Typography

### Font stack

| Token | Value | Usage |
|---|---|---|
| `--bb-font-mono` | `'JetBrains Mono', 'SF Mono', 'Fira Code', Menlo, Monaco, Consolas, monospace` | All dashboard text (default) |
| `--bb-font-sans` | `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif` | Available for non-monospace overrides |

The entire `.bloomberg-terminal` container uses `--bb-font-mono` as its `font-family`. The dashboard is intentionally monospace-first.

### Text colors

| Token | Value | Usage |
|---|---|---|
| `--bb-text-bright` | `#FFFFFF` | Input values, primary header text, recommended path |
| `--bb-text-primary` | `#E2E8F0` | Body text, verdict narrative |
| `--bb-text-secondary` | `#94A3B8` | Supporting labels, secondary values |
| `--bb-text-muted` | `#64748B` | Section labels, timestamps |
| `--bb-text-dim` | `#475569` | Placeholder text, decorative separators |

### Scale conventions (no formal type scale tokens)

| Use | Size | Weight |
|---|---|---|
| Panel header labels | `11px` / `text-xs` | `700` |
| Section labels (uppercase) | `10px` | `700`, `tracking-wider` |
| Body text / narrative | `12px` / `text-xs` | `400` |
| Ticker tape | `10px` | `400`/`700` (symbol) |
| Badge text | `10px` | `700` |
| Footer strip | `10px` | `400`/`700` |
| Tabular figures | `--bb-font-mono` + `font-variant-numeric: tabular-nums lining-nums` (`.bb-tabular` class) | |

---

## Component primitives

### `.bloomberg-terminal`

Root container. Sets `background-color: var(--bb-bg-base)`, `color: var(--bb-text-primary)`, `font-family: var(--bb-font-mono)`, `-webkit-font-smoothing: antialiased`.

### `.bb-panel`

Core workstation panel. `background: var(--bb-bg-surface)`, `border: 1px solid var(--bb-border-subtle)`, `position: relative`. Hover: `border-color: var(--bb-border-mid)`. Focus variant `.bb-focused`: amber border + inner amber glow via `box-shadow`.

### `.bb-panel-header`

Strip header bar inside a panel. Linear gradient from `--bb-bg-raised` to `--bb-bg-surface`, bottom border, `6px 10px` padding, `11px` font, `700` weight, uppercase, `letter-spacing: 0.08em`. Flex row with space-between for title/badge layout.

### `.bb-badge`

Status badge. `10px` monospace, `700` weight, `2px 6px` padding, `border-radius: 2px`, uppercase. Variants:

| Class | Border / text color | Background |
|---|---|---|
| `.bb-badge-amber` | `--bb-amber` | `--bb-amber-dim` |
| `.bb-badge-cyan` | `--bb-cyan` | `--bb-cyan-dim` |
| `.bb-badge-green` | `--bb-green` | `--bb-green-dim` |
| `.bb-badge-red` | `--bb-red` | `--bb-red-dim` |
| `.bb-badge-dim` | `--bb-border-mid` | `rgba(100,116,139,0.12)` |

### `.bb-button`

Interactive button. `11px` monospace, `700`, uppercase, `2px` border-radius, `5px 12px` padding, 0.12s transition. Disabled: `opacity: 0.45`, `cursor: not-allowed`.

| Variant | Description |
|---|---|
| `.bb-button-go` | Primary CTA — amber background, black text, amber glow shadow. Used for `<GO>` and `EXECUTE SOURCING VERDICT`. |
| `.bb-button-ghost` | Secondary — surface background, subtle border. Used for ADD, cancel actions. |

---

## Animations

### `.bb-live-indicator`

Applied to the backend health beacon (when online) and the `SYNTHESIZING` pipeline badge. Keyframe `bb-pulse-glow`: opacity oscillates 1 → 0.4 → 1 with a green `drop-shadow` at full opacity. Duration: `1.8s`, `ease-in-out`, `infinite`.

### `.bb-ticker-track`

Continuous left-scroll ticker tape. Keyframe `bb-ticker`: `translate3d(0,0,0)` → `translate3d(-50%,0,0)` over `40s linear infinite`. The track contains duplicate items (`[...TICKER_ITEMS, ...TICKER_ITEMS]`) so the loop is seamless. Animation pauses on `:hover`.

### Transition conventions

- Panel border color change: `0.15s ease`.
- Button interactions: `0.12s ease` (including `translateY(-1px)` lift on `.bb-button-go:hover`).
- Tab ribbon button color change: uses Tailwind `transition-all`.

---

## Scrollbar conventions

`.bb-scroll` applies custom webkit scrollbar styling: `6px` width, `--bb-bg-base` track, `--bb-border-mid` thumb. Thumb turns amber (`--bb-amber`) on hover. All scrollable panel bodies receive the `.bb-scroll` class.

---

## Scanline overlay (optional)

`.bb-scanline` — a `linear-gradient` repeating every 4px to simulate CRT scanlines. `pointer-events: none`. Applied as an optional aesthetic layer — not active by default in the current build.

---

## Responsive stance

**Desktop-only for MVP.** No responsive breakpoints are defined in `terminal.css`. The quadrant grid uses `grid-cols-1 lg:grid-cols-2` from Tailwind (collapses to single-column on small screens) but the overall workstation experience degrades significantly below 1280px. No mobile layout is planned.
