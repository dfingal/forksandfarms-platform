# Forks And Farms — Web Platform

Forks And Farms places curated plants inside St. Louis hospitality venues (coffee shops, wine
bars, restaurants, breweries). Customers buy the plants they see on display; venues partner
via Retail Shelf, Design & Install, or Lease + Maintenance.

This repo is the public web platform: a home page with a map of partner venues, city/venue
pages, and a partner application form.

**Phase I only** — no cart, checkout, Square integration, QR codes, accounts, or dashboards yet.
See [`docs/phase1-spec.md`](docs/phase1-spec.md) for the full spec (pages, data models, API,
build order) and [`docs/wireframes/`](docs/wireframes/) for layout references.

## Stack

| Layer | Choice |
|---|---|
| Frontend | Next.js (App Router, TypeScript), Tailwind CSS → Vercel |
| Backend | Django + Django REST Framework → Render |
| Database | PostgreSQL (Render managed Postgres in production, local Postgres in dev) |
| Images | Cloudinary (required in production — Render's disk isn't persistent) |
| Maps | Google Maps JS API (`@vis.gl/react-google-maps`) |
| Email | Resend |
| Spam protection | Cloudflare Turnstile |

## Repo layout

```
backend/     Django project — API (/api/v1/) + admin
frontend/    Next.js site
docs/        Spec and wireframes
render.yaml  Render Blueprint (backend web service + managed Postgres)
```

## Local development

### Backend

```bash
cd backend
python3.14 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in real values; .env is gitignored
python manage.py migrate
python manage.py seed_demo_data      # St. Louis + 4 current venues, placeholder content
python manage.py createsuperuser
python manage.py runserver           # http://localhost:8000
```

Run the test suite with `python manage.py test`.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local   # fill in real values; .env.local is gitignored
npm run dev                  # http://localhost:3000
```

`npm run build` / `npm run lint` for a production build or lint check. The frontend needs the
backend running (`NEXT_PUBLIC_API_BASE_URL`) to show real data — pages fall back to a friendly
message instead of crashing if the API is unreachable, including at build time.

## Deploying

- **Backend → Render**, via the [`render.yaml`](render.yaml) Blueprint (web service + managed
  Postgres, same region). Secrets are left unset in the blueprint (`sync: false`) — fill them in
  from the Render dashboard after the first deploy.
- **Frontend → Vercel**, root directory `frontend/`.

Both need real environment variables wired up (Cloudinary, Google Maps key + Map ID, Resend,
Turnstile, CORS/CSRF origins for each other's domain) before they're production-ready — see the
comments in `backend/.env.example` and `frontend/.env.example` for what each one does.

## Status

Build order (see spec §11): **1–2, 4–6 built**; step 3 (deploy) has the Render/Vercel
configuration ready but isn't necessarily live yet; step 7 (polish — mobile QA, SEO, sitemap,
analytics, real content/photography) not started. Plenty of `TODO(copy)` placeholders remain for
final brand copy, photography, and the exact brand color palette.

## Contributing / working on this repo

See [`CLAUDE.md`](CLAUDE.md) for the conventions this codebase follows (scope rules, backend/
frontend conventions, brand/copy guidelines) if you're using Claude Code here, or just as a
quick orientation to how the project is organized either way.
