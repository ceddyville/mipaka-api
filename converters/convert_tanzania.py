"""
Tanzania Geo Data Converter
============================
Converts Kijacode/Tanzania_Geo_Data files into Mipaka per-level JSON files.

Source repo: https://github.com/Kijacode/Tanzania_Geo_Data

Clone the repo:
  git clone https://github.com/Kijacode/Tanzania_Geo_Data.git

Then run:
  python convert_tanzania.py --src ./Tanzania_Geo_Data --out ./data/TZ

Source file schemas:

  Regions.json — one of two possible formats, we handle both:
    Format A (array of strings):
      ["Arusha", "Dar es Salaam", ...]

    Format B (array of objects):
      [{"id": 1, "name": "Arusha"}, ...]

  Districts.json — one of two possible formats:
    Format A (array of objects with region reference):
      [{"id": 1, "name": "Arusha City", "region": "Arusha"}, ...]

    Format B (GeoJSON):
      {"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"Region": "Arusha Region", "District": "Arusha City"}}, ...
      ]}

  Wards.json — GeoJSON FeatureCollection (confirmed from search results):
    {"type": "FeatureCollection", "features": [
      {"type": "Feature", "properties": {"District": "Bahi District", "Ward": "Babayu"}, "geometry": null},
      ...
    ]}

Output files:
  data/TZ/regions.json
  data/TZ/districts.json
  data/TZ/wards.json
"""

import json
import os
import argparse

SOURCE = "Kijacode/Tanzania_Geo_Data"
SOURCE_URL = "https://github.com/Kijacode/Tanzania_Geo_Data"


def clean(name):
    """Normalize name — strip suffixes like ' Region', ' District', title-case."""
    name = name.strip()
    for suffix in [" Region", " District"]:
        if name.endswith(suffix):
            name = name[: -len(suffix)].strip()
    return name.title()


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def parse_regions(data):
    """Handles string arrays, object arrays, and GeoJSON-like features."""
    out = []
    # Handle GeoJSON-like format: {"name": "Regions", "features": [...]}
    if isinstance(data, dict) and "features" in data:
        entries = data["features"]
        for i, feat in enumerate(entries, start=1):
            props = feat.get("properties", {})
            name = clean(props.get("region", props.get("name", "")))
            out.append({
                "id":         f"TZ-R-{str(i).zfill(3)}",
                "native_id":  str(i),
                "name":       name,
                "level":      1,
                "level_name": "Region",
                "country":    "TZ",
                "source":     SOURCE,
                "source_url": SOURCE_URL,
            })
        return out
    entries = data if isinstance(data, list) else data.get(
        "regions", data.get("data", []))
    for i, item in enumerate(entries, start=1):
        if isinstance(item, str):
            name = clean(item)
            native_id = str(i)
        else:
            name = clean(item.get("name", item.get("region", "")))
            native_id = str(item.get("id", i))
        out.append({
            "id":         f"TZ-R-{native_id.zfill(3)}",
            "native_id":  native_id,
            "name":       name,
            "level":      1,
            "level_name": "Region",
            "country":    "TZ",
            "source":     SOURCE,
            "source_url": SOURCE_URL,
        })
    return out


def parse_districts(data, region_name_to_native_id):
    """Handles object arrays and GeoJSON."""
    out = []
    counter = 1

    # GeoJSON / GeoJSON-like format (with "type": "FeatureCollection" or "features" key)
    if isinstance(data, dict) and (data.get("type") == "FeatureCollection" or "features" in data):
        features = data.get("features", [])
        for feat in features:
            props = feat.get("properties", {})
            region_name = clean(props.get("Region", props.get("region", "")))
            district_name = clean(
                props.get("District", props.get("district", "")))
            parent_id = region_name_to_native_id.get(region_name)
            out.append({
                "id":               f"TZ-D-{str(counter).zfill(4)}",
                "native_id":        str(counter),
                "name":             district_name,
                "level":            2,
                "level_name":       "District",
                "country":          "TZ",
                "parent_region_id": parent_id,
                "source":           SOURCE,
                "source_url":       SOURCE_URL,
            })
            counter += 1
        return out

    # Array of objects format
    entries = data if isinstance(data, list) else data.get(
        "districts", data.get("data", []))
    for item in entries:
        region_name = clean(item.get("region", item.get("Region", "")))
        district_name = clean(item.get("name", item.get(
            "district", item.get("District", ""))))
        native_id = str(item.get("id", counter))
        parent_id = region_name_to_native_id.get(region_name)
        out.append({
            "id":               f"TZ-D-{native_id.zfill(4)}",
            "native_id":        native_id,
            "name":             district_name,
            "level":            2,
            "level_name":       "District",
            "country":          "TZ",
            "parent_region_id": parent_id,
            "source":           SOURCE,
            "source_url":       SOURCE_URL,
        })
        counter += 1
    return out


def parse_wards(data, district_name_to_native_id):
    """Handles GeoJSON FeatureCollection (confirmed format)."""
    out = []
    counter = 1

    features = []
    if isinstance(data, dict) and data.get("type") == "FeatureCollection":
        features = data.get("features", [])
    elif isinstance(data, list):
        features = data

    for feat in features:
        props = feat.get("properties", feat) if isinstance(feat, dict) else {}
        district_name = clean(props.get("District", props.get("district", "")))
        ward_name = props.get("Ward", props.get("ward", "")).strip().title()
        parent_id = district_name_to_native_id.get(district_name)
        out.append({
            "id":                f"TZ-W-{str(counter).zfill(5)}",
            "native_id":         str(counter),
            "name":              ward_name,
            "level":             3,
            "level_name":        "Ward",
            "country":           "TZ",
            "parent_district_id": parent_id,
            "source":            SOURCE,
            "source_url":        SOURCE_URL,
        })
        counter += 1
    return out


def save(out_dir, filename, data):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✓ {filename:<20} {len(data):>6,} records  →  {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert Tanzania_Geo_Data to Mipaka format")
    parser.add_argument("--src", required=True,
                        help="Path to cloned Tanzania_Geo_Data repo")
    parser.add_argument("--out", required=True,
                        help="Output directory (e.g. data/TZ/)")
    args = parser.parse_args()

    src = args.src
    out = args.out

    # --- Load source files ---
    regions_path = os.path.join(src, "Regions.json")
    districts_path = os.path.join(src, "Districts.json")
    wards_path = os.path.join(src, "Wards.json")

    for p in [regions_path, districts_path]:
        if not os.path.exists(p):
            print(f"ERROR: {p} not found.")
            print(f"  Clone: git clone https://github.com/Kijacode/Tanzania_Geo_Data.git")
            return

    print("Loading source files...")
    regions_raw = load(regions_path)
    districts_raw = load(districts_path)
    wards_raw = load(wards_path) if os.path.exists(wards_path) else []

    # --- Convert ---
    print("\nConverting regions...")
    regions = parse_regions(regions_raw)
    region_name_to_id = {r["name"]: r["native_id"] for r in regions}
    print(f"  {len(regions)} regions found.")

    print("Converting districts...")
    districts = parse_districts(districts_raw, region_name_to_id)
    district_name_to_id = {d["name"]: d["native_id"] for d in districts}
    unlinked = sum(1 for d in districts if not d["parent_region_id"])
    if unlinked:
        print(
            f"  ⚠ {unlinked} districts could not be linked to a region (name mismatch — check manually)")
    print(f"  {len(districts)} districts found.")

    print("Converting wards...")
    wards = parse_wards(wards_raw, district_name_to_id)
    unlinked = sum(1 for w in wards if not w["parent_district_id"])
    if unlinked:
        print(
            f"  ⚠ {unlinked} wards could not be linked to a district (name mismatch — check manually)")
    print(f"  {len(wards)} wards found.")

    # --- Save ---
    print("\nSaving...")
    save(out, "regions.json",   regions)
    save(out, "districts.json", districts)
    save(out, "wards.json",     wards)

    total = len(regions) + len(districts) + len(wards)
    print(f"""
Summary
-------
Regions   : {len(regions):>6,}
Districts : {len(districts):>6,}
Wards     : {len(wards):>6,}
─────────────────
Total     : {total:>6,}

Next step:
  python manage.py sync_tanzania --levels regions districts wards
""")


if __name__ == "__main__":
    main()
