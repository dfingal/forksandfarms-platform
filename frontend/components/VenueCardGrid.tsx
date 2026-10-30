import type { VenueCard as VenueCardData } from "@/lib/types";
import VenueCard from "./VenueCard";

// City locations list grid (spec §3.2): 2-3 cards per row on desktop,
// compact rows on mobile (handled inside VenueCard itself).
export default function VenueCardGrid({ venues }: { venues: VenueCardData[] }) {
  if (venues.length === 0) {
    return <p className="text-forest/70">No locations here yet — check back soon.</p>;
  }

  return (
    <div className="grid gap-3 sm:grid-cols-2 sm:gap-4 lg:grid-cols-3">
      {venues.map((venue) => (
        <VenueCard key={venue.id} venue={venue} showDescription />
      ))}
    </div>
  );
}
