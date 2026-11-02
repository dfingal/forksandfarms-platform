// Mirrors the DRF serializers in backend/core/serializers.py and
// backend/partners/serializers.py. Deliberately does NOT include
// partner_tier or square_location_id anywhere — the public API never
// returns them, so there is nothing to type here (spec §5).

export interface City {
  name: string;
  slug: string;
  state: string;
  intro: string;
  map_center_lat: string;
  map_center_lng: string;
  map_zoom: number;
  // Optional: a Render preview/deploy can lag behind a frontend deploy
  // that already expects this field (it was added after the rest of
  // City) — never assume it's present.
  timezone?: string | null; // IANA name, e.g. "America/Chicago"
}

export interface VenueCard {
  id: number;
  name: string;
  slug: string;
  city: string; // city slug
  neighborhood: string;
  status: "active" | "seasonal" | "coming_soon"; // "paused" never appears publicly
  short_description: string;
  hero_image: string | null;
  latitude: string;
  longitude: string;
}

export interface CityDetail extends City {
  venues: VenueCard[];
}

export interface VenuePhoto {
  image: string;
  alt_text: string;
  order: number;
}

export interface OpeningHoursRange {
  open: string; // "HH:MM", 24h
  close: string; // "HH:MM", 24h — earlier than open means past midnight
}

export interface OpeningHoursDay {
  day: string; // "Monday".."Sunday"
  // Only true when a day is explicitly marked closed. False + empty
  // ranges means "not set yet" — never render that as "Closed".
  is_closed: boolean;
  ranges: OpeningHoursRange[];
}

export interface VenueDetail extends VenueCard {
  setup_description: string;
  photos: VenuePhoto[];
  address_line1: string;
  address_line2: string;
  postal_code: string;
  // TODO(release): superseded by opening_hours below; kept for backward
  // compatibility until nothing reads it.
  hours: Record<string, string>;
  // Optional: a Render preview/deploy can lag behind a frontend deploy
  // that already expects this field — a build must never crash just
  // because the live API hasn't shipped it yet. Treat missing/null the
  // same as "no hours set" everywhere this is read.
  opening_hours?: OpeningHoursDay[] | null;
  website_url: string;
  instagram_handle: string;
}

// venue_type choices, shared with the partner application form
export type VenueType =
  | "coffee_shop"
  | "restaurant"
  | "bar"
  | "wine_bar"
  | "brewery"
  | "retail"
  | "hotel"
  | "library"
  | "office"
  | "other";

export type InterestedTier =
  | "retail_shelf"
  | "design_install"
  | "lease_maintenance"
  | "not_sure";

export interface PartnerApplicationPayload {
  contact_name: string;
  email: string;
  phone?: string;
  venue_name: string;
  venue_type: VenueType;
  address: string;
  space_description?: string;
  interested_tiers: InterestedTier[];
  referral_source?: string;
  notes?: string;
  turnstile_token: string;
}

export interface PartnerApplicationResponse {
  id: number;
  contact_name: string;
}
