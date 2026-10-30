import Link from "next/link";
import type { CityDetail } from "@/lib/types";
import { VENUE_STATUS_LABELS } from "@/lib/labels";

// Up to 4 venue cards (spec §3.1.4, layout 1a). City.venues already comes
// ordered display_order, then name from the API.
//
// Mobile-first: a compact horizontal row (small thumbnail + text) by
// default, switching to the full stacked photo card at sm: and up —
// avoids 4 tall image cards stacked on a 375px screen.
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
          <Link
            key={venue.id}
            href={`/locations/${venue.city}/${venue.slug}`}
            className="group flex items-center gap-3 rounded-lg border border-forest/10 bg-white p-3 sm:flex-col sm:items-stretch sm:gap-0 sm:overflow-hidden sm:p-0"
          >
            <div
              aria-hidden="true"
              className="h-16 w-16 shrink-0 rounded bg-forest/10 sm:aspect-[4/3] sm:h-auto sm:w-full sm:shrink sm:rounded-none"
              style={
                venue.hero_image
                  ? { backgroundImage: `url(${venue.hero_image})`, backgroundSize: "cover" }
                  : undefined
              }
            />
            <div className="min-w-0 flex-1 sm:p-4">
              <p className="truncate font-semibold text-forest">{venue.name}</p>
              <p className="truncate text-sm text-forest/70">{venue.neighborhood}</p>
              <div className="mt-1 flex items-center gap-2 sm:mt-2">
                <span className="rounded bg-forest/10 px-2 py-0.5 text-xs text-forest">
                  {VENUE_STATUS_LABELS[venue.status]}
                </span>
                <span className="text-sm font-medium text-terracotta group-hover:underline">
                  View →
                </span>
              </div>
            </div>
          </Link>
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
