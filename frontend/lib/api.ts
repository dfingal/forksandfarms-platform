/**
 * Typed client for the Django API (backend/docs/phase1-spec.md §5).
 *
 * GET helpers never throw — if the API is unreachable (network error, 5xx,
 * bad JSON), they log and return `null` so pages can render a friendly
 * fallback instead of crashing. This matters for Vercel builds: a page
 * statically generated while the API happens to be down must still build.
 *
 * The POST helper (submitPartnerApplication) is different: a form needs
 * to distinguish "network/server trouble" from "validation errors" from
 * "success", so it returns a discriminated result instead of null.
 */

import type {
  City,
  CityDetail,
  VenueCard,
  VenueDetail,
  PartnerApplicationPayload,
  PartnerApplicationResponse,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

if (!API_BASE_URL && typeof window === "undefined") {
  // Server-side only warning (avoids noisy console spam in the browser on
  // every render) — a missing env var should be obvious, not a silent 404.
  console.warn(
    "NEXT_PUBLIC_API_BASE_URL is not set — API calls will fail. Check frontend/.env.local."
  );
}

/** Revalidate static pages every 10 minutes by default (spec §7 fallback). */
const DEFAULT_REVALIDATE_SECONDS = 600;

async function apiGet<T>(path: string, params?: Record<string, string>): Promise<T | null> {
  if (!API_BASE_URL) return null;

  const url = new URL(`${API_BASE_URL}${path}`);
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value) url.searchParams.set(key, value);
    }
  }

  try {
    const response = await fetch(url.toString(), {
      next: { revalidate: DEFAULT_REVALIDATE_SECONDS },
    });
    if (!response.ok) {
      console.error(`API GET ${url} failed: ${response.status}`);
      return null;
    }
    return (await response.json()) as T;
  } catch (error) {
    console.error(`API GET ${url} failed:`, error);
    return null;
  }
}

export function getCities(): Promise<City[] | null> {
  return apiGet<City[]>("/cities/");
}

export function getCity(citySlug: string): Promise<CityDetail | null> {
  return apiGet<CityDetail>(`/cities/${citySlug}/`);
}

export function getVenues(options?: { city?: string }): Promise<VenueCard[] | null> {
  return apiGet<VenueCard[]>("/venues/", options?.city ? { city: options.city } : undefined);
}

export function getVenue(citySlug: string, venueSlug: string): Promise<VenueDetail | null> {
  return apiGet<VenueDetail>(`/cities/${citySlug}/venues/${venueSlug}/`);
}

export type PartnerApplicationResult =
  | { ok: true; data: PartnerApplicationResponse }
  | { ok: false; status: number; errors: Record<string, string[]> | null };

/**
 * POST a partner application. Unlike the GET helpers, this surfaces
 * failure detail (field errors on 400, "too many requests" on 429, etc.)
 * so the form built in a later step can show the visitor what went wrong.
 */
export async function submitPartnerApplication(
  payload: PartnerApplicationPayload
): Promise<PartnerApplicationResult> {
  if (!API_BASE_URL) {
    return { ok: false, status: 0, errors: null };
  }

  try {
    const response = await fetch(`${API_BASE_URL}/partner-applications/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (response.status === 201) {
      const data = (await response.json()) as PartnerApplicationResponse;
      return { ok: true, data };
    }

    let errors: Record<string, string[]> | null = null;
    try {
      errors = await response.json();
    } catch {
      // non-JSON error body (e.g. a proxy's own 502 page) — leave errors null
    }
    return { ok: false, status: response.status, errors };
  } catch (error) {
    console.error("API POST /partner-applications/ failed:", error);
    return { ok: false, status: 0, errors: null };
  }
}
