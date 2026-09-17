import { FileText, ArrowDownToLine } from 'lucide-react';
import { useScrollReveal } from '../../shared/useScrollReveal';
import { SiteHeader } from '../../shared/SiteHeader';
import { SiteFooter } from '../../shared/SiteFooter';
import { Button } from '../../shared/Button';

export const About: React.FC = () => {
  const containerRef = useScrollReveal<HTMLDivElement>();

  return (
    <div className="min-h-screen bg-site-bg text-site-text-primary selection:bg-site-accent selection:text-white flex flex-col font-sans" ref={containerRef}>
      <SiteHeader />

      <main className="flex-1 flex flex-col">
        {/* Section 2: Editorial hero */}
        <section className="flex flex-col items-center justify-center min-h-[72vh] px-6 py-20 text-center">
          <div className="max-w-4xl w-full flex flex-col items-center gap-6">
            <span
              className="hero-reveal font-mono text-sm tracking-wider text-site-text-secondary uppercase"
              style={{ '--reveal-delay': '100ms' } as React.CSSProperties}
            >
              The premise
            </span>
            <h1
              className="hero-reveal font-serif text-5xl md:text-6xl lg:text-7xl leading-tight text-site-text-primary"
              style={{ '--reveal-delay': '200ms' } as React.CSSProperties}
            >
              Every organisation adopting AI eventually faces a sourcing fork.
            </h1>
          </div>
        </section>

        {/* Section 3: Narrative */}
        <section className="px-6 py-24 md:py-32 flex flex-col items-center border-t border-hairline border-site-border">
          <div className="max-w-[680px] w-full flex flex-col gap-12">
            <header className="flex flex-col gap-4 text-center items-center">
              <span className="scroll-reveal font-mono text-xs tracking-wider text-site-text-secondary uppercase">
                Why Helios exists
              </span>
              <h2 className="scroll-reveal font-serif text-3xl md:text-4xl leading-tight">
                A tool for choices whose dependencies emerge later.
              </h2>
            </header>

            <div className="flex flex-col gap-8 text-lg text-site-text-secondary leading-relaxed">
              <p className="scroll-reveal drop-cap">
                A defence unit that needs a small language model on a drone can train it privately, license an existing model, or bring in an outside vendor. The same fork appears in ministries, procurement teams, and companies choosing their next AI capability.
              </p>
              <p className="scroll-reveal">
                Each route quietly creates a different dependency. It may only become visible years later—when terms change, a licence expires, or a partner is no longer there. Yet the choice is often made from instinct, feature lists, and vendor pitches.
              </p>
              <p className="scroll-reveal">
                Helios Terminal closes that gap. It focuses on one concrete sourcing decision at a time, comparing realistic paths and making their long-term dependency risks visible before the decision is locked in.
              </p>
            </div>
          </div>
        </section>

        {/* Section 4: Who it's for */}
        <section className="px-6 py-24 md:py-32 flex flex-col items-center bg-site-surface border-y border-hairline border-site-border">
          <div className="max-w-4xl w-full flex flex-col gap-16">
            <header className="flex flex-col gap-4 text-center items-center">
              <span className="scroll-reveal font-mono text-xs tracking-wider text-site-text-secondary uppercase">
                Who it is for
              </span>
              <h2 className="scroll-reveal font-serif text-3xl md:text-4xl leading-tight">
                For people accountable for the path they choose.
              </h2>
            </header>

            <dl className="scroll-reveal flex flex-col divide-y divide-site-border border-y border-site-border">
              {[
                { title: "Government ministries", desc: "Evaluating sovereign AI capability decisions with long public consequences." },
                { title: "Defence units", desc: "Sourcing AI for sensitive, field-deployed, or locally operated systems." },
                { title: "Companies and subsidiaries", desc: "Making consequential build, buy, or outsource calls on AI capability." },
                { title: "Procurement and policy teams", desc: "Needing a defensible, repeatable rationale rather than a vendor pitch deck." }
              ].map((persona, i) => (
                <div key={i} className="group relative flex flex-col md:flex-row gap-2 md:gap-8 py-8 transition-colors hover:bg-site-bg">
                  <div className="absolute left-0 top-0 bottom-0 w-1 bg-site-accent opacity-0 group-hover:opacity-100 transition-opacity" />
                  <dt className="md:w-1/3 font-serif text-xl pl-6 text-site-text-primary">
                    {persona.title}
                  </dt>
                  <dd className="md:w-2/3 pl-6 md:pl-0 text-site-text-secondary text-lg">
                    {persona.desc}
                  </dd>
                </div>
              ))}
            </dl>
          </div>
        </section>

        {/* Section 5: Pull-quote */}
        <section className="px-6 py-24 md:py-32 flex flex-col items-center">
          <div className="scroll-reveal max-w-4xl w-full bg-site-surface border border-hairline border-site-border rounded-site p-12 md:p-20 text-center relative overflow-hidden flex flex-col items-center gap-8">
            <span className="absolute top-4 left-6 text-8xl md:text-9xl text-site-border opacity-20 font-serif leading-none select-none">"</span>
            <span className="absolute bottom-[-2rem] right-6 text-8xl md:text-9xl text-site-border opacity-20 font-serif leading-none select-none">"</span>

            <p className="font-serif italic text-2xl md:text-4xl text-site-text-primary leading-snug relative z-10 max-w-2xl">
              A usable decision-support tool—and a repeatable method for forecasting AI dependency risk before it is locked in.
            </p>
            <span className="font-mono text-xs uppercase tracking-widest text-site-text-secondary relative z-10">
              Helios Terminal's twofold contribution
            </span>
          </div>
        </section>

        {/* Section 6: Synopsis download card */}
        <section className="px-6 pb-32 flex flex-col items-center">
          <div className="scroll-reveal max-w-2xl w-full border border-hairline border-site-border rounded-site p-8 md:p-12 flex flex-col md:flex-row items-center gap-8 md:gap-12 bg-site-bg hover:bg-site-surface transition-colors group">
            <div className="p-4 bg-site-surface border border-site-border rounded-full group-hover:bg-site-bg transition-colors">
              <FileText className="w-8 h-8 text-site-text-secondary group-hover:text-site-accent transition-colors" />
            </div>

            <div className="flex-1 flex flex-col gap-2 text-center md:text-left">
              <span className="font-mono text-xs tracking-wider text-site-text-secondary uppercase">
                Project document / DOCX
              </span>
              <h3 className="font-serif text-2xl text-site-text-primary">
                Helios Terminal Synopsis
              </h3>
              <p className="text-site-text-secondary">
                Read the project framing, architecture, and research contribution in the full synopsis.
              </p>
            </div>

            <Button
              variant="primary"
              href="/assets/Helios-Terminal-Synopsis.docx"
              download={true}
              className="shrink-0 flex items-center gap-2"
            >
              Download <ArrowDownToLine className="w-4 h-4" />
            </Button>
          </div>
        </section>

      </main>

      <SiteFooter />
    </div>
  );
};