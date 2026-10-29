import Link from "next/link";

const OPTIONS = [
  {
    title: "Retail Shelf",
    // TODO(copy)
    body: "We stock a plant shelf; you earn a share of sales.",
  },
  {
    title: "Design & Install",
    body: "We design and install plants your venue purchases.",
  },
  {
    title: "Lease + Maintenance",
    body: "We lease plants with ongoing care included. Starts at 20 plants.",
  },
] as const;

export default function PartnerTeaser() {
  return (
    <section className="bg-forest/5">
      <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h2 className="text-forest">Put plants to work in your space.</h2>
            {/* TODO(copy) */}
            <p className="mt-2 max-w-md text-sm text-forest/70">
              Three plans, all the perks: revenue from décor, no plant-care burden, and
              customers who love being around plants.
            </p>
          </div>
          <Link
            href="/partner"
            className="inline-block self-start rounded bg-forest px-5 py-2.5 text-sm font-semibold text-cream hover:bg-forest/90"
          >
            Partner With Us →
          </Link>
        </div>

        <div className="mt-6 grid gap-4 sm:grid-cols-3">
          {OPTIONS.map((option) => (
            <div key={option.title} className="rounded-lg border border-forest/10 bg-white p-4">
              <h3 className="text-forest">{option.title}</h3>
              <p className="mt-1 text-sm text-forest/70">{option.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
