import React from 'react';
import { ArrowRight, GitFork, RefreshCw, ScanSearch, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';
import { SiteHeader } from '../../shared/SiteHeader';
import { SiteFooter } from '../../shared/SiteFooter';
import { Button } from '../../shared/Button';

const pipelineStages = ['Ingest', 'Map stack', 'Generate', 'Predict', 'Diagnose', 'Verdict'];

const pillars = [
  {
    icon: GitFork,
    title: 'Decision-scoped',
    description: 'Starts with the sourcing choice in front of you—not a generic technology forecast.',
  },
  {
    icon: ShieldCheck,
    title: 'Verified',
    description: 'Every stage keeps its claims grounded in traceable, cited source material.',
  },
  {
    icon: RefreshCw,
    title: 'Self-correcting',
    description: 'When context is thin, targeted recalibration closes the gap before a verdict is made.',
  },
];

export const Home: React.FC = () => {
  return (
    <div className="theme-site min-h-screen bg-site-bg text-site-text-primary">
      <SiteHeader />

      <main>
        <section className="flex min-h-[calc(80vh-4rem)] items-center px-6 py-20 sm:py-28">
          <div className="mx-auto max-w-3xl text-center">
            <p className="mx-auto mb-7 w-max border-hairline border-site-border bg-site-surface px-3 py-1.5 font-mono text-[11px] uppercase tracking-[0.18em] text-site-text-secondary">
              [ strategic autonomy / decision engine ]
            </p>
            <h1 className="font-serif text-5xl font-semibold leading-[1.02] tracking-[-0.035em] sm:text-6xl lg:text-7xl">
              Build, buy, or outsource—
              <span className="block">choose with the full picture.</span>
            </h1>
            <p className="mx-auto mt-7 max-w-2xl text-base leading-7 text-site-text-secondary sm:text-lg">
              Helios Terminal turns a high-stakes AI sourcing decision into a verified,
              comparative path forward—so capability today does not become dependency tomorrow.
            </p>
            <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Button to="/dashboard" variant="primary" size="lg">
                Enter dashboard <ArrowRight className="ml-2 h-4 w-4" aria-hidden="true" />
              </Button>
              <Button to="/architecture" variant="secondary" size="lg">
                See the architecture
              </Button>
            </div>
          </div>
        </section>

        <section className="border-y border-site-border px-6 py-20 sm:py-28">
          <div className="mx-auto grid max-w-6xl items-center gap-14 lg:grid-cols-2 lg:gap-24">
            <div>
              <p className="font-mono text-[11px] uppercase tracking-[0.16em] text-site-accent">
                The decision beneath the decision
              </p>
              <h2 className="mt-4 max-w-lg font-serif text-4xl leading-tight tracking-[-0.025em] sm:text-5xl">
                An AI choice changes more than the tool you use.
              </h2>
              <div className="mt-6 max-w-xl space-y-4 text-base leading-7 text-site-text-secondary">
                <p>
                  Every sourcing path carries a different mix of capability, control, and future
                  exposure. The trade-off is rarely visible in a feature comparison alone.
                </p>
                <p>
                  Helios maps the stack, compares plausible paths, and makes the dependencies
                  behind each outcome explicit before they harden into lock-in.
                </p>
              </div>
            </div>

            <div className="mx-auto w-full max-w-md border-hairline border-site-border p-6 sm:p-9">
              <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-site-text-secondary">
                Three sourcing paths
              </p>
              <svg
                className="mt-7 h-auto w-full"
                viewBox="0 0 420 220"
                role="img"
                aria-labelledby="fork-diagram-title fork-diagram-description"
              >
                <title id="fork-diagram-title">A sourcing decision branches into three paths</title>
                <desc id="fork-diagram-description">
                  A central decision point branches to build in-house, buy a platform, or outsource
                  a capability.
                </desc>
                <circle cx="74" cy="110" r="7" fill="var(--site-accent)" />
                <path
                  d="M82 110 H155 C185 110 184 42 218 42 H310 M155 110 H310 M155 110 C185 110 184 178 218 178 H310"
                  fill="none"
                  stroke="var(--site-accent)"
                  strokeWidth="1.5"
                />
                <circle cx="322" cy="42" r="5" fill="var(--site-bg)" stroke="var(--site-accent)" strokeWidth="1.5" />
                <circle cx="322" cy="110" r="5" fill="var(--site-bg)" stroke="var(--site-accent)" strokeWidth="1.5" />
                <circle cx="322" cy="178" r="5" fill="var(--site-bg)" stroke="var(--site-accent)" strokeWidth="1.5" />
                <text x="16" y="142" fill="var(--site-text-secondary)" fontFamily="var(--site-font-mono)" fontSize="11">decision</text>
                <text x="342" y="46" fill="var(--site-text-primary)" fontFamily="var(--site-font-mono)" fontSize="12">BUILD</text>
                <text x="342" y="114" fill="var(--site-text-primary)" fontFamily="var(--site-font-mono)" fontSize="12">BUY</text>
                <text x="342" y="182" fill="var(--site-text-primary)" fontFamily="var(--site-font-mono)" fontSize="12">OUTSOURCE</text>
              </svg>
            </div>
          </div>
        </section>

        <section className="px-6 py-20 sm:py-28">
          <div className="mx-auto max-w-6xl">
            <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
              <div>
                <p className="font-mono text-[11px] uppercase tracking-[0.16em] text-site-accent">Six-stage reasoning flow</p>
                <h2 className="mt-3 font-serif text-4xl tracking-[-0.025em] sm:text-5xl">From context to a grounded verdict.</h2>
              </div>
              <Button to="/architecture" variant="ghost" className="w-max text-sm">
                Explore the full architecture <ArrowRight className="ml-1.5 h-4 w-4" aria-hidden="true" />
              </Button>
            </div>

            <Link
              to="/architecture"
              className="mt-10 block overflow-x-auto border-y border-site-border py-6 focus:outline-none focus:ring-1 focus:ring-site-accent"
              aria-label="Explore the full six-stage Helios architecture"
            >
              <ol className="flex min-w-[700px] items-center justify-between gap-0">
                {pipelineStages.map((stage, index) => (
                  <React.Fragment key={stage}>
                    <li className="flex w-24 flex-col gap-2">
                      <span className="font-mono text-[10px] tracking-[0.12em] text-site-accent">0{index + 1}</span>
                      <span className="text-sm font-medium text-site-text-primary">{stage}</span>
                    </li>
                    {index < pipelineStages.length - 1 && <span className="mx-3 h-px flex-1 bg-site-accent" aria-hidden="true" />}
                  </React.Fragment>
                ))}
              </ol>
              <span className="sr-only">
                The pipeline proceeds from ingestion through stack mapping, scenario generation,
                outcome prediction, dependency diagnosis, and a comparative verdict.
              </span>
            </Link>
          </div>
        </section>

        <section className="border-t border-site-border px-6 py-20 sm:py-28">
          <div className="mx-auto max-w-6xl">
            <div className="max-w-2xl">
              <p className="font-mono text-[11px] uppercase tracking-[0.16em] text-site-accent">What makes Helios different</p>
              <h2 className="mt-3 font-serif text-4xl tracking-[-0.025em] sm:text-5xl">
                A decision aid built for the consequences of a choice.
              </h2>
            </div>
            <div className="mt-10 grid gap-4 md:grid-cols-3">
              {pillars.map(({ icon: Icon, title, description }) => (
                <article key={title} className="border-hairline border-site-border p-6 transition-transform duration-300 hover:-translate-y-1">
                  <Icon className="h-5 w-5 text-site-accent" strokeWidth={1.5} aria-hidden="true" />
                  <h3 className="mt-8 text-base font-semibold">{title}</h3>
                  <p className="mt-3 text-sm leading-6 text-site-text-secondary">{description}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="relative overflow-hidden border-y border-site-border bg-site-surface px-6 py-20 text-center sm:py-24">
          <div className="mx-auto max-w-2xl">
            <ScanSearch className="mx-auto h-5 w-5 text-site-accent" strokeWidth={1.5} aria-hidden="true" />
            <h2 className="mt-5 font-serif text-4xl tracking-[-0.025em] sm:text-5xl">See the decision behind the decision.</h2>
            <p className="mx-auto mt-5 max-w-xl text-base leading-7 text-site-text-secondary">
              Open the Helios Terminal to examine sourcing paths, verify claims, and surface the
              dependencies that should shape your next move.
            </p>
            <div className="mt-8">
              <Button to="/dashboard" variant="primary" size="lg">
                Enter dashboard <ArrowRight className="ml-2 h-4 w-4" aria-hidden="true" />
              </Button>
            </div>
          </div>
          <div
            className="absolute bottom-0 left-0 h-1 w-full"
            style={{ background: 'linear-gradient(90deg, transparent, var(--site-text-primary), transparent)' }}
            aria-hidden="true"
          />
        </section>
      </main>

      <SiteFooter />
    </div>
  );
};
