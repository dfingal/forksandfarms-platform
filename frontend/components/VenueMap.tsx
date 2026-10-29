"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  APIProvider,
  Map,
  AdvancedMarker,
  Pin,
  useMap,
} from "@vis.gl/react-google-maps";
import type { CityDetail, VenueCard } from "@/lib/types";
import { VENUE_STATUS_LABELS } from "@/lib/labels";

const API_KEY = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;
// A Map ID is required to render AdvancedMarker with custom pin styling.
// Google's own "DEMO_MAP_ID" works for local dev without creating one;
// require a real Map ID (env var) once this ships to production.
const MAP_ID =
  process.env.NEXT_PUBLIC_GOOGLE_MAPS_MAP_ID ||
  (process.env.NODE_ENV !== "production" ? "DEMO_MAP_ID" : undefined);

interface VenueMapProps {
  city: CityDetail;
  venues: VenueCard[];
}

/** Fits the map to every venue pin; falls back to the city's own
 * center/zoom when there are no venues with usable coordinates. */
function FitToVenues({ venues }: { venues: VenueCard[] }) {
  const map = useMap();

  useEffect(() => {
    if (!map) return;
    const points = venues
      .map((v) => ({ lat: Number(v.latitude), lng: Number(v.longitude) }))
      .filter((p) => Number.isFinite(p.lat) && Number.isFinite(p.lng));

    if (points.length === 0) return; // keep the city center/zoom default

    if (points.length === 1) {
      map.setCenter(points[0]);
      map.setZoom(15);
      return;
    }

    const bounds = new google.maps.LatLngBounds();
    points.forEach((p) => bounds.extend(p));
    map.fitBounds(bounds, 48);
  }, [map, venues]);

  return null;
}

function MapPlaceholder({ city, venues }: VenueMapProps) {
  // No API key, no load, or a runtime script error: a styled fallback
  // instead of a broken/blank map (never crash the page over this).
  return (
    <div className="flex min-h-80 flex-col items-center justify-center gap-3 rounded-lg border border-forest/10 bg-forest/5 p-6 text-center">
      <p className="text-sm text-forest/70">
        Map unavailable right now — here are our {city.name} locations:
      </p>
      <ul className="flex flex-wrap justify-center gap-2">
        {venues.map((venue) => (
          <li key={venue.id}>
            <Link
              href={`/locations/${venue.city}/${venue.slug}`}
              className="inline-block rounded border border-forest/20 bg-cream px-3 py-1 text-sm text-forest hover:border-forest"
            >
              {venue.name}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function VenueMap({ city, venues }: VenueMapProps) {
  const [selected, setSelected] = useState<VenueCard | null>(null);
  const [loadFailed, setLoadFailed] = useState(false);

  if (!API_KEY || loadFailed) {
    return <MapPlaceholder city={city} venues={venues} />;
  }

  return (
    <APIProvider apiKey={API_KEY} onError={() => setLoadFailed(true)}>
      <div className="relative min-h-80 overflow-hidden rounded-lg border border-forest/10">
        <Map
          mapId={MAP_ID}
          defaultCenter={{ lat: Number(city.map_center_lat), lng: Number(city.map_center_lng) }}
          defaultZoom={city.map_zoom}
          gestureHandling="cooperative"
          disableDefaultUI={false}
          style={{ width: "100%", height: "100%", minHeight: "20rem" }}
        >
          <FitToVenues venues={venues} />

          {venues.map((venue) => {
            const lat = Number(venue.latitude);
            const lng = Number(venue.longitude);
            if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null;

            return (
              <AdvancedMarker
                key={venue.id}
                position={{ lat, lng }}
                onClick={() => setSelected(venue)}
              >
                {/* tabIndex/role/onKeyDown make the pin keyboard-focusable
                    and activatable — AdvancedMarker's own element doesn't
                    get one by default. */}
                <div
                  role="button"
                  tabIndex={0}
                  aria-label={`${venue.name}, ${venue.neighborhood}`}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      setSelected(venue);
                    }
                  }}
                  className="cursor-pointer rounded-full focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-terracotta"
                >
                  <Pin
                    background="var(--color-terracotta)"
                    borderColor="var(--color-forest)"
                    glyphColor="var(--color-cream)"
                  />
                </div>
              </AdvancedMarker>
            );
          })}
        </Map>

        {selected && (
          <div className="absolute bottom-3 left-3 right-3 flex gap-3 rounded-lg border border-forest/10 bg-cream p-3 shadow-md sm:max-w-xs">
            <div
              aria-hidden="true"
              className="h-14 w-14 shrink-0 rounded bg-forest/10"
              style={
                selected.hero_image
                  ? { backgroundImage: `url(${selected.hero_image})`, backgroundSize: "cover" }
                  : undefined
              }
            />
            <div className="min-w-0 flex-1">
              <p className="truncate font-semibold text-forest">{selected.name}</p>
              <p className="truncate text-sm text-forest/70">{selected.neighborhood}</p>
              <p className="text-xs text-forest/60">{VENUE_STATUS_LABELS[selected.status]}</p>
              <Link
                href={`/locations/${selected.city}/${selected.slug}`}
                className="mt-1 inline-block text-sm font-medium text-terracotta hover:underline"
              >
                View location →
              </Link>
            </div>
            <button
              type="button"
              aria-label="Close"
              onClick={() => setSelected(null)}
              className="h-6 w-6 shrink-0 text-forest/50 hover:text-forest"
            >
              ×
            </button>
          </div>
        )}
      </div>
    </APIProvider>
  );
}
