import Link from "next/link";
import { NAV_LINKS, INSTAGRAM_URL, CONTACT_EMAIL } from "@/lib/nav-links";

export default function Footer() {
  return (
    <footer className="border-t border-forest/10 bg-cream">
      <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-6 text-sm text-forest sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <span className="font-semibold tracking-tight">Forks And Farms</span>

        <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
          <a href={`mailto:${CONTACT_EMAIL}`} className="hover:text-terracotta">
            {CONTACT_EMAIL}
          </a>
          <a
            href={INSTAGRAM_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-terracotta"
          >
            Instagram
          </a>
          {NAV_LINKS.map((link) => (
            <Link key={link.href} href={link.href} className="hover:text-terracotta">
              {link.label}
            </Link>
          ))}
        </div>
      </div>
    </footer>
  );
}
