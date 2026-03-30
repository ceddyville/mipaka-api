"""
Convert Tanzania ward data from the 'mtaa' package into Mipaka-standard JSON.

Source: https://github.com/Kalebu/mtaa (MIT license)
        https://github.com/HackEAC/tanzania-locations-db (GPL-3.0, raw data)

Usage:
    python converters/convert_tanzania_wards.py

Output:
    data/TZ/wards.json  — ~3,900 ward records (level 3)
    
Also rewrites data/TZ/districts.json to add any new districts from mtaa
that weren't in the original Kijacode source.
"""

import json
import os
from mtaa import tanzania

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "TZ")

SOURCE = "HackEAC/tanzania-locations-db + Kalebu/mtaa"
SOURCE_URL = "https://github.com/HackEAC/tanzania-locations-db"


# ── Region name mapping (mtaa name → our name) ──────────────────────────

REGION_NAME_MAP = {
    "Dar-es-salaam": "Dar Es Salaam",
}


# ── District name mapping (mtaa name → our name) ────────────────────────
# For "cbd" districts that are sub-parts of a city, we merge their wards
# into the parent city/municipal district in our data.

# Format: (mtaa_region, mtaa_district) → our_district_name
# If value is None, skip this district (e.g., duplicates)
DISTRICT_NAME_MAP = {
    # "cbd" districts → merge into the main city/municipal district
    ("Arusha", "Arusha cbd"): "Arusha",
    ("Dar Es Salaam", "Ilala cbd"): "Ilala Municipal",
    ("Dar Es Salaam", "Ilala"): "Ilala Municipal",
    ("Dar Es Salaam", "Kinondoni"): "Kinondoni Municipal",
    ("Dar Es Salaam", "Temeke"): "Temeke Municipal",
    ("Dar Es Salaam", "Ubungo"): "Ubungo Municipal",
    ("Dar Es Salaam", "Kigamboni"): "Kigamboni Municipal",
    ("Dodoma", "Dodoma\ncbd"): "Dodoma Municipal",
    ("Dodoma", "Dodoma"): "Dodoma Municipal",
    ("Geita", "Geita"): "Geita Town",
    ("Iringa", "Iringa cbd"): "Iringa",
    ("Kagera", "Bukoba cbd"): "Bukoba",
    ("Katavi", "Mpanda -cbd"): "Mpanda",
    ("Kigoma", "Kigoma\ncbd"): "Kigoma",
    ("Kilimanjaro", "Moshi cbd"): "Moshi",
    ("Lindi", "Lindi  cbd"): "Lindi",
    ("Manyara", "Babati cbd"): "Babati",
    ("Manyara", "Hanang'"): "Hanang",
    ("Mara", "Musoma cbd"): "Musoma",
    ("Mbeya", "Mbeya cbd"): "Mbeya",
    ("Mbeya", "Mbarali"): "Mbarali City",
    ("Morogoro", "Morogoro\ncbd"): "Morogoro",
    ("Mtwara", "Mtwara cbd"): "Mtwara",
    ("Mwanza", "Nyamagana"): "Nyamagana Municipal",
    ("Mwanza", "Ilemela"): "Ilemela Municipal",
    ("Njombe", "Njombe cbd"): "Njombe",
    ("Pwani", "Kibaha cbd"): "Kibaha",
    ("Rukwa", "Sumbawanga\ncbd"): "Sumbawanga",
    ("Ruvuma", "Songea cbd"): "Songea",
    ("Shinyanga", "Shinyanga\ncbd"): "Shinyanga",
    ("Singida", "Singida cbd"): "Singida",
    ("Tanga", "Tanga"): "Tanga City",
    # Arumeru is the old name for Meru district
    ("Arusha", "Arumeru"): "Meru",
    # Case difference
    ("Geita", "Nyang'hwale"): "Nyang'Hwale",
}

# Districts in mtaa that don't exist in our data — will be added
# (region_name, mtaa_district_name) → our clean name
NEW_DISTRICTS = {
    ("Katavi", "Tanganyika"): "Tanganyika",
    ("Njombe", "Wanging'o\nmbe"): "Wanging'ombe",
    ("Pwani", "Kibiti"): "Kibiti",
    ("Tabora", "Tabora cbd"): "Tabora Urban",
    ("Tanga", "Tanga cbd"): "Tanga Urban",
}


def load_existing():
    """Load existing regions and districts."""
    with open(os.path.join(DATA_DIR, "regions.json"), encoding="utf-8") as f:
        regions = json.load(f)
    with open(os.path.join(DATA_DIR, "districts.json"), encoding="utf-8") as f:
        districts = json.load(f)
    return regions, districts


def build_lookups(regions, districts):
    """Build lookup dictionaries."""
    region_name_to_id = {r["name"]: r["native_id"] for r in regions}
    dist_key_to_id = {}  # (region_name, district_name) -> native_id
    region_id_to_name = {r["native_id"]: r["name"] for r in regions}

    for d in districts:
        reg_name = region_id_to_name.get(d["parent_region_id"], "?")
        dist_key_to_id[(reg_name, d["name"])] = d["native_id"]

    return region_name_to_id, dist_key_to_id


def get_next_district_id(districts):
    """Get next sequential native_id for districts."""
    max_id = max(int(d["native_id"]) for d in districts)
    return max_id + 1


def normalize_ward_name(name):
    """Clean up ward names."""
    name = name.strip()
    name = name.replace("\n", " ")
    # Title case if all caps or all lower
    if name.isupper() or name.islower():
        name = name.title()
    return name


def main():
    regions, districts = load_existing()
    region_name_to_id, dist_key_to_id = build_lookups(regions, districts)

    next_dist_id = get_next_district_id(districts)
    new_districts_added = []

    wards = []
    ward_id = 1
    skipped_districts = set()

    mtaa_regions = sorted(tanzania)

    for mtaa_region in mtaa_regions:
        our_region = REGION_NAME_MAP.get(mtaa_region, mtaa_region)
        region_id = region_name_to_id.get(our_region)

        if not region_id:
            print(f"  [!] Region '{our_region}' not in our data — skipping")
            continue

        region = tanzania.get(mtaa_region)
        mtaa_districts = [d for d in region.districts if d != "ward_post_code"]

        for mtaa_dist in mtaa_districts:
            # Resolve district name
            map_key = (our_region, mtaa_dist)
            our_dist_name = DISTRICT_NAME_MAP.get(map_key, mtaa_dist)

            if our_dist_name is None:
                continue  # Explicitly skip

            dist_id = dist_key_to_id.get((our_region, our_dist_name))

            if not dist_id:
                # Check if it's a known new district
                if map_key in NEW_DISTRICTS:
                    # Add new district
                    dist_id = str(next_dist_id)
                    clean_name = NEW_DISTRICTS[map_key]
                    new_dist = {
                        "id": f"TZ-D-{next_dist_id:04d}",
                        "native_id": dist_id,
                        "name": clean_name,
                        "level": 2,
                        "level_name": "District",
                        "country": "TZ",
                        "parent_region_id": region_id,
                        "source": SOURCE,
                        "source_url": SOURCE_URL,
                    }
                    districts.append(new_dist)
                    dist_key_to_id[(our_region, new_dist["name"])] = dist_id
                    new_districts_added.append(new_dist["name"])
                    next_dist_id += 1
                    print(
                        f"  [+] New district: {new_dist['name']} ({our_region})")
                else:
                    if map_key not in skipped_districts:
                        print(
                            f"  [!] District '{mtaa_dist}' in {our_region} — no mapping, skipping")
                        skipped_districts.add(map_key)
                    continue

            # Get wards for this district
            district_obj = region.districts.get(mtaa_dist)
            if district_obj is None:
                continue

            try:
                ward_list = list(district_obj.wards)
            except Exception:
                continue

            for ward_name in ward_list:
                if ward_name == "ward_post_code":
                    continue

                clean_name = normalize_ward_name(ward_name)
                if not clean_name:
                    continue

                wards.append({
                    "id": f"TZ-W-{ward_id:05d}",
                    "native_id": str(ward_id),
                    "name": clean_name,
                    "level": 3,
                    "level_name": "Ward",
                    "country": "TZ",
                    "parent_district_id": dist_id,
                    "source": SOURCE,
                    "source_url": SOURCE_URL,
                })
                ward_id += 1

    # Write wards
    wards_path = os.path.join(DATA_DIR, "wards.json")
    with open(wards_path, "w", encoding="utf-8") as f:
        json.dump(wards, f, indent=2, ensure_ascii=False)
    print(f"\nWrote {len(wards):,} wards to {wards_path}")

    # Update districts if new ones were added
    if new_districts_added:
        districts_path = os.path.join(DATA_DIR, "districts.json")
        with open(districts_path, "w", encoding="utf-8") as f:
            json.dump(districts, f, indent=2, ensure_ascii=False)
        print(
            f"Updated districts.json with {len(new_districts_added)} new districts: {new_districts_added}")

    # Summary
    print(f"\nSummary:")
    print(f"  Wards: {len(wards):,}")
    print(f"  New districts: {len(new_districts_added)}")
    if skipped_districts:
        print(f"  Skipped unmapped districts: {len(skipped_districts)}")


if __name__ == "__main__":
    main()
