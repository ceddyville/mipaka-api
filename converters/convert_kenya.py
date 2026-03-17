"""
Kenya Area Data Converter
=========================
Downloads and converts kenyaareadata.vercel.app data into Mipaka per-level JSON files.

Source: https://kenyaareadata.vercel.app
API Key: keyPub1569gsvndc123kg9sjhg (public key, free)

Usage:
  python convert_kenya.py --out ./data/KE

Or if you already have the raw JSON saved:
  python convert_kenya.py --src ./kenya_raw.json --out ./data/KE

Output files:
  data/KE/counties.json         (47 counties)
  data/KE/constituencies.json   (290 constituencies)
  data/KE/wards.json            (1,450 wards)

Source response format:
  {
    "Mombasa": {
      "Changamwe": ["Port Reitz", "Kipevu", "Airport", "Changamwe", "Chaani"],
      "Jomvu": ["Jomvu Kuu", "Miritini", "Mikindani"],
      ...
    },
    "Kwale": { ... },
    ...
  }
"""

import json
import os
import sys
import argparse
import urllib.request

API_URL    = "https://kenyaareadata.vercel.app/api/areas?apiKey=keyPub1569gsvndc123kg9sjhg"
SOURCE     = "kenyaareadata.vercel.app"
SOURCE_URL = "https://kenyaareadata.vercel.app"


def fetch(url):
    print(f"Fetching {url} ...")
    req = urllib.request.Request(url, headers={"User-Agent": "mipaka-converter/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def convert(raw):
    counties        = []
    constituencies  = []
    wards           = []

    county_counter        = 1
    constituency_counter  = 1
    ward_counter          = 1

    for county_name, constituencies_data in sorted(raw.items()):
        county_native_id = str(county_counter)

        counties.append({
            "id":         f"KE-CO-{county_counter:03d}",
            "native_id":  county_native_id,
            "name":       county_name.title(),
            "level":      1,
            "level_name": "County",
            "country":    "KE",
            "source":     SOURCE,
            "source_url": SOURCE_URL,
        })

        for constituency_name, wards_list in sorted(constituencies_data.items()):
            constituency_native_id = str(constituency_counter)

            constituencies.append({
                "id":               f"KE-CN-{constituency_counter:04d}",
                "native_id":        constituency_native_id,
                "name":             constituency_name.title(),
                "level":            2,
                "level_name":       "Constituency",
                "country":          "KE",
                "parent_county_id": county_native_id,
                "source":           SOURCE,
                "source_url":       SOURCE_URL,
            })

            for ward_name in sorted(wards_list):
                wards.append({
                    "id":                        f"KE-W-{ward_counter:05d}",
                    "native_id":                 str(ward_counter),
                    "name":                      ward_name.title(),
                    "level":                     3,
                    "level_name":                "Ward",
                    "country":                   "KE",
                    "parent_constituency_id":    constituency_native_id,
                    "source":                    SOURCE,
                    "source_url":                SOURCE_URL,
                })
                ward_counter += 1

            constituency_counter += 1
        county_counter += 1

    return counties, constituencies, wards


def save(out_dir, filename, data):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✓ {filename:<25} {len(data):>6,} records  →  {path}")


def main():
    parser = argparse.ArgumentParser(description="Convert Kenya area data to Mipaka format")
    parser.add_argument("--src",  default=None, help="Path to saved raw JSON (skip download)")
    parser.add_argument("--out",  required=True, help="Output directory e.g. data/KE/")
    parser.add_argument("--save-raw", default=None, help="Also save raw API response to this path")
    args = parser.parse_args()

    # Load or fetch
    if args.src:
        print(f"Loading {args.src}...")
        with open(args.src, encoding="utf-8") as f:
            raw = json.load(f)
    else:
        raw = fetch(API_URL)
        if args.save_raw:
            with open(args.save_raw, "w", encoding="utf-8") as f:
                json.dump(raw, f, indent=2, ensure_ascii=False)
            print(f"  Raw response saved to {args.save_raw}")

    print(f"\n  {len(raw)} counties found in source.\n")

    # Convert
    print("Converting...")
    counties, constituencies, wards = convert(raw)

    # Save
    print("\nSaving...")
    save(args.out, "counties.json",       counties)
    save(args.out, "constituencies.json", constituencies)
    save(args.out, "wards.json",          wards)

    total = len(counties) + len(constituencies) + len(wards)
    print(f"""
Summary
-------
Counties        : {len(counties):>6,}
Constituencies  : {len(constituencies):>6,}
Wards           : {len(wards):>6,}
─────────────────────────
Total           : {total:>6,}

Next step:
  python manage.py sync_kenya --levels counties constituencies wards
""")


if __name__ == "__main__":
    main()
