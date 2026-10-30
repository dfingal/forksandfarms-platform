import Link from "next/link";
import type { VenueCard as VenueCardData } from "@/lib/types";
import { VENUE_STATUS_LABELS } from "@/lib/labels";

interface VenueCardProps {
  venue: VenueCardData;
  showDescription?: boolean;
  // Spec wording differs by page: home cards say "View →" (§3.1.4), city
  // list cards say "View location →" (§3.2).
  linkText?: string;
}

// Single venue card, shared by the home page (VenueCards) and the city
// locations page (VenueCardGrid) so both stay visually identical.
//
// Mobile-first: a compact horizontal row (small thumbnail + text) by
// default, switching to a stacked photo card at sm: and up.
export default function VenueCard({
  venue,
  showDescription = false,
  linkText = "View location →",
}: VenueCardProps) {
  return (
    <Link
      href={`/locations/${venue.city}/${venue.slug}`}
      className="group flex items-center gap-3 rounded-lg border border-forest/10 bg-white p-3 sm:flex-col sm:items-stretch sm:gap-0 sm:overflow-hidden sm:p-0"
    >
      <div
        aria-hidden="true"
        className="h-16 w-16 shrink-0 rounded bg-forest/10 sm:aspect-[4/3] sm:h-auto sm:w-full sm:shrink sm:rounded-none"
        style={
          venue.hero_image
            ? { backgroundImage: `url(${venue.hero_image})`, backgroundSize: "cover" }
            : undefined
        }
      />
      <div className="min-w-0 flex-1 sm:p-4">
        <p className="truncate font-semibold text-forest">{venue.name}</p>
        <p className="truncate text-sm text-forest/70">{venue.neighborhood}</p>
        {showDescription && venue.short_description && (
          <p className="mt-1 line-clamp-2 text-sm text-forest/70">{venue.short_description}</p>
        )}
        <div className="mt-1 flex items-center gap-2 sm:mt-2">
          <span className="rounded bg-forest/10 px-2 py-0.5 text-xs text-forest">
            {VENUE_STATUS_LABELS[venue.status]}
          </span>
          <span className="text-sm font-medium text-terracotta group-hover:underline">
            {linkText}
          </span>
        </div>
      </div>
    </Link>
  );
}
