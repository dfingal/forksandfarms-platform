# Forks And Farms — Phase I Spec

Status: Draft v1 · Last updated: 2026-10-29

## 1. Overview

Forks And Farms places curated plants inside St. Louis hospitality venues (coffee shops, wine bars, restaurants, breweries). Customers can buy the plants they see. Venues partner in one of three ways:

1. **Retail Shelf** — FnF stocks a plant shelf; the venue earns a share of sales.
2. **Design & Install** — FnF designs and installs plants the venue purchases.
3. **Lease + Maintenance** — FnF leases plants to the venue with ongoing care included. Minimum 20 plants.

Current partner venues: Northwest Coffee, Scarlett's Wine Bar, Egg Midtown, Rockwell Beer Co.

### Phase I goal
A simple, fast public site that:
- Explains what Forks And Farms does
- Shows every partner venue on a map, with a page for each venue
- Collects applications from venues that want to partner

Two audiences: **plant shoppers** (where can I find you?) and **venue owners** (how do I partner?).

### Guiding rule
Build **only** Phase I scope, but never make choices that block Phase II (Square catalog, QR checkout, cart, revenue-share tracking). Where a Phase II hook is noted below, include the field/structure but do not build the feature.

---

## 2. Tech stack

| Layer | Choice | Purpose |
|---|---|---|
| Frontend | Next.js (App Router, TypeScript) + Tailwind CSS | Public site; pages pre-rendered for speed and SEO |
| Frontend hosting | Vercel | Auto-deploys from GitHub, preview links per branch |
| Backend | Django + Django REST Framework | API, data models, Django admin as the back office |
| Backend hosting | Railway | Runs Django |
| Database | PostgreSQL (Railway) | All data |
| Images | Cloudinary | Venue photo storage + resizing |
| Maps | Google Maps JavaScript API | Home map, venue mini-maps, custom pins |
| Email | Resend | Notify FnF of new partner applications; confirmation to applicant |
| Spam protection | Cloudflare Turnstile | Invisible bot check on the partner form |
| Phase II | Square APIs (Catalog, Inventory, Orders, Payments, Web Payments SDK) | Not built in Phase I |

### Repo layout (monorepo)
```
forksandfarms-platform/
  CLAUDE.md
  README.md
  docs/
    phase1-spec.md
    wireframes/
  backend/        # Django + DRF
  frontend/       # Next.js
```

---

## 3. Pages & routes

| Route | Page | Notes |
|---|---|---|
| `/` | Home | Hero, What We Do, map, venue cards, partner teaser |
| `/locations` | Locations index | Phase I: redirects to `/locations/st-louis`. Becomes a city picker when a 2nd city exists |
| `/locations/[city]` | City locations list | e.g. `/locations/st-louis` |
| `/locations/[city]/[venue]` | Venue page | e.g. `/locations/st-louis/northwest-coffee` |
| `/partner` | Partner With Us + application form | |
| `/partner/thanks` | Application received | |

Global header: logo (links home), nav: Locations, Partner With Us, Instagram icon. Mobile: hamburger menu.
Global footer: logo, contact email, Instagram, Locations, Partner With Us.

Only venues with status `active`, `seasonal`, or `coming_soon` appear publicly. `paused` venues are hidden everywhere.

### 3.1 Home (`/`)
1. **Hero** — headline ("Plants in the places you already go."), one-line explanation, hero photo. Buttons: "Find Plants Near You" (scrolls to map) and "Partner With Us" (→ `/partner`).
2. **What We Do** — three blocks: plants in places you already love · buy what you see · we handle the care.
3. **Map section** ("Find plants near you") — large Google Map centered on the city, custom branded pin for every public venue. Clicking a pin opens a small card: photo, venue name, neighborhood, "View location →".
4. **Venue cards** (layout 1a) — below the map, up to **4** venue cards (photo, name, neighborhood, "View →"). If more than 4 venues exist, show a **"See all St. Louis locations →"** button linking to `/locations/st-louis`. Ordering: `display_order`, then name.
5. **Partner teaser** — short pitch for venue owners, three option cards (Retail Shelf, Design & Install, Lease + Maintenance), "Partner With Us →" button.

Mobile: map on top, cards stacked in a single column; tapping a pin shows the card at the bottom of the map.

### 3.2 City locations list (`/locations/[city]`)
- Title "Forks And Farms in {City}" + one-line intro (from City record).
- Grid of venue cards: photo, name, neighborhood, status badge (Active / Seasonal / Coming Soon), 1–2 sentence `short_description`, "View location →".
- Desktop: 2–3 cards per row. Mobile: single column.
- Partner callout + footer.
- Unknown city slug → 404.

### 3.3 Venue page (`/locations/[city]/[venue]`)
1. "← All {City} locations" link.
2. **Hero** — large hero photo, venue name, neighborhood, status badge.
3. **Info block** — address with "Get directions" link (Google Maps), hours, link to venue's own website, small embedded map with one pin.
4. **The plant setup** — `setup_description` + photo gallery. Leave layout room for a future "Plants here" inventory section (Phase II) but show nothing about it publicly.
5. **Other locations** — row of cards for other public venues in the same city (max 3; becomes "nearby" later).
6. **Partner callout** — "Want plants like these in your space?" → `/partner`.
- Unknown or paused venue → 404.

### 3.4 Partner page (`/partner`)
1. **Intro** — headline ("Plants that pay their way."), short pitch; three value points: revenue from décor · no plant-care burden · draws customers who enjoy being around plants. Button "Apply below ↓".
2. **Three ways to partner** — Retail Shelf, Design & Install, Lease + Maintenance; 1–2 line description each; Lease card carries a "Starts at 20 plants" tag.
3. **How it works** — 01 Apply · 02 Walkthrough · 03 Install · 04 Ongoing care.
4. **Application form** — fields in §4.3. Inline validation. Turnstile check. On success → `/partner/thanks`.

### 3.5 Thanks (`/partner/thanks`)
"Application received" badge, "Thanks, {first name}." (fallback "Thanks!"), "We'll be in touch at {email} to schedule a walkthrough." What-happens-next steps (Apply ✓, Walkthrough, Install, Ongoing care). Buttons: "See our locations", "Back to home".

---

## 4. Data models (Django)

All models get `created_at` and `updated_at` timestamps.

### 4.1 City
| Field | Type | Notes |
|---|---|---|
| name | char(100) | "St. Louis" |
| slug | slug, unique | "st-louis" |
| state | char(2) | "MO" |
| intro | text, blank | One-liner for the city page |
| map_center_lat | decimal(9,6) | |
| map_center_lng | decimal(9,6) | |
| map_zoom | int, default 12 | |
| is_active | bool, default true | Hidden from public if false |

### 4.2 Venue
| Field | Type | Notes |
|---|---|---|
| city | FK → City | |
| name | char(150) | |
| slug | slug | Unique per city (`unique_together = city, slug`) |
| neighborhood | char(100) | |
| venue_type | choice | coffee_shop, restaurant, bar, wine_bar, brewery, retail, hotel, library, office, other |
| status | choice | `active`, `seasonal`, `coming_soon`, `paused` |
| partner_tier | choice | `retail_shelf`, `design_install`, `lease_maintenance` (internal; not shown publicly in Phase I) |
| address_line1 | char | |
| address_line2 | char, blank | |
| postal_code | char(10) | |
| latitude | decimal(9,6) | |
| longitude | decimal(9,6) | |
| hours | JSON | e.g. `{"mon": "7:00–18:00", ...}` or `{"display": "Mon–Fri 7–6 · Sat–Sun 8–4"}` |
| website_url | URL, blank | |
| instagram_handle | char, blank | |
| short_description | char(280) | Used on cards |
| setup_description | text | "The plant setup" section |
| hero_image | Cloudinary image | |
| display_order | int, default 0 | Lower = earlier |
| square_location_id | char, blank, null | **Phase II hook** — leave empty |

### 4.3 VenuePhoto
| Field | Type | Notes |
|---|---|---|
| venue | FK → Venue (related_name `photos`) | |
| image | Cloudinary image | |
| alt_text | char(200) | Required for accessibility |
| order | int, default 0 | |

### 4.4 PartnerApplication
| Field | Type | Notes |
|---|---|---|
| contact_name | char(150) | required |
| email | email | required |
| phone | char(30), blank | |
| venue_name | char(150) | required |
| venue_type | choice | same choices as Venue |
| address | char(255) | required |
| space_description | char(255), blank | "Approx. space or number of plants" |
| interested_tiers | JSON list | any of `retail_shelf`, `design_install`, `lease_maintenance`, `not_sure` |
| referral_source | char(150), blank | "How did you hear about us?" |
| notes | text, blank | |
| status | choice, default `new` | `new`, `contacted`, `walkthrough_scheduled`, `proposal_sent`, `signed`, `declined` |
| internal_notes | text, blank | Admin only |
| converted_venue | FK → Venue, null | Set when a signed application becomes a Venue |
| source_ip | IP, null | For spam review |

---

## 5. API (Django REST Framework)

Base path: `/api/v1/`. JSON only. Public read endpoints are unauthenticated; only public venue statuses are returned.

| Method | Endpoint | Returns / does |
|---|---|---|
| GET | `/cities/` | Active cities: name, slug, state, intro, map center/zoom |
| GET | `/cities/{city_slug}/` | One city + its public venues (card fields) |
| GET | `/venues/?city={slug}` | Public venues, card fields (id, name, slug, city slug, neighborhood, status, short_description, hero_image URL, lat/lng) |
| GET | `/cities/{city_slug}/venues/{venue_slug}/` | Full venue detail incl. photos, hours, address, website, setup_description |
| POST | `/partner-applications/` | Validates, verifies Turnstile token, saves, sends emails. Returns `201 {id, contact_name}` |

Notes:
- Never expose `partner_tier`, `square_location_id`, or any PartnerApplication data via public GET.
- POST is rate-limited (DRF throttle, e.g. 5/hour per IP).
- Image URLs returned as Cloudinary URLs; frontend requests sized variants.
- CORS: allow the Vercel production domain + preview domains + localhost.

---

## 6. Django admin (back office)

- **City** — list: name, state, active.
- **Venue** — list: name, city, neighborhood, status, tier, display_order; filters: city, status, tier; slug auto-filled from name; inline VenuePhoto editor; map coordinates editable.
- **PartnerApplication** — list: venue_name, contact_name, email, status, created_at; filters: status, venue_type, interested tiers; search by name/email/venue; status editable from the list; action "Create Venue from application" (pre-fills a draft Venue with status `coming_soon`).

---

## 7. Integrations & behavior

- **Emails (Resend)** on new application:
  1. To FnF (hello@ address): summary of all fields + link to the admin record.
  2. To applicant: "Thanks, we got your application — we'll reach out to schedule a walkthrough."
- **Turnstile**: frontend renders widget; backend verifies token before saving.
- **Page freshness**: Next.js pages are statically generated and revalidated. When a City or Venue is saved in admin, Django calls a protected Next.js revalidate endpoint so changes appear within seconds (fallback: time-based revalidation every 10 minutes).
- **Map pins**: custom SVG pin in brand colors; pins only for public venues.
- **Google Maps key**: restricted to production + preview domains; daily quota cap set in Google Cloud.

---

## 8. Design

- Follow the Phase I wireframes in `docs/wireframes/`.
- Brand palette: forest green, cream, terracotta (exact hex values TBD — define as Tailwind theme tokens so they can be swapped in one place).
- Mobile-first; test at 375px and 1200px+.
- Accessible: alt text on all images, keyboard-navigable map cards and form, visible focus states, form labels.

---

## 9. SEO & analytics

- Unique `<title>` and meta description per page; venue pages use venue name + neighborhood ("Plants at Northwest Coffee · Forks And Farms").
- Open Graph image per venue (hero image).
- `sitemap.xml` and `robots.txt` generated from cities/venues.
- LocalBusiness-style structured data on venue pages (optional, nice to have).
- Privacy-friendly analytics (e.g. Vercel Analytics or Plausible); track "Partner With Us" clicks and form submissions.

---

## 10. Environments & config

Env vars (never committed):
- Backend: `DATABASE_URL`, `DJANGO_SECRET_KEY`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `CLOUDINARY_URL`, `RESEND_API_KEY`, `TURNSTILE_SECRET_KEY`, `FNF_NOTIFY_EMAIL`, `FRONTEND_REVALIDATE_URL`, `REVALIDATE_SECRET`
- Frontend: `NEXT_PUBLIC_API_BASE_URL`, `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY`, `NEXT_PUBLIC_TURNSTILE_SITE_KEY`, `REVALIDATE_SECRET`

Provide `.env.example` files in both `backend/` and `frontend/`.

---

## 11. Build order

1. Backend foundation — Django project, Postgres, models, admin, API, seed data for St. Louis + 4 venues.
2. Frontend foundation — Next.js, Tailwind theme tokens, header/footer, API client.
3. Deploy — Vercel (frontend), Railway (backend + DB). Env vars wired.
4. Home page.
5. City list page + venue pages.
6. Partner page, form, Turnstile, emails, thanks page.
7. Polish — mobile QA, SEO, sitemap, analytics, real content.

Each step: propose a plan → build → run locally → compare to wireframe → commit.

---

## 12. Out of scope for Phase I

Plant catalog/product pages, cart, checkout, Square integration, QR codes, customer accounts, partner logins/dashboards, revenue-share reporting, lease/maintenance billing, referral program, delivery. (All planned for Phase II+; see hooks above.)

---

## 13. Phase II preview (do not build)

- Plant pages pulled from Square Catalog/Inventory per venue (via `Venue.square_location_id`).
- QR codes on plant tags → plant page → buy.
- Cart + checkout using Square Web Payments SDK on our own checkout page (Online API rate); Square decrements inventory on paid orders; stock re-checked at checkout.
- Order records in Django with venue attribution for revenue share (15% leased / 10% non-leased).
- Pickup at venue first; local delivery later.

---

## 14. Open items

- Domain name and production URLs
- Brand hex values + logo files
- Hero and venue photography
- FnF notification email address
- Final copy for hero, What We Do, and partner sections
