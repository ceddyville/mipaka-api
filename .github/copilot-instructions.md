# Mipaka API — Copilot Instructions

## Project Overview

**Mipaka API** (_mipaka_ = "boundaries" in Swahili) is an open-source REST API providing normalized administrative divisions across 7 East/Central African countries through a single consistent interface. Built by **Cedric Ongoro** (GitHub: ceddyville), a Kenyan software developer based in Denmark.

- **Stack**: Django 4.2 + Django REST Framework + PostgreSQL + drf-spectacular
- **Repo**: https://github.com/ceddyville/mipaka-api
- **Live URL**: https://mipaka-api.up.railway.app
- **RapidAPI**: https://rapidapi.com/ceddyville/api/mipaka
- **License**: MIT
- **Buy Me a Coffee**: https://buymeacoffee.com/ceddyville

## Countries & Data (103,194 total records)

| Country     | Code | Levels                                                     | Records | Status                       |
| ----------- | ---- | ---------------------------------------------------------- | ------- | ---------------------------- |
| Kenya       | KE   | County → Constituency → Ward                               | 1,787   | Complete                     |
| Tanzania    | TZ   | Region → District                                          | 207     | Partial (no wards in source) |
| Uganda      | UG   | Region → District → County → Sub-county → Parish → Village | 83,012  | Complete                     |
| Rwanda      | RW   | Province → District → Sector → Cell → Village              | 17,441  | Complete                     |
| Burundi     | BI   | Province → Commune → Colline                               | 491     | Complete                     |
| DRC         | CD   | Province → Territory                                       | 174     | Partial                      |
| South Sudan | SS   | State → County → Payam                                     | 82      | Partial                      |

Historical names seeded for ~60 major cities covering pre-colonial, colonial, and post-independence eras.

## Architecture

### Models (divisions/models.py)

- **Country** — code (ISO 2-letter), name, native_name, max_levels, is_active
- **Era** — historical periods per country (precolonial/colonial/independence/current) with colonial_power tracking
- **DivisionLevel** — level definitions per country (e.g. L1="County" in Kenya, L1="Region" in Tanzania)
- **Division** — self-referential parent/child hierarchy, unlimited depth. Fields: name, name_sw, code, native_id, source, latitude, longitude. Indexed on (country,level), (parent), (code)
- **DivisionName** — historical names across eras and languages (e.g. Léopoldville → Kinshasa)

### API Endpoints (divisions/views.py, divisions/urls.py)

- `GET /api/v1/countries/` — all countries with division levels and eras
- `GET /api/v1/countries/{code}/` — country detail
- `GET /api/v1/countries/{code}/top/` — level-1 divisions
- `GET /api/v1/countries/{code}/eras/` — historical eras
- `GET /api/v1/divisions/` — list with filters (country, level, parent, q, name, year, code)
- `GET /api/v1/divisions/{id}/` — detail with ancestors, children, historical names
- `GET /api/v1/divisions/{id}/children/` — direct children
- `GET /api/v1/divisions/{id}/names/` — historical names
- `GET /api/v1/divisions/export/` — bulk CSV export (streaming)
- `GET /api/v1/eras/` — all eras, filterable
- `GET /api/v1/names/` — search historical names
- `GET /api/docs/` — Swagger UI
- `GET /api/redoc/` — ReDoc
- `GET /health/` — health check

### Key Files

- `config/middleware.py` — RapidAPIProxyMiddleware (blocks direct /api/v1/ access when RAPIDAPI_PROXY_SECRET is set) + RequestLoggingMiddleware (logs method, path, status, duration, subscriber)
- `config/settings/base.py` — shared settings, DRF config, cache, CORS, logging
- `config/settings/production.py` — security headers, Redis cache with locmem fallback
- `config/settings/development.py` — DEBUG=True, SQLite fallback
- `config/settings/testing.py` — test settings
- `divisions/throttles.py` — SmartAnonThrottle (skips rate-limiting for RapidAPI-proxied requests, applies 1000/day for direct anonymous traffic)
- `divisions/filters.py` — DivisionFilter and DivisionNameFilter
- `divisions/serializers.py` — Country, Division, DivisionDetail, DivisionBrief, Era, DivisionName serializers
- `converters/` — one-time scripts that transform external data → standardized JSON
- `data/` — pre-built JSON files per country (KE/, TZ/, UG/, RW/, BI/, CD/, SS/)
- `divisions/management/commands/` — sync_kenya, sync_tanzania, sync_uganda, sync_rwanda, sync_burundi, sync_drc, sync_south_sudan, seed_eras
- `marketing/` — blog post draft and RapidAPI listing content

### Deployment

- **Host**: Railway (managed PostgreSQL, gunicorn)
- **Config**: railway.toml + Procfile
- **Start command**: migrate then gunicorn
- **Health check**: /health/ endpoint (30s timeout)
- **RAPIDAPI_PROXY_SECRET**: set in Railway env vars — blocks direct API access
- **Cache**: locmem fallback in production (no Redis addon yet)

## What Has Been Completed

### Core Build (completed)

- All 7 countries loaded with full hierarchies from external data sources
- Historical names (eras + division names) for ~60 major cities
- Kenya historical divisions: 8 provinces (1963), 41 districts (1963), 48 districts (1992)
- OpenAPI docs via drf-spectacular (Swagger + ReDoc)
- Read-only API with explicit AllowAny permissions
- 24-hour cache on list/retrieve endpoints
- CORS enabled

### Monetization & Access Control (completed)

- Listed on RapidAPI marketplace (public, pricing set)
- RapidAPIProxyMiddleware blocks direct Railway URL access
- SmartAnonThrottle skips Django rate-limiting for RapidAPI traffic
- RequestLoggingMiddleware logs all /api/ requests with duration and subscriber

### Features Added (completed)

- Bulk CSV export endpoint: GET /api/v1/divisions/export/?country=KE
- Latitude/longitude fields on Division model (nullable, migration applied, no data populated yet)
- latitude/longitude exposed in API serializers

### Testing (completed)

- 49 tests passing (pytest-django)
- Covers: countries, eras, divisions, historical names, filters, search, pagination, read-only enforcement, CSV export
- Note: if tests fail with `test_children_count` or `test_pagination_structure`, check for stale DJANGO_SETTINGS_MODULE env var — clear it with `Remove-Item Env:DJANGO_SETTINGS_MODULE`

### Marketing (completed)

- README with ASCII logo, badges (RapidAPI, Buy Me a Coffee, MIT, Python, Django, PRs Welcome)
- Blog post draft: marketing/blog-devto-kenya-counties-api.md (ready for dev.to)
- RapidAPI listing content: marketing/rapidapi-listing-content.md
- Support & Contact section in README

## What Remains (TODO)

### Data Enrichment

- [ ] Populate latitude/longitude coordinates (fields exist, no data yet)
- [ ] Expand historical data coverage (only ~60 cities have historical names)
- [ ] Tanzania wards (not available in upstream source)
- [ ] DRC — more territories and disputed province assignments
- [ ] Population data, urban classification

### Infrastructure

- [ ] Add Redis addon on Railway (code already handles fallback)
- [ ] Custom domain (e.g. api.mipaka.dev)

### Marketing

- [ ] Publish dev.to blog post
- [ ] Update RapidAPI listing with long description and tags
- [ ] Social media promotion

### Future Features (see memories/repo/future-ideas.md)

- Boundary polygons (GeoJSON)
- Settlements/Places model
- Cross-border relationships
- Timeline/changelog for admin division changes

## Development Commands

```bash
# Activate venv
.\venv\Scripts\Activate.ps1

# Run with SQLite (dev)
$env:DATABASE_URL="sqlite:///db.sqlite3"
python manage.py migrate
python manage.py sync_kenya
python manage.py seed_eras
python manage.py runserver

# Run tests (make sure DJANGO_SETTINGS_MODULE is NOT set)
Remove-Item Env:DJANGO_SETTINGS_MODULE -ErrorAction SilentlyContinue
$env:DATABASE_URL="sqlite:///db.sqlite3"
python -m pytest divisions/tests.py -v

# Load all countries
python manage.py sync_kenya
python manage.py sync_tanzania
python manage.py sync_uganda
python manage.py sync_rwanda
python manage.py sync_burundi
python manage.py sync_drc
python manage.py sync_south_sudan
python manage.py seed_eras
```

## Known Gotchas

- PowerShell displays UTF-8 characters like é as garbled Ã© — the actual JSON response is correct
- DJANGO_SETTINGS_MODULE env var can get stuck in terminal sessions — always clear before running tests
- Uganda has 83K records, sync takes a while
- Burundi uses legacy 18-province structure (pre-2025) to maintain parent relationships with HDX data
- Uganda source uses `sub_counties.json` (underscore) but parish key is `subcounty` (no underscore)
