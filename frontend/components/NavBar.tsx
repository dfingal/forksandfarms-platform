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
 * The header's inner row. Only this wrapper is a client component; the
 * logo and links inside it stay server-rendered (passed in as children
 * from Header.tsx).
 *
 * Below lg (1024px) it's just the content-width row inside the regular
 * full-width cream header — no scroll effect. From lg up (every lg:
 * class below) it becomes the floating, rounded bar: up to 1440px wide
 * (wider than the page content), cream at the top of the page, then
 * nav-scrolled + a shadow once data-scrolled is true. The colour change
 * animates over 200ms, except for visitors who ask for reduced motion,
 * who get an instant switch.
 */
export default function NavBar({ children }: { children: React.ReactNode }) {
  const scrolled = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  return (
    <div
      data-scrolled={scrolled}
      className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6 lg:pointer-events-auto lg:max-w-[1440px] lg:rounded-2xl lg:bg-cream lg:transition-[background-color,box-shadow] lg:duration-200 lg:motion-reduce:transition-none lg:data-[scrolled=true]:bg-nav-scrolled lg:data-[scrolled=true]:shadow-md"
    >
      {children}
    </div>
  );
}
