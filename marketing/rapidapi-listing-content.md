# RapidAPI Listing Content

Copy-paste these into your RapidAPI Studio dashboard under API → Documentation.

---

## Short Description (150 chars)

Administrative divisions for 7 East African countries — counties, districts, wards, villages — with parent-child hierarchies and historical names.

---

## Long Description (paste into RapidAPI "About" section)

### Mipaka API — Every Border. One API.

Access **103,194 administrative divisions** across 7 East African countries through a single, consistent REST API. No more hardcoding location arrays.

#### Supported Countries

| Country     | Levels                                                     | Records |
| ----------- | ---------------------------------------------------------- | ------- |
| Kenya       | County → Constituency → Ward                               | 1,787   |
| Tanzania    | Region → District                                          | 207     |
| Uganda      | Region → District → County → Sub-county → Parish → Village | 83,012  |
| Rwanda      | Province → District → Sector → Cell → Village              | 17,441  |
| Burundi     | Province → Commune → Colline                               | 491     |
| DRC         | Province → Territory                                       | 174     |
| South Sudan | State → County → Payam                                     | 82      |

#### Key Features

- **Full Hierarchies** — Parent-child relationships at every level. Build cascading dropdowns in minutes.
- **Smart Filtering** — Filter by country, level, parent, name, and code. Combine filters freely.
- **Text Search** — Search division names across all countries with `?q=nairobi`.
- **Historical Names** — ~60 major cities with pre-colonial, colonial, and post-independence names. Query by year: `?year=1923`.
- **Bulk CSV Export** — Download entire countries as CSV: `/divisions/export/?country=KE`
- **Pagination** — Default 100 per page, customizable.

#### Common Use Cases

- **Form Location Pickers** — Cascading country → county → ward dropdowns
- **Address Validation** — Verify user-submitted locations against official divisions
- **KYC / Onboarding** — Standardize location data for fintech and insurance
- **Delivery Zones** — Map coverage areas to administrative boundaries
- **Research & Analytics** — Track data by administrative region
- **Genealogy** — Resolve historical place names to modern divisions

#### Quick Start

```bash
# List all countries
GET /api/v1/countries/

# Kenya's 47 counties
GET /api/v1/countries/KE/top/

# Constituencies in Nairobi (id=7)
GET /api/v1/divisions/7/children/

# Search for "kampala" across all countries
GET /api/v1/divisions/?q=kampala

# Uganda districts
GET /api/v1/divisions/?country=UG&level=2

# Historical names for colonial era
GET /api/v1/names/?era_type=colonial
```

#### Data Quality

- Sourced from government datasets, OCHA humanitarian data, and verified community repositories
- Regularly maintained and open source: https://github.com/ceddyville/mipaka-api
- Swahili names included where available

---

## RapidAPI Tags (add all of these)

Africa, Kenya, Uganda, Tanzania, Rwanda, Burundi, DRC, South Sudan, Geography, Administrative Divisions, Location, Counties, Districts, Regions, Wards, Address, GeoData, Mapping, REST API

---

## Category

Data > Location

---

## API Thumbnail / Description for Social

"Mipaka API: 103,000+ administrative divisions across 7 East African countries. Build location dropdowns, validate addresses, and explore historical place names through one REST API."
