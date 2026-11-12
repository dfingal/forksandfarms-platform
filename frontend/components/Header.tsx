import Image from "next/image";
import Link from "next/link";
import { BRAND_NAME, LOGO_ICON_DETAILED } from "@/lib/brand";
import { NAV_LINKS, INSTAGRAM_URL } from "@/lib/nav-links";
import InstagramIcon from "./InstagramIcon";
import MobileNav from "./MobileNav";
import NavBar from "./NavBar";

// Server component — only NavBar (scroll colour) and MobileNav (menu
// toggle) below need client-side state.
//
// Two looks, switching at lg (1024px):
// - Below lg: a regular full-width sticky header, cream with a subtle
//   bottom border, edge to edge.
// - lg and up: a floating, rounded bar (styled in NavBar) with a 24px
//   side gap and a 12px top gap. Here the <header> is a
//   transparent sticky strip that provides the gap; it ignores clicks
//   (pointer-events-none) so the gap doesn't block the page underneath,
//   and the bar turns clicks back on.
// Either way it stays in normal flow, so page content starts below it
// rather than hiding under it. z-40 keeps it above the Google Map.
export default function Header() {
  return (
    <header className="sticky top-0 z-40 border-b border-forest/10 bg-cream lg:pointer-events-none lg:border-b-0 lg:bg-transparent lg:px-6 lg:pt-3">
      <NavBar>
        {/* Logo + name are one link. The image's alt is empty because the
            visible name already labels the link — otherwise screen readers
            would read "Forks And Farms" twice. */}
        <Link
          href="/"
          // text-xl (1.25rem) on mobile so name + logo + hamburger fit on
          // one line at 375px; text-2xl (1.5rem) from md up. nowrap keeps
          // the name on one line rather than wrapping under the logo.
          className="flex items-center gap-2 whitespace-nowrap text-xl font-semibold tracking-tight text-forest md:text-2xl"
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
          {BRAND_NAME}
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
    </header>
  );
}
