import React from 'react';
import { 
  Database, 
  Layers3, 
  Route, 
  ChartNoAxesCombined, 
  Link2, 
  Scale, 
  CircleCheck, 
  ArrowRight
} from 'lucide-react';
import { useScrollReveal } from '../../shared/useScrollReveal';
import { SiteHeader } from '../../shared/SiteHeader';
import { SiteFooter } from '../../shared/SiteFooter';
import { Button } from '../../shared/Button';
import { Mermaid } from '../../shared/Mermaid';

const pipelineChart = `
graph LR
    A["01<br/>Ingestion"] --> B["02<br/>Stack mapping"]
    B --> C["03<br/>Scenario generation"]
    C --> D["04<br/>Outcome prediction"]
    D --> E["05<br/>Dependency diagnosis"]
    E --> F["06<br/>Comparative verdict"]

    B -.-> A
    C -.-> B
    D -.-> C
    E -.-> D
    F -.-> E
`;

const recalibrationChart = `
graph LR
    A["Step 01<br/>Sufficiency check"] --> B["Step 02<br/>Gap payload"]
    B --> C["Step 03<br/>Bounded retry"]
`;

const stages = [
  {
    number: '01',
    title: 'Ingestion',
    icon: Database,
    description: 'Gathers only the context relevant to this decision.',
  },
  {
    number: '02',
    title: 'Stack mapping',
    icon: Layers3,
    description: 'Narrows the AI stack layers the choice touches.',
  },
  {
    number: '03',
    title: 'Scenario generation',
    icon: Route,
    description: 'Sets out realistic sourcing paths to compare.',
  },
  {
    number: '04',
    title: 'Outcome prediction',
    icon: ChartNoAxesCombined,
    description: 'Projects the plausible trajectory of each path.',
  },
  {
    number: '05',
    title: 'Dependency diagnosis',
    icon: Link2,
    description: 'Names the lock-in and exposure each outcome creates.',
  },
  {
    number: '06',
    title: 'Comparative verdict',
    icon: Scale,
    description: 'Synthesises diagnoses into an auditable recommendation.',
  }
];

const recalibrationSteps = [
  {
    number: '01',
    title: 'Sufficiency check',
    description: 'A stage asks whether it has enough grounded input to continue.',
  },
  {
    number: '02',
    title: 'Gap payload',
    description: 'It names the specific missing context and the upstream owner.',
  },
  {
    number: '03',
    title: 'Bounded retry',
    description: 'Context accumulates on a targeted re-run, capped at two retries.',
  }
];

export const Architecture: React.FC = () => {
  const containerRef = useScrollReveal<HTMLDivElement>();

  return (
    <div className="min-h-screen bg-site-bg text-site-text-primary flex flex-col font-sans selection:bg-site-accent/20">
      <SiteHeader />

      <main ref={containerRef} className="flex-1 flex flex-col w-full max-w-7xl mx-auto px-6 py-12 gap-20">
        {/* Intro */}
        <section className="max-w-[700px] mx-auto text-center flex flex-col items-center gap-6 mt-6">
          <span 
            className="hero-reveal inline-block px-3 py-1 rounded-site border border-site-border bg-site-surface text-site-text-secondary text-sm font-mono tracking-wider uppercase"
            style={{ '--reveal-delay': '0ms' } as React.CSSProperties}
          >
            Architecture / conditional graph
          </span>
          <h1 
            className="hero-reveal text-4xl md:text-5xl lg:text-6xl font-serif tracking-tight text-site-text-primary leading-tight"
            style={{ '--reveal-delay': '100ms' } as React.CSSProperties}
          >
            How Helios thinks through a sourcing decision.
          </h1>
          <p 
            className="hero-reveal text-lg md:text-xl text-site-text-secondary leading-relaxed"
            style={{ '--reveal-delay': '200ms' } as React.CSSProperties}
          >
            Six specialised agents turn a decision brief into a comparative verdict. Each handoff is verified, and insufficient context loops back to the stage best placed to fill the gap.
          </p>
        </section>

        {/* Pipeline flow diagram */}
        <section className="flex flex-col gap-12" aria-label="Pipeline Flow Diagram">
          <div className="sr-only">
            Six stages: 1. Ingestion, 2. Stack mapping, 3. Scenario generation, 4. Outcome prediction, 5. Dependency diagnosis, 6. Comparative verdict. Verified handoffs connect stages forward. Dashed lines indicate backward recalibration loops.
          </div>

          <div className="scroll-reveal w-full overflow-hidden bg-site-surface border border-site-border rounded-site py-8 px-4 flex justify-center">
            <Mermaid chart={pipelineChart} />
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-6 xl:gap-8 relative">
            {stages.map((stage) => (
              <div key={stage.number} className="scroll-reveal relative flex flex-col h-full bg-site-surface border border-site-border rounded-site p-6 hover:-translate-y-1 transition-transform duration-300 group z-10">
                <div className="flex items-start justify-between mb-8">
                  <span className="font-mono text-sm tracking-wider text-site-accent">{stage.number}</span>
                  <stage.icon className="w-5 h-5 text-site-accent" strokeWidth={1.5} />
                </div>
                <h3 className="text-lg font-semibold text-site-text-primary mb-3 leading-tight">{stage.title}</h3>
                <p className="text-sm text-site-text-secondary leading-relaxed flex-1">{stage.description}</p>
              </div>
            ))}
          </div>

          <div className="scroll-reveal flex items-center justify-center gap-4 mt-4 px-6 text-sm text-site-text-secondary font-sans border-t border-dashed border-site-border pt-6 max-w-fit mx-auto">
            <span className="inline-block border border-dashed border-site-text-secondary w-8" /> 
            Dashed lines represent backward recalibration loops where insufficient context returns to an earlier stage.
          </div>
        </section>

        {/* Recalibration explainer */}
        <section className="flex flex-col gap-12 items-center mx-auto max-w-5xl w-full border-t border-hairline border-site-border pt-16">
          <header className="text-center">
            <h2 className="scroll-reveal text-3xl font-serif text-site-text-primary mb-4">The recalibration sequence</h2>
            <p className="scroll-reveal text-lg text-site-text-secondary max-w-2xl">When context is insufficient, the system follows a strict retry sequence to gather missing information before failing.</p>
          </header>

          <div className="scroll-reveal w-full overflow-hidden bg-site-surface border border-site-border rounded-site py-8 px-4 flex justify-center">
            <Mermaid chart={recalibrationChart} />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full relative">
            {recalibrationSteps.map((step) => (
              <div key={step.number} className="scroll-reveal flex flex-col gap-4 bg-site-bg border border-site-border p-6 rounded-site">
                <span className="font-mono text-xs tracking-wider text-site-accent uppercase bg-site-surface px-2 py-1 rounded w-max">Step {step.number}</span>
                <h3 className="text-xl font-semibold text-site-text-primary">{step.title}</h3>
                <p className="text-site-text-secondary text-sm leading-relaxed">{step.description}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Tech stack strip */}
        <section className="scroll-reveal w-full border-y border-site-border bg-site-surface py-6 px-6 sm:px-12 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="font-mono text-sm text-site-text-secondary uppercase tracking-wider">
            Built with
          </div>
          <div className="flex flex-wrap items-center justify-center gap-x-8 gap-y-4">
            {['React', 'FastAPI', 'LangGraph', 'DeepSeek V4 Flash'].map(tech => (
              <div key={tech} className="flex items-center gap-2 text-site-text-primary text-sm font-medium">
                <CircleCheck className="w-4 h-4 text-site-accent" strokeWidth={1.5} />
                {tech}
              </div>
            ))}
          </div>
        </section>

        {/* CTA */}
        <section className="flex flex-col items-center text-center max-w-[600px] mx-auto gap-6 pb-16">
          <span className="scroll-reveal inline-block px-3 py-1 rounded-site border border-site-border bg-site-surface text-site-text-secondary text-sm font-mono tracking-wider uppercase">
            The interface for the verdict
          </span>
          <h2 className="scroll-reveal text-3xl md:text-4xl font-serif tracking-tight text-site-text-primary">
            See it in action.
          </h2>
          <p className="scroll-reveal text-lg text-site-text-secondary mb-2 leading-relaxed">
            Move from the model of the system to the workspace where a decision becomes a comparative, sourced verdict.
          </p>
          <div className="scroll-reveal">
            <Button to="/dashboard" variant="primary">
              Enter dashboard <ArrowRight className="ml-2 h-4 w-4" aria-hidden="true" />
            </Button>
          </div>
        </section>
      </main>

      <SiteFooter />
    </div>
  );
};
