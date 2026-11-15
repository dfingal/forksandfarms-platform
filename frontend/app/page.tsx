import { getCity, getSiteImages } from "@/lib/api";
import Hero from "@/components/Hero";
import WhatWeDo from "@/components/WhatWeDo";
import MapSection from "@/components/MapSection";
import VenueCards from "@/components/VenueCards";
import PartnerTeaser from "@/components/PartnerTeaser";

// Phase I has one city; hardcoding the slug matches spec §3 ("/locations
// redirects to /locations/st-louis" until a second city exists).
const CITY_SLUG = "st-louis";

export default async function Home() {
  // Fetched in parallel; site images fall back to placeholders on failure.
  const [city, siteImages] = await Promise.all([getCity(CITY_SLUG), getSiteImages()]);

  return (
    <div>
      <Hero image={siteImages.homeHero} />
      <WhatWeDo />

      {city === null ? (
        <section id="map" className="scroll-mt-24 mx-auto max-w-6xl px-4 py-7 sm:px-6">
          <h2 className="mb-3 text-forest">Find plants near you</h2>
          <p className="rounded border border-terracotta/30 bg-terracotta/5 px-4 py-3 text-sm text-terracotta">
            We couldn&rsquo;t reach our location data right now. Please check back soon.
          </p>
        </section>
      ) : (
        <>
          <MapSection city={city} />
          <VenueCards city={city} />
        </>
      )}

      <PartnerTeaser />
    </div>
  );
}
