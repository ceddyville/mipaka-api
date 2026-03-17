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

*Mipaka* — Swahili for *boundaries*

[![License: MIT](https://img.shields.io/badge/License-MIT-c8622a.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-e8b86d.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.1-c8622a.svg)](https://djangoproject.com)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-e8b86d.svg)](CONTRIBUTING.md)
[![Countries](https://img.shields.io/badge/Countries-7-c8622a.svg)](#coverage)

</div>

---

## What Is Mipaka?

Mipaka is a free, open source REST API providing normalized access to administrative divisions across East and Central Africa — counties, regions, districts, wards, villages — through a **single consistent interface** regardless of country.

Every country has different hierarchy names and depths. Mipaka normalizes them all:

| Country | L1 | L2 | L3 | L4 | L5 | L6 |
|---------|----|----|----|----|----|----|
| 🇰🇪 Kenya | County | Constituency | Ward | — | — | — |
| 🇹🇿 Tanzania | Region | District | Ward | — | — | — |
| 🇺🇬 Uganda | Region | District | County | Sub-county | Parish | Village |
| 🇷🇼 Rwanda | Province | District | Sector | Cell | Village | — |
| 🇧🇮 Burundi | Province | Commune | Colline | — | — | — |
| 🇨🇩 DRC | Province | Territory | — | — | — | — |
| 🇸🇸 South Sudan | State | County | Payam | — | — | — |

### Beyond Boundaries — Historical Names

Mipaka also carries **period-based historical naming** — every division can hold multiple names across eras. Built for genealogy research, where a birth certificate from 1923 saying *"Léopoldville"* needs to resolve to modern *"Kinshasa"* with full historical context.

```bash
# What was Kinshasa called in 1923?
GET /api/v1/divisions/?name=Léopoldville&year=1923

# All colonial-era names for Uganda
GET /api/v1/names/?country=UG&era_type=colonial

# Indigenous pre-colonial names across all countries
GET /api/v1/names/?name_type=indigenous
```

---

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/mipaka-api.git
cd mipaka-api

python -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt

cp .env.example .env   # fill in your DB details
createdb mipaka
python manage.py migrate

python converters/convert_kenya.py --out ./data/KE
python manage.py sync_kenya
python manage.py seed_eras

python manage.py runserver
```

Full setup instructions in **[SETUP.md](SETUP.md)**.

---

## API Reference

Base URL: `http://localhost:8000/api/v1/`

### Core Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /countries/` | All countries with division level labels |
| `GET /countries/{code}/` | Country detail |
| `GET /countries/{code}/top/` | Level-1 divisions (counties, regions…) |
| `GET /countries/{code}/eras/` | Historical eras for a country |
| `GET /divisions/` | List divisions — filterable |
| `GET /divisions/{id}/` | Detail with ancestors + children |
| `GET /divisions/{id}/children/` | Direct children |
| `GET /divisions/{id}/names/` | All historical names |
| `GET /eras/` | All historical eras |
| `GET /names/` | Search historical place names |
| `GET /health/` | Health check |

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

| Country | Status | Levels Available | Records |
|---------|--------|-----------------|---------|
| 🇰🇪 Kenya | ✅ Complete | County → Ward | ~1,800 |
| 🇹🇿 Tanzania | ✅ Complete | Region → Ward | ~4,100 |
| 🇺🇬 Uganda | ✅ Complete | Region → Village | ~65,000 |
| 🇷🇼 Rwanda | ✅ Complete | Province → Village | ~17,500 |
| 🇧🇮 Burundi | ⚠️ Partial | Province + Communes (collines incomplete) | ~160 |
| 🇨🇩 DRC | ⚠️ Partial | Provinces + Territories | ~175 |
| 🇸🇸 South Sudan | ⚠️ Partial | States + Counties | ~82 |

**Historical names seeded for:** ~60 major cities across all 7 countries covering pre-colonial, colonial, and post-independence eras.

---

## Data Sources

| Country | Source | License |
|---------|--------|---------|
| Kenya | [kenyaareadata.vercel.app](https://kenyaareadata.vercel.app) | Public |
| Tanzania | [Kijacode/Tanzania_Geo_Data](https://github.com/Kijacode/Tanzania_Geo_Data) | Open |
| Uganda | [kusaasira/uganda-geo-data](https://github.com/kusaasira/uganda-geo-data) | MIT |
| Rwanda | [jnkindi/rwanda-locations-json](https://github.com/jnkindi/rwanda-locations-json) | Open |
| Burundi | Wikipedia + OCHA HDX | CC-BY |
| DRC | Wikipedia + OCHA COD-AB | Public |
| South Sudan | OCHA COD-AB | Public |
| Historical names | Wikipedia + Encyclopaedia Britannica | CC-BY |

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
├── data/                   # Pre-built JSON files (the mipaka-data dataset)
│   ├── KE/  TZ/  UG/  RW/
│   └── BI/  CD/  SS/
├── config/                 # Django settings
└── SETUP.md                # Full local setup guide
```

---

## Contributing

Mipaka is only as good as its contributors. **If you live in or know a region well, your PR is worth more than any dataset we could scrape.**

The highest-value contributions right now:

- 🇧🇮 **Burundi collines** — 97 communes still need their collines mapped
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

## License

MIT — see [LICENSE](LICENSE)

---

<div align="center">

Built with ❤️ for the African developer community

*"Mipaka ni zaidi ya mistari kwenye ramani."*
*Boundaries are more than lines on a map.*

</div>
