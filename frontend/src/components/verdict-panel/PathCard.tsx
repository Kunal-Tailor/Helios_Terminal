import type { PathComparison } from '../../lib/api'
import { severityLabel } from '../../lib/severity'

interface PathCardProps {
  path: PathComparison
}

function PathCard({ path }: PathCardProps) {
  return (
    <article>
      <h3>{path.scenario_name}</h3>
      <section>
        <h4>Outcome</h4>
        <p>{path.path_summary || 'No outcome summary available.'}</p>
      </section>
      <section>
        <h4>Dependency</h4>
        {path.lock_in_count === 0 ? (
          <p>No meaningful dependency identified for this path.</p>
        ) : (
          <p>
            {path.lock_in_count} lock-in{' '}
            {path.lock_in_count === 1 ? 'dependency' : 'dependencies'} identified.
          </p>
        )}
      </section>
      <section>
        <h4>Severity</h4>
        <p>
          {severityLabel(path.max_severity_score)} ({path.max_severity_score.toFixed(1)} / 10)
        </p>
      </section>
      {path.key_tradeoffs.length > 0 && (
        <section>
          <h4>Key trade-offs</h4>
          <ul>
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
