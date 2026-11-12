/**
 * Brand values needed outside CSS (the web manifest can't read Tailwind
 * tokens). Keep the hex values in sync with app/globals.css.
 */

import logoIcon from "@/public/brand/fnf-logo-small-icons/logo-icon-small-144.png";

export const BRAND_NAME = "Forks And Farms";

export const BRAND_COLORS = {
  forest: "#365540", // = --color-forest in app/globals.css (the logo's green)
  cream: "#f6f1e7", // = --color-cream in app/globals.css
} as const;

/**
 * The simplified round badge, for every small use (header, footer).
 * The 144px source keeps it sharp on 3× screens at the 32-44px sizes we
 * show it; next/image serves it as WebP to browsers that support it,
 * falling back to this PNG.
 *
 * The detailed badge in public/brand/fnf-logo-icons/ is kept for future
 * large uses only — its fine detail turns to mush at small sizes.
 */
export const LOGO_ICON = logoIcon;
