import json
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from divisions.models import Country, Division, DivisionLevel

BASE_DIR = os.path.join(os.path.dirname(__file__),
                        "..", "..", "..", "data", "TZ")

LEVEL_MAP = {
    1: ("Region",   "Mkoa"),
    2: ("District", "Wilaya"),
    3: ("Ward",     "Kata"),
}


class Command(BaseCommand):
    help = "Sync Tanzania administrative divisions from local JSON files (data/TZ/)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--levels", nargs="+", type=str,
            choices=["regions", "districts", "wards"],
            default=["regions", "districts", "wards"],
        )

    def handle(self, *args, **options):
        levels = options["levels"]

        country, _ = Country.objects.get_or_create(
            code="TZ",
            defaults={"name": "Tanzania",
                      "native_name": "Tanzania", "max_levels": 3},
        )
        for level, (name, name_sw) in LEVEL_MAP.items():
            DivisionLevel.objects.get_or_create(
                country=country, level=level,
                defaults={"name": name, "name_sw": name_sw}
            )

        with transaction.atomic():
            if "regions" in levels:
                self._sync_regions(country)
            if "districts" in levels:
                self._sync_districts(country)
            if "wards" in levels:
                self._sync_wards(country)

        self.stdout.write(self.style.SUCCESS("✓ Tanzania sync complete."))

    def _load(self, filename):
        path = os.path.join(BASE_DIR, filename)
        if not os.path.exists(path):
            self.stdout.write(self.style.ERROR(
                f"  {filename} not found in data/TZ/\n"
                f"  Run: git clone https://github.com/Kijacode/Tanzania_Geo_Data.git\n"
                f"  Then: python convert_tanzania.py --src ./Tanzania_Geo_Data --out ./data/TZ"
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

    def _sync_regions(self, country):
        self.stdout.write("Syncing regions...")
        data = self._load("regions.json")
        if data is None:
            return
        for item in data:
            obj, created = Division.objects.update_or_create(
                country=country, native_id=item["native_id"], level=1,
                defaults={"name": item["name"], "parent": None,
                          "source": item["source"], "source_url": item["source_url"]},
            )
            self.stdout.write(f"  {'[+]' if created else '[~]'} {obj.name}")

    def _sync_districts(self, country):
        self.stdout.write("Syncing districts...")
        data = self._load("districts.json")
        if data is None:
            return
        region_map = self._build_map(country, 1)
        ok = skipped = 0
        for item in data:
            parent = region_map.get(item.get("parent_region_id"))
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
            f"  Synced {ok:,} districts." + (f" Skipped {skipped}." if skipped else ""))

    def _sync_wards(self, country):
        self.stdout.write("Syncing wards...")
        data = self._load("wards.json")
        if data is None:
            return
        district_map = self._build_map(country, 2)
        ok = skipped = 0
        for item in data:
            parent = district_map.get(item.get("parent_district_id"))
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
