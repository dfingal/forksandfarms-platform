/**
 * Brand values needed outside CSS (the web manifest can't read Tailwind
 * tokens). Keep the hex values in sync with app/globals.css.
 */

import logoIconDetailed from "@/public/brand/fnf-logo-icons/logo-icon-144.png";
import logoIcon from "@/public/brand/fnf-logo-small-icons/logo-icon-small-144.png";

export const BRAND_NAME = "Forks And Farms";

export const BRAND_COLORS = {
  forest: "#365540", // = --color-forest in app/globals.css (the logo's green)
  laurel: "#b8c7ae", // = --color-laurel in app/globals.css (page background)
} as const;

/*
 * Two versions of the round badge. Both use 144px sources, which stay
 * sharp on 3× screens at the sizes we show them; next/image serves them
 * as WebP to browsers that support it, falling back to the PNG.
 *
 * - LOGO_ICON: the simplified badge — footer (32px). The browser icons
 *   and manifest icons use the same simplified artwork (app/ and
 *   public/brand/fnf-logo-small-icons/).
 * - LOGO_ICON_DETAILED: the detailed badge — header nav bar only
 *   (29px mobile / 35px desktop).
 */
export const LOGO_ICON = logoIcon;
export const LOGO_ICON_DETAILED = logoIconDetailed;
