# Mipaka API — Local Setup Guide

Instructions for **Windows 10/11**, **macOS**, and **Linux**.
Follow the steps in order. Should take about 25 minutes.

---

## Part 1 — Install Prerequisites

### 1.1 Python 3.11+

| OS | Download | Notes |
|----|----------|-------|
| Windows | https://www.python.org/downloads/ | ⚠️ Check **"Add Python to PATH"** during install |
| macOS | https://www.python.org/downloads/ | Or `brew install python` |
| Linux | `sudo apt install python3.11 python3.11-venv` | |

Verify:
```bash
python --version    # should show 3.11+
```

**If you have Conda installed**, use that instead of venv (see Step 2).

---

### 1.2 PostgreSQL 18

| OS | Download |
|----|----------|
| Windows | https://www.enterprisedb.com/downloads/postgres-postgresql-downloads → Windows x86-64 |
| macOS | https://www.enterprisedb.com/downloads/postgres-postgresql-downloads → macOS |
| Linux | `sudo apt install postgresql postgresql-contrib` |

**During the Windows installer:**
- Note the password you set for the `postgres` user — you'll need it
- Leave port as `5432`
- Click **Skip** when Stack Builder appears at the end

**After install on Windows — add PostgreSQL to PATH:**
1. `Win + S` → search "Environment Variables" → "Edit the system environment variables"
2. Click "Environment Variables..." → under "System variables" find "Path" → "Edit"
3. Click "New" → add `C:\Program Files\PostgreSQL\18\bin`
4. OK → OK → OK → **restart PowerShell**

**Windows known issue — COMSPEC error during install:**
If you see *"The environment variable COMSPEC does not seem to point to cmd.exe"*:
1. Open Environment Variables (as above)
2. Find `COMSPEC` in System variables → Edit
3. Value must be exactly `C:\Windows\system32\cmd.exe` (no trailing semicolon)
4. Click OK, restart, run installer again

Verify:
```powershell
psql --version    # should show psql (PostgreSQL) 18.x
```

---

### 1.3 Redis

| OS | Download | Notes |
|----|----------|-------|
| Windows | https://github.com/tporadowski/redis/releases → download `.msi` | Installs as a Windows service, auto-starts |
| macOS | `brew install redis` then `brew services start redis` | |
| Linux | `sudo apt install redis-server` then `sudo service redis start` | |

Verify:
```bash
redis-cli ping    # should return PONG
```

---

### 1.4 Git

| OS | Download |
|----|----------|
| Windows | https://git-scm.com/download/win |
| macOS | `brew install git` or Xcode Command Line Tools |
| Linux | `sudo apt install git` |

---

## Part 2 — Project Setup

### Step 1 — Get the Project

If you downloaded the zip:

**Windows (PowerShell):**
```powershell
Expand-Archive mipaka-api-final.zip -DestinationPath .
cd mipaka-api
```

**macOS / Linux:**
```bash
unzip mipaka-api-final.zip
cd mipaka-api
```

Or if you're cloning from GitHub:
```bash
git clone https://github.com/YOUR_USERNAME/mipaka-api.git
cd mipaka-api
```

---

### Step 2 — Python Environment

**Option A — Using Conda (recommended if Conda is installed):**
```powershell
conda create -n mipaka python=3.11
conda activate mipaka
pip install -r requirements-dev.txt
```

**Option B — Using venv:**

Windows:
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements-dev.txt
```

macOS / Linux:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

Your prompt should show `(mipaka)` or `(venv)` confirming the environment is active.

---

### Step 3 — Environment Variables

Windows:
```powershell
copy .env.example .env
```

macOS / Linux:
```bash
cp .env.example .env
```

Open `.env` in any text editor and fill in:

```env
SECRET_KEY=replace-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://postgres:YOUR_POSTGRES_PASSWORD@localhost:5432/mipaka
REDIS_URL=redis://localhost:6379/0
DJANGO_SETTINGS_MODULE=config.settings.development
```

Generate a secret key by running:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Copy the output into `SECRET_KEY=` in `.env`.

**Quick-start without PostgreSQL or Redis:**
If you just want to explore the code and don't have PostgreSQL installed yet,
remove the `DATABASE_URL` and `REDIS_URL` lines from `.env`. The app will
automatically fall back to SQLite (file-based, zero setup). Redis is only needed
for caching — everything works without it, just slower on repeat queries.

```env
# Minimal .env for SQLite-only development:
SECRET_KEY=replace-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=config.settings.development
```

---

### Step 4 — Create the Database

**If using PostgreSQL:**

Windows:
```powershell
psql -U postgres -c "CREATE DATABASE mipaka;"
```
Enter your PostgreSQL password when prompted (characters won't show — that's normal).

macOS / Linux:
```bash
createdb mipaka
```

**If using SQLite (no PostgreSQL needed):**
Skip the above — Django creates the SQLite file automatically on migrate.

Then run migrations:
```bash
python manage.py migrate
python manage.py createsuperuser
```

---

### Step 5 — Data Files (pre-built — no action needed)

All converted JSON files are **already included** in the repo under `data/`.
You do **not** need to run any converters or clone any external repos.

The `data/` directory contains:

| Country | Files | Records |
|---------|-------|---------|
| BI (Burundi) | provinces, communes, collines | ~478 |
| CD (DRC) | provinces, territories | ~174 |
| KE (Kenya) | counties, constituencies, wards | ~1,787 |
| RW (Rwanda) | provinces, districts, sectors, cells, villages | ~17,441 |
| SS (South Sudan) | states, counties | ~82 |
| TZ (Tanzania) | regions, districts | ~207 |
| UG (Uganda) | regions, districts, counties, subcounties, parishes, villages | ~83,903 |

Raw source files are also saved (prefixed `raw_`) in case you need to re-run converters.

<details>
<summary>Click to see how to re-run converters (only if source data changes)</summary>

**Windows (PowerShell):**
```powershell
# Kenya — fetches live from API
python converters\convert_kenya.py --out data\KE

# Tanzania — clone source repo first
git clone https://github.com/Kijacode/Tanzania_Geo_Data.git
python converters\convert_tanzania.py --src .\Tanzania_Geo_Data --out data\TZ

# Rwanda — download source file first
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/jnkindi/rwanda-locations-json/refs/heads/main/locations.json" -OutFile "locations.json"
python converters\convert_rwanda.py --src .\locations.json --out data\RW

# Uganda — clone source repo first
git clone https://github.com/kusaasira/uganda-geo-data.git
python converters\convert_uganda.py --src .\uganda-geo-data\src\Uganda\Data --out data\UG --counties data\UG\counties.json
```

**macOS / Linux:**
```bash
python converters/convert_kenya.py --out ./data/KE

git clone https://github.com/Kijacode/Tanzania_Geo_Data.git
python converters/convert_tanzania.py --src ./Tanzania_Geo_Data --out ./data/TZ

curl -O https://raw.githubusercontent.com/jnkindi/rwanda-locations-json/refs/heads/main/locations.json
python converters/convert_rwanda.py --src ./locations.json --out ./data/RW

git clone https://github.com/kusaasira/uganda-geo-data.git
python converters/convert_uganda.py \
  --src ./uganda-geo-data/src/Uganda/Data \
  --out ./data/UG \
  --counties ./data/UG/counties.json
```

</details>

---

### Step 6 — Sync All Countries into Database

Run in order. Villages last — large datasets, uses bulk_create.

```bash
python manage.py sync_kenya
python manage.py sync_tanzania

python manage.py sync_rwanda --levels provinces districts sectors cells
python manage.py sync_rwanda --levels villages

python manage.py sync_uganda --levels regions districts counties
python manage.py sync_uganda --levels subcounties parishes
python manage.py sync_uganda --levels villages

python manage.py sync_burundi --levels provinces communes collines
python manage.py sync_drc --levels provinces territories
python manage.py sync_south_sudan --levels states counties
```

---

### Step 7 — Seed Historical Eras & Place Names

Run **after** all sync commands — requires Division records to exist first.

```bash
python manage.py seed_eras
```

Seeds historical eras for all 7 countries and ~60 historical place names
(pre-colonial indigenous names + colonial names) for major cities.

---

### Step 8 — Run the Dev Server

```bash
python manage.py runserver
```

Open your browser and test these URLs:
```
http://localhost:8000/health/
http://localhost:8000/api/v1/countries/
http://localhost:8000/api/v1/countries/UG/eras/
http://localhost:8000/api/v1/divisions/?country=KE&level=1
http://localhost:8000/api/v1/eras/?era_type=colonial
http://localhost:8000/api/v1/names/?name_type=indigenous
http://localhost:8000/api/v1/divisions/?name=Léopoldville
http://localhost:8000/api/v1/divisions/?year=1923&country=CD
```

---

## Troubleshooting

**`'python' is not recognized` (Windows)**
→ Python wasn't added to PATH during install. Reinstall Python and check "Add to PATH".

**`venv\Scripts\activate` fails with execution policy error (Windows)**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**`ModuleNotFoundError: No module named 'decouple'`**
→ Environment isn't active. Run `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux).

**`could not connect to server` (PostgreSQL)**
→ PostgreSQL service isn't running.
- Windows: `Win + R` → `services.msc` → find **postgresql-x64-18** → Start
- Mac: `brew services start postgresql`
- Linux: `sudo service postgresql start`

**`psql` not recognized (Windows)**
→ Add `C:\Program Files\PostgreSQL\18\bin` to PATH (see Step 1.2 above).

**`redis.exceptions.ConnectionError`**
→ Redis isn't running.
- Windows: `Win + R` → `services.msc` → find **Redis** → Start
- Mac: `brew services start redis`
- Linux: `sudo service redis start`

**`psycopg2` install fails (Windows)**
```powershell
pip install psycopg2-binary
```

**`dj_database_url` import error**
```bash
pip install dj-database-url
```

**`sync_kenya` fails with connection error**
→ Kenya converter fetches live from kenyaareadata.vercel.app — check internet connection.

**`seed_eras` says "Division X not found"**
→ Run all sync commands first — `seed_eras` needs Division records to already exist.

**COMSPEC error during PostgreSQL install (Windows)**
→ See Step 1.2 above for the fix.

---

## Pre-built Data Files

All data files are included in the repo — no converters need to be run.
Raw source copies (prefixed `raw_`) are also saved in case the original
repositories or APIs go offline.

```
data/BI/  provinces.json (5), provinces_legacy_18.json (18), communes.json (128), collines.json (345)
data/CD/  provinces.json (26), territories.json (148)
data/KE/  counties.json (47), constituencies.json (290), wards.json (1,450), raw_api_response.json
data/RW/  provinces.json (5), districts.json (30), sectors.json (416), cells.json (2,148), villages.json (14,842), raw_locations.json
data/SS/  states.json (10), counties.json (72)
data/TZ/  regions.json (31), districts.json (176), raw_Regions.json, raw_Districts.json
data/UG/  regions.json (4), districts.json (146), counties.json (168), subcounties.json (2,120),
          parishes.json (10,365), villages.json (71,250), raw_*.json backups
```
