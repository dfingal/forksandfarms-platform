/**
 * Turn the API's `seo` object (backend/core/seo.py) into Next.js page
 * metadata: title, description, Open Graph + Twitter share image,
 * canonical URL, and robots noindex.
 *
 * The backend already applies fallbacks, but `seo` itself may be missing
 * (the frontend can deploy before the backend that adds it). Then each
 * page's own `fallback` values are used, which match what the pages
 * showed before SEO fields existed.
 */

import type { Metadata } from "next";
import type { SeoMeta } from "./types";

// TODO(brand): replace public/og-default.png with a real share image
// (1200 × 630 px).
export const DEFAULT_SHARE_IMAGE = {
  url: "/og-default.png",
  width: 1200,
  height: 630,
  alt: "Forks And Farms",
};

export const SITE_NAME = "Forks And Farms";

/**
 * The public site address from NEXT_PUBLIC_SITE_URL (e.g.
 * https://forksandfarms.com), or undefined if unset/invalid. Used as
 * metadataBase so relative URLs (the default share image, canonical
 * paths) become absolute.
 */
export function getSiteUrl(value = process.env.NEXT_PUBLIC_SITE_URL): URL | undefined {
  if (!value) return undefined;
  try {
    return new URL(value);
  } catch {
    console.warn(`NEXT_PUBLIC_SITE_URL is not a valid URL: ${value}`);
    return undefined;
  }
}

export interface MetadataFallback {
  title: string;
  description: string;
  /** This page's path, e.g. /locations/st-louis — the default canonical. */
  path: string;
}

export function buildMetadata(
  seo: SeoMeta | null | undefined,
  fallback: MetadataFallback,
  siteUrl: URL | undefined = getSiteUrl()
): Metadata {
  const title = seo?.title || fallback.title;
  const description = seo?.description || fallback.description;
  const image = seo?.og_image ? { url: seo.og_image } : DEFAULT_SHARE_IMAGE;

  // An explicit canonical from admin always wins. Otherwise the page's
  // own path — but only when we know the real site address: without
  // metadataBase, Next would resolve it against localhost, and a
  // canonical pointing at localhost is worse than none.
  const canonical = seo?.canonical_url || (siteUrl ? fallback.path : undefined);

  return {
    title,
    description,
    ...(canonical ? { alternates: { canonical } } : {}),
    openGraph: {
      title,
      description,
      siteName: SITE_NAME,
      type: "website",
      ...(canonical ? { url: canonical } : {}),
      images: [image],
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images: [image.url],
    },
    // noindex: ask search engines not to list the page, but still follow
    // its links (to other venues, etc.).
    ...(seo?.noindex ? { robots: { index: false, follow: true } } : {}),
  };
}
