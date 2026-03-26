# Mipaka API — Copilot Instructions

## Project Overview

**Mipaka API** (_mipaka_ = "boundaries" in Swahili) is an open-source REST API providing normalized administrative divisions across 7 East/Central African countries through a single consistent interface. Built by **Cedric Ongoro** (GitHub: ceddyville), a Kenyan software developer based in Denmark.

- **Stack**: Django 4.2 + Django REST Framework + PostgreSQL + drf-spectacular
- **Repo**: https://github.com/ceddyville/mipaka-api
- **Live URL**: https://api.mipaka.dev (Railway: https://mipaka-api.up.railway.app)
- **RapidAPI**: https://rapidapi.com/ceddyville/api/mipaka
- **License**: MIT
- **Buy Me a Coffee**: https://buymeacoffee.com/ceddyville

## Countries & Data (~103,400 total records)

| Country     | Code | Levels                                                     | Records | Status                       |
| ----------- | ---- | ---------------------------------------------------------- | ------- | ---------------------------- |
| Kenya       | KE   | County → Constituency → Ward                               | 1,954   | Complete                     |
| Tanzania    | TZ   | Region → District                                          | 213     | Partial (no wards in source) |
| Uganda      | UG   | Region → District → County → Sub-county → Parish → Village | 83,017  | Complete                     |
| Rwanda      | RW   | Province → District → Sector → Cell → Village              | 17,453  | Complete                     |
| Burundi     | BI   | Province → Commune → Colline                               | 491     | Complete                     |
| DRC         | CD   | Province → Territory                                       | 185     | Partial                      |
| South Sudan | SS   | State → County → Payam                                     | 110     | Partial                      |

Historical names seeded for ~60 major cities covering pre-colonial, colonial, and post-independence eras.

### Historical Divisions (across all countries, level 100/101, is_active=False)

| Country     | Data                              | Records | Source    |
| ----------- | --------------------------------- | ------- | --------- |
| Kenya       | Provinces (8) + Districts (159)   | 167     | Wikipedia |
| Rwanda      | Prefectures pre-2006 (12)         | 12      | Wikipedia |
| DRC         | Provinces 1997–2015 (11)          | 11      | Wikipedia |
| South Sudan | States 2015–2020 (28)             | 28      | Wikipedia |
| Tanzania    | New regions 2002–2016 (6)         | 6       | Wikipedia |
| Uganda      | Traditional kingdoms (5)          | 5       | Wikipedia |

## Architecture

### Models (divisions/models.py)

- **Country** — code (ISO 2-letter), name, native_name, max_levels, is_active
- **Era** — historical periods per country (precolonial/colonial/independence/current) with colonial_power tracking
- **DivisionLevel** — level definitions per country (e.g. L1="County" in Kenya, L1="Region" in Tanzania)
- **Division** — self-referential parent/child hierarchy, unlimited depth. Fields: name, name_sw, code, native_id, source, description, latitude, longitude, is_active. Indexed on (country,level), (parent), (code). Historical divisions use level 100/101 with is_active=False
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
- **Start command**: collectstatic → migrate → gunicorn
- **Health check**: /health/ endpoint exists but Railway healthcheck disabled (networking probe issue); restartPolicyType=ON_FAILURE handles crashes
- **Custom domain**: api.mipaka.dev (CNAME → 5nb3riuk.up.railway.app, verified with TXT record _railway-verify.api)
- **Landing page**: mipaka.dev (separate repo: mipaka-site, static HTML, planned for GitHub Pages)
- **RAPIDAPI_PROXY_SECRET**: set in Railway env vars — blocks direct /api/v1/ access
- **Railway env vars**: ALLOWED_HOSTS, DATABASE_URL, DEBUG, DJANGO_SETTINGS_MODULE, RAPIDAPI_PROXY_SECRET, REDIS_URL, SECRET_KEY, PORT (8080)
- **Cache**: locmem fallback in production (no Redis addon yet)
- **Domain registrar**: simply.com (mipaka.dev, "Only domains" plan)
- **DNS records**: CNAME api → 5nb3riuk.up.railway.app, TXT _railway-verify.api → railway verification token

## What Has Been Completed

### Core Build (completed)

- All 7 countries loaded with full hierarchies from external data sources
- Historical names (eras + division names) for ~60 major cities
- Historical divisions for all 7 countries:
  - Kenya: 8 provinces + 159 districts (1963/1992/2007 eras)
  - Rwanda: 12 prefectures (pre-2006)
  - DRC: 11 provinces (1997–2015 structure)
  - South Sudan: 28 states (2015–2020 decree)
  - Tanzania: 6 new regions (2002–2016 splits)
  - Uganda: 5 traditional kingdoms (abolished 1967, restored 1993)
  - Burundi: legacy 18-province structure (via --legacy flag)
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
- Description field on Division model (used for historical context/notes)
- description exposed in DivisionSerializer
- Browsable API renderer enabled (BrowsableAPIRenderer + JSONRenderer) — shows formatted HTML view in browser
- collectstatic added to Railway start command (fixes WhiteNoise staticfiles directory warning)

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
- [x] Historical divisions for all countries (completed — 229 records across 7 countries)

### Infrastructure

- [ ] Add Redis addon on Railway (code already handles fallback)
- [x] Custom domain — api.mipaka.dev live and verified on Railway
- [x] DNS setup — CNAME + TXT verification record added on simply.com
- [ ] Investigate Railway healthcheck probe failure (app works but probe returns "service unavailable" during deploy)
- [ ] Set up GitHub Pages for mipaka-site landing page (repo not yet created)
- [ ] Cloudflare email routing for hello@mipaka.dev

### Landing Page (mipaka-site)

- [x] Static site created at ../mipaka-site/ (single index.html + CNAME)
- [x] Interactive explorer: country pills → cascading dropdowns → result cards → breadcrumbs → JSON toggle
- [ ] Create mipaka-site GitHub repo and push
- [ ] Enable GitHub Pages, add A records for mipaka.dev root domain
- [ ] Deploy landing page to mipaka.dev

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

# Load historical divisions (run after current data is synced)
python manage.py sync_kenya --levels provinces districts_1963 districts_1992 districts_2007
python manage.py sync_rwanda --levels prefectures_2006
python manage.py sync_drc --levels provinces_1997
python manage.py sync_south_sudan --levels states_2015
python manage.py sync_tanzania --levels regions_historical
python manage.py sync_uganda --levels kingdoms
```

## Known Gotchas

- PowerShell displays UTF-8 characters like é as garbled Ã© — the actual JSON response is correct
- DJANGO_SETTINGS_MODULE env var can get stuck in terminal sessions — always clear before running tests
- Uganda has 83K records, sync takes a while
- Burundi uses legacy 18-province structure (pre-2025) to maintain parent relationships with HDX data
- Uganda source uses `sub_counties.json` (underscore) but parish key is `subcounty` (no underscore)
- Railway healthcheck probe fails with "service unavailable" even though gunicorn starts fine — removed healthcheckPath from railway.toml; restartPolicyType=ON_FAILURE handles crashes instead
- collectstatic must run before gunicorn in the start command (WhiteNoise needs /app/staticfiles/ to exist)
- api.mipaka.dev required both CNAME and TXT (_railway-verify.api) DNS records for Railway domain verification
- Local dev requires `$env:DATABASE_URL="sqlite:///db.sqlite3"` since PostgreSQL isn't running locally
- Landing page explorer fetches from api.mipaka.dev — RapidAPIProxyMiddleware blocks /api/v1/ on production; landing page needs middleware bypass or RapidAPI proxy headers to work
