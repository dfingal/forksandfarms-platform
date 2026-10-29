import Link from "next/link";
import { NAV_LINKS, INSTAGRAM_URL } from "@/lib/nav-links";
import InstagramIcon from "./InstagramIcon";
import MobileNav from "./MobileNav";

// Server component — only MobileNav below needs client-side state.
export default function Header() {
  return (
    <header className="sticky top-0 z-30 border-b border-forest/10 bg-cream">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
        <Link href="/" className="text-lg font-semibold tracking-tight text-forest">
          Forks And Farms
        </Link>

        <nav aria-label="Primary" className="hidden items-center gap-6 md:flex">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-sm font-medium text-forest hover:text-terracotta"
            >
              {link.label}
            </Link>
          ))}
          <a
            href={INSTAGRAM_URL}
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Forks And Farms on Instagram"
            className="text-forest hover:text-terracotta"
          >
            <InstagramIcon className="h-5 w-5" />
          </a>
        </nav>

        <MobileNav />
      </div>
    </header>
  );
}
