import type { VenueCard, VenueType, InterestedTier } from "./types";

// Readable labels for Venue.status — used anywhere a status badge is
// shown (home page cards now; locations/venue pages reuse this later).
// "paused" is deliberately omitted: the public API never returns it.
export const VENUE_STATUS_LABELS: Record<VenueCard["status"], string> = {
  active: "Active",
  seasonal: "Seasonal",
  coming_soon: "Coming soon",
};

// Matches Venue.VenueType / PartnerApplication.venue_type choices
// (backend/core/models.py) — used in the partner application form's
// venue type select.
export const VENUE_TYPE_LABELS: Record<VenueType, string> = {
  coffee_shop: "Coffee shop",
  restaurant: "Restaurant",
  bar: "Bar",
  wine_bar: "Wine bar",
  brewery: "Brewery",
  retail: "Retail",
  hotel: "Hotel",
  library: "Library",
  office: "Office",
  other: "Other",
};

// Matches PartnerApplication.InterestedTier choices — used for the
// application form's checkboxes.
export const INTERESTED_TIER_LABELS: Record<InterestedTier, string> = {
  retail_shelf: "Retail Shelf",
  design_install: "Design & Install",
  lease_maintenance: "Lease + Maintenance",
  not_sure: "Not sure yet",
};
