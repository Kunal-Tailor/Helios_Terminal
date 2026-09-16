import React from 'react';
import { ArrowUpRight, Layers3 } from 'lucide-react';
import { SiteHeader } from '../../shared/SiteHeader';
import { SiteFooter } from '../../shared/SiteFooter';

const team = [
  { initials: 'RS', name: 'Rishav Singh', role: 'System architecture & full-stack engineering' },
  { initials: 'KT', name: 'Kunal Tailor', role: 'AI pipeline & agent design' },
  { initials: 'P', name: 'Prakash', role: 'Research, verification & evaluation' },
  { initials: 'NG', name: 'Neeraj Gupta', role: 'Product strategy & decision analysis' },
];

const GithubIcon: React.FC<{ className?: string }> = ({ className = 'h-4 w-4' }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
    <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
  </svg>
);

export const Team: React.FC = () => {
  return (
    <div className="theme-site min-h-screen bg-site-bg text-site-text-primary">
      <SiteHeader />
      <main>
        <section className="px-6 pb-16 pt-20 text-center sm:pb-20 sm:pt-28">
          <div className="mx-auto max-w-2xl">
            <p className="font-mono text-[11px] uppercase tracking-[0.16em] text-site-accent">CSE-AIDS capstone / panel B</p>
            <h1 className="mt-5 font-serif text-5xl font-semibold tracking-[-0.04em] sm:text-6xl">The team.</h1>
            <p className="mx-auto mt-5 max-w-xl text-base leading-7 text-site-text-secondary sm:text-lg">
              A multidisciplinary project team building a more defensible way to reason about AI sourcing decisions.
            </p>
          </div>
        </section>

        <section className="px-6 pb-20 sm:pb-28" aria-labelledby="team-heading">
          <h2 id="team-heading" className="sr-only">Helios Terminal project team</h2>
          <div className="mx-auto grid max-w-6xl gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {team.map(({ initials, name, role }) => (
              <article key={name} className="flex min-h-72 flex-col border-hairline border-site-border p-6 transition-transform duration-300 hover:-translate-y-1">
                <div className="flex h-12 w-12 items-center justify-center rounded-full border border-site-border bg-site-surface font-mono text-xs font-medium tracking-[0.1em] text-site-text-primary">
                  {initials}
                </div>
                <h3 className="mt-9 text-lg font-semibold">{name}</h3>
                <p className="mt-2 text-sm leading-6 text-site-text-secondary">{role}</p>
                <div className="mt-auto flex items-center gap-3 pt-8">
                  <a
                    href="https://github.com/Rishav408/helios-terminal"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 text-xs text-site-text-secondary transition-colors hover:text-site-text-primary focus:outline-none focus:ring-1 focus:ring-site-accent"
                    aria-label={`${name}: view the Helios Terminal project on GitHub`}
                  >
                    <GithubIcon className="h-4 w-4 text-site-accent" />
                    Project GitHub
                    <ArrowUpRight className="h-3 w-3" aria-hidden="true" />
                  </a>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="border-y border-site-border bg-site-surface px-6 py-12 sm:py-16">
          <div className="mx-auto flex max-w-4xl flex-col gap-5 sm:flex-row sm:items-start">
            <Layers3 className="mt-1 h-5 w-5 shrink-0 text-site-accent" strokeWidth={1.5} aria-hidden="true" />
            <div>
              <p className="font-mono text-[10px] uppercase tracking-[0.15em] text-site-text-secondary">One shared system</p>
              <p className="mt-3 max-w-3xl text-base leading-7 text-site-text-secondary">
                The team’s work converges in Helios’ six-stage pipeline: decision context becomes stack scope,
                realistic scenarios, projected outcomes, dependency diagnoses, and a comparative verdict—each
                step supported by verification and targeted recalibration.
              </p>
              <a
                href="/architecture"
                className="mt-4 inline-flex items-center gap-1.5 text-sm text-site-text-primary underline decoration-site-accent underline-offset-4 transition-colors hover:text-site-accent focus:outline-none focus:ring-1 focus:ring-site-accent"
              >
                Explore the architecture <ArrowUpRight className="h-3.5 w-3.5" aria-hidden="true" />
              </a>
            </div>
          </div>
        </section>
      </main>
      <SiteFooter />
    </div>
  );
};
