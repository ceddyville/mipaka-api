<div align="center">

```
███╗   ███╗██╗██████╗  █████╗ ██╗  ██╗ █████╗
████╗ ████║██║██╔══██╗██╔══██╗██║ ██╔╝██╔══██╗
██╔████╔██║██║██████╔╝███████║█████╔╝ ███████║
██║╚██╔╝██║██║██╔═══╝ ██╔══██║██╔═██╗ ██╔══██║
██║ ╚═╝ ██║██║██║     ██║  ██║██║  ██╗██║  ██║
╚═╝     ╚═╝╚═╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
```

**Every border. One API.**

_Mipaka_ — Swahili for _boundaries_

[![License: MIT](https://img.shields.io/badge/License-MIT-c8622a.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-e8b86d.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.1-c8622a.svg)](https://djangoproject.com)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-e8b86d.svg)](CONTRIBUTING.md)
[![Countries](https://img.shields.io/badge/Countries-7-c8622a.svg)](#coverage)
[![Live API](https://img.shields.io/badge/Live_API-api.mipaka.dev-e8b86d.svg)](https://api.mipaka.dev/api/v1/)
[![RapidAPI](https://img.shields.io/badge/RapidAPI-Mipaka-c8622a.svg)](https://rapidapi.com/ceddyville/api/mipaka)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy_Me_a_Coffee-ceddyville-e8b86d.svg)](https://buymeacoffee.com/ceddyville)

</div>

---

## What Is Mipaka?

Mipaka is a free, open source REST API providing normalized access to administrative divisions across East and Central Africa — counties, regions, districts, wards, villages — through a **single consistent interface** regardless of country.

Every country has different hierarchy names and depths. Mipaka normalizes them all:

| Country        | L1       | L2           | L3      | L4         | L5      | L6      |
| -------------- | -------- | ------------ | ------- | ---------- | ------- | ------- |
| 🇰🇪 Kenya       | County   | Constituency | Ward    | —          | —       | —       |
| 🇹🇿 Tanzania    | Region   | District     | Ward    | —          | —       | —       |
| 🇺🇬 Uganda      | Region   | District     | County  | Sub-county | Parish  | Village |
| 🇷🇼 Rwanda      | Province | District     | Sector  | Cell       | Village | —       |
| 🇧🇮 Burundi     | Province | Commune      | Colline | —          | —       | —       |
| 🇨🇩 DRC         | Province | Territory    | —       | —          | —       | —       |
| 🇸🇸 South Sudan | State    | County       | Payam   | —          | —       | —       |

### Beyond Boundaries — Historical Names

Mipaka also carries **period-based historical naming** — every division can hold multiple names across eras. Built for genealogy research, where a birth certificate from 1923 saying _"Léopoldville"_ needs to resolve to modern _"Kinshasa"_ with full historical context.

```bash
# What was Kinshasa called in 1923?
GET /api/v1/divisions/?name=Léopoldville&year=1923

# All colonial-era names for Uganda
GET /api/v1/names/?country=UG&era_type=colonial

# Indigenous pre-colonial names across all countries
GET /api/v1/names/?name_type=indigenous
```

---

## Live API

The API is live at **https://api.mipaka.dev** — no setup required.

```bash
# Try it now
curl https://api.mipaka.dev/api/v1/countries/

# Interactive docs
open https://api.mipaka.dev/api/docs/
```

---

## Quick Start

```bash
git clone https://github.com/ceddyville/mipaka-api.git
cd mipaka-api

python -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt

# Option A: SQLite (no extra installs)
export DATABASE_URL=sqlite:///db.sqlite3

# Option B: PostgreSQL
cp .env.example .env   # fill in your DB details
createdb mipaka

python manage.py migrate
python manage.py sync_kenya      # loads pre-built JSON from data/KE/
python manage.py seed_eras        # loads historical names
python manage.py runserver
```

All division data is **pre-built** in the `data/` directory — no need to run converters or pull from external sources.

Full setup instructions in **[SETUP.md](SETUP.md)**.

---

## API Reference

Base URL: `https://api.mipaka.dev/api/v1/`

### Core Endpoints

| Endpoint                        | Description                              |
| ------------------------------- | ---------------------------------------- |
| `GET /countries/`               | All countries with division level labels |
| `GET /countries/{code}/`        | Country detail                           |
| `GET /countries/{code}/top/`    | Level-1 divisions (counties, regions…)   |
| `GET /countries/{code}/eras/`   | Historical eras for a country            |
| `GET /divisions/`               | List divisions — filterable              |
| `GET /divisions/{id}/`          | Detail with ancestors + children         |
| `GET /divisions/{id}/children/` | Direct children                          |
| `GET /divisions/{id}/names/`    | All historical names                     |
| `GET /eras/`                    | All historical eras                      |
| `GET /names/`                   | Search historical place names            |
| `GET /health/`                  | Health check                             |
| `GET /api/docs/`                | Interactive Swagger UI                   |
| `GET /api/redoc/`               | ReDoc API documentation                  |

### Filter Parameters

```bash
# Geography filters
GET /divisions/?country=KE&level=1          # Kenya counties
GET /divisions/?country=TZ&level=2          # Tanzania districts
GET /divisions/?parent=42                   # Children of division #42
GET /divisions/?q=nairobi                   # Name search

# Historical name filters
GET /divisions/?name=Stanleyville           # Find by historical name
GET /divisions/?year=1905&country=CD        # DRC as it was in 1905
GET /names/?era_type=colonial               # All colonial-era names
GET /names/?language=Luganda                # Names in Luganda
GET /names/?name_type=indigenous            # Pre-colonial names only
GET /eras/?colonial_power=belgian           # Belgian-administered eras
```

### Example Response

```json
GET /api/v1/divisions/?country=KE&level=1&q=nairobi

[
  {
    "id": 7,
    "country_code": "KE",
    "level": 1,
    "level_name": "County",
    "name": "Nairobi",
    "parent": null,
    "children_count": 17,
    "source": "kenyaareadata.vercel.app"
  }
]
```

```json
GET /api/v1/divisions/42/names/

[
  {
    "name": "Kasozi k'Empala",
    "language": "Luganda",
    "name_type": "indigenous",
    "era_name": "Buganda Kingdom",
    "era_type": "precolonial",
    "era_started": "~1300",
    "era_ended": "1894",
    "etymology": "Hill of impala — Buganda royal seat from 1880s"
  },
  {
    "name": "Kampala",
    "language": "English",
    "name_type": "colonial",
    "era_name": "Uganda Protectorate",
    "era_type": "colonial",
    "era_started": "1894",
    "era_ended": "1962",
    "etymology": "British fort established 1890 on Old Kampala Hill"
  }
]
```

---

## Coverage

<a name="coverage"></a>

| Country        | Status      | Levels Available        | Records |
| -------------- | ----------- | ----------------------- | ------- |
| 🇰🇪 Kenya       | ✅ Complete | County → Ward           | 1,954   |
| 🇹🇿 Tanzania    | ⚠️ Partial  | Region → District       | 213     |
| 🇺🇬 Uganda      | ✅ Complete | Region → Village        | 83,017  |
| 🇷🇼 Rwanda      | ✅ Complete | Province → Village      | 17,453  |
| 🇧🇮 Burundi     | ✅ Complete | Province → Colline      | 491     |
| 🇨🇩 DRC         | ⚠️ Partial  | Provinces + Territories | 185     |
| 🇸🇸 South Sudan | ⚠️ Partial  | States + Counties       | 110     |

> **Kenya historical divisions:** 8 provinces, 41 districts (1963), 48 districts (1992), and 70 districts (2007) are also included for historical research.

> **Historical divisions across all countries:** Rwanda pre-2006 prefectures (12), DRC 1997–2015 provinces (11), South Sudan 2015–2020 states (28), Tanzania new regions (6), Uganda traditional kingdoms (5) — 229 total historical records.

> **Tanzania note:** Ward-level data is not available in the upstream source; only regions and districts are included.

> **Burundi note:** Uses the legacy 18-province administrative structure (pre-2025) to maintain parent relationships with commune/colline data from OCHA HDX.

**Historical names seeded for:** ~60 major cities across all 7 countries covering pre-colonial, colonial, and post-independence eras.

---

## Data Sources

| Country          | Source                                                                            | License |
| ---------------- | --------------------------------------------------------------------------------- | ------- |
| Kenya            | [kenyaareadata.vercel.app](https://kenyaareadata.vercel.app)                      | Public  |
| Tanzania         | [Kijacode/Tanzania_Geo_Data](https://github.com/Kijacode/Tanzania_Geo_Data)       | Open    |
| Uganda           | [kusaasira/uganda-geo-data](https://github.com/kusaasira/uganda-geo-data)         | MIT     |
| Rwanda           | [jnkindi/rwanda-locations-json](https://github.com/jnkindi/rwanda-locations-json) | Open    |
| Burundi          | Wikipedia + OCHA HDX                                                              | CC-BY   |
| DRC              | Wikipedia + OCHA COD-AB                                                           | Public  |
| South Sudan      | OCHA COD-AB                                                                       | Public  |
| Historical names | Wikipedia + Encyclopaedia Britannica                                              | CC-BY   |

---

## Project Structure

```
mipaka-api/
├── divisions/              # Core Django app
│   ├── models.py           # Country, Era, Division, DivisionName
│   ├── views.py            # API viewsets
│   ├── serializers.py
│   └── management/commands/
│       ├── sync_*.py       # One per country
│       └── seed_eras.py    # Historical names
├── converters/             # One-time data conversion scripts
├── data/                   # Pre-built JSON — all division data lives here
│   ├── KE/                 # counties, constituencies, wards + historical provinces/districts
│   ├── TZ/  UG/  RW/      # + historical regions, kingdoms, prefectures
│   └── BI/  CD/  SS/      # + historical provinces, states
├── config/                 # Django settings
└── SETUP.md                # Full local setup guide
```

---

## Contributing

Mipaka is only as good as its contributors. **If you live in or know a region well, your PR is worth more than any dataset we could scrape.**

The highest-value contributions right now:

- �🇿 **Tanzania wards** — ward-level data not available in upstream source
- 🇨🇩 **DRC territories** — 5 entries with disputed province assignments
- 🇸🇸 **South Sudan payams** — 512 payams not yet in the dataset
- 🌍 **Indigenous place names** — pre-colonial names in local languages for any city

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for how to submit data corrections and additions.

---

## Running Tests

```bash
pytest
```

---

## Support & Contact

- **Bug reports & feature requests:** [GitHub Issues](https://github.com/ceddyville/mipaka-api/issues)
- **Data corrections:** See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Buy Me a Coffee:** [buymeacoffee.com/ceddyville](https://buymeacoffee.com/ceddyville)
- **RapidAPI:** [rapidapi.com/ceddyville/api/mipaka](https://rapidapi.com/ceddyville/api/mipaka)

---

## License

MIT — see [LICENSE](LICENSE)

---

<div align="center">

Built with ❤️ for the African developer community

_"Mipaka ni zaidi ya mistari kwenye ramani."_
_Boundaries are more than lines on a map._

</div>
