"""
HDX COD-AB Converter for Burundi, DRC, South Sudan
====================================================
Converts the tabular Pcode Excel/CSV files from HDX into Mipaka JSON format.

This covers the DEEPER levels not already seeded from Wikipedia:
  - Burundi: Communes (ADM2), Collines (ADM3)
  - DRC: Territories (ADM2)
  - South Sudan: Payams (ADM3)

Top-level files (provinces/states) are already built — no HDX needed for those.

DOWNLOAD INSTRUCTIONS
─────────────────────

Burundi (Communes + Collines):
  URL: https://data.humdata.org/dataset/burundi-admin-bounderies
  Download: "SHP Admin2 Communes.zip" and "SHP Admin3 Collines.zip"
  OR better: use the tabular CSV exports from the same page
  Save CSV files as: burundi_admin2.csv, burundi_admin3.csv

DRC (Territories):
  URL: https://data.humdata.org/dataset/cod-ab-cod
  Download: "Pcode_admin1&2_health_zone.xlsx" (tabular Pcode file)
  Save as: drc_admin2.xlsx (or .csv)

South Sudan (Payams):
  URL: https://data.humdata.org/dataset/cod-ab-ssd
  Download the ADM3 shapefile or tabular CSV
  Save as: south_sudan_admin3.csv

USAGE
─────
  pip install pandas openpyxl

  # Burundi
  python convert_hdx.py --country BI --admin2 burundi_admin2.csv --admin3 burundi_admin3.csv --out ./data/BI

  # DRC
  python convert_hdx.py --country CD --admin2 drc_admin2.xlsx --out ./data/CD

  # South Sudan
  python convert_hdx.py --country SS --admin3 south_sudan_admin3.csv --out ./data/SS

EXPECTED COLUMN NAMES (HDX COD-AB standard)
────────────────────────────────────────────
  ADM0_PCODE, ADM0_EN
  ADM1_PCODE, ADM1_EN  ← parent reference
  ADM2_PCODE, ADM2_EN  ← for territories/communes
  ADM3_PCODE, ADM3_EN  ← for collines/payams

These are the standard HDX p-code column names used across all COD-AB datasets.
If your downloaded file uses different column names, check the first few rows and
pass --col-mapping to override (see --help).
"""

import json
import os
import argparse

SOURCE     = "HDX / OCHA COD-AB"
SOURCE_URL = "https://data.humdata.org"

COUNTRY_CONFIG = {
    "BI": {
        "admin2_level": 2, "admin2_name": "Commune",
        "admin3_level": 3, "admin3_name": "Colline",
        "admin2_file": "communes.json",
        "admin3_file": "collines.json",
        "parent2_key": "parent_province_id",
        "parent3_key": "parent_commune_id",
        "id_prefix2": "BI-C",
        "id_prefix3": "BI-CO",
    },
    "CD": {
        "admin2_level": 2, "admin2_name": "Territory",
        "admin2_file": "territories.json",
        "parent2_key": "parent_province_id",
        "id_prefix2": "CD-T",
    },
    "SS": {
        "admin3_level": 3, "admin3_name": "Payam",
        "admin3_file": "payams.json",
        "parent3_key": "parent_county_id",
        "id_prefix3": "SS-PA",
    },
}


def load_tabular(path):
    """Load CSV or Excel into list of dicts."""
    try:
        import pandas as pd
    except ImportError:
        print("ERROR: pandas not installed. Run: pip install pandas openpyxl")
        raise

    if path.endswith(".xlsx") or path.endswith(".xls"):
        df = pd.read_excel(path, dtype=str)
    else:
        df = pd.read_csv(path, dtype=str)
    return df.fillna("").to_dict("records")


def find_col(row, candidates):
    """Find first matching column name (case-insensitive)."""
    row_keys_lower = {k.lower(): k for k in row.keys()}
    for c in candidates:
        if c.lower() in row_keys_lower:
            return row_keys_lower[c.lower()]
    return None


def convert_admin2(rows, country_code, cfg):
    """Convert ADM2 rows to Mipaka format."""
    out = []
    prefix = cfg["id_prefix2"]
    level  = cfg["admin2_level"]
    name   = cfg["admin2_name"]
    parent_key = cfg["parent2_key"]

    for i, row in enumerate(rows, start=1):
        pcode_col  = find_col(row, ["ADM2_PCODE", "admin2pcode", "pcode2"])
        name_col   = find_col(row, ["ADM2_EN", "admin2name", "name_en", "name"])
        parent_col = find_col(row, ["ADM1_PCODE", "admin1pcode", "pcode1"])

        if not all([pcode_col, name_col, parent_col]):
            continue

        pcode  = str(row[pcode_col]).strip()
        nm     = str(row[name_col]).strip().title()
        parent = str(row[parent_col]).strip()

        if not pcode or not nm:
            continue

        out.append({
            "id":         f"{prefix}-{i:04d}",
            "native_id":  pcode,
            "name":       nm,
            "level":      level,
            "level_name": name,
            "country":    country_code,
            parent_key:   parent,
            "source":     SOURCE,
            "source_url": SOURCE_URL,
        })
    return out


def convert_admin3(rows, country_code, cfg):
    """Convert ADM3 rows to Mipaka format."""
    out = []
    prefix = cfg["id_prefix3"]
    level  = cfg["admin3_level"]
    name   = cfg["admin3_name"]
    parent_key = cfg["parent3_key"]

    for i, row in enumerate(rows, start=1):
        pcode_col  = find_col(row, ["ADM3_PCODE", "admin3pcode", "pcode3"])
        name_col   = find_col(row, ["ADM3_EN", "admin3name", "name_en", "name"])
        parent_col = find_col(row, ["ADM2_PCODE", "admin2pcode", "pcode2"])

        if not all([pcode_col, name_col, parent_col]):
            continue

        pcode  = str(row[pcode_col]).strip()
        nm     = str(row[name_col]).strip().title()
        parent = str(row[parent_col]).strip()

        if not pcode or not nm:
            continue

        out.append({
            "id":         f"{prefix}-{i:05d}",
            "native_id":  pcode,
            "name":       nm,
            "level":      level,
            "level_name": name,
            "country":    country_code,
            parent_key:   parent,
            "source":     SOURCE,
            "source_url": SOURCE_URL,
        })
    return out


def save(out_dir, filename, data):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✓ {filename:<25} {len(data):>6,} records  →  {path}")


def main():
    parser = argparse.ArgumentParser(description="Convert HDX COD-AB tabular files to Mipaka format")
    parser.add_argument("--country", required=True, choices=["BI","CD","SS"], help="Country code")
    parser.add_argument("--admin2",  default=None, help="Path to ADM2 CSV/Excel file")
    parser.add_argument("--admin3",  default=None, help="Path to ADM3 CSV/Excel file")
    parser.add_argument("--out",     required=True, help="Output directory (e.g. data/BI/)")
    args = parser.parse_args()

    cc  = args.country
    cfg = COUNTRY_CONFIG[cc]

    if args.admin2:
        print(f"Loading ADM2 from {args.admin2}...")
        rows = load_tabular(args.admin2)
        data = convert_admin2(rows, cc, cfg)
        save(args.out, cfg["admin2_file"], data)

    if args.admin3:
        print(f"Loading ADM3 from {args.admin3}...")
        rows = load_tabular(args.admin3)
        data = convert_admin3(rows, cc, cfg)
        save(args.out, cfg["admin3_file"], data)

    if not args.admin2 and not args.admin3:
        print("Nothing to convert — pass --admin2 and/or --admin3")


if __name__ == "__main__":
    main()
