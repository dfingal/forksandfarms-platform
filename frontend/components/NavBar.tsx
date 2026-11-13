"use client";

import { useSyncExternalStore } from "react";

// How far the page must scroll before the bar switches to its "scrolled"
// colour + shadow.
const SCROLL_THRESHOLD_PX = 20;

// Scroll position is a browser-only external source, so it's read via
// useSyncExternalStore (same pattern as partner/ThanksContent.tsx). The
// listener is passive, and React only re-renders when the true/false
// answer flips — not on every scroll event.
function subscribe(onChange: () => void) {
  window.addEventListener("scroll", onChange, { passive: true });
  return () => window.removeEventListener("scroll", onChange);
}

function getSnapshot(): boolean {
  return window.scrollY > SCROLL_THRESHOLD_PX;
}

function getServerSnapshot(): boolean {
  return false; // no scroll position during SSR: render the top-of-page look
}

/**
 * The sticky <header> and its inner row. Only this wrapper is a client
 * component; the logo and links inside it stay server-rendered (passed
 * in as children from Header.tsx).
 *
 * Both looks are transparent at the top of the page (blending into the
 * background) and turn cream with a faint border + shadow once
 * data-scrolled is true:
 * - Below lg (1024px, the max-lg: classes): the <header> itself is the
 *   full-width bar, edge to edge.
 * - lg and up (the lg: classes): the <header> is a transparent strip
 *   that provides a 24px side / 12px top gap, and the inner row is the
 *   floating, rounded bar, up to 1440px wide (wider than the page
 *   content). The strip ignores clicks (pointer-events-none) so the gap
 *   doesn't block the page underneath; the bar turns clicks back on.
 * The change animates over 200ms (motion-safe:), so visitors who ask for
 * reduced motion get an instant switch. Borders are always there, just
 * transparent at the top, so the header's height never jumps.
 *
 * It stays in normal flow, so page content starts below it rather than
 * hiding under it. z-40 keeps it above the Google Map.
 */
export default function NavBar({ children }: { children: React.ReactNode }) {
  const scrolled = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  return (
    <header
      data-scrolled={scrolled}
      className="group/header sticky top-0 z-40 border-b border-transparent motion-safe:transition-[background-color,border-color,box-shadow] motion-safe:duration-200 max-lg:data-[scrolled=true]:border-forest/15 max-lg:data-[scrolled=true]:bg-cream max-lg:data-[scrolled=true]:shadow-sm lg:pointer-events-none lg:border-b-0 lg:px-6 lg:pt-3"
    >
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6 lg:pointer-events-auto lg:max-w-[1440px] lg:rounded-3xl lg:border lg:border-transparent motion-safe:lg:transition-[background-color,border-color,box-shadow] motion-safe:lg:duration-200 lg:group-data-[scrolled=true]/header:border-forest/15 lg:group-data-[scrolled=true]/header:bg-cream lg:group-data-[scrolled=true]/header:shadow-md">
        {children}
      </div>
    </header>
  );
}
