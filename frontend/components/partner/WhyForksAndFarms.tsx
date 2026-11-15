import SitePhoto from "@/components/SitePhoto";
import type { SiteImage } from "@/lib/siteSettings";

// "Why Forks And Farms" mission/story block (spec §3.4.2). The photo
// comes from the admin's Site settings; until one is uploaded it's a
// placeholder box.
export default function WhyForksAndFarms({ image = null }: { image?: SiteImage | null }) {
  return (
    <section className="mx-auto grid max-w-6xl gap-6 px-4 py-7 sm:px-6 lg:grid-cols-2 lg:items-center">
      <SitePhoto
        image={image}
        placeholderLabel="Forks And Farms at work (placeholder)"
        placeholderText="Photo coming soon"
        className="order-last lg:order-first"
      />

      <div>
        <h2 className="text-forest">Why Forks And Farms</h2>
        {/* TODO(copy): 2-3 sentence mission/story */}
        <p className="mt-2 text-forest">
          We started Forks And Farms because the places we love in St. Louis deserved more
          life in them. We handpick, deliver, and maintain plants in local coffee shops, wine
          bars, and restaurants — so owners get the look without the upkeep, and customers get
          a reason to stay a little longer.
        </p>
      </div>
    </section>
  );
}
