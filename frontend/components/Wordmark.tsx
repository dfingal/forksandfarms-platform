import { Figtree, Red_Hat_Display } from "next/font/google";
import { BRAND_NAME } from "@/lib/brand";

/*
 * The wordmark's own typeface: used only for the "forks and farms" name
 * next to the logo badge (header + footer), nowhere else on the site.
 *
 * Both candidates are declared here (next/font needs each loader called
 * at module level with literal options). Only Red Hat Display is
 * preloaded, so the alternative doesn't cost every visitor an extra
 * download. If you switch to Figtree for good, set its preload to true
 * too (otherwise it still works, it's just fetched a moment later).
 */
const redHatDisplay = Red_Hat_Display({ subsets: ["latin"], weight: "400", display: "swap" });
const figtree = Figtree({ subsets: ["latin"], weight: "400", display: "swap", preload: false });

const WORDMARK_FONTS = { redHatDisplay, figtree };

// ↓ Switch the wordmark font here: "redHatDisplay" or "figtree".
const WORDMARK_FONT = WORDMARK_FONTS["redHatDisplay"];

/**
 * "Forks And Farms" shown in lowercase. The lowercase is CSS only
 * (text-transform), so the text in the page — what screen readers and
 * search engines read — stays "Forks And Farms". Size, colour and
 * letter-spacing come from the parent, so it keeps each spot's look.
 */
export default function Wordmark() {
  return <span className={`${WORDMARK_FONT.className} font-normal lowercase`}>{BRAND_NAME}</span>;
}
