import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Turn off the floating dev-mode route indicator.
  devIndicators: false,
  // cacheComponents (Next 16's new experimental prerendering model) is OFF
  // on purpose: it treats any uncached/failed fetch during build as a hard
  // error, which broke the build the moment the Django API was down —
  // exactly the case our lib/api.ts fallback UI exists to handle gracefully.
  // Revisit once the feature is stable and we actually want its benefits.
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
