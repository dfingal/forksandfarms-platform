"use client";

import { useSyncExternalStore } from "react";
import Link from "next/link";
import { THANKS_NAME_KEY } from "@/lib/partnerStorage";

const STEPS = [
  { title: "Apply", done: true },
  { title: "Walkthrough", done: false },
  { title: "Install", done: false },
  { title: "Ongoing care", done: false },
] as const;

// sessionStorage is a browser-only external source, so this reads it via
// useSyncExternalStore (no subscription needed — nothing else on this
// page changes it) rather than useState+useEffect, which avoids both a
// setState-in-effect render cascade and an SSR/hydration mismatch.
function subscribe() {
  return () => {};
}

function getSnapshot(): string | null {
  try {
    return sessionStorage.getItem(THANKS_NAME_KEY);
  } catch {
    return null;
  }
}

function getServerSnapshot(): string | null {
  return null; // sessionStorage doesn't exist during SSR
}

// Reads the first name the application form stashed in sessionStorage
// right before redirecting here — never from the URL, and the email is
// never stored at all (spec §3.5). Falls back to "Thanks!" when it's
// missing (private browsing, storage cleared, or a direct page visit).
export default function ThanksContent() {
  const firstName = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  return (
    <div className="mx-auto max-w-xl px-4 py-16 text-center sm:px-6">
      <span className="inline-block rounded-full bg-forest/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-forest">
        Application received
      </span>

      <h1 className="mt-4 text-forest">{firstName ? `Thanks, ${firstName}.` : "Thanks!"}</h1>
      <p className="mt-2 text-forest/80">We&rsquo;ll be in touch soon to schedule a walkthrough.</p>

      <ol className="mt-8 grid grid-cols-2 gap-4 text-left sm:grid-cols-4">
        {STEPS.map((step) => (
          <li key={step.title}>
            <p className={`text-sm font-semibold ${step.done ? "text-terracotta" : "text-forest/40"}`}>
              {step.done ? "✓" : "○"}
            </p>
            <p className={`mt-1 text-sm ${step.done ? "text-forest" : "text-forest/50"}`}>
              {step.title}
            </p>
          </li>
        ))}
      </ol>

      <div className="mt-8 flex flex-wrap justify-center gap-3">
        <Link
          href="/locations/st-louis"
          className="rounded bg-forest px-5 py-2.5 text-sm font-semibold text-cream hover:bg-forest/90"
        >
          See our locations
        </Link>
        <Link
          href="/"
          className="rounded border border-forest px-5 py-2.5 text-sm font-semibold text-forest hover:bg-forest/5"
        >
          Back to home
        </Link>
      </div>
    </div>
  );
}
