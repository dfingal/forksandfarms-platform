# CLAUDE.md — Forks And Farms Platform

## What this project is
Forks And Farms (FnF) is a St. Louis business that places curated plants inside hospitality venues (coffee shops, wine bars, restaurants, breweries). Customers buy the plants they see. Venues partner via Retail Shelf, Design & Install, or Lease + Maintenance.

This repo is the FnF web platform. We are building **Phase I**: a public site with a home page + map of partner venues, city and venue pages, and a partner application form.

**Read `docs/phase1-spec.md` before starting any task.** It is the source of truth for pages, routes, data models, API endpoints, and build order. Wireframes are in `docs/wireframes/`.

## Golden rules
1. **Phase I scope only.** Do not build cart, checkout, Square integration, QR codes, accounts, or dashboards. But never make choices that block them (see "Phase II hooks" in the spec).
2. **Plan before code.** For any non-trivial task, propose a short plan (files to create/change, approach) and wait for approval before writing code.
3. **One chunk at a time.** Work on the step requested; don't jump ahead in the build order.
4. **Keep it simple.** Prefer boring, well-documented solutions over clever ones. The owner is not a full-time developer — code should be readable and commented where intent isn't obvious.
5. **Never commit secrets.** Real values live in `backend/.env` and `frontend/.env.local` (gitignored). When adding a new env var, add it to the matching `.env.example` with a placeholder and a comment.
6. **Explain how to run/verify.** At the end of each task, tell the owner exactly which commands to run and what to look at to confirm it works.

## Stack
- **Frontend:** Next.js (App Router, TypeScript), Tailwind CSS — in `frontend/`, deployed to Vercel
- **Backend:** Django + Django REST Framework — in `backend/`, deployed to Render
- **Database:** PostgreSQL (Render managed Postgres in production, local Postgres in dev)
- **Images:** Cloudinary · **Maps:** Google Maps JS API · **Email:** Resend · **Spam:** Cloudflare Turnstile
- **Phase II (not now):** Square APIs for catalog, inventory, and payments

## Repo layout
```
backend/     Django project (API + admin)
frontend/    Next.js site
docs/        Spec and wireframes
```

## Backend conventions (Django)
- Python 3.14. Create the venv with `python3.14 -m venv .venv` inside `backend/`. The owner's default `python`/`python3` is an old 3.8 (Anaconda) — never use it.
- Dependencies pinned in `backend/requirements.txt`
- Config via environment variables (use `django-environ` or similar); one settings module that reads env vars, `DEBUG` from env
- App structure: a `core` app (City, Venue, VenuePhoto) and a `partners` app (PartnerApplication) unless a plan proposes better
- API under `/api/v1/`, DRF serializers + viewsets/generic views, JSON only
- Public endpoints only return venues with status `active`, `seasonal`, `coming_soon`; never expose `partner_tier`, `square_location_id`, or application data publicly
- Django admin is the back office — make it pleasant (list displays, filters, search, inlines)
- Include migrations; provide a management command or fixture to seed St. Louis + the 4 current venues with placeholder content
- Tests with Django's test runner or pytest for models, API permissions/filters, and the application POST

## Frontend conventions (Next.js)
- TypeScript, App Router, server components by default; client components only where needed (map, form)
- Tailwind with brand colors defined once as theme tokens: `forest` (green), `cream`, `terracotta` — placeholder hex values until the final palette is provided
- Data fetched from the Django API via a small typed client in `frontend/lib/api.ts`
- Pages statically generated with revalidation; on-demand revalidation endpoint at `/api/revalidate` protected by `REVALIDATE_SECRET`
- Mobile-first; check layouts at 375px and 1200px
- Accessibility: alt text, labels on every form field, keyboard-usable controls, visible focus
- Routes: `/`, `/locations`, `/locations/[city]`, `/locations/[city]/[venue]`, `/partner`, `/partner/thanks`

## Commands (update as the project is set up)
```
# Backend
cd backend && source .venv/bin/activate
python manage.py runserver          # http://localhost:8000
python manage.py migrate
python manage.py test

# Frontend
cd frontend
npm run dev                         # http://localhost:3000
npm run build
npm run lint
```

## Git
- Small, focused commits with clear messages (e.g. "Add Venue model and admin")
- Don't push or force-push unless asked
- Before committing, confirm no `.env` files are staged

## Brand & copy
- Brand name is always written "Forks And Farms" (capital A); "FnF" only in code/internal notes
- Tone: warm, local, simple, a little playful — not corporate
- Use placeholder copy marked `TODO(copy)` where final text isn't provided
