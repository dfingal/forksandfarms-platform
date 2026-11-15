import Link from "next/link";
import HeroHeadline from "./HeroHeadline";
import SitePhoto from "./SitePhoto";
import type { SiteImage } from "@/lib/siteSettings";

// Hero section (spec §3.1.1). The photo comes from the admin's Site
// settings; until one is uploaded it's a styled placeholder box.
export default function Hero({ image = null }: { image?: SiteImage | null }) {
  return (
    <section className="mx-auto grid max-w-6xl gap-6 px-4 py-7 sm:px-6 sm:py-11 lg:grid-cols-2 lg:items-center">
      <div>
        <HeroHeadline />
        {/* mt-[17px]: 5px more than the standard mt-3 (12px) below the headline. */}
        <p className="mt-[17px] max-w-md text-lg text-forest">
          Then you&rsquo;re in the right place. We curate plants in St. Louis&rsquo; best
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

      {/* Preloaded: it's the first big image on the home page. */}
      <SitePhoto
        image={image}
        placeholderLabel="Plants on display at a Forks And Farms partner venue (placeholder)"
        placeholderText="Hero photo coming soon"
        preload
      />
    </section>
  );
}
