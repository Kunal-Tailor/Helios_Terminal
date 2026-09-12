import React from 'react';
import {
  ArrowRight,
  ChartNoAxesCombined,
  CircleCheck,
  Database,
  Layers3,
  Link2,
  Route,
  Scale,
} from 'lucide-react';
import { SiteHeader } from '../../shared/SiteHeader';
import { SiteFooter } from '../../shared/SiteFooter';
import { Button } from '../../shared/Button';

const stages = [
  { number: '01', title: 'Ingestion', description: 'Gathers only the context relevant to this decision.', icon: Database },
  { number: '02', title: 'Stack mapping', description: 'Narrows the AI stack layers the choice touches.', icon: Layers3 },
  { number: '03', title: 'Scenario generation', description: 'Sets out realistic sourcing paths to compare.', icon: Route },
  { number: '04', title: 'Outcome prediction', description: 'Projects the plausible trajectory of each path.', icon: ChartNoAxesCombined },
  { number: '05', title: 'Dependency diagnosis', description: 'Names the lock-in and exposure each outcome creates.', icon: Link2 },
  { number: '06', title: 'Comparative verdict', description: 'Synthesises diagnoses into an auditable recommendation.', icon: Scale },
];

const recalibrationSteps = [
  { number: '01', title: 'Sufficiency check', description: 'A stage asks whether it has enough grounded input to continue.' },
  { number: '02', title: 'Gap payload', description: 'It names the specific missing context and the upstream owner.' },
  { number: '03', title: 'Bounded retry', description: 'Context accumulates on a targeted re-run, capped at two retries.' },
];

export const Architecture: React.FC = () => {
  return (
    <div className="theme-site min-h-screen bg-site-bg text-site-text-primary">
      <SiteHeader />
      <main>
        <section className="px-6 pb-20 pt-20 text-center sm:pb-28 sm:pt-28">
          <div className="mx-auto max-w-3xl">
            <p className="font-mono text-[11px] uppercase tracking-[0.16em] text-site-accent">
              Architecture / conditional graph
            </p>
            <h1 className="mt-5 font-serif text-5xl font-semibold leading-[1.04] tracking-[-0.035em] sm:text-6xl">
              How Helios thinks through a sourcing decision.
            </h1>
            <p className="mx-auto mt-6 max-w-2xl text-base leading-7 text-site-text-secondary sm:text-lg">
              Six specialised agents turn a decision brief into a comparative verdict. Each handoff is
              verified, and insufficient context loops back to the stage best placed to fill the gap.
            </p>
          </div>
        </section>

        <section className="border-y border-site-border px-6 py-20 sm:py-24" aria-labelledby="pipeline-heading">
          <div className="mx-auto max-w-7xl">
            <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
              <div>
                <p className="font-mono text-[11px] uppercase tracking-[0.16em] text-site-accent">The pipeline</p>
                <h2 id="pipeline-heading" className="mt-3 font-serif text-4xl tracking-[-0.025em] sm:text-5xl">
                  Six stages, one accountable trail.
                </h2>
              </div>
              <p className="max-w-xs text-sm leading-6 text-site-text-secondary">
                Solid lines move verified work forward. Dashed lines carry a targeted recalibration request backward.
              </p>
            </div>

            <div className="relative mt-12">
              <svg
                className="pointer-events-none absolute inset-x-0 top-0 hidden h-[330px] w-full xl:block"
                viewBox="0 0 1200 330"
                preserveAspectRatio="none"
                aria-hidden="true"
              >
                <defs>
                  <marker id="forward-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
                    <path d="M0,0 L8,4 L0,8" fill="var(--site-accent)" />
                  </marker>
                  <marker id="backward-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
                    <path d="M0,0 L8,4 L0,8" fill="var(--site-accent)" />
                  </marker>
                </defs>
                <path d="M190 77 H202 M392 77 H404 M594 77 H606 M796 77 H808 M998 77 H1010" fill="none" stroke="var(--site-accent)" strokeWidth="1.5" markerEnd="url(#forward-arrow)" />
                <path d="M292 156 C292 215 108 215 108 156" fill="none" stroke="var(--site-accent)" strokeWidth="1.25" strokeDasharray="5 5" markerEnd="url(#backward-arrow)" />
                <path d="M494 156 C494 245 108 245 108 156" fill="none" stroke="var(--site-accent)" strokeWidth="1.25" strokeDasharray="5 5" markerEnd="url(#backward-arrow)" />
                <path d="M696 156 C696 275 494 275 494 156" fill="none" stroke="var(--site-accent)" strokeWidth="1.25" strokeDasharray="5 5" markerEnd="url(#backward-arrow)" />
                <path d="M898 156 C898 305 696 305 696 156" fill="none" stroke="var(--site-accent)" strokeWidth="1.25" strokeDasharray="5 5" markerEnd="url(#backward-arrow)" />
                <path d="M1092 156 C1092 325 898 325 898 156" fill="none" stroke="var(--site-accent)" strokeWidth="1.25" strokeDasharray="5 5" markerEnd="url(#backward-arrow)" />
              </svg>

              <ol className="relative z-10 grid gap-3 sm:grid-cols-2 xl:grid-cols-6">
                {stages.map(({ number, title, description, icon: Icon }, index) => (
                  <li key={title} className="bg-site-bg">
                    <article className="flex min-h-40 flex-col border-hairline border-site-border p-5 transition-transform duration-300 hover:-translate-y-1">
                      <div className="flex items-start justify-between gap-3">
                        <span className="font-mono text-[10px] tracking-[0.14em] text-site-accent">{number}</span>
                        <Icon className="h-4 w-4 text-site-accent" strokeWidth={1.5} aria-hidden="true" />
                      </div>
                      <h3 className="mt-7 text-sm font-semibold leading-5">{title}</h3>
                      <p className="mt-2 text-xs leading-5 text-site-text-secondary">{description}</p>
                      {index < stages.length - 1 && (
                        <span className="mt-auto pt-4 font-mono text-[9px] uppercase tracking-[0.12em] text-site-text-secondary xl:hidden">
                          verified handoff →
                        </span>
                      )}
                    </article>
                  </li>
                ))}
              </ol>
            </div>

            <div className="mt-8 border-l border-site-accent pl-4 text-sm leading-6 text-site-text-secondary xl:hidden">
              Dashed backward paths represent targeted recalibration: insufficient context returns to a specific
              earlier stage, is accumulated, and is retried no more than twice.
            </div>
            <p className="sr-only">
              The pipeline proceeds from Ingestion to Stack Mapping, Scenario Generation, Outcome Prediction,
              Dependency Diagnosis, and a Comparative Verdict. Stack Mapping can return to Ingestion;
              Scenario Generation can return to Stack Mapping or Ingestion; Outcome Prediction can return to
              Scenario Generation; Dependency Diagnosis can return to Outcome Prediction; and the final verdict
              can return to Dependency Diagnosis when a path is incomplete.
            </p>
          </div>
        </section>

        <section className="px-6 py-20 sm:py-28" aria-labelledby="recalibration-heading">
          <div className="mx-auto max-w-6xl">
            <div className="max-w-2xl">
              <p className="font-mono text-[11px] uppercase tracking-[0.16em] text-site-accent">The recovery path</p>
              <h2 id="recalibration-heading" className="mt-3 font-serif text-4xl tracking-[-0.025em] sm:text-5xl">
                Recalibration keeps thin inputs from becoming thin answers.
              </h2>
              <p className="mt-5 text-base leading-7 text-site-text-secondary">
                Verification asks whether a claim is grounded. Recalibration asks whether the stage received enough
                information to do useful work at all. They are different checks, and both are necessary.
              </p>
            </div>

            <ol className="mt-11 grid gap-5 md:grid-cols-3">
              {recalibrationSteps.map(({ number, title, description }, index) => (
                <li key={title} className="relative border-t border-site-border pt-5">
                  <span className="font-mono text-[10px] tracking-[0.14em] text-site-accent">{number}</span>
                  {index < recalibrationSteps.length - 1 && <ArrowRight className="absolute right-0 top-5 hidden h-4 w-4 text-site-accent md:block" strokeWidth={1.25} aria-hidden="true" />}
                  <h3 className="mt-5 text-base font-semibold">{title}</h3>
                  <p className="mt-2 max-w-xs text-sm leading-6 text-site-text-secondary">{description}</p>
                </li>
              ))}
            </ol>
          </div>
        </section>

        <section className="border-y border-site-border bg-site-surface px-6 py-8">
          <div className="mx-auto flex max-w-6xl flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
            <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-site-text-secondary">Built with</p>
            <ul className="flex flex-wrap gap-x-7 gap-y-3 font-mono text-xs tracking-[0.1em] text-site-text-primary">
              {['React', 'FastAPI', 'LangGraph', 'DeepSeek V4 Flash'].map((technology) => (
                <li key={technology} className="flex items-center gap-2">
                  <CircleCheck className="h-3.5 w-3.5 text-site-accent" strokeWidth={1.5} aria-hidden="true" />
                  {technology}
                </li>
              ))}
            </ul>
          </div>
        </section>

        <section className="px-6 py-20 text-center sm:py-28">
          <div className="mx-auto max-w-2xl">
            <p className="font-mono text-[11px] uppercase tracking-[0.16em] text-site-accent">The interface for the verdict</p>
            <h2 className="mt-4 font-serif text-4xl tracking-[-0.025em] sm:text-5xl">See it in action.</h2>
            <p className="mt-5 text-base leading-7 text-site-text-secondary">
              Move from the model of the system to the workspace where a decision becomes a comparative, sourced verdict.
            </p>
            <div className="mt-8">
              <Button to="/dashboard" variant="primary" size="lg">
                Enter dashboard <ArrowRight className="ml-2 h-4 w-4" aria-hidden="true" />
              </Button>
            </div>
          </div>
        </section>
      </main>
      <SiteFooter />
    </div>
  );
};
