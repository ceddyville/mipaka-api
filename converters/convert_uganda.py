"""
Uganda Geo Data Converter
=========================
Converts kusaasira/uganda-geo-data raw JSON files into Mipaka format.

Usage (after cloning the repo):
  git clone https://github.com/kusaasira/uganda-geo-data.git
  python convert_uganda.py --src ./uganda-geo-data/src/Uganda/Data --out ./data/UG

Expected source files:
  subcounties.json  → { id, name, county }
  parishes.json     → { id, name, sub_county }
  villages.json     → { id, name, parish }
"""

import json
import os
import argparse
from collections import defaultdict


def load(path, filename):
    full = os.path.join(path, filename)
    if not os.path.exists(full):
        raise FileNotFoundError(f"Missing: {full}")
    with open(full, encoding="utf-8") as f:
        return json.load(f)


def convert_subcounties(data, src_counties):
    """
    Source format: { id, name, county }
    Output format: { id, name, level, level_name, parent_county_id, ... }
    """
    # Build a county id → name lookup from our existing counties.json
    county_lookup = {c["id"]: c["name"] for c in src_counties}

    out = []
    for item in data:
        out.append({
            "id": f"UG-SC-{item['id']}",
            "native_id": str(item["id"]),
            "name": item["name"].title(),       # normalize ALL CAPS
            "level": 4,
            "level_name": "Sub-county",
            "country": "UG",
            "parent_county_native_id": str(item["county"]),
            "source": "kusaasira/uganda-geo-data",
            "source_url": "https://github.com/kusaasira/uganda-geo-data",
            "children": []
        })
    return out


def convert_parishes(data):
    """
    Source format: { id, name, sub_county }
    Output format: { id, name, level, level_name, parent_subcounty_native_id, ... }
    """
    out = []
    for item in data:
        out.append({
            "id": f"UG-PA-{item['id']}",
            "native_id": str(item["id"]),
            "name": item["name"].title(),
            "level": 5,
            "level_name": "Parish",
            "country": "UG",
            "parent_subcounty_native_id": str(item["subcounty"]),
            "source": "kusaasira/uganda-geo-data",
            "source_url": "https://github.com/kusaasira/uganda-geo-data",
        })
    return out


def convert_villages(data):
    """
    Source format: { id, name, parish }
    Output format: { id, name, level, level_name, parent_parish_native_id, ... }
    """
    out = []
    for item in data:
        out.append({
            "id": f"UG-VI-{item['id']}",
            "native_id": str(item["id"]),
            "name": item["name"].title(),
            "level": 6,
            "level_name": "Village",
            "country": "UG",
            "parent_parish_native_id": str(item["parish"]),
            "source": "kusaasira/uganda-geo-data",
            "source_url": "https://github.com/kusaasira/uganda-geo-data",
        })
    return out


def save(out_dir, filename, data):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  Saved {len(data):,} records → {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert Uganda geo data to Mipaka format")
    parser.add_argument("--src", required=True,
                        help="Path to kusaasira src/Uganda/Data/")
    parser.add_argument("--out", required=True,
                        help="Output path (e.g. data/UG/)")
    parser.add_argument("--counties", default=None,
                        help="Path to existing counties.json (for ID lookups)")
    args = parser.parse_args()

    print("Loading source files...")
    # Source repo uses "sub_counties.json" (with underscore)
    subcounties_raw = load(args.src, "sub_counties.json")
    parishes_raw = load(args.src, "parishes.json")
    villages_raw = load(args.src, "villages.json")

    # Load existing counties for cross-referencing
    counties_path = args.counties or os.path.join(args.out, "counties.json")
    if os.path.exists(counties_path):
        with open(counties_path, encoding="utf-8") as f:
            counties = json.load(f)
    else:
        counties = []
        print(
            "  Warning: counties.json not found — sub-county parent names won't be resolved")

    print("\nConverting...")
    subcounties = convert_subcounties(subcounties_raw, counties)
    parishes = convert_parishes(parishes_raw)
    villages = convert_villages(villages_raw)

    print("\nSaving...")
    save(args.out, "subcounties.json", subcounties)
    save(args.out, "parishes.json",    parishes)
    save(args.out, "villages.json",    villages)

    print(f"""
Summary
-------
Sub-counties : {len(subcounties):,}
Parishes     : {len(parishes):,}
Villages     : {len(villages):,}
Total records: {len(subcounties) + len(parishes) + len(villages):,}

Next step:
  python manage.py sync_uganda --levels subcounties parishes villages
""")


if __name__ == "__main__":
    main()
