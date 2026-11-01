const OPTIONS = [
  {
    title: "Retail Shelf",
    // TODO(copy)
    body: "We stock a plant shelf; you earn a share of sales.",
    bestFor: "TODO(copy): best for...", // e.g. "Best for: low-commitment, high-traffic counters"
    tag: null,
  },
  {
    title: "Design & Install",
    body: "We design and install plants your venue purchases.",
    bestFor: "TODO(copy): best for...",
    tag: null,
  },
  {
    title: "Lease + Maintenance",
    body: "We lease plants with ongoing care included.",
    bestFor: "TODO(copy): best for...",
    tag: "Starts at 20 plants",
  },
] as const;

// "Partnership options" (spec §3.4.5). No pricing or revenue-share
// percentages shown here on purpose — that's a walkthrough conversation,
// not page copy.
export default function PartnershipOptions() {
  return (
    <section className="mx-auto max-w-6xl px-4 py-7 sm:px-6">
      <h2 className="text-forest">Partnership options</h2>
      <div className="mt-4 grid gap-4 sm:grid-cols-3">
        {OPTIONS.map((option) => (
          <div key={option.title} className="rounded-lg border border-forest/10 bg-white p-4">
            <div className="flex items-start justify-between gap-2">
              <h3 className="text-forest">{option.title}</h3>
              {option.tag && (
                <span className="shrink-0 rounded bg-terracotta/10 px-2 py-0.5 text-xs font-medium text-terracotta">
                  {option.tag}
                </span>
              )}
            </div>
            <p className="mt-1 text-sm text-forest/70">{option.body}</p>
            <p className="mt-2 text-xs text-forest/60">{option.bestFor}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
