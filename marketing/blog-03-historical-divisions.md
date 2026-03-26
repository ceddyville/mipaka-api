---
title: "From Léopoldville to Kinshasa: How Our API Tracks 500 Years of African Border Changes"
published: false
description: "Mipaka API now carries 47 historical eras, 124 colonial and pre-colonial place names, and administrative divisions from the Congo Free State to modern-day DRC — all queryable via REST."
tags: api, history, africa, opensource
cover_image:
canonical_url:
series: Mipaka API — Every Border, One API
---

## Africa's Borders Have Stories

Every city in East and Central Africa carries layers of names. Kinshasa was Léopoldville. Kisangani was Stanleyville. Lubumbashi was Élisabethville. Before all of those, they had indigenous names in Kikongo, Kiluba, and Lokele.

These aren't just trivia — they're essential for anyone working with historical records, genealogy data, colonial-era documents, or research datasets that reference places by names that no longer exist on any map.

I built [Mipaka API](https://rapidapi.com/ceddyville/api/mipaka) to solve the modern problem of location dropdowns. But it's become something more: **a timeline of how African administrative boundaries evolved through pre-colonial kingdoms, colonial occupation, and independence.**

---

## 47 Eras Across 7 Countries

Every country in Mipaka has a chain of historical eras — each with a name, date range, type (pre-colonial, colonial, independence, current), and notes:

```bash
GET /api/v1/countries/CD/eras/
```

```json
[
  {
    "name": "Kingdom of Kongo",
    "era_type": "precolonial",
    "started": "~1390",
    "ended": "1914",
    "notes": "Central African kingdom in western Congo basin..."
  },
  {
    "name": "Congo Free State",
    "era_type": "colonial",
    "colonial_power": "belgian",
    "started": "1885",
    "ended": "1908",
    "notes": "Personal property of King Leopold II..."
  },
  {
    "name": "Belgian Congo",
    "era_type": "colonial",
    "started": "1908",
    "ended": "1960"
  },
  {
    "name": "Republic of the Congo (Léopoldville)",
    "era_type": "independence",
    "started": "1960",
    "ended": "1964"
  },
  // ... Republic of Zaire (1971-1997) ...
  {
    "name": "Democratic Republic of the Congo",
    "era_type": "current",
    "started": "1997"
  }
]
```

The DRC alone has **11 eras** — from five pre-colonial kingdoms (Kongo, Luba, Lunda, Kuba, Azande) through the Congo Free State, Belgian Congo, and three name changes after independence.

---

## Historical Place Names

Every major city can be queried for its names across eras:

```bash
GET /api/v1/divisions/{kinshasa_id}/names/
```

```json
[
  {
    "name": "Nshasa",
    "language": "Kikongo",
    "name_type": "indigenous",
    "era": "Kingdom of Kongo",
    "etymology": "Original Teke fishing village on the Congo River"
  },
  {
    "name": "Léopoldville",
    "language": "French",
    "name_type": "colonial",
    "era": "Congo Free State",
    "etymology": "Stanley's trading post, 1881"
  },
  {
    "name": "Léopoldville",
    "language": "French",
    "name_type": "colonial",
    "era": "Belgian Congo"
  }
]
```

### Some Favorites from the Dataset

| Modern Name   | Colonial Name  | Pre-Colonial                            | Country     |
| ------------- | -------------- | --------------------------------------- | ----------- |
| Kinshasa      | Léopoldville   | Nshasa (Kikongo)                        | 🇨🇩 DRC      |
| Kisangani     | Stanleyville   | Boyoma (Lokele)                         | 🇨🇩 DRC      |
| Lubumbashi    | Élisabethville | — (Luba territory)                      | 🇨🇩 DRC      |
| Kampala       | Kampala        | Kasozi k'Empala (Luganda)               | 🇺🇬 Uganda   |
| Jinja         | Ripon Falls    | Jinja — "stone" (Lusoga)                | 🇺🇬 Uganda   |
| Nairobi       | Nairobi        | Enkare Nyorobi — "cool waters" (Maasai) | 🇰🇪 Kenya    |
| Mombasa       | Mombasa        | Mvita — "island of war" (Swahili)       | 🇰🇪 Kenya    |
| Dar es Salaam | Dar es Salaam  | Mzizima — "healthy town" (Swahili)      | 🇹🇿 Tanzania |
| Kigali        | Kigali         | Kigali — "hill of many" (Kinyarwanda)   | 🇷🇼 Rwanda   |
| Butare        | Astrida        | Butare (Kinyarwanda)                    | 🇷🇼 Rwanda   |
| Bujumbura     | Usumbura       | Bujumbura (Kirundi)                     | 🇧🇮 Burundi  |

---

## Congo's Six Administrative Eras

The DRC is the most dramatic example. The country's internal borders were redrawn with almost every regime change:

**1910 — Congo Free State:** 12 districts under Leopold's rubber terror

```bash
GET /api/v1/divisions/?country=CD&level=101&q=district
```

**1933 — Belgian Congo:** Reorganized into 6 provinces and 16 districts

```bash
GET /api/v1/divisions/?country=CD&level=100
# Returns provinces from each historical era
```

**1966 — Post-Independence:** 9 provinces (Léopoldville renamed Kinshasa)

**1988 — Zaire:** 11 regions under Mobutu (Shaba, Bas-Zaïre, Haut-Zaïre...)

**1997 — DRC Restored:** 11 provinces reverted to pre-Mobutu names

**2015 — Current:** Split into 26 provinces (today's structure)

All of these are queryable. You can trace how Katanga became Shaba, then went back to being split into Haut-Katanga, Lualaba, Haut-Lomami, and Tanganyika.

---

## Uganda's Five Kingdoms

Uganda's pre-colonial history is dominated by five kingdoms that were abolished in 1967 and (mostly) restored in the 1990s as cultural institutions:

```bash
GET /api/v1/divisions/?country=UG&level=100
```

```json
[
  {
    "name": "Buganda",
    "description": "Largest and most influential kingdom; 52 clans under the Kabaka. Capital at Mengo (Kampala). Abolished 1967, restored 1993. Current ruler: Kabaka Ronald Muwenda Mutebi II"
  },
  {
    "name": "Bunyoro-Kitara",
    "description": "One of the oldest kingdoms in East Africa, traces origins to the Bachwezi dynasty. Capital at Hoima. Abolished 1967, restored 1993."
  },
  {
    "name": "Toro",
    "description": "Founded c. 1830 when Prince Kaboyo broke away from Bunyoro. King Oyo crowned at age 3 in 1995."
  },
  {
    "name": "Ankole",
    "description": "NOT officially restored due to Bairu vs Bahima disagreements."
  },
  {
    "name": "Busoga",
    "description": "Confederation of chieftainships. Kyabazinga title rotates among clan chiefs."
  }
]
```

Each kingdom is stored as a historical division (level 100) with `is_active=false`, complete with descriptions about their founding, abolition, and current status.

---

## Who Uses Historical Border Data?

This isn't just an academic exercise. Real use cases:

1. **Genealogy platforms** — Birth certificates from "Élisabethville" need to map to modern Lubumbashi
2. **Historical research** — Datasets from the 1950s reference Belgian Congo districts that don't exist anymore
3. **Government modernization** — Kenya's 2010 constitution replaced 8 provinces with 47 counties; old records still reference the provinces
4. **Education** — Interactive tools showing how borders evolved
5. **Journalism** — Contextualizing place references in historical documents

---

## The Numbers

|                            | Count                             |
| -------------------------- | --------------------------------- |
| Countries                  | 7                                 |
| Total divisions            | 88,000+                           |
| Historical eras            | 47                                |
| Historical place names     | 124                               |
| DRC historical divisions   | 117 across 6 eras                 |
| Kenya historical divisions | 167 (8 provinces + 159 districts) |
| Uganda kingdoms            | 5                                 |

---

## Try It

- **RapidAPI:** [rapidapi.com/ceddyville/api/mipaka](https://rapidapi.com/ceddyville/api/mipaka) — free tier available
- **Landing Page:** [mipaka.dev](https://mipaka.dev)
- **GitHub:** [github.com/ceddyville/mipaka-api](https://github.com/ceddyville/mipaka-api) — MIT license, PRs welcome
- **Swagger Docs:** [api.mipaka.dev/api/docs/](https://api.mipaka.dev/api/docs/)

The historical data is especially thin for South Sudan and Tanzania — if you have expertise in those regions, contributions are welcome.

---

## Next in the Series

- **Part 4:** Building Location Dropdowns for African Apps (React + Vue tutorial)
- **Part 5:** Uganda's Five Kingdoms — Pre-Colonial Data in a Modern API
- **Part 6:** Bulk Export & Data Analysis — Working with 88K Administrative Records

Follow me to catch the next post!

_Mipaka — every border, one API._

---

<a href="https://www.buymeacoffee.com/ceddyville"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=☕&slug=ceddyville&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff" /></a>
