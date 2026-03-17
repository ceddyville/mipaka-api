import json, os
from django.core.management.base import BaseCommand
from django.db import transaction
from divisions.models import Country, Division, DivisionLevel

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data", "CD")

LEVEL_MAP = {
    1: ("Province",  "Province"),
    2: ("Territory", "Territoire"),
}


class Command(BaseCommand):
    help = "Sync DRC administrative divisions from local JSON files (data/CD/)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--levels", nargs="+", type=str,
            choices=["provinces", "territories"],
            default=["provinces", "territories"],
        )

    def handle(self, *args, **options):
        levels = options["levels"]

        country, _ = Country.objects.get_or_create(
            code="CD",
            defaults={"name": "Democratic Republic of Congo", "native_name": "République Démocratique du Congo", "max_levels": 2},
        )
        for level, (name, name_sw) in LEVEL_MAP.items():
            DivisionLevel.objects.get_or_create(
                country=country, level=level,
                defaults={"name": name, "name_sw": name_sw}
            )

        with transaction.atomic():
            if "provinces"   in levels: self._sync_provinces(country)
            if "territories" in levels: self._sync_territories(country)

        self.stdout.write(self.style.SUCCESS("✓ DRC sync complete."))

    def _load(self, filename):
        path = os.path.join(BASE_DIR, filename)
        if not os.path.exists(path):
            self.stdout.write(self.style.ERROR(
                f"  {filename} not found in data/CD/\n"
                f"  Territories: download from https://data.humdata.org/dataset/cod-ab-cod\n"
                f"  Then run: python convert_hdx.py --country CD --out ./data/CD"
            ))
            return None
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def _sync_provinces(self, country):
        self.stdout.write("Syncing DRC provinces...")
        data = self._load("provinces.json")
        if data is None: return
        for item in data:
            obj, created = Division.objects.update_or_create(
                country=country, native_id=item["native_id"], level=1,
                defaults={"name": item["name"], "parent": None,
                          "source": item["source"], "source_url": item["source_url"]},
            )
            self.stdout.write(f"  {'[+]' if created else '[~]'} {obj.name}")

    def _sync_territories(self, country):
        self.stdout.write("Syncing DRC territories...")
        data = self._load("territories.json")
        if data is None: return
        province_map = {d.native_id: d for d in Division.objects.filter(country=country, level=1) if d.native_id}
        ok = skipped = 0
        for item in data:
            parent = province_map.get(item.get("parent_province_id"))
            if not parent: skipped += 1; continue
            Division.objects.update_or_create(
                country=country, native_id=item["native_id"], level=2,
                defaults={"name": item["name"], "parent": parent,
                          "source": item["source"], "source_url": item["source_url"]},
            )
            ok += 1
        self.stdout.write(f"  Synced {ok:,} territories." + (f" Skipped {skipped}." if skipped else ""))
