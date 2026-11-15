/**
 * Site-wide images from the admin's "Site settings" (GET
 * /api/v1/site-settings/, backend/core/serializers.py
 * SiteSettingsSerializer): the home hero, the partner hero and the
 * "Why Forks And Farms" photo.
 *
 * The frontend may deploy before the backend that adds this endpoint, and
 * any field can be empty, so everything here is defensive: whatever is
 * missing or malformed becomes `null`, and the page shows its
 * placeholder box instead.
 */

export interface SiteImage {
  url: string;
  alt: string;
}

export interface SiteImages {
  homeHero: SiteImage | null;
  partnerHero: SiteImage | null;
  why: SiteImage | null;
}

export const NO_SITE_IMAGES: SiteImages = { homeHero: null, partnerHero: null, why: null };

/** One `{url, alt}` entry from the API, or null if it isn't usable. */
export function parseSiteImage(value: unknown): SiteImage | null {
  if (typeof value !== "object" || value === null) return null;
  const { url, alt } = value as { url?: unknown; alt?: unknown };
  if (typeof url !== "string" || !isHttpUrl(url)) return null;
  // The admin requires alt text with every image; an empty string is
  // still valid (decorative) if it ever slips through.
  return { url, alt: typeof alt === "string" ? alt : "" };
}

/** The whole API response (or null when the request failed). */
export function parseSiteImages(data: unknown): SiteImages {
  if (typeof data !== "object" || data === null) return NO_SITE_IMAGES;
  const raw = data as Record<string, unknown>;
  return {
    homeHero: parseSiteImage(raw.home_hero),
    partnerHero: parseSiteImage(raw.partner_hero),
    why: parseSiteImage(raw.why_image),
  };
}

/**
 * Whether next/image may optimize this URL. Only Cloudinary is
 * allow-listed (next.config.ts). Anything else (in practice local-dev
 * uploads served by Django at localhost, which Next 16 refuses to
 * optimize) is shown as-is with `unoptimized` instead.
 */
export function isOptimizableImage(url: string): boolean {
  try {
    const { protocol, hostname } = new URL(url);
    return protocol === "https:" && hostname === "res.cloudinary.com";
  } catch {
    return false;
  }
}

function isHttpUrl(value: string): boolean {
  try {
    const { protocol } = new URL(value);
    return protocol === "https:" || protocol === "http:";
  } catch {
    return false;
  }
}
