import Link from "next/link";
import HeroHeadline from "./HeroHeadline";

// Hero section (spec §3.1.1). Hero photo is a styled placeholder box
// until real photography exists (spec §14 open item).
export default function Hero() {
  return (
    <section className="mx-auto grid max-w-6xl gap-6 px-4 py-7 sm:px-6 sm:py-11 lg:grid-cols-2 lg:items-center">
      <div>
        <HeroHeadline />
        <p className="mt-3 max-w-md text-forest">
          Then you&rsquo;re in the right place. We curate plants in St. Louis&rsquo;s best
          coffee shops, wine bars, restaurants and more. Enjoy what you see. Buy what you see.
        </p>

        <div className="mt-4 flex flex-wrap gap-3">
          <a
            href="#map"
            className="rounded bg-forest px-5 py-2.5 text-sm font-semibold text-cream hover:bg-forest/90"
          >
            Find Plants Near You
          </a>
          <Link
            href="/partner"
            className="rounded border border-forest px-5 py-2.5 text-sm font-semibold text-forest hover:bg-cream"
          >
            Partner With Us
          </Link>
        </div>
      </div>

      {/* Hero photo placeholder — TODO(assets): real hero photography */}
      <div
        role="img"
        aria-label="Plants on display at a Forks And Farms partner venue (placeholder)"
        className="flex aspect-[4/3] items-center justify-center rounded-lg border border-forest/20 bg-cream text-sm text-muted"
      >
        Hero photo coming soon
      </div>
    </section>
  );
}
