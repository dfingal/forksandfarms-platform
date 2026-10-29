import { getVenues } from "@/lib/api";

// Placeholder home page for build step 2 — just proves the API connection.
// The real wireframe layout (hero, map, venue cards, partner teaser) is
// build step 4.
export default async function Home() {
  const venues = await getVenues();

  return (
    <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
      <h1 className="text-forest">Plants in the places you already go.</h1>
      <p className="mt-2 max-w-xl text-forest/80">
        {/* TODO(copy): real one-line explanation */}
        We place curated plants in St. Louis coffee shops, wine bars, restaurants, and
        breweries — find them, and buy what you see.
      </p>

      <h2 className="mt-10 mb-4 text-forest">Venues (from the API)</h2>

      {venues === null && (
        <p className="rounded border border-terracotta/30 bg-terracotta/5 px-4 py-3 text-sm text-terracotta">
          We couldn&rsquo;t reach the venue list right now. Check that the backend is
          running at <code>{process.env.NEXT_PUBLIC_API_BASE_URL}</code> and try again.
        </p>
      )}

      {venues !== null && venues.length === 0 && (
        <p className="text-forest/70">No venues yet.</p>
      )}

      {venues !== null && venues.length > 0 && (
        <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {venues.map((venue) => (
            <li key={venue.id} className="rounded border border-forest/10 bg-white p-4">
              <p className="font-semibold text-forest">{venue.name}</p>
              <p className="text-sm text-forest/70">{venue.neighborhood}</p>
              <p className="mt-1 inline-block rounded bg-forest/10 px-2 py-0.5 text-xs text-forest">
                {venue.status}
              </p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
