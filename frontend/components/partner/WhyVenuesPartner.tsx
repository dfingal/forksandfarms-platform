const BENEFITS = [
  {
    title: "Revenue from your décor",
    body: "Earn on every plant sold — décor that pays for itself.",
  },
  {
    title: "Zero plant care",
    body: "We handle watering, rotation, and replacements. Not your job.",
  },
  {
    title: "A space people want to stay in",
    body: "Customers come back to be around the plants, not just the menu.",
  },
] as const;

// "Why venues partner" — three benefits (spec §3.4.3).
export default function WhyVenuesPartner() {
  return (
    <section className="mx-auto max-w-6xl px-4 py-7 sm:px-6">
      <h2 className="mb-3 text-xs font-semibold uppercase tracking-wide text-forest/60">
        Why venues partner
      </h2>
      <div className="grid gap-4 sm:grid-cols-3">
        {BENEFITS.map((benefit) => (
          <div key={benefit.title} className="rounded-lg border border-forest/10 bg-white p-4">
            <h3 className="text-forest">{benefit.title}</h3>
            <p className="mt-2 text-sm text-forest/70">{benefit.body}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
