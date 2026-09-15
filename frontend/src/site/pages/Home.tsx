import { Link } from 'react-router-dom';
import { ArrowRight, GitFork, ShieldCheck, RefreshCw, ScanSearch } from 'lucide-react';
import { SiteHeader } from '../../shared/SiteHeader';
import { SiteFooter } from '../../shared/SiteFooter';
import { Button } from '../../shared/Button';
import { useScrollReveal } from '../../shared/useScrollReveal';

export const Home: React.FC = () => {
  const revealRef = useScrollReveal();

  return (
    <div className="min-h-screen bg-site-bg text-site-text-primary font-sans flex flex-col">
      <SiteHeader />

      <main ref={revealRef} className="flex-1 flex flex-col">
        {/* 2. Hero */}
        <section className="w-full max-w-[760px] mx-auto px-6 pt-32 pb-24 text-center flex flex-col items-center justify-center min-h-[80vh]">
          <div
            className="hero-reveal text-site-accent font-mono text-sm tracking-wider mb-6"
            style={{ '--reveal-delay': '0ms' } as React.CSSProperties}
          >
            [ strategic autonomy / decision engine ]
          </div>
          <h1
            className="hero-reveal font-serif text-5xl md:text-6xl font-semibold leading-tight text-site-text-primary mb-6"
            style={{ '--reveal-delay': '80ms' } as React.CSSProperties}
          >
            Build, buy, or outsource—<br />choose with the full picture.
          </h1>
          <p
            className="hero-reveal font-sans text-lg md:text-xl text-site-text-secondary leading-relaxed mb-10 max-w-[640px]"
            style={{ '--reveal-delay': '160ms' } as React.CSSProperties}
          >
            Helios Terminal turns a high-stakes AI sourcing decision into a verified, comparative path forward—so capability today does not become dependency tomorrow.
          </p>
          <div
            className="hero-reveal flex flex-col sm:flex-row items-center gap-4"
            style={{ '--reveal-delay': '240ms' } as React.CSSProperties}
          >
            <Button to="/dashboard" variant="primary">
              Enter dashboard <ArrowRight className="ml-2 h-4 w-4" aria-hidden="true" />
            </Button>
            <Button to="/architecture" variant="secondary">
              See the architecture
            </Button>
          </div>
        </section>

        {/* 3. Problem teaser */}
        <section className="w-full max-w-6xl mx-auto px-6 py-24 scroll-reveal" style={{ '--reveal-delay': '100ms' } as React.CSSProperties}>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div>
              <div className="font-mono text-site-accent text-sm tracking-widest uppercase mb-4">
                The decision beneath the decision
              </div>
              <h2 className="font-serif text-3xl md:text-4xl text-site-text-primary mb-6 leading-tight">
                An AI choice changes more than the tool you use.
              </h2>
              <div className="text-site-text-secondary space-y-4 font-sans text-lg leading-relaxed">
                <p>
                  Sourcing an AI capability isn't just a technical evaluation. It reshapes your intellectual property boundary, operational agility, and long-term risk profile.
                </p>
                <p>
                  Helios Terminal models these trade-offs mathematically. It maps the cascading effects of building in-house, buying off-the-shelf, or outsourcing—empowering you to act with conviction.
                </p>
              </div>
            </div>
            
            <div className="border border-site-border rounded-site bg-site-surface p-8 relative flex justify-center items-center overflow-hidden aspect-video">
              <svg width="400" height="240" viewBox="0 0 400 240" className="w-full h-full max-w-[400px]">
                {/* Decision central point */}
                <circle cx="80" cy="120" r="12" fill="var(--site-surface)" stroke="var(--site-accent)" strokeWidth="4" />
                <text x="80" y="150" fill="var(--site-text-secondary)" fontFamily="var(--site-font-mono)" fontSize="12" textAnchor="middle">DECISION</text>
                
                {/* Paths */}
                {/* BUILD path */}
                <path d="M 92 120 C 150 120, 180 50, 240 50" fill="none" stroke="var(--site-accent)" strokeWidth="2" opacity="0.6" />
                <circle cx="240" cy="50" r="8" fill="var(--site-accent)" />
                <text x="256" y="54" fill="var(--site-text-primary)" fontFamily="var(--site-font-sans)" fontSize="14" fontWeight="bold">BUILD</text>
                
                {/* BUY path */}
                <path d="M 92 120 C 150 120, 180 120, 240 120" fill="none" stroke="var(--site-accent)" strokeWidth="2" opacity="0.6" />
                <circle cx="240" cy="120" r="8" fill="var(--site-accent)" />
                <text x="256" y="124" fill="var(--site-text-primary)" fontFamily="var(--site-font-sans)" fontSize="14" fontWeight="bold">BUY</text>
                
                {/* OUTSOURCE path */}
                <path d="M 92 120 C 150 120, 180 190, 240 190" fill="none" stroke="var(--site-accent)" strokeWidth="2" opacity="0.6" />
                <circle cx="240" cy="190" r="8" fill="var(--site-accent)" />
                <text x="256" y="194" fill="var(--site-text-primary)" fontFamily="var(--site-font-sans)" fontSize="14" fontWeight="bold">OUTSOURCE</text>
              </svg>
            </div>
          </div>
        </section>

        {/* 4. Pipeline strip */}
        <section className="w-full max-w-6xl mx-auto px-6 py-12 scroll-reveal" style={{ '--reveal-delay': '100ms' } as React.CSSProperties}>
          <Link to="/architecture" className="block group">
            <div className="border border-site-border bg-site-surface rounded-site p-8 md:p-12 hover:border-site-accent transition-colors duration-300">
              <div className="font-mono text-xs text-site-text-secondary uppercase mb-8 text-center group-hover:text-site-accent transition-colors duration-300">
                Helios Terminal Analysis Pipeline — Click to see architecture
              </div>
              <div className="relative flex flex-col md:flex-row justify-between items-center w-full">
                {/* Connecting line (desktop) */}
                <div className="hidden md:block absolute top-6 left-0 right-0 h-[2px] bg-site-accent opacity-30 -z-0"></div>
                {/* Connecting line (mobile) */}
                <div className="md:hidden absolute top-0 bottom-0 left-6 w-[2px] bg-site-accent opacity-30 -z-0"></div>
                
                {[
                  { num: '01', label: 'Ingest' },
                  { num: '02', label: 'Map stack' },
                  { num: '03', label: 'Generate' },
                  { num: '04', label: 'Predict' },
                  { num: '05', label: 'Diagnose' },
                  { num: '06', label: 'Verdict' }
                ].map((step, idx) => (
                  <div key={idx} className="relative z-10 flex flex-row md:flex-col items-center gap-4 md:gap-3 w-full md:w-auto py-4 md:py-0 bg-site-surface">
                    <div className="w-12 h-12 rounded-full border-2 border-site-accent bg-site-surface flex items-center justify-center font-mono text-sm text-site-text-primary">
                      {step.num}
                    </div>
                    <div className="font-sans font-medium text-site-text-primary">{step.label}</div>
                  </div>
                ))}
              </div>
            </div>
          </Link>
        </section>

        {/* 5. Three pillars */}
        <section className="w-full max-w-6xl mx-auto px-6 py-24">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="scroll-reveal border border-hairline border-site-border rounded-site bg-site-surface p-8 transition-transform duration-300 hover:-translate-y-1 hover:border-site-accent" style={{ '--reveal-delay': '100ms' } as React.CSSProperties}>
              <div className="w-12 h-12 rounded-full bg-site-accent/10 flex items-center justify-center text-site-accent mb-6">
                <GitFork size={24} />
              </div>
              <h3 className="font-sans font-bold text-xl text-site-text-primary mb-3">Decision-scoped</h3>
              <p className="font-sans text-site-text-secondary leading-relaxed">
                Starts with the sourcing choice in front of you—not a generic technology forecast.
              </p>
            </div>

            <div className="scroll-reveal border border-hairline border-site-border rounded-site bg-site-surface p-8 transition-transform duration-300 hover:-translate-y-1 hover:border-site-accent" style={{ '--reveal-delay': '200ms' } as React.CSSProperties}>
              <div className="w-12 h-12 rounded-full bg-site-accent/10 flex items-center justify-center text-site-accent mb-6">
                <ShieldCheck size={24} />
              </div>
              <h3 className="font-sans font-bold text-xl text-site-text-primary mb-3">Verified</h3>
              <p className="font-sans text-site-text-secondary leading-relaxed">
                Every stage keeps its claims grounded in traceable, cited source material.
              </p>
            </div>

            <div className="scroll-reveal border border-hairline border-site-border rounded-site bg-site-surface p-8 transition-transform duration-300 hover:-translate-y-1 hover:border-site-accent" style={{ '--reveal-delay': '300ms' } as React.CSSProperties}>
              <div className="w-12 h-12 rounded-full bg-site-accent/10 flex items-center justify-center text-site-accent mb-6">
                <RefreshCw size={24} />
              </div>
              <h3 className="font-sans font-bold text-xl text-site-text-primary mb-3">Self-correcting</h3>
              <p className="font-sans text-site-text-secondary leading-relaxed">
                When context is thin, targeted recalibration closes the gap before a verdict is made.
              </p>
            </div>
          </div>
        </section>

        {/* 6. Dashboard CTA band */}
        <section className="w-full bg-site-surface mt-12 scroll-reveal relative" style={{ '--reveal-delay': '100ms' } as React.CSSProperties}>
          <div className="max-w-4xl mx-auto px-6 py-24 text-center flex flex-col items-center">
            <div className="text-site-accent mb-6">
              <ScanSearch size={48} strokeWidth={1.5} />
            </div>
            <h2 className="font-serif text-4xl text-site-text-primary mb-6">
              See the decision behind the decision.
            </h2>
            <p className="font-sans text-lg text-site-text-secondary mb-10 max-w-2xl">
              Access the Helios Terminal dashboard to start modeling your AI sourcing decisions with empirical rigour.
            </p>
            <Button to="/dashboard" variant="primary">
              Enter dashboard <ArrowRight className="ml-2 h-4 w-4" aria-hidden="true" />
            </Button>
          </div>
          {/* Dark gradient sliver at the bottom */}
          <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-site-text-primary to-transparent opacity-20"></div>
        </section>
      </main>

      <SiteFooter />
    </div>
  );
};
