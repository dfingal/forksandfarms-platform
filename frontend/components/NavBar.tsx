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
 * The floating, rounded header bar. Only this wrapper is a client
 * component; the logo and links inside it stay server-rendered (passed
 * in as children from Header.tsx).
 *
 * It exposes its state as data-scrolled, so children (the mobile menu
 * panel) can match its colour with `group-data-[scrolled=true]/navbar:`.
 * The colour change animates over 200ms, except for visitors who ask
 * for reduced motion, who get an instant switch.
 */
export default function NavBar({ children }: { children: React.ReactNode }) {
  const scrolled = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  return (
    <div
      data-scrolled={scrolled}
      className="group/navbar pointer-events-auto relative mx-auto flex max-w-6xl items-center justify-between rounded-2xl bg-cream px-4 py-4 transition-[background-color,box-shadow] duration-200 motion-reduce:transition-none data-[scrolled=true]:bg-nav-scrolled data-[scrolled=true]:shadow-md sm:px-6"
    >
      {children}
    </div>
  );
}
