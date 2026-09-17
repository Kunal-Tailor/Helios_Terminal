# 05 — Design system (website)

Scoped to the marketing website. The Dashboard maintains its own dark terminal token set defined in `src/dashboard/styles/terminal.css`, sharing only the accent color.

## Color Tokens

| Token | Value | Tailwind Class | Use |
| --- | --- | --- | --- |
| `--site-bg` | `#F7F3EE` | `bg-site-bg` | Page canvas (warm bone/sand) |
| `--site-surface` | `#EDE6DC` | `bg-site-surface` | Cards, bands, pill tags, diagram backgrounds |
| `--site-text-primary` | `#2A2724` | `text-site-text-primary` | Body text, headlines (warm charcoal) |
| `--site-text-secondary` | `#6B645C` | `text-site-text-secondary` | Supporting text, captions, metadata |
| `--site-border` | `#DDD5C9` | `border-site-border` | Hairline borders (0.5px) |
| `--site-accent` | `#3FA7B3` | `bg-site-accent`, `text-site-accent` | Muted teal accent — CTAs, links, flowchart edges |

## Typography

| Role | Font Family | Tailwind Class | Usage |
| --- | --- | --- | --- |
| Headline / Editorial | "Source Serif 4", Georgia, serif | `font-serif` | Hero headlines, About narrative, pull-quotes |
| UI / Body | Inter, system-ui, sans-serif | `font-sans` | Body copy, navigation links, buttons, cards |
| Technical Accent | "IBM Plex Mono", Menlo, monospace | `font-mono` | Stage tags, category labels, metrics, code snippets |

### Editorial Styling: Drop Cap (`.drop-cap`)
```css
.drop-cap::first-letter {
  float: left;
  font-family: var(--site-font-serif);
  font-size: 3.75rem;
  line-height: 0.8;
  padding-right: 0.6rem;
  padding-top: 0.2rem;
  color: var(--site-text-primary);
  font-weight: 600;
}
```

## Motion System & Animation Classes

### 1. Hero Reveal (`.hero-reveal`)
Used on top-of-page headlines and intro copy to smoothly fade up upon initial mount:
```css
.hero-reveal {
  opacity: 0;
  transform: translateY(12px);
  animation: hero-fade-up 600ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
  animation-delay: var(--reveal-delay, 0ms);
}
```

### 2. Scroll-Triggered Reveal (`.scroll-reveal`)
Triggered via `useScrollReveal` hook as elements enter the viewport:
```css
.scroll-reveal {
  opacity: 0;
  transform: translateY(16px);
  transition: opacity 500ms cubic-bezier(0.16, 1, 0.3, 1), transform 500ms cubic-bezier(0.16, 1, 0.3, 1);
  transition-delay: var(--reveal-delay, 0ms);
  will-change: opacity, transform;
}

.scroll-reveal.visible {
  opacity: 1;
  transform: translateY(0);
}
```

### 3. Reduced Motion
Fully disabled when `prefers-reduced-motion: reduce` is detected:
```css
@media (prefers-reduced-motion: reduce) {
  .theme-site .site-reveal,
  .hero-reveal,
  .scroll-reveal {
    opacity: 1 !important;
    transform: none !important;
    transition: none !important;
    animation: none !important;
  }
}
```

## Diagram Theming (Mermaid)

Flowcharts in `src/shared/Mermaid.tsx` are initialized with brand design tokens:
```typescript
themeVariables: {
  primaryColor: '#EDE6DC',        // --site-surface
  primaryTextColor: '#2A2724',    // --site-text-primary
  primaryBorderColor: '#DDD5C9',  // --site-border
  lineColor: '#3FA7B3',           // --site-accent
  secondaryColor: '#F7F3EE',      // --site-bg
  tertiaryColor: '#F7F3EE',
  fontFamily: '"Inter", sans-serif',
}
```

## Button Variants (`Button.tsx`)

- **Primary:** `bg-site-accent text-white hover:opacity-90 active:scale-[0.99]`
- **Secondary:** `bg-transparent border border-site-border text-site-text-primary hover:border-site-text-secondary hover:bg-site-surface/50`
- **Ghost:** `bg-transparent text-site-text-secondary hover:text-site-text-primary hover:underline`
- **File Downloads:** Supports `download` prop on `href` targets, automatically bypassing `target="_blank"`.
