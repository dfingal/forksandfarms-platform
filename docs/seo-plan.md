# SEO fields — approved plan (not built yet)

**Status:** approved 2026-11-09, paused. Build on `feature/seo-fields`,
branched from `main` **after** `feature/instant-revalidation` is merged.
Phase I scope (spec §9 "SEO & analytics").

## Goal
Let the owner edit SEO metadata for cities and venues in Django admin,
with sensible automatic fallbacks, and have the Next.js pages use it.

## Backend
- **`core/seo.py`**: an abstract `SEOFieldsMixin` with optional fields, all
  blank/default so the migration is backward-compatible:
  - `seo_title` (char, blank)
  - `meta_description` (text, blank)
  - `og_image` (ImageField on the default storage, i.e. Cloudinary in prod, like `hero_image`)
  - `target_phrases` (text, blank). **Internal only**: a note for writing
    copy. Never serialized, never output as meta keywords.
  - `noindex` (bool, default False)
  - `canonical_url` (URL, blank)
- Plus `resolve_seo()`, which fills in fallbacks. Designed so Neighborhood/Tag
  can reuse both later by adding the mixin.
- Apply the mixin to `City` and `Venue`, with one migration.
- **Fallbacks** (resolved on the backend):

  | | Venue | City |
  |---|---|---|
  | title | `Plants at {venue} · Forks And Farms` | `Forks And Farms in {city}` |
  | description | `{neighborhood} — {short_description}` | `intro`, else generic line |
  | og_image | venue `og_image`, else `hero_image` | city `og_image`, else **site-wide default share image** |

  Fallback descriptions are truncated to about 160 characters **at a word boundary**.
  The site-wide default image lives in `frontend/public/` (placeholder,
  `TODO` replace). The backend returns `null` for og_image in that case and the
  frontend substitutes the default.
- **API**: an `seo` object on the city detail and venue detail endpoints only:
  `{ title, description, og_image (absolute URL or null), canonical_url, noindex }`.
- **Admin**: a collapsible "SEO" fieldset on City and Venue, with:
  - Live character counters (title about 60, description about 160; warn when over).
  - A simple Google-result preview that updates as you type and shows the
    fallback values when fields are blank.
  - `target_phrases` help text: for writing copy, never published.
  - JS/CSS in `core/static/core/admin/`.
- **Revalidation**: no new wiring needed. SEO fields live on City/Venue,
  so saving them already triggers `core/signals.py` and refreshes the
  pages. Add a test confirming an SEO-only edit sends a refresh.

## Frontend
- `lib/types.ts`: `seo?: SeoMeta | null` on `CityDetail` and `VenueDetail`
  (optional: the frontend may deploy before the backend).
- `lib/seo.ts`: `buildMetadata(seo, fallback)` returns Next `Metadata`: title,
  description, Open Graph and Twitter image, canonical, and `robots: { index: false }`
  when `noindex`. Missing/null `seo` falls back to today's hard-coded titles.
- `generateMetadata` on `/locations/[city]` and `/locations/[city]/[venue]`
  uses it.
- New env var `NEXT_PUBLIC_SITE_URL` (add to `.env.example`): used as
  `metadataBase` in the root layout (absolute Open Graph URLs) and for the
  default canonical when `canonical_url` is blank.

## Sitemap
There is no sitemap yet. Note in spec §9: when it is built, it must
exclude `noindex` pages.

## Tests
- Backend: each fallback, overrides beating fallbacks, word-boundary
  truncation, `noindex` passes through, `target_phrases` absent from every
  public endpoint, old rows with no SEO data still work.
- Frontend (vitest, `lib/seo.test.ts`): missing `seo`, `null` `seo`, full
  `seo`, `noindex`, default share image.

Commit on the branch; do not push.
