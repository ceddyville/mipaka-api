"""
Rwanda Locations Converter
==========================
Splits jnkindi/rwanda-locations-json flat file into Mipaka per-level JSON files.

Usage:
  python convert_rwanda.py --src ./locations.json --out ./data/RW

Source: https://raw.githubusercontent.com/jnkindi/rwanda-locations-json/refs/heads/main/locations.json

Output files:
  data/RW/regions.json      (5 provinces)
  data/RW/districts.json    (30 districts)
  data/RW/sectors.json      (416 sectors)
  data/RW/cells.json        (2,148 cells)
  data/RW/villages.json     (14,837 villages)
"""

import json
import os
import argparse

SOURCE     = "jnkindi/rwanda-locations-json"
SOURCE_URL = "https://github.com/jnkindi/rwanda-locations-json"

# Rwanda's 4 provinces use English names, Kigali is the capital city province
PROVINCE_NAME_MAP = {
    "KIGALI":    "Kigali City",
    "NORTH":     "Northern Province",
    "SOUTH":     "Southern Province",
    "EAST":      "Eastern Province",
    "WEST":      "Western Province",
}


def title(s):
    """Capitalize nicely — handles names like 'NYARUGENGE' → 'Nyarugenge'."""
    return s.strip().title()


def convert(rows):
    provinces   = {}   # code → entry
    districts   = {}
    sectors     = {}
    cells       = {}
    villages    = {}

    for row in rows:
        pc  = str(row["province_code"])
        dc  = str(row["district_code"])
        sc  = str(row["sector_code"])
        cc  = str(row["cell_code"])
        vc  = str(row["village_code"])

        pn = PROVINCE_NAME_MAP.get(row["province_name"].strip().upper(), title(row["province_name"]))

        # Province
        if pc not in provinces:
            provinces[pc] = {
                "id":         f"RW-P-{pc}",
                "native_id":  pc,
                "name":       pn,
                "level":      1,
                "level_name": "Province",
                "country":    "RW",
                "source":     SOURCE,
                "source_url": SOURCE_URL,
            }

        # District
        if dc not in districts:
            districts[dc] = {
                "id":                f"RW-D-{dc}",
                "native_id":         dc,
                "name":              title(row["district_name"]),
                "level":             2,
                "level_name":        "District",
                "country":           "RW",
                "parent_province_id": pc,
                "source":            SOURCE,
                "source_url":        SOURCE_URL,
            }

        # Sector
        if sc not in sectors:
            sectors[sc] = {
                "id":                 f"RW-S-{sc}",
                "native_id":          sc,
                "name":               title(row["sector_name"]),
                "level":              3,
                "level_name":         "Sector",
                "country":            "RW",
                "parent_district_id": dc,
                "source":             SOURCE,
                "source_url":         SOURCE_URL,
            }

        # Cell
        if cc not in cells:
            cells[cc] = {
                "id":                f"RW-C-{cc}",
                "native_id":         cc,
                "name":              title(row["cell_name"]),
                "level":             4,
                "level_name":        "Cell",
                "country":           "RW",
                "parent_sector_id":  sc,
                "source":            SOURCE,
                "source_url":        SOURCE_URL,
            }

        # Village
        if vc not in villages:
            villages[vc] = {
                "id":              f"RW-V-{vc}",
                "native_id":       vc,
                "name":            title(row["village_name"]),
                "level":           5,
                "level_name":      "Village",
                "country":         "RW",
                "parent_cell_id":  cc,
                "source":          SOURCE,
                "source_url":      SOURCE_URL,
            }

    return (
        sorted(provinces.values(), key=lambda x: x["native_id"]),
        sorted(districts.values(), key=lambda x: x["native_id"]),
        sorted(sectors.values(),   key=lambda x: x["native_id"]),
        sorted(cells.values(),     key=lambda x: x["native_id"]),
        sorted(villages.values(),  key=lambda x: x["native_id"]),
    )


def save(out_dir, filename, data):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✓ {filename:<20} {len(data):>6,} records  →  {path}")


def main():
    parser = argparse.ArgumentParser(description="Convert Rwanda locations.json to Mipaka format")
    parser.add_argument("--src", required=True, help="Path to locations.json")
    parser.add_argument("--out", required=True, help="Output directory (e.g. data/RW/)")
    args = parser.parse_args()

    print(f"Loading {args.src}...")
    with open(args.src, encoding="utf-8") as f:
        rows = json.load(f)
    print(f"  {len(rows):,} rows loaded.\n")

    print("Converting...")
    provinces, districts, sectors, cells, villages = convert(rows)

    print("\nSaving...")
    save(args.out, "provinces.json", provinces)
    save(args.out, "districts.json", districts)
    save(args.out, "sectors.json",   sectors)
    save(args.out, "cells.json",     cells)
    save(args.out, "villages.json",  villages)

    total = len(provinces) + len(districts) + len(sectors) + len(cells) + len(villages)

    print(f"""
Summary
-------
Provinces : {len(provinces):>6,}
Districts : {len(districts):>6,}
Sectors   : {len(sectors):>6,}
Cells     : {len(cells):>6,}
Villages  : {len(villages):>6,}
─────────────────
Total     : {total:>6,}

Next step:
  python manage.py sync_rwanda --levels provinces districts sectors cells
  python manage.py sync_rwanda --levels villages
""")


if __name__ == "__main__":
    main()
