---
title: "Mipaka API Update: 47 Historical Eras, 124 Colonial-Era Place Names, and DRC's Complete Administrative History"
published: false
description: "Since launching Mipaka, we've added 47 historical eras spanning 500 years, 124 historical place names, DRC's six administrative eras, Uganda's five pre-colonial kingdoms, and historical divisions across all 7 countries."
tags: api, africa, opensource, history
cover_image:
canonical_url:
series: Mipaka API — Every Border, One API
---

## What's Changed Since Launch

In [Part 1](https://dev.to/ceddyville/i-built-a-free-rest-api-for-kenyas-47-counties-290-constituencies-and-1450-wards-31j7), I introduced Mipaka — a free REST API for administrative divisions across 7 East/Central African countries. The focus was the basics: cascading dropdowns, search, filtering, and historical names.

Since then, the API has grown significantly. Here's everything new.

---

## By the Numbers

| Metric                  | At Launch | Now          |
| ----------------------- | --------- | ------------ |
| Divisions               | 103,194   | 88,000+      |
| Countries               | 7         | 7            |
| Historical eras         | ~10       | **47**       |
| Historical place names  | ~60       | **124**      |
| Historical divisions    | 0         | **229**      |
| Cities with coordinates | 0         | **34** (DRC) |

> **Why did the division count drop?** Rwanda's data was resynced with corrected upstream sources, removing duplicate villages. The data is more accurate now.

---

## 47 Historical Eras

Every country now has a complete chain of eras — from pre-colonial kingdoms through colonial occupation to the present day.

```bash
GET /api/v1/eras/?country=CD
```

**DRC alone has 7 eras:**

| Era                                               | Period       | Type               |
| ------------------------------------------------- | ------------ | ------------------ |
| Kingdom of Kongo                                  | ~1390–1914   | Pre-colonial       |
| Luba Empire                                       | ~1585–1889   | Pre-colonial       |
| Congo Free State                                  | 1885–1908    | Colonial (Belgian) |
| Belgian Congo                                     | 1908–1960    | Colonial (Belgian) |
| Republic of the Congo                             | 1960–1964    | Independence       |
| Democratic Republic of the Congo (First Republic) | 1964–1971    | Independence       |
| Republic of Zaire                                 | 1971–1997    | Independence       |
| Democratic Republic of the Congo                  | 1997–present | Current            |

**Uganda has 10 eras** — including 8 pre-colonial kingdoms and chiefdoms with their current rulers:

- **Buganda Kingdom** (~1300–present) — Kabaka Ronald Muwenda Mutebi II
- **Bunyoro-Kitara Kingdom** (~1300–present) — Omukama Solomon Gafabusa Iguru I
- **Kingdom of Toro** (~1830–present) — Omukama Oyo Nyimba Kabamba Iguru Rukidi IV
- **Kingdom of Ankole** (~1500–1967) — abolished, never restored
- **Busoga Kingdom** (~1500–present) — Kyabazinga William Wilberforce Gabula Nadiope IV

Each era carries notes, date ranges, colonial power tracking, and links to the divisions that existed during that period.

---

## 124 Historical Place Names

Major cities now have their full naming history — indigenous, colonial, and modern names mapped to specific eras and languages.

**Kinshasa through the centuries:**

```bash
GET /api/v1/divisions/{kinshasa_id}/names/
```

```json
[
  {
    "name": "Nshasa",
    "language": "Kikongo",
    "name_type": "indigenous",
    "era_name": "Kingdom of Kongo",
    "etymology": "Named after Nshasa village on the riverbank"
  },
  {
    "name": "Léopoldville",
    "language": "French",
    "name_type": "colonial",
    "era_name": "Congo Free State",
    "etymology": "Named after King Leopold II by Henry Morton Stanley (1881)"
  },
  {
    "name": "Kinshasa",
    "language": "Lingala",
    "name_type": "official",
    "era_name": "Democratic Republic of the Congo",
    "etymology": "Restored to indigenous name at independence (1966)"
  }
]
```

**Name coverage by country:**

| Country     | Historical Names | Examples                                                                                |
| ----------- | ---------------- | --------------------------------------------------------------------------------------- |
| DRC         | 31               | Nshasa → Léopoldville → Kinshasa, Stanleyville → Kisangani, Élisabethville → Lubumbashi |
| Uganda      | 28               | Kasozi k'Empala → Kampala, Bugiri → Port Bell, Entebbe (Luganda: "seat")                |
| Kenya       | 21               | Enkare Nyirobi → Nairobi, Kisumo/Kisuma → Port Florence → Kisumu                        |
| Tanzania    | 18               | Dar es Salaam (Arabic: "Haven of Peace"), Bagamoyo (Swahili: "Lay down your heart")     |
| Rwanda      | 14               | Nyarugenge → Kigali, Butare → Huye                                                      |
| South Sudan | 14               | Gondokoro → Juba, Mongalla → colonial river station                                     |
| Burundi     | 13               | Usumbura → Bujumbura, Kitega → Gitega                                                   |

---

## 229 Historical Divisions

Beyond current administrative boundaries, the API now includes divisions that no longer exist — searchable by country and level:

```bash
# Kenya's 8 former provinces (1963–2010)
GET /api/v1/divisions/?country=KE&level=100

# DRC's 11 provinces under Mobutu (1997–2015)
GET /api/v1/divisions/?country=CD&level=100

# South Sudan's 28 states (2015–2020 decree)
GET /api/v1/divisions/?country=SS&level=100
```

Level 100 is a convention used to separate historical divisions from active administrative data — they won't appear in standard queries unless you filter explicitly.

**What's available:**

| Country     | Historical Divisions | What                                                   |
| ----------- | -------------------- | ------------------------------------------------------ |
| Kenya       | 167                  | 8 provinces + 159 districts (1963/1992/2007)           |
| DRC         | 117                  | 6 eras of provinces and districts (1910–present)       |
| South Sudan | 28                   | 28 states from 2015 presidential decree                |
| Rwanda      | 12                   | 12 prefectures (pre-2006 restructuring)                |
| Tanzania    | 6                    | 6 regions created between 2002–2016                    |
| Uganda      | 5                    | 5 traditional kingdoms (abolished 1967, restored 1993) |

Historical divisions use `is_active=false` so they don't pollute standard queries. Filter explicitly to find them.

---

## DRC Deep Data: 325 Records Across 6 Administrative Eras

DRC got the biggest upgrade. The original API had 174 records (provinces + territories). It now has **325 records** tracing how the country was divided from Leopold's 15 districts in 1910 to today's 26 provinces:

| Era            | Divisions        | Example                                                           |
| -------------- | ---------------- | ----------------------------------------------------------------- |
| 1910 Districts | 15               | District du Katanga, District de l'Équateur                       |
| 1933 Provinces | 6                | Province du Katanga, Province de Léopoldville                     |
| 1963 Provinces | 21               | Nord-Katanga, Sud-Kasaï (first post-independence split)           |
| 1966 Provinces | 9                | Shaba (renamed from Katanga under Mobutu)                         |
| 1997 Provinces | 11               | Katanga restored, Congo-Kinshasa                                  |
| Current (2015) | 26 + territories | Katanga split into Haut-Katanga, Lualaba, Tanganyika, Haut-Lomami |

Plus **34 cities with coordinates** — the first geo-coded data in the API.

---

## What's Next

This data enrichment sets the foundation for features coming soon:

- **Coordinates for all countries** — DRC is the pilot, on the roadmap expand to Kenya, Uganda, and others
- **GeoJSON boundaries** — polygon data for map rendering
- **Population data** — census figures tied to divisions

---

## Try It

Try the live explorer at [mipaka.dev](https://mipaka.dev/#explorer) — pick a country, drill through divisions, and see historical eras in action.

Everything above is also available on [RapidAPI](https://rapidapi.com/ceddyville/api/mipaka) with a free tier, and the code is [open source on GitHub](https://github.com/ceddyville/mipaka-api) — MIT licensed.

The historical data is the part of Mipaka I'm most proud of. There's nothing else like it — a structured, queryable dataset of how African cities and borders have changed across centuries. If you're a historian, genealogist, or just someone who finds African history fascinating, I'd genuinely love your contributions. The data is open source — PRs welcome.

### Links

- **Website:** [mipaka.dev](https://mipaka.dev)
- **API Docs:** [api.mipaka.dev/api/docs/](https://api.mipaka.dev/api/docs/)
- **API on RapidAPI:** [rapidapi.com/ceddyville/api/mipaka](https://rapidapi.com/ceddyville/api/mipaka)
- **GitHub:** [github.com/ceddyville/mipaka-api](https://github.com/ceddyville/mipaka-api)

---

## Coming Next

This is **Part 2** of the Mipaka API series. Missed the intro? Start with [Part 1: Mipaka: A Free REST API for 100K+ Administrative Divisions Across East Africa](https://dev.to/ceddyville/i-built-a-free-rest-api-for-kenyas-47-counties-290-constituencies-and-1450-wards-31j7).

Next up:

- **Part 3:** From Léopoldville to Kinshasa — 500 Years of African Border Changes

Follow me to catch the next one!

_Mipaka — every border, one API._
