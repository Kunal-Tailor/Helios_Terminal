/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        base: 'var(--bg-base)',
        surface: 'var(--bg-surface)',
        'surface-raised': 'var(--bg-surface-raised)',
        hairline: 'var(--border-hairline)',
        primary: 'var(--text-primary)',
        secondary: 'var(--text-secondary)',
        tertiary: 'var(--text-tertiary)',
        accent: 'var(--accent)',
        risk: {
          critical: 'var(--risk-critical)',
          elevated: 'var(--risk-elevated)',
          low: 'var(--risk-low)',
        },
      },
      fontFamily: {
        mono: ['var(--font-mono)'],
        serif: ['var(--font-serif)'],
        ui: ['var(--font-ui)'],
      },
      fontSize: {
        metadata: ['var(--text-metadata)'],
        'body-mono': ['var(--text-body-mono)'],
        'body-ui': ['var(--text-body-ui)'],
        prose: ['var(--text-prose)'],
        'section-header': ['var(--text-section-header)'],
        'verdict-headline': ['var(--text-verdict-headline)'],
      },
    },
  },
  plugins: [],
}
