import type { PathComparison } from '../../lib/api'
import { severityLabel } from '../../lib/severity'

const SEVERITY_TEXT_CLASS: Record<string, string> = {
  Critical: 'text-risk-critical',
  Elevated: 'text-risk-elevated',
  Low: 'text-risk-low',
}

interface PathCardProps {
  path: PathComparison
}

function PathCard({ path }: PathCardProps) {
  const severity = severityLabel(path.max_severity_score)

  return (
    <article className="space-y-4 rounded-sm border border-hairline bg-surface p-8 leading-[1.6]">
      <h3 className="font-mono text-section-header leading-[1.3] text-primary">
        {path.scenario_name}
      </h3>
      <div className="relative space-y-4 pl-4">
        <span
          aria-hidden="true"
          className="absolute bottom-2 left-[3px] top-2 w-px bg-accent"
        />
        <section className="relative">
          <span
            aria-hidden="true"
            className="absolute -left-4 top-[5px] h-[7px] w-[7px] rounded-full border border-accent bg-surface"
          />
          <h4 className="font-mono text-metadata leading-[1.3] text-secondary">Outcome</h4>
          <p className="font-serif text-prose text-primary">
            {path.path_summary || 'No outcome summary available.'}
          </p>
        </section>
        <section className="relative">
          <span
            aria-hidden="true"
            className="absolute -left-4 top-[5px] h-[7px] w-[7px] rounded-full border border-accent bg-surface"
          />
          <h4 className="font-mono text-metadata leading-[1.3] text-secondary">Dependency</h4>
          {path.lock_in_count === 0 ? (
            <p className="font-serif text-prose text-secondary">
              No meaningful dependency identified for this path.
            </p>
          ) : (
            <p className="font-serif text-prose text-primary">
              {path.lock_in_count} lock-in{' '}
              {path.lock_in_count === 1 ? 'dependency' : 'dependencies'} identified.
            </p>
          )}
        </section>
        <section className="relative">
          <span
            aria-hidden="true"
            className="absolute -left-4 top-[5px] h-[7px] w-[7px] rounded-full border border-accent bg-surface"
          />
          <h4 className="font-mono text-metadata leading-[1.3] text-secondary">Severity</h4>
          <p className="font-serif text-prose">
            <span className={`${SEVERITY_TEXT_CLASS[severity]} text-body-ui`}>{severity}</span>{' '}
            <span className="font-mono text-metadata leading-[1.3] text-secondary">
              ({path.max_severity_score.toFixed(1)} / 10)
            </span>
          </p>
        </section>
      </div>
      {path.key_tradeoffs.length > 0 && (
        <section className="space-y-1">
          <h4 className="font-mono text-metadata leading-[1.3] text-secondary">
            Key trade-offs
          </h4>
          <ul className="list-disc space-y-1 pl-5 font-serif text-prose text-primary">
            {path.key_tradeoffs.map((tradeoff) => (
              <li key={tradeoff}>{tradeoff}</li>
            ))}
          </ul>
        </section>
      )}
    </article>
  )
}

export default PathCard
