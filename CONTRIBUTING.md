# Contributing to Mipaka

Thank you for wanting to improve Mipaka. This project exists because no reliable,
normalized, open source dataset of East and Central African administrative divisions
exists anywhere. Every contribution makes it better for every developer in the region.

---

## Ways to Contribute

### 1. Fix or Add Geographic Data (most needed)

The data lives in the `data/` folder as plain JSON files. You do not need to know
Django or Python to contribute data — just JSON.

**Highest priority right now:**

| Country | What's needed | File to edit |
|---------|--------------|--------------|
| 🇧🇮 Burundi | Collines for 97 communes | `data/BI/collines.json` |
| 🇨🇩 DRC | Verify 5 flagged territories | `data/CD/territories.json` |
| 🇸🇸 South Sudan | 512 payams | `data/SS/payams.json` (create) |
| All | Indigenous pre-colonial place names | `data/*/` + `seed_eras.py` |

**How to add a colline (Burundi example):**

Find your commune's `native_id` in `data/BI/communes.json`, then add entries
to `data/BI/collines.json` following this exact structure:

```json
{
  "id": "BI-CO-0346",
  "native_id": "BI-CO-0346",
  "name": "Gasura",
  "level": 3,
  "level_name": "Colline",
  "country": "BI",
  "parent_commune_id": "BI-C-042",
  "parent_commune_name": "Ngozi",
  "source": "Your source here",
  "source_url": "https://your-source-url"
}
```

Keep IDs sequential from the last existing entry.

---

### 2. Add or Correct Historical Place Names (unique to Mipaka)

Historical names live in `divisions/management/commands/seed_eras.py` in the
`HISTORICAL_NAMES` dictionary.

**To add a new historical name:**

```python
# Format: (current_name, era_name, historical_name, language, name_type, etymology)
("Kisangani", "Belgian Congo", "Stanleyville", "French", "colonial", "Named after Henry Morton Stanley"),
("Kisangani", "Pre-colonial Kingdoms", "Boyoma", "Lokele", "indigenous", "Lokele people's name for the falls area"),
```

**name_type options:** `official` | `indigenous` | `colonial` | `colloquial` | `historical`

Indigenous pre-colonial names in local languages are especially valuable — these
exist in no other structured dataset anywhere.

---

### 3. Fix a Bug or Add a Feature

Standard GitHub flow:

```bash
git checkout -b fix/your-description
# make your changes
git commit -m "fix: description of what you fixed"
git push origin fix/your-description
# open a Pull Request
```

**Branch naming:**
- `fix/` — data corrections or bug fixes
- `feat/` — new features
- `data/` — data additions (collines, payams, historical names etc.)
- `docs/` — documentation improvements

---

## Data Quality Standards

When adding or correcting data, please:

- **Cite your source** — add `source` and `source_url` fields to every record
- **Good sources:** Government websites, OCHA HDX, Wikipedia (for stable facts),
  academic references, official electoral commission data
- **For indigenous names:** Please include the language name and an etymology
  if you know it — this context is what makes the data irreplaceable
- **Do not flag as `needs_verification`** unless you genuinely aren't sure —
  if you know the data is correct, submit it as clean

---

## Submitting a Pull Request

1. Fork the repo
2. Create a branch (`git checkout -b data/burundi-ngozi-collines`)
3. Make your changes
4. Test locally if possible (`python manage.py sync_burundi` to verify your JSON loads)
5. Open a PR with a clear title and description:
   - What you added or fixed
   - What source you used
   - For indigenous names: what language and region

**PR title format:**
```
data(BI): add collines for Ngozi and Kiremba communes
fix(CD): correct Mitwaba territory province assignment
feat: add payams for Central Equatoria, South Sudan
data(UG): add Acholi indigenous place names for Gulu region
```

---

## Running the Project Locally

See [SETUP.md](SETUP.md) for full local setup instructions.

Quick check after making data changes:

```bash
# Verify your JSON is valid
python -c "import json; json.load(open('data/BI/collines.json')); print('JSON valid')"

# Test the sync command loads your data without errors
python manage.py sync_burundi --levels collines
```

---

## Code of Conduct

- Be respectful of all contributors regardless of background or location
- Colonial-era names are historical facts, not endorsements — document them accurately
- Indigenous names deserve the same care and accuracy as official names
- If you are unsure about a name or boundary, open an issue rather than guessing

---

## Questions?

Open an issue on GitHub. If you have data to contribute but aren't sure how to
format it, just open an issue describing what you have — we will help you get it
into the right format.

---

*The best person to fix Mipaka's data for your region is someone who lives there.*
