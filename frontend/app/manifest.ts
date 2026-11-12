import type { MetadataRoute } from "next";
import { BRAND_COLORS, BRAND_NAME } from "@/lib/brand";

// Served at /manifest.webmanifest; Next adds the <link rel="manifest">
// automatically. Browser-tab icons themselves are app/favicon.ico,
// app/icon.png and app/apple-icon.png (Next's file conventions).
export default function manifest(): MetadataRoute.Manifest {
  return {
    name: BRAND_NAME,
    short_name: BRAND_NAME,
    description: "Plants in the places you already go.", // TODO(copy)
    start_url: "/",
    display: "browser",
    theme_color: BRAND_COLORS.forest,
    background_color: BRAND_COLORS.cream,
    icons: [
      // purpose "any" only — not "maskable": the logo is a full circle,
      // so Android's mask would crop its edges.
      { src: "/brand/fnf-logo-small-icons/icon-192.png", sizes: "192x192", type: "image/png", purpose: "any" },
      { src: "/brand/fnf-logo-small-icons/icon-512.png", sizes: "512x512", type: "image/png", purpose: "any" },
    ],
  };
}
