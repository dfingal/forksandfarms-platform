import Image from "next/image";
import Link from "next/link";
import { LOGO_ICON_DETAILED } from "@/lib/brand";
import { NAV_LINKS, INSTAGRAM_URL } from "@/lib/nav-links";
import InstagramIcon from "./InstagramIcon";
import MobileNav from "./MobileNav";
import NavBar from "./NavBar";
import Wordmark from "./Wordmark";

// Server component. Only NavBar (the sticky <header> itself, which
// changes colour on scroll) and MobileNav (menu toggle) need client-side
// state; see NavBar.tsx for the two looks (full width below lg, floating
// bar from lg up).
export default function Header() {
  return (
    <NavBar>
      {/* Logo + name are one link. The image's alt is empty because the
          visible name already labels the link — otherwise screen readers
          would read "Forks And Farms" twice. */}
      <Link
        href="/"
        // Wordmark at 1.75rem with a 2.25rem line height (leading-9), so
        // the bar's height barely changes. nowrap keeps the name on one
        // line rather than wrapping under the logo.
        className="flex items-center gap-2 whitespace-nowrap text-[1.75rem] leading-9 tracking-tight text-forest"
      >
        <Image
          src={LOGO_ICON_DETAILED}
          alt=""
          // 29px on mobile, 35px from md up (where the hamburger gives
          // way to the full nav). Not on Tailwind's spacing scale, hence
          // the [..px] values. sizes lets the browser pick a sharp
          // enough file for 2x/3x screens.
          sizes="(min-width: 768px) 35px, 29px"
          className="h-[29px] w-[29px] shrink-0 object-contain md:h-[35px] md:w-[35px]"
          preload
        />
        <Wordmark weight={500} />
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
    </NavBar>
  );
}
