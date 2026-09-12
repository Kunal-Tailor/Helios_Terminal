import React from 'react';
import { ArrowDownToLine, FileText } from 'lucide-react';
import { SiteHeader } from '../../shared/SiteHeader';
import { SiteFooter } from '../../shared/SiteFooter';
import { Button } from '../../shared/Button';

const audiences = [
  {
    label: 'Government ministries',
    description: 'Evaluating sovereign AI capability decisions with long public consequences.',
  },
  {
    label: 'Defence units',
    description: 'Sourcing AI for sensitive, field-deployed, or locally operated systems.',
  },
  {
    label: 'Companies and subsidiaries',
    description: 'Making consequential build, buy, or outsource calls on AI capability.',
  },
  {
    label: 'Procurement and policy teams',
    description: 'Needing a defensible, repeatable rationale rather than a vendor pitch deck.',
  },
];

export const About: React.FC = () => {
  return (
    <div className="theme-site min-h-screen bg-site-bg text-site-text-primary">
      <SiteHeader />
      <main>
        <section className="flex min-h-[calc(72vh-4rem)] items-center px-6 py-20 text-center sm:py-28">
          <div className="mx-auto max-w-4xl">
            <p className="font-mono text-[11px] uppercase tracking-[0.16em] text-site-accent">
              The premise
            </p>
            <h1 className="mt-6 font-serif text-5xl font-semibold leading-[1.04] tracking-[-0.04em] sm:text-6xl lg:text-7xl">
              Every organisation adopting AI eventually faces a sourcing fork.
            </h1>
          </div>
        </section>

        <section className="border-y border-site-border px-6 py-20 sm:py-28" aria-labelledby="narrative-heading">
          <div className="mx-auto max-w-[680px]">
            <p className="font-mono text-[11px] uppercase tracking-[0.16em] text-site-accent">Why Helios exists</p>
            <h2 id="narrative-heading" className="mt-4 font-serif text-4xl tracking-[-0.025em] sm:text-5xl">
              A tool for choices whose dependencies emerge later.
            </h2>
            <div className="mt-9 space-y-6 text-base leading-8 text-site-text-secondary sm:text-lg">
              <p>
                <span className="float-left mr-2 font-serif text-6xl leading-[0.76] text-site-text-primary sm:text-7xl">A</span>
                defence unit that needs a small language model on a drone can train it privately,
                license an existing model, or bring in an outside vendor. The same fork appears in
                ministries, procurement teams, and companies choosing their next AI capability.
              </p>
              <p>
                Each route quietly creates a different dependency. It may only become visible years
                later—when terms change, a licence expires, or a partner is no longer there. Yet the
                choice is often made from instinct, feature lists, and vendor pitches.
              </p>
              <p>
                Helios Terminal closes that gap. It focuses on one concrete sourcing decision at a
                time, comparing realistic paths and making their long-term dependency risks visible
                before the decision is locked in.
              </p>
            </div>
          </div>
        </section>

        <section className="px-6 py-20 sm:py-28" aria-labelledby="audience-heading">
          <div className="mx-auto max-w-4xl">
            <div className="max-w-xl">
              <p className="font-mono text-[11px] uppercase tracking-[0.16em] text-site-accent">Who it is for</p>
              <h2 id="audience-heading" className="mt-4 font-serif text-4xl tracking-[-0.025em] sm:text-5xl">
                For people accountable for the path they choose.
              </h2>
            </div>
            <dl className="mt-10 divide-y divide-site-border border-y border-site-border">
              {audiences.map(({ label, description }) => (
                <div key={label} className="grid gap-2 py-5 sm:grid-cols-[minmax(12rem,0.75fr)_1.5fr] sm:gap-8">
                  <dt className="text-sm font-semibold text-site-text-primary">{label}</dt>
                  <dd className="text-sm leading-6 text-site-text-secondary">{description}</dd>
                </div>
              ))}
            </dl>
          </div>
        </section>

        <section className="border-y border-site-border bg-site-surface px-6 py-20 text-center sm:py-28">
          <blockquote className="mx-auto max-w-4xl font-serif text-4xl italic leading-tight tracking-[-0.025em] sm:text-5xl lg:text-6xl">
            “A usable decision-support tool—and a repeatable method for forecasting AI dependency risk before it is locked in.”
          </blockquote>
          <p className="mt-7 font-mono text-[10px] uppercase tracking-[0.16em] text-site-text-secondary">
            Helios Terminal’s twofold contribution
          </p>
        </section>

        <section className="px-6 py-20 sm:py-24" aria-labelledby="synopsis-heading">
          <div className="mx-auto max-w-3xl border-hairline border-site-border p-6 sm:p-9">
            <div className="flex flex-col justify-between gap-8 sm:flex-row sm:items-center">
              <div className="flex max-w-xl gap-4">
                <FileText className="mt-1 h-5 w-5 shrink-0 text-site-accent" strokeWidth={1.5} aria-hidden="true" />
                <div>
                  <p className="font-mono text-[10px] uppercase tracking-[0.15em] text-site-text-secondary">Project document / DOCX</p>
                  <h2 id="synopsis-heading" className="mt-2 font-serif text-2xl tracking-[-0.02em] sm:text-3xl">Helios Terminal Synopsis</h2>
                  <p className="mt-2 text-sm leading-6 text-site-text-secondary">
                    Read the project framing, architecture, and research contribution in the full synopsis.
                  </p>
                </div>
              </div>
              <Button href="/assets/Helios-Terminal-Synopsis.docx" variant="primary" size="md" className="shrink-0">
                Download <ArrowDownToLine className="ml-2 h-4 w-4" aria-hidden="true" />
              </Button>
            </div>
          </div>
        </section>
      </main>
      <SiteFooter />
    </div>
  );
};
