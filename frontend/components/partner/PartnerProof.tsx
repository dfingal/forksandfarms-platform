import { getVenues } from "@/lib/api";
import VenueCard from "@/components/VenueCard";

interface Testimonial {
  quote: string;
  name: string;
  venue: string;
}

// Empty for now — TODO(copy): real testimonials once partners provide
// them. The block below renders nothing at all when this is empty,
// rather than showing placeholder quotes attributed to no one.
const TESTIMONIALS: Testimonial[] = [];

// "Proof" section (spec §3.4.4): active partner venues, an optional
// testimonial block (hidden if empty), an optional stat line.
export default async function PartnerProof() {
  const venues = await getVenues();
  const activeVenues = (venues ?? []).filter((v) => v.status === "active");

  return (
    <section className="mx-auto max-w-6xl px-4 py-7 sm:px-6">
      <h2 className="mb-3 text-xs font-semibold uppercase tracking-wide text-forest/60">
        Trusted by local venues
      </h2>

      {activeVenues.length > 0 ? (
        <div className="grid gap-3 sm:grid-cols-2 sm:gap-4 lg:grid-cols-4">
          {activeVenues.map((venue) => (
            <VenueCard key={venue.id} venue={venue} />
          ))}
        </div>
      ) : (
        <p className="text-sm text-forest/70">
          We&rsquo;re just getting started — check back soon for our partner venues.
        </p>
      )}

      {TESTIMONIALS.length > 0 && (
        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          {TESTIMONIALS.map((t) => (
            <figure key={t.name} className="rounded-lg border border-forest/10 bg-white p-4">
              <blockquote className="text-forest/80">&ldquo;{t.quote}&rdquo;</blockquote>
              <figcaption className="mt-2 text-sm font-medium text-forest">
                {t.name}, {t.venue}
              </figcaption>
            </figure>
          ))}
        </div>
      )}

      {/* TODO(copy): optional stat line, e.g. "X venues · Y plants placed" */}
      <p className="mt-4 text-sm text-forest/60">TODO(copy): a stat worth bragging about.</p>
    </section>
  );
}
