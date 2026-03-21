---
title: I Built a Free REST API for Kenya's 47 Counties, 290 Constituencies, and 1,450 Wards
published: false
description: Mipaka API — a free REST API for administrative divisions across 7 East African countries. No more hardcoding county arrays.
tags: api, python, django, africa
cover_image:
---

## The Problem Every African Developer Knows

You're building a form. It has a location dropdown. You need Kenya's 47 counties, then the constituencies under each county, then the wards.

So you do what we all do:

```javascript
const counties = ["Baringo", "Bomet", "Bungoma", "Busia" /* ...43 more */];
```

Then the client asks: "Can you add Uganda too?" And Tanzania. And Rwanda. Each country has completely different administrative structures — counties vs regions vs provinces, wards vs sub-counties vs cells.

You end up with a mess of hardcoded arrays, outdated data, and no parent-child relationships.

I built **Mipaka API** to solve this.

---

## What Is Mipaka?

[Mipaka](https://rapidapi.com/ceddyville/api/mipaka) (_Swahili for "boundaries"_) is a free REST API that gives you normalized access to administrative divisions across 7 East African countries — through a single consistent interface.

**103,194 divisions** across **7 countries** with full parent-child hierarchies:

| Country        | Levels                                                     | Records |
| -------------- | ---------------------------------------------------------- | ------- |
| 🇰🇪 Kenya       | County → Constituency → Ward                               | 1,787   |
| 🇹🇿 Tanzania    | Region → District                                          | 207     |
| 🇺🇬 Uganda      | Region → District → County → Sub-county → Parish → Village | 83,012  |
| 🇷🇼 Rwanda      | Province → District → Sector → Cell → Village              | 17,441  |
| 🇧🇮 Burundi     | Province → Commune → Colline                               | 491     |
| 🇨🇩 DRC         | Province → Territory                                       | 174     |
| 🇸🇸 South Sudan | State → County → Payam                                     | 82      |

---

## Quick Demo: Kenya Counties in 3 Lines

### JavaScript

```javascript
const res = await fetch(
  "https://rapidapi.com/proxy/mipaka/api/v1/countries/KE/top/",
  {
    headers: { "X-RapidAPI-Key": "YOUR_KEY" },
  },
);
const counties = await res.json();
console.log(counties);
// [{ name: "Baringo", level: 1, level_name: "County", children_count: 6 }, ...]
```

### Python

```python
import requests

url = "https://mipaka.p.rapidapi.com/api/v1/countries/KE/top/"
headers = {"X-RapidAPI-Key": "YOUR_KEY"}

counties = requests.get(url, headers=headers).json()
for c in counties:
    print(f"{c['name']} — {c['children_count']} constituencies")
```

**Output:**

```
Baringo — 6 constituencies
Bomet — 5 constituencies
Bungoma — 9 constituencies
Busia — 7 constituencies
...
Nairobi — 17 constituencies
```

---

## Building Cascading Dropdowns

The most common use case — a location picker that cascades from country → level 1 → level 2 → etc.

```javascript
// Step 1: Get all countries
const countries = await mipaka("/countries/");
// [{ code: "KE", name: "Kenya" }, { code: "UG", name: "Uganda" }, ...]

// Step 2: User picks Kenya → get counties
const counties = await mipaka("/countries/KE/top/");
// [{ id: 1, name: "Baringo" }, { id: 2, name: "Bomet" }, ...]

// Step 3: User picks Nairobi (id=7) → get constituencies
const constituencies = await mipaka("/divisions/7/children/");
// [{ id: 48, name: "Dagoretti North" }, { id: 49, name: "Dagoretti South" }, ...]

// Step 4: User picks Dagoretti North → get wards
const wards = await mipaka("/divisions/48/children/");
// [{ name: "Gatina" }, { name: "Kileleshwa" }, { name: "Kilimani" }, ...]
```

One API. One interface. Works the same for all 7 countries. No more maintaining separate county/district/province arrays.

---

## Filtering & Search

The API supports rich filtering out of the box:

```bash
# All Kenyan counties
GET /api/v1/divisions/?country=KE&level=1

# Search by name across all countries
GET /api/v1/divisions/?q=kampala

# Children of a specific division
GET /api/v1/divisions/?parent=42

# Combine filters
GET /api/v1/divisions/?country=UG&level=3&q=buganda
```

---

## The Bonus Feature: Historical Names

This is my favorite part. Every division can have multiple names across historical eras.

**Example:** What was Kinshasa called in 1923?

```bash
GET /api/v1/divisions/?name=Léopoldville&year=1923
```

The API carries ~60 major cities with pre-colonial, colonial, and post-independence names. Perfect for:

- **Genealogy research** — birth certificates from colonial-era cities
- **Historical data mapping** — connecting old datasets to modern divisions
- **Education** — exploring how borders and names evolved

```json
// GET /api/v1/divisions/{kampala_id}/names/
[
  {
    "name": "Kasozi k'Empala",
    "language": "Luganda",
    "name_type": "indigenous",
    "era_name": "Buganda Kingdom",
    "era_type": "precolonial",
    "era_started": "~1300",
    "etymology": "Hill of impala — Buganda royal seat"
  },
  {
    "name": "Kampala",
    "era_name": "Uganda Protectorate",
    "era_type": "colonial",
    "era_started": "1894",
    "era_ended": "1962"
  }
]
```

---

## Bulk Export

Need all the data at once? The CSV export endpoint streams the entire dataset:

```bash
GET /api/v1/divisions/export/?country=KE
# Downloads: mipaka_divisions.csv
```

Great for data analysis, offline use, or loading into your own database.

---

## Try It Free

Mipaka is available on [RapidAPI](https://rapidapi.com/ceddyville/api/mipaka) with a generous free tier.

The code is also [open source on GitHub](https://github.com/ceddyville/mipaka-api) under the MIT license — contributions welcome, especially for countries with partial data (Tanzania wards, DRC territories).

### Links

- **API on RapidAPI:** [rapidapi.com/ceddyville/api/mipaka](https://rapidapi.com/ceddyville/api/mipaka)
- **GitHub:** [github.com/ceddyville/mipaka-api](https://github.com/ceddyville/mipaka-api)
- **Interactive Docs:** [mipaka-api.up.railway.app/api/docs/](https://mipaka-api.up.railway.app/api/docs/)

---

## Tech Stack

For those curious about the internals:

- **Django 4.2 + Django REST Framework** — handles serialization, filtering, pagination, OpenAPI docs
- **PostgreSQL** on Railway — 103K records with proper indexes
- **drf-spectacular** — auto-generated Swagger/ReDoc documentation
- **7 management commands** — one per country, idempotent syncs from pre-built JSON data

---

If you're building anything that needs East African location data — forms, KYC flows, delivery zones, research dashboards — give Mipaka a try. And if you have data for regions I haven't covered yet, [PRs are welcome](https://github.com/ceddyville/mipaka-api/blob/main/CONTRIBUTING.md).

_Mipaka — every border, one API._
