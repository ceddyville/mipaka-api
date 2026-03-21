import json
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from divisions.models import Country, Division, DivisionLevel

BASE_DIR = os.path.join(os.path.dirname(__file__),
                        "..", "..", "..", "data", "KE")

LEVEL_MAP = {
    1: ("County",       "Kaunti"),
    2: ("Constituency", "Jimbo"),
    3: ("Ward",         "Wadi"),
}

# Historical levels use high numbers to avoid collisions with current levels.
# 100 = Province (dissolved 2013), 101 = Historical District
HISTORICAL_LEVEL_MAP = {
    100: ("Province",  "Mkoa"),
    101: ("District",  "Wilaya"),
}


class Command(BaseCommand):
    help = "Sync Kenya administrative divisions from local JSON files (data/KE/)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--levels", nargs="+", type=str,
            choices=[
                "counties", "constituencies", "wards",
                "provinces", "districts_1963", "districts_1992", "districts_2007",
            ],
            default=["counties", "constituencies", "wards"],
        )

    def handle(self, *args, **options):
        levels = options["levels"]

        country, _ = Country.objects.get_or_create(
            code="KE",
            defaults={"name": "Kenya",
                      "native_name": "Kenya", "max_levels": 3},
        )
        for level, (name, name_sw) in LEVEL_MAP.items():
            DivisionLevel.objects.get_or_create(
                country=country, level=level,
                defaults={"name": name, "name_sw": name_sw}
            )

        with transaction.atomic():
            if "counties" in levels:
                self._sync_counties(country)
            if "constituencies" in levels:
                self._sync_constituencies(country)
            if "wards" in levels:
                self._sync_wards(country)
            if "provinces" in levels:
                self._sync_provinces(country)
            if "districts_1963" in levels:
                self._sync_historical_districts(
                    country, "districts_1963.json", "provinces")
            if "districts_1992" in levels:
                self._sync_historical_districts(
                    country, "districts_1992.json", "provinces")
            if "districts_2007" in levels:
                self._sync_historical_districts(
                    country, "districts_2007.json", "provinces")

        self.stdout.write(self.style.SUCCESS("✓ Kenya sync complete."))

    def _load(self, filename):
        path = os.path.join(BASE_DIR, filename)
        if not os.path.exists(path):
            self.stdout.write(self.style.ERROR(
                f"  {filename} not found in data/KE/\n"
                f"  Run: python convert_kenya.py --out ./data/KE"
            ))
            return None
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def _build_map(self, country, level):
        return {
            d.native_id: d
            for d in Division.objects.filter(country=country, level=level)
            if d.native_id
        }

    def _sync_counties(self, country):
        self.stdout.write("Syncing counties...")
        data = self._load("counties.json")
        if data is None:
            return
        for item in data:
            obj, created = Division.objects.update_or_create(
                country=country, native_id=item["native_id"], level=1,
                defaults={"name": item["name"], "parent": None,
                          "source": item["source"], "source_url": item["source_url"]},
            )
            self.stdout.write(f"  {'[+]' if created else '[~]'} {obj.name}")

    def _sync_constituencies(self, country):
        self.stdout.write("Syncing constituencies...")
        data = self._load("constituencies.json")
        if data is None:
            return
        county_map = self._build_map(country, 1)
        ok = skipped = 0
        for item in data:
            parent = county_map.get(item.get("parent_county_id"))
            if not parent:
                skipped += 1
                continue
            Division.objects.update_or_create(
                country=country, native_id=item["native_id"], level=2,
                defaults={"name": item["name"], "parent": parent,
                          "source": item["source"], "source_url": item["source_url"]},
            )
            ok += 1
        self.stdout.write(
            f"  Synced {ok:,} constituencies." + (f" Skipped {skipped}." if skipped else ""))

    def _sync_wards(self, country):
        self.stdout.write("Syncing wards...")
        data = self._load("wards.json")
        if data is None:
            return
        constituency_map = self._build_map(country, 2)
        ok = skipped = 0
        for item in data:
            parent = constituency_map.get(item.get("parent_constituency_id"))
            if not parent:
                skipped += 1
                continue
            Division.objects.update_or_create(
                country=country, native_id=item["native_id"], level=3,
                defaults={"name": item["name"], "parent": parent,
                          "source": item["source"], "source_url": item["source_url"]},
            )
            ok += 1
        self.stdout.write(
            f"  Synced {ok:,} wards." + (f" Skipped {skipped}." if skipped else ""))

    # ── Historical data ──────────────────────────────────────────────────

    def _sync_provinces(self, country):
        """Load dissolved provinces (level -1) from provinces.json."""
        self.stdout.write("Syncing historical provinces...")
        data = self._load("provinces.json")
        if data is None:
            return
        # Ensure Province level exists
        DivisionLevel.objects.get_or_create(
            country=country, level=100,
            defaults={"name": "Province", "name_sw": "Mkoa"},
        )
        for item in data:
            desc_parts = [item.get("notes", "")]
            if item.get("era"):
                desc_parts.append(
                    f"Era: {item['era']} ({item.get('era_years', '')})")
            description = ". ".join(p for p in desc_parts if p)

            obj, created = Division.objects.update_or_create(
                country=country, native_id=item["native_id"], level=100,
                defaults={
                    "name": item["name"],
                    "parent": None,
                    "is_active": False,
                    "description": description,
                    "source": item.get("source", "Wikipedia"),
                    "source_url": item.get("source_url", ""),
                },
            )
            self.stdout.write(f"  {'[+]' if created else '[~]'} {obj.name}")

    def _sync_historical_districts(self, country, filename, province_level):
        """Load historical districts (level -2) with parent province link."""
        self.stdout.write(f"Syncing historical districts from {filename}...")
        data = self._load(filename)
        if data is None:
            return
        # Ensure District level exists
        DivisionLevel.objects.get_or_create(
            country=country, level=101,
            defaults={"name": "District", "name_sw": "Wilaya"},
        )
        # Build province lookup by name
        province_map = {
            d.name: d
            for d in Division.objects.filter(country=country, level=100)
        }
        ok = skipped = 0
        for item in data:
            parent = province_map.get(item.get("parent_province"))
            if not parent:
                self.stdout.write(
                    self.style.WARNING(
                        f"  [!] Province '{item.get('parent_province')}' "
                        f"not found for {item['name']} — skipping"))
                skipped += 1
                continue

            desc_parts = []
            if item.get("notes"):
                desc_parts.append(item["notes"])
            if item.get("headquarters"):
                desc_parts.append(f"Headquarters: {item['headquarters']}")
            if item.get("era"):
                desc_parts.append(
                    f"Era: {item['era']} ({item.get('era_years', '')})")
            if item.get("successor_county"):
                desc_parts.append(
                    f"Successor: {item['successor_county']} County")
            description = ". ".join(desc_parts)

            Division.objects.update_or_create(
                country=country, native_id=item["native_id"], level=101,
                defaults={
                    "name": item["name"],
                    "parent": parent,
                    "is_active": False,
                    "description": description,
                    "source": item.get("source", "Wikipedia"),
                    "source_url": item.get("source_url", ""),
                },
            )
            ok += 1
        self.stdout.write(
            f"  Synced {ok:,} districts from {filename}."
            + (f" Skipped {skipped}." if skipped else ""))
