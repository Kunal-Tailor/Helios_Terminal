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
      <section
        aria-busy="true"
        className="rounded-sm border border-hairline bg-surface p-8 font-mono text-body-mono leading-[1.3] text-secondary"
      >
        <p>Loading verdict…</p>
      </section>
    )
  }

  if (!summary) {
    return (
      <section className="rounded-sm border border-hairline bg-surface p-8 font-mono text-body-mono leading-[1.3] text-secondary">
        <p>Verdict unavailable.</p>
      </section>
    )
  }

  return (
    <section className="space-y-4 rounded-sm border border-hairline bg-surface p-8 leading-[1.6]">
      <p className="font-mono text-metadata leading-[1.3] text-secondary">
        {entity} — {capability} — {optionsNote}
      </p>
      <h2 className="font-serif text-verdict-headline text-primary">{summary}</h2>
      {recommendedPath && (
        <p>
          <span className="font-mono text-metadata leading-[1.3] text-secondary">
            Recommended path:
          </span>{' '}
          <span className="font-serif text-prose text-primary">{recommendedPath}</span>
        </p>
      )}
    </section>
  )
}

export default VerdictBanner
