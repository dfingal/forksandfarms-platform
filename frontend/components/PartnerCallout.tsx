import Link from "next/link";

// Lighter one-line callout for city/venue pages (per the wireframe) — the
// full three-option pitch (PartnerTeaser) only appears on the home page.
export default function PartnerCallout() {
  return (
    <section className="bg-forest/5">
      <div className="mx-auto flex max-w-6xl flex-col items-center gap-4 px-4 py-7 text-center sm:flex-row sm:justify-between sm:px-6 sm:text-left">
        <h2 className="text-forest">Want plants like these in your space?</h2>
        <Link
          href="/partner"
          className="inline-block shrink-0 rounded bg-forest px-5 py-2.5 text-sm font-semibold text-cream hover:bg-forest/90"
        >
          Partner With Us →
        </Link>
      </div>
    </section>
  );
}
