interface VerdictBannerProps {
  entity: string
  capability: string
  optionsNote: string
  summary?: string | null
  recommendedPath?: string | null
  loading?: boolean
}

function VerdictBanner({
  entity,
  capability,
  optionsNote,
  summary,
  recommendedPath,
  loading = false,
}: VerdictBannerProps) {
  if (loading) {
    return (
      <section aria-busy="true">
        <p>Loading verdict…</p>
      </section>
    )
  }

  if (!summary) {
    return (
      <section>
        <p>Verdict unavailable.</p>
      </section>
    )
  }

  return (
    <section>
      <p>
        {entity} — {capability} — {optionsNote}
      </p>
      <h2>{summary}</h2>
      {recommendedPath && <p>Recommended path: {recommendedPath}</p>}
    </section>
  )
}

export default VerdictBanner
