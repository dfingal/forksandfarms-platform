"use client";

import { useState } from "react";
import Link from "next/link";
import { NAV_LINKS, INSTAGRAM_URL } from "@/lib/nav-links";
import InstagramIcon from "./InstagramIcon";

// Only the hamburger toggle needs client-side state — the rest of the
// header stays a server component (see Header.tsx).
export default function MobileNav() {
  const [open, setOpen] = useState(false);

  return (
    <div className="md:hidden">
      <button
        type="button"
        aria-expanded={open}
        aria-controls="mobile-nav-panel"
        aria-label={open ? "Close menu" : "Open menu"}
        onClick={() => setOpen((v) => !v)}
        className="flex h-10 w-10 items-center justify-center rounded text-forest"
      >
        {open ? (
          <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth={2}>
            <path d="M6 6l12 12M18 6L6 18" strokeLinecap="round" />
          </svg>
        ) : (
          <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth={2}>
            <path d="M4 7h16M4 12h16M4 17h16" strokeLinecap="round" />
          </svg>
        )}
      </button>

      {open && (
        <div
          id="mobile-nav-panel"
          className="absolute inset-x-0 top-full z-20 flex flex-col gap-1 border-t border-forest/10 bg-cream px-4 py-4 shadow-sm"
        >
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              onClick={() => setOpen(false)}
              className="rounded px-2 py-2 text-base font-medium text-forest hover:bg-forest/5"
            >
              {link.label}
            </Link>
          ))}
          <a
            href={INSTAGRAM_URL}
            target="_blank"
            rel="noopener noreferrer"
            onClick={() => setOpen(false)}
            className="flex items-center gap-2 rounded px-2 py-2 text-base font-medium text-forest hover:bg-forest/5"
          >
            <InstagramIcon className="h-5 w-5" />
            Instagram
          </a>
        </div>
      )}
    </div>
  );
}
