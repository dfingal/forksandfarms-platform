import Link from "next/link";
import type { CityDetail } from "@/lib/types";
import VenueCard from "./VenueCard";

// Up to 4 venue cards (spec §3.1.4, layout 1a). City.venues already comes
// ordered display_order, then name from the API.
export default function VenueCards({ city }: { city: CityDetail }) {
  const shown = city.venues.slice(0, 4);
  const hasMore = city.venues.length > 4;

  if (shown.length === 0) {
    return null; // nothing to show yet — not an error, just no public venues
  }

  return (
    <section className="mx-auto max-w-6xl px-4 py-7 sm:px-6">
      <div className="grid gap-3 sm:grid-cols-2 sm:gap-4 lg:grid-cols-4">
        {shown.map((venue) => (
          <VenueCard key={venue.id} venue={venue} linkText="View →" />
        ))}
      </div>

      {hasMore && (
        <div className="mt-4 text-center">
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
