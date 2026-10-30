const BLOCKS = [
  {
    title: "Plants in places you already love",
    // TODO(copy)
    body: "One line here, from the coffee shops, wine bars, and restaurants you already visit.",
  },
  {
    title: "Buy what you see",
    body: "One line here, about buying the exact plant on display.",
  },
  {
    title: "We handle the care",
    body: "One line here, about ongoing maintenance being our job, not the venue's.",
  },
] as const;

export default function WhatWeDo() {
  return (
    <section className="mx-auto max-w-6xl px-4 py-7 sm:px-6">
      <h2 className="mb-3 text-xs font-semibold uppercase tracking-wide text-forest/60">
        What we do
      </h2>
      <div className="grid gap-4 sm:grid-cols-3">
        {BLOCKS.map((block) => (
          <div key={block.title} className="rounded-lg border border-forest/10 bg-white p-4">
            <h3 className="text-forest">{block.title}</h3>
            <p className="mt-2 text-sm text-forest/70">{block.body}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
