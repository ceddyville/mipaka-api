# Mipaka API — Blog Content Calendar

Series name: **Mipaka API — Every Border, One API**
Platform: dev.to (cross-post to Hashnode, Medium)
Schedule: Weekly (Tuesdays)
Author: Cedric Ongoro (@ceddyville)

---

## Published / Ready

### Week 1 — The Launch Post (ready to publish)

**File:** `blog-devto-kenya-counties-api.md`
**Title:** Mipaka: A Free REST API for 100K+ Administrative Divisions Across East Africa
**Target audience:** African developers building forms, KYC, delivery apps
**Tags:** api, python, django, africa
**Hook:** The "hardcoded county arrays" pain point every dev knows
**CTA:** Try Mipaka on RapidAPI

### Week 2 — The What's New Post (ready to publish)

**File:** `blog-02-whats-new.md`
**Title:** Mipaka API Update: 47 Historical Eras, 124 Colonial-Era Place Names, and DRC's Complete Administrative History
**Target audience:** Existing readers, API users, history-curious developers
**Tags:** api, africa, opensource, history
**Hook:** Changelog-style update with concrete numbers
**CTA:** Explore the new eras and names endpoints

### Week 3 — The Landing Page Post (to write)

**File:** `blog-03-try-it-live.md` (to write)
**Title:** Try Africa's Administrative Data API — No Signup, No Download, Just Click
**Target audience:** Casual explorers, product managers, non-technical stakeholders, developers evaluating the API
**Tags:** api, africa, webdev, opensource
**Hook:** Most APIs make you sign up before you see any data. We built an interactive explorer instead.
**Content:**

- What mipaka.dev does (country pills → cascading dropdowns → result cards → breadcrumbs → JSON toggle)
- Walk through a real exploration: pick Kenya → Nairobi → Dagoretti North → see wards
- Try Uganda's 6-level depth: Region → District → County → Sub-county → Parish → Village
- Search historical names: type "Léopoldville" and find Kinshasa
- Compare it to the raw API (show the JSON response alongside the card)
- "Ready to build? Here's how to get an API key" — bridge to RapidAPI
  **CTA:** Visit mipaka.dev and explore, then grab an API key on RapidAPI

### Week 4 — The History Deep Dive (ready to publish)

**File:** `blog-03-historical-divisions.md`
**Title:** From Léopoldville to Kinshasa: How Our API Tracks 500 Years of African Border Changes
**Target audience:** Historians, researchers, genealogy enthusiasts, data journalists
**Tags:** api, history, africa, opensource
**Hook:** Every city in East Africa carries layers of names
**CTA:** Explore the eras endpoint, contribute missing data

---

## Planned

### Week 5 — The Tutorial Post

**File:** `blog-05-cascading-dropdowns.md` (to write)
**Title:** Building Location Dropdowns for African Apps (React + Vue + vanilla JS)
**Target audience:** Frontend developers, full-stack developers
**Tags:** javascript, react, vue, tutorial
**Content:**

- Vanilla JS cascading select example
- React component with hooks (useEffect chain)
- Vue 3 composable
- Handling 6 levels deep (Uganda's village hierarchy)
- Loading states, error handling
- Mobile-friendly select vs. searchable dropdown for 70K+ villages

### Week 6 — The Kingdom Post

**File:** `blog-06-uganda-kingdoms.md` (to write)
**Title:** Uganda's Five Kingdoms — Pre-Colonial Data in a Modern REST API
**Target audience:** History/culture enthusiasts, Ugandan diaspora, educators
**Tags:** africa, history, api, opensource
**Content:**

- Buganda, Bunyoro-Kitara, Toro, Ankole, Busoga
- Current rulers and restoration story
- The politics of Ankole's non-restoration
- How the API models kingdoms as historical divisions
- Code examples: querying kingdoms and their territories

### Week 7 — The Data Post

**File:** `blog-07-bulk-export-analysis.md` (to write)
**Title:** Analyzing 88,000 Administrative Divisions with Python and Pandas
**Target audience:** Data scientists, analysts, GIS people
**Tags:** python, datascience, api, tutorial
**Content:**

- CSV export endpoint walkthrough
- Pandas analysis: distribution across countries
- Hierarchy depth analysis (Uganda's 6 levels vs DRC's 2)
- Visualizing the data with matplotlib/plotly
- Comparing administrative structures across countries

### Week 8 — The DRC Deep Dive

**File:** `blog-08-drc-six-eras.md` (to write)
**Title:** DRC's Six Administrative Eras — From Leopold's Districts to 26 Modern Provinces
**Target audience:** Central Africa researchers, political scientists, Congo diaspora
**Tags:** africa, history, api, opensource
**Content:**

- The 12 districts of 1910 vs 26 provinces today
- How Katanga became Shaba then split into 4
- Léopoldville → Kinshasa and other city name changes
- 34 cities with coordinates
- Code examples for tracing a province through all eras

### Week 9 — The Open Source Post

**File:** `blog-09-open-source-african-data.md` (to write)
**Title:** Why I Open-Sourced Africa's Administrative Boundary Data
**Target audience:** Open source community, African tech ecosystem
**Tags:** opensource, africa, community, api
**Content:**

- The problem of fragmented, paywalled African data
- Data sources: Wikipedia, HDX, government gazettes
- How to contribute (adding countries, correcting data)
- The sync command architecture (one per country)
- Future: GeoJSON boundaries, population data

### Week 10 — The Technical Post

**File:** `blog-10-django-api-architecture.md` (to write)
**Title:** Designing a REST API for Unlimited-Depth Hierarchies with Django
**Target audience:** Backend developers, Django community
**Tags:** django, python, api, database
**Content:**

- Self-referential parent-child model pattern
- Handling 6 levels of nesting with a single Division model
- Caching strategy (24h on list/retrieve)
- The SmartAnonThrottle pattern (RapidAPI bypass)
- Streaming CSV exports for large datasets
- Browsable API as documentation

---

## Evergreen / Reference Posts (no schedule)

### The Migration Post

**Title:** Kenya's 2010 Constitutional Boundary Changes — 8 Provinces to 47 Counties
**Audience:** Kenyan developers, political data researchers

### The Genealogy Post

**Title:** Finding Colonial-Era Place Names with a Free API
**Audience:** Genealogy researchers, family history enthusiasts

### The Comparison Post

**Title:** How 7 African Countries Organize Their Administrative Divisions (And Why It Matters for Developers)
**Audience:** General developer audience, geography enthusiasts

---

## Cross-Posting Strategy

1. **dev.to** — Primary (series feature, good discovery)
2. **Hashnode** — Cross-post with canonical URL to dev.to
3. **X/Twitter** — Thread for each post with key highlights
4. **Reddit** — r/Africa, r/django, r/datasets, r/genealogy (match post to subreddit)
5. **LinkedIn** — Shortened version for professional audience
