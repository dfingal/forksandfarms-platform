import Link from "next/link";

// Catches notFound() from both /locations/[city] and
// /locations/[city]/[venue] (unknown slug or a paused venue) — Next
// bubbles an uncaught notFound() up to the nearest not-found.tsx.
export default function LocationsNotFound() {
  return (
    <div className="mx-auto max-w-xl px-4 py-16 text-center sm:px-6">
      <h1 className="text-forest">We couldn&rsquo;t find that location.</h1>
      <p className="mt-3 text-forest/70">
        It may have moved, closed, or the link might be out of date.
      </p>
      <Link
        href="/locations/st-louis"
        className="mt-6 inline-block rounded bg-forest px-5 py-2.5 text-sm font-semibold text-cream hover:bg-forest/90"
      >
        See all St. Louis locations →
      </Link>
    </div>
  );
}
