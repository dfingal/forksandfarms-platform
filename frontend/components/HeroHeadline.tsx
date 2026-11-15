"use client";

import { useEffect, useState, useSyncExternalStore } from "react";

// The rotating words, in order (loops back to the first). The first one
// is what the server renders, so the initial HTML is stable.
const WORDS = ["coffee", "wine", "brunch", "mimosas", "cocktails"] as const;
const ROTATE_EVERY_MS = 2800;
// Length of the slide-and-fade (.hero-word-in/-out in app/globals.css).
const WORD_TRANSITION_MS = 350;
// Backup for removing the outgoing word if animationend never arrives
// (e.g. the tab was backgrounded mid-animation, so browsers paused it).
const EXIT_FALLBACK_MS = WORD_TRANSITION_MS + 150;

// What screen readers and search engines get instead of the animation.
// TODO(copy): keep in sync with WORDS.
const FULL_SENTENCE = "Like your coffee, wine, brunch, mimosas or cocktails with plants?";

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
 * Homepage hero <h1>, two lines: "Like your [word]" / "with plants?",
 * where the word at the end of line 1 rotates every 2.8s with a soft slide-and-fade (.hero-word-in /
 * .hero-word-out in app/globals.css). The word is bold and in the
 * accent-orange highlight colour: 3.16:1 on the light-green background,
 * which passes WCAG AA because it's large text (36px bold). Keep it
 * large if the heading size ever changes.
 *
 * During a change, the outgoing word is rendered once more with the exit
 * animation, then unmounted on animationend (or after a short timeout if
 * that never fires), so only one word is visible once it settles.
 *
 * Accessibility: the h1's accessible name is the full sentence in a
 * visually-hidden span; everything visible is aria-hidden, and nothing
 * is an aria-live region, so screen readers don't hear each change.
 *
 * Rotation stops entirely for visitors who prefer reduced motion
 * ("coffee" stays), and pauses while the headline is hovered or the tab
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

  const removeLeavingWord = () => setWords((words) => ({ ...words, leaving: null }));

  // Fallback removal of the outgoing word (normally animationend does it).
  useEffect(() => {
    if (leaving === null) return;
    const timer = window.setTimeout(removeLeavingWord, EXIT_FALLBACK_MS);
    return () => window.clearTimeout(timer);
  }, [leaving]);

  useEffect(() => {
    if (paused) return;
    // Resuming (after a hover or tab switch) starts a fresh 2.8s wait
    // rather than switching instantly.
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
      className="hero-headline text-forest"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <span className="sr-only">{FULL_SENTENCE}</span>
      <span aria-hidden="true" className="block">
        Like your{" "}
        {/* The word slot. Its width is always the widest word's: every
            word is stacked invisibly in the same grid cell, so nothing
            reflows as the word changes. Its height is exactly one headline
            line (h-[1lh]: one line of the h1's own line height, which
            grows from lg up via .hero-headline in globals.css; the
            invisible words give the same height in browsers without lh
            support). overflow-hidden clips
            the slide, and align-top plus the matching line height keeps the
            word on the text's baseline.
            ("Like your cocktails" is 331px of the 343px available at 375px.
            On narrower phones the slot wraps onto its own line, the same
            for every word, so there's still no shift. From lg up the fit is
            worked out in globals.css.) */}
        <span className="relative inline-grid h-[1lh] overflow-hidden align-top font-bold text-accent-orange">
          {WORDS.map((word) => (
            <span key={word} className="invisible col-start-1 row-start-1 whitespace-nowrap">
              {word}
            </span>
          ))}
          {leaving !== null && !reducedMotion && (
            <span
              key={`out-${leaving}`}
              className="hero-word-out absolute inset-x-0 top-0 whitespace-nowrap"
              onAnimationEnd={removeLeavingWord}
            >
              {WORDS[leaving]}
            </span>
          )}
          <span
            key={`in-${shown}`}
            className={`absolute inset-x-0 top-0 whitespace-nowrap${animate ? " hero-word-in" : ""}`}
          >
            {WORDS[shown]}
          </span>
        </span>
      </span>
      {/* Its own line, so it never moves as the word above changes. */}
      <span aria-hidden="true" className="block">
        with plants?
      </span>
    </h1>
  );
}
