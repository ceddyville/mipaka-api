import json
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from divisions.models import Country, Division, DivisionLevel

BASE_DIR = os.path.join(os.path.dirname(__file__),
                        "..", "..", "..", "data", "BI")

LEVEL_MAP = {
    1: ("Province", "Intara"),
    2: ("Commune",  "Komine"),
    3: ("Colline",  "Umusozi"),
}


class Command(BaseCommand):
    help = "Sync Burundi administrative divisions from local JSON files (data/BI/)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--levels", nargs="+", type=str,
            choices=["provinces", "communes", "collines"],
            default=["provinces"],
        )
        parser.add_argument(
            "--legacy", action="store_true",
            help="Use pre-2025 18-province structure instead of new 5-province structure"
        )

    def handle(self, *args, **options):
        levels = options["levels"]
        legacy = options["legacy"]

        country, _ = Country.objects.get_or_create(
            code="BI",
            defaults={"name": "Burundi",
                      "native_name": "Uburundi", "max_levels": 3},
        )
        for level, (name, name_sw) in LEVEL_MAP.items():
            DivisionLevel.objects.get_or_create(
                country=country, level=level,
                defaults={"name": name, "name_sw": name_sw}
            )

        with transaction.atomic():
            if "provinces" in levels:
                self._sync_provinces(country, legacy)
            if "communes" in levels:
                self._sync_communes(country)
            if "collines" in levels:
                self._sync_collines(country)

        self.stdout.write(self.style.SUCCESS("✓ Burundi sync complete."))

    def _load(self, filename):
        path = os.path.join(BASE_DIR, filename)
        if not os.path.exists(path):
            self.stdout.write(self.style.ERROR(
                f"  {filename} not found in data/BI/\n"
                f"  Communes/Collines: download from https://data.humdata.org/dataset/burundi-admin-bounderies\n"
                f"  Then run: python convert_hdx.py --country BI --out ./data/BI"
            ))
            return None
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def _sync_provinces(self, country, legacy=False):
        filename = "provinces_legacy_18.json" if legacy else "provinces.json"
        label = "18-province legacy" if legacy else "5-province (2025)"
        self.stdout.write(f"Syncing provinces ({label})...")
        data = self._load(filename)
        if data is None:
            return
        # Clear existing before re-seeding if switching structure
        Division.objects.filter(country=country, level=1).delete()
        for item in data:
            obj, created = Division.objects.update_or_create(
                country=country, native_id=item["native_id"], level=1,
                defaults={"name": item["name"], "parent": None,
                          "source": item["source"], "source_url": item["source_url"]},
            )
            self.stdout.write(f"  {'[+]' if created else '[~]'} {obj.name}")

    def _sync_communes(self, country):
        self.stdout.write("Syncing communes...")
        data = self._load("communes.json")
        if data is None:
            return
        province_map = {d.native_id: d for d in Division.objects.filter(
            country=country, level=1) if d.native_id}
        ok = skipped = 0
        for item in data:
            parent = province_map.get(item.get("parent_province_id"))
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
            f"  Synced {ok:,} communes." + (f" Skipped {skipped}." if skipped else ""))

    def _sync_collines(self, country):
        self.stdout.write("Syncing collines...")
        data = self._load("collines.json")
        if data is None:
            return
        commune_map = {d.native_id: d for d in Division.objects.filter(
            country=country, level=2) if d.native_id}
        ok = skipped = 0
        for item in data:
            parent = commune_map.get(item.get("parent_commune_id"))
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
            f"  Synced {ok:,} collines." + (f" Skipped {skipped}." if skipped else ""))
