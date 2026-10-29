import Link from "next/link";
import type { CityDetail } from "@/lib/types";

// Up to 4 venue cards (spec §3.1.4, layout 1a). City.venues already comes
// ordered display_order, then name from the API.
export default function VenueCards({ city }: { city: CityDetail }) {
  const shown = city.venues.slice(0, 4);
  const hasMore = city.venues.length > 4;

  if (shown.length === 0) {
    return null; // nothing to show yet — not an error, just no public venues
  }

  return (
    <section className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {shown.map((venue) => (
          <Link
            key={venue.id}
            href={`/locations/${venue.city}/${venue.slug}`}
            className="group overflow-hidden rounded-lg border border-forest/10 bg-white"
          >
            <div
              aria-hidden="true"
              className="aspect-[4/3] bg-forest/10"
              style={
                venue.hero_image
                  ? { backgroundImage: `url(${venue.hero_image})`, backgroundSize: "cover" }
                  : undefined
              }
            />
            <div className="p-4">
              <p className="font-semibold text-forest">{venue.name}</p>
              <p className="text-sm text-forest/70">{venue.neighborhood}</p>
              <span className="mt-2 inline-block text-sm font-medium text-terracotta group-hover:underline">
                View →
              </span>
            </div>
          </Link>
        ))}
      </div>

      {hasMore && (
        <div className="mt-6 text-center">
          <Link
            href={`/locations/${city.slug}`}
            className="inline-block rounded border border-forest px-5 py-2.5 text-sm font-semibold text-forest hover:bg-forest/5"
          >
            See all {city.name} locations →
          </Link>
        </div>
      )}
    </section>
  );
}
