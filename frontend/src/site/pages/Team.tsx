import { Link } from 'react-router-dom';
import { Layers3, ArrowUpRight } from 'lucide-react';
import { SiteHeader } from '../../shared/SiteHeader';
import { SiteFooter } from '../../shared/SiteFooter';
import { useScrollReveal } from '../../shared/useScrollReveal';

const GithubIcon = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.02c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A4.8 4.8 0 0 0 8 18v4" />
  </svg>
);

const teamMembers = [
  {
    id: 'RS',
    name: 'Rishav Singh',
    initials: 'RS',
    role: 'System architecture & full-stack engineering',
    colorClass: 'bg-[#b45309] text-white',
  },
  {
    id: 'KT',
    name: 'Kunal Tailor',
    initials: 'KT',
    role: 'AI pipeline & agent design',
    colorClass: 'bg-[#4d7c0f] text-white',
  },
  {
    id: 'P',
    name: 'Prakash',
    initials: 'P',
    role: 'Research, verification & evaluation',
    colorClass: 'bg-[#be123c] text-white',
  },
  {
    id: 'NG',
    name: 'Neeraj Gupta',
    initials: 'NG',
    role: 'Product strategy & decision analysis',
    colorClass: 'bg-[#334155] text-white',
  }
];

export const Team: React.FC = () => {
  const containerRef = useScrollReveal<HTMLDivElement>();

  return (
    <div className="min-h-screen flex flex-col bg-site-bg text-site-text-primary selection:bg-site-accent selection:text-white">
      <SiteHeader />

      <main ref={containerRef} className="flex-1 w-full max-w-7xl mx-auto px-6 py-24 sm:py-32 flex flex-col gap-24">
        {/* Intro */}
        <section className="flex flex-col items-center text-center gap-6 max-w-3xl mx-auto">
          <div 
            className="hero-reveal text-xs font-mono uppercase tracking-wider text-site-text-secondary"
            style={{ '--reveal-delay': '100ms' } as React.CSSProperties}
          >
            CSE-AIDS capstone / panel B
          </div>
          <h1 
            className="hero-reveal text-5xl md:text-7xl font-serif tracking-tight text-site-text-primary"
            style={{ '--reveal-delay': '200ms' } as React.CSSProperties}
          >
            The team.
          </h1>
          <p 
            className="hero-reveal text-xl md:text-2xl font-sans text-site-text-secondary leading-relaxed"
            style={{ '--reveal-delay': '300ms' } as React.CSSProperties}
          >
            A multidisciplinary project team building a more defensible way to reason about AI sourcing decisions.
          </p>
        </section>

        {/* Team grid */}
        <section className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-6">
          {teamMembers.map((member, i) => (
            <div 
              key={member.id}
              className="scroll-reveal flex flex-col p-6 rounded-site border border-hairline border-site-border bg-site-surface hover:-translate-y-1 transition-transform duration-300"
              style={{ '--reveal-delay': `${100 + i * 100}ms` } as React.CSSProperties}
            >
              <div className={`w-16 h-16 rounded-full flex items-center justify-center text-xl font-medium mb-6 ${member.colorClass}`}>
                {member.initials}
              </div>
              <h3 className="text-xl font-semibold font-sans mb-2">
                {member.name}
              </h3>
              <p className="text-sm font-sans text-site-text-secondary flex-1 mb-8">
                {member.role}
              </p>
              
              <a 
                href="https://github.com/Rishav408/helios-terminal" 
                target="_blank" 
                rel="noreferrer"
                className="group flex items-center gap-2 text-sm font-medium text-site-text-primary hover:text-site-accent transition-colors mt-auto"
              >
                <GithubIcon className="w-4 h-4" />
                <span>Project GitHub</span>
                <ArrowUpRight className="w-4 h-4 text-site-text-secondary group-hover:text-site-accent transition-colors ml-auto" />
              </a>
            </div>
          ))}
        </section>

        {/* Contribution note */}
        <section 
          className="scroll-reveal max-w-4xl mx-auto w-full p-8 md:p-12 rounded-site border border-hairline border-site-border bg-site-surface flex flex-col gap-6"
        >
          <div className="flex items-center gap-4 text-site-accent">
            <Layers3 className="w-6 h-6" />
            <span className="text-sm font-mono uppercase tracking-wider">One shared system</span>
          </div>
          <p className="text-lg md:text-xl font-sans text-site-text-primary leading-relaxed">
            The team's work converges in Helios' six-stage pipeline: decision context becomes stack scope, realistic scenarios, projected outcomes, dependency diagnoses, and a comparative verdict—each step supported by verification and targeted recalibration.
          </p>
          <Link 
            to="/architecture" 
            className="group inline-flex items-center gap-2 text-site-accent font-medium hover:opacity-80 transition-opacity w-fit mt-4"
          >
            <span>Explore the architecture</span>
            <ArrowUpRight className="w-4 h-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
          </Link>
        </section>
      </main>

      <SiteFooter />
    </div>
  );
};
