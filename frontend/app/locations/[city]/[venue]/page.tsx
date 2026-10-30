import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getCities, getCity, getVenue, getVenues } from "@/lib/api";
import { VENUE_STATUS_LABELS } from "@/lib/labels";
import { formatHours } from "@/lib/hours";
import VenueMap from "@/components/VenueMap";
import VenueCard from "@/components/VenueCard";
import PartnerCallout from "@/components/PartnerCallout";

// Prerender every known public venue at build time...
export async function generateStaticParams() {
  const cities = await getCities();
  if (!cities) return [];

  const params: { city: string; venue: string }[] = [];
  for (const city of cities) {
    const venues = await getVenues({ city: city.slug });
    for (const venue of venues ?? []) {
      params.push({ city: city.slug, venue: venue.slug });
    }
  }
  return params;
}

// ...but a venue added after the last build still renders on first visit
// (dynamicParams defaults to true — explicit here), and a venue switched
// to "paused" 404s again once this page revalidates, since getVenue()
// only ever returns public statuses.
export const dynamicParams = true;
export const revalidate = 600; // 10 minutes, matches the rest of the site

interface PageProps {
  params: Promise<{ city: string; venue: string }>;
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { city: citySlug, venue: venueSlug } = await params;
  const venue = await getVenue(citySlug, venueSlug);
  if (!venue) return {};

  return {
    title: `Plants at ${venue.name} · Forks And Farms`,
    description:
      venue.short_description || `Find Forks And Farms plants at ${venue.name} in ${venue.neighborhood}.`,
  };
}

export default async function VenuePage({ params }: PageProps) {
  const { city: citySlug, venue: venueSlug } = await params;
  const [venue, city] = await Promise.all([getVenue(citySlug, venueSlug), getCity(citySlug)]);

  // Covers an unknown city slug, an unknown venue slug, and a paused
  // venue — the API 404s all three identically.
  if (!venue) {
    notFound();
  }

  const cityName = city?.name ?? citySlug;

  const otherVenues = (await getVenues({ city: citySlug }))
    ?.filter((v) => v.slug !== venue.slug)
    .slice(0, 3);

  const addressLines = [venue.address_line1, venue.address_line2].filter(Boolean);
  const fullAddress = addressLines.join(", ");
  const directionsQuery = encodeURIComponent(`${venue.name}, ${fullAddress}`);
  const directionsUrl = `https://www.google.com/maps/search/?api=1&query=${directionsQuery}`;
  const hoursLines = formatHours(venue.hours);

  return (
    <div>
      <div className="mx-auto max-w-6xl px-4 py-5 sm:px-6">
        <Link href={`/locations/${citySlug}`} className="text-sm text-forest/70 hover:text-forest">
          ← All {cityName} locations
        </Link>
      </div>

      {/* Hero */}
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div
          aria-hidden={!venue.hero_image}
          role={venue.hero_image ? "img" : undefined}
          aria-label={venue.hero_image ? `${venue.name} hero photo` : undefined}
          className="aspect-[16/9] rounded-lg bg-forest/10 sm:aspect-[21/9]"
          style={
            venue.hero_image
              ? { backgroundImage: `url(${venue.hero_image})`, backgroundSize: "cover", backgroundPosition: "center" }
              : undefined
          }
        >
          {!venue.hero_image && (
            <div className="flex h-full items-center justify-center text-sm text-forest/50">
              Photo coming soon
            </div>
          )}
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-3">
          <h1 className="text-forest">{venue.name}</h1>
          <span className="rounded bg-forest/10 px-2 py-0.5 text-xs text-forest">
            {VENUE_STATUS_LABELS[venue.status]}
          </span>
        </div>
        <p className="text-forest/70">{venue.neighborhood}</p>
      </div>

      {/* Info block */}
      <div className="mx-auto mt-7 grid max-w-6xl gap-6 px-4 sm:grid-cols-2 sm:px-6">
        <div className="space-y-4">
          <div>
            <h3 className="text-forest">Address</h3>
            <p className="text-sm text-forest/70">
              {addressLines.map((line) => (
                <span key={line} className="block">
                  {line}
                </span>
              ))}
              {venue.postal_code && <span className="block">{venue.postal_code}</span>}
            </p>
            <a
              href={directionsUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-1 inline-block text-sm font-medium text-terracotta hover:underline"
            >
              Get directions →
            </a>
          </div>

          {hoursLines.length > 0 && (
            <div>
              <h3 className="text-forest">Hours</h3>
              <p className="text-sm text-forest/70">
                {hoursLines.map((line) => (
                  <span key={line} className="block">
                    {line}
                  </span>
                ))}
              </p>
            </div>
          )}

          {venue.website_url && (
            <div>
              <a
                href={venue.website_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm font-medium text-terracotta hover:underline"
              >
                Visit website →
              </a>
            </div>
          )}
        </div>

        <VenueMap
          city={{
            name: cityName,
            map_center_lat: venue.latitude,
            map_center_lng: venue.longitude,
            map_zoom: 15,
          }}
          venues={[venue]}
        />
      </div>

      {/* Plant setup */}
      <div className="mx-auto mt-7 max-w-6xl px-4 sm:px-6">
        <h2 className="text-forest">The plant setup at {venue.name}</h2>
        <p className="mt-2 max-w-2xl text-forest/80">{venue.setup_description}</p>

        {venue.photos.length > 0 ? (
          <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
            {venue.photos.map((photo, i) => (
              <div
                key={i}
                role="img"
                aria-label={photo.alt_text}
                className="aspect-[4/3] rounded bg-forest/10"
                style={{ backgroundImage: `url(${photo.image})`, backgroundSize: "cover" }}
              />
            ))}
          </div>
        ) : (
          <div className="mt-4 flex aspect-[16/9] max-w-md items-center justify-center rounded bg-forest/10 text-sm text-forest/50">
            Photos coming soon
          </div>
        )}
      </div>

      {/* Other locations */}
      {otherVenues && otherVenues.length > 0 && (
        <div className="mx-auto mt-7 max-w-6xl px-4 sm:px-6">
          <h2 className="mb-3 text-forest">Other locations</h2>
          <div className="grid gap-3 sm:grid-cols-2 sm:gap-4 lg:grid-cols-3">
            {otherVenues.map((other) => (
              <VenueCard key={other.id} venue={other} />
            ))}
          </div>
        </div>
      )}

      <div className="mt-7">
        <PartnerCallout />
      </div>
    </div>
  );
}
