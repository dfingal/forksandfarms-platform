import Link from "next/link";

// Hero section (spec §3.1.1). Hero photo is a styled placeholder box
// until real photography exists (spec §14 open item).
export default function Hero() {
  return (
    <section className="mx-auto grid max-w-6xl gap-8 px-4 py-10 sm:px-6 sm:py-16 lg:grid-cols-2 lg:items-center">
      <div>
        <h1 className="text-forest">Plants in the places you already go.</h1>
        {/* TODO(copy): real one-line explanation */}
        <p className="mt-4 max-w-md text-forest/80">
          We place curated plants in St. Louis coffee shops, wine bars, restaurants, and
          breweries. Buy what you see — we handle the care.
        </p>

        <div className="mt-6 flex flex-wrap gap-3">
          <a
            href="#map"
            className="rounded bg-forest px-5 py-2.5 text-sm font-semibold text-cream hover:bg-forest/90"
          >
            Find Plants Near You
          </a>
          <Link
            href="/partner"
            className="rounded border border-forest px-5 py-2.5 text-sm font-semibold text-forest hover:bg-forest/5"
          >
            Partner With Us
          </Link>
        </div>
      </div>

      {/* Hero photo placeholder — TODO(assets): real hero photography */}
      <div
        role="img"
        aria-label="Plants on display at a Forks And Farms partner venue (placeholder)"
        className="flex aspect-[4/3] items-center justify-center rounded-lg border border-forest/10 bg-forest/5 text-sm text-forest/50"
      >
        Hero photo coming soon
      </div>
    </section>
  );
}
