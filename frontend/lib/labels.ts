import type { VenueCard } from "./types";

// Readable labels for Venue.status — used anywhere a status badge is
// shown (home page cards now; locations/venue pages reuse this later).
// "paused" is deliberately omitted: the public API never returns it.
export const VENUE_STATUS_LABELS: Record<VenueCard["status"], string> = {
  active: "Active",
  seasonal: "Seasonal",
  coming_soon: "Coming soon",
};
