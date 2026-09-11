export default function App() {
  return (
    <div className="theme-site min-h-screen bg-site-bg text-site-text-primary flex flex-col justify-between">
      <main className="max-w-4xl mx-auto px-6 py-16">
        <div className="inline-block px-2.5 py-1 mb-6 text-xs font-mono tracking-wider uppercase bg-site-surface border border-site-border rounded-site text-site-text-secondary">
          [HELIOS TERMINAL // PHASE 8.2 SCAFFOLD]
        </div>

        <h1 className="text-4xl sm:text-5xl font-serif font-bold text-site-text-primary tracking-tight mb-4 leading-tight">
          Strategic Tech Sovereignty Decision Engine
        </h1>

        <p className="text-lg text-site-text-secondary font-sans max-w-2xl mb-8 leading-relaxed">
          Evaluating critical build vs. buy vs. outsource sovereignty forks through 
          verified multi-agent reasoning and bounded backward recalibration.
        </p>

        <div className="p-6 bg-site-surface border border-site-border rounded-site max-w-lg mb-8">
          <h2 className="text-sm font-mono uppercase tracking-wider text-site-accent mb-2">
            Design Tokens Active
          </h2>
          <p className="text-sm text-site-text-secondary leading-normal">
            Theme variables loaded from <code className="font-mono text-site-text-primary">site-theme.css</code>: 
            Source Serif 4, Inter, IBM Plex Mono, and muted phosphor-teal accent.
          </p>
        </div>

        <div className="flex items-center gap-4">
          <button className="px-5 py-2.5 bg-site-accent text-white font-sans text-sm font-medium rounded-site transition-colors hover:opacity-90">
            Enter Dashboard
          </button>
          <button className="px-5 py-2.5 bg-transparent border border-site-border text-site-text-primary font-sans text-sm font-medium rounded-site transition-colors hover:border-site-text-secondary">
            See Architecture
          </button>
        </div>
      </main>

      <footer className="border-t border-site-border py-6 text-center text-xs text-site-text-secondary font-sans">
        Helios Terminal &middot; Strategic Autonomy & Sovereign AI
      </footer>
    </div>
  );
}
