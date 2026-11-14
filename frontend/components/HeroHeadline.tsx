"use client";

import { useEffect, useState, useSyncExternalStore } from "react";

// The rotating words, in order (loops back to the first). The first one
// is what the server renders, so the initial HTML is stable.
const WORDS = ["coffee.", "wine.", "brunch.", "mimosas.", "pastries."] as const;
const ROTATE_EVERY_MS = 5000;

// What screen readers and search engines get instead of the animation.
// TODO(copy): keep in sync with WORDS.
const FULL_SENTENCE = "If you like your plants with coffee, wine, brunch, mimosas or pastries.";

// Browser-only external sources, read via useSyncExternalStore (same
// pattern as NavBar.tsx). The server snapshots assume "motion allowed,
// tab visible"; either way the server shows the first word, unmoving.
const REDUCED_MOTION = "(prefers-reduced-motion: reduce)";

function subscribeReducedMotion(onChange: () => void) {
  const query = window.matchMedia(REDUCED_MOTION);
  query.addEventListener("change", onChange);
  return () => query.removeEventListener("change", onChange);
}

function subscribeVisibility(onChange: () => void) {
  document.addEventListener("visibilitychange", onChange);
  return () => document.removeEventListener("visibilitychange", onChange);
}

interface WordState {
  index: number; // the word currently shown
  leaving: number | null; // the previous word, while it animates out
  rotated: boolean; // has it rotated at least once? (first paint never animates)
}

/**
 * Homepage hero <h1>: "If you like your plants with" + one word below it
 * that rotates every 5s with a soft slide-and-fade (keyframes
 * word-in / word-out in app/globals.css).
 *
 * Accessibility: the h1's accessible name is the full sentence in a
 * visually-hidden span; everything visible is aria-hidden, and nothing
 * is an aria-live region, so screen readers don't hear each change.
 *
 * Rotation stops entirely for visitors who prefer reduced motion
 * ("coffee." stays), and pauses while the headline is hovered or the tab
 * is in the background.
 */
export default function HeroHeadline() {
  const [{ index, leaving, rotated }, setWords] = useState<WordState>({
    index: 0,
    leaving: null,
    rotated: false,
  });
  const [hovered, setHovered] = useState(false);

  const reducedMotion = useSyncExternalStore(
    subscribeReducedMotion,
    () => window.matchMedia(REDUCED_MOTION).matches,
    () => false
  );
  const tabHidden = useSyncExternalStore(
    subscribeVisibility,
    () => document.visibilityState === "hidden",
    () => false
  );

  const paused = reducedMotion || hovered || tabHidden;

  useEffect(() => {
    if (paused) return;
    // Resuming starts a fresh 5s wait rather than switching instantly.
    const timer = window.setInterval(() => {
      setWords(({ index }) => ({ index: (index + 1) % WORDS.length, leaving: index, rotated: true }));
    }, ROTATE_EVERY_MS);
    return () => window.clearInterval(timer);
  }, [paused]);

  // With reduced motion, always show the first word, whatever happened
  // before the preference changed.
  const shown = reducedMotion ? 0 : index;
  // Only animate words that arrived by rotating, never the first paint.
  // (Stays on after the slide-in ends; it doesn't replay, because the
  // span is only re-created when the word changes.)
  const animate = !reducedMotion && rotated;

  return (
    <h1
      className="text-forest"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <span className="sr-only">{FULL_SENTENCE}</span>
      <span aria-hidden="true" className="block">
        If you like your plants with
      </span>
      {/* Fixed height (one h1 line, 2.5rem) so the swap never shifts the
          layout; overflow-hidden clips the slide. Words are stacked on
          top of each other, left-aligned. */}
      <span aria-hidden="true" className="relative block h-10 overflow-hidden">
        {leaving !== null && !reducedMotion && (
          <span
            key={`out-${leaving}`}
            className="absolute inset-x-0 top-0 whitespace-nowrap animate-word-out"
            onAnimationEnd={() => setWords((words) => ({ ...words, leaving: null }))}
          >
            {WORDS[leaving]}
          </span>
        )}
        <span
          key={`in-${shown}`}
          className={`absolute inset-x-0 top-0 whitespace-nowrap${animate ? " animate-word-in" : ""}`}
        >
          {WORDS[shown]}
        </span>
      </span>
    </h1>
  );
}
