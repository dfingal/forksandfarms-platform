import Image from "next/image";
import type { SiteImage } from "@/lib/siteSettings";
import { isOptimizableImage } from "@/lib/siteSettings";

interface SitePhotoProps {
  /** The admin-set image, or null to show the placeholder box. */
  image: SiteImage | null;
  /** Screen-reader label and visible text for the placeholder. */
  placeholderLabel: string;
  placeholderText: string;
  /** Load early (above-the-fold heroes): next/image's preload. */
  preload?: boolean;
  /** Extra classes for the box, e.g. column ordering. */
  className?: string;
}

// The 4:3 rounded box shared by the home hero, the partner hero and
// "Why Forks And Farms".
const BOX = "aspect-[4/3] rounded-lg border border-forest/20 bg-cream";

/**
 * A Site settings photo, cropped to fill its 4:3 box (object-cover), or
 * the original placeholder box when no image is set.
 *
 * sizes: full width on mobile/tablet; from lg (1024px) the box is one
 * of two columns, at most 540px wide.
 */
export default function SitePhoto({
  image,
  placeholderLabel,
  placeholderText,
  preload = false,
  className = "",
}: SitePhotoProps) {
  if (!image) {
    return (
      <div
        role="img"
        aria-label={placeholderLabel}
        className={`${BOX} flex items-center justify-center text-sm text-muted ${className}`}
      >
        {placeholderText}
      </div>
    );
  }

  return (
    <div className={`${BOX} relative overflow-hidden ${className}`}>
      <Image
        src={image.url}
        alt={image.alt}
        fill
        sizes="(min-width: 1024px) 540px, 100vw"
        className="object-cover"
        preload={preload}
        // Local-dev uploads (not Cloudinary) can't go through Next's
        // optimizer; show them as-is. Production images are optimized.
        unoptimized={!isOptimizableImage(image.url)}
      />
    </div>
  );
}
