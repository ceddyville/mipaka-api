import json
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from divisions.models import Country, Division, DivisionLevel

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data", "RW")

LEVEL_MAP = {
    1: ("Province", "Intara"),
    2: ("District", "Akarere"),
    3: ("Sector",   "Umurenge"),
    4: ("Cell",     "Akagari"),
    5: ("Village",  "Umudugudu"),
}

ALL_LEVELS = ["provinces", "districts", "sectors", "cells", "villages"]


class Command(BaseCommand):
    help = "Sync Rwanda administrative divisions from local JSON files (data/RW/)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--levels", nargs="+", type=str,
            choices=ALL_LEVELS,
            default=["provinces", "districts", "sectors", "cells"],
            help="Which levels to sync (default: all except villages)",
        )

    def handle(self, *args, **options):
        levels = options["levels"]

        country, _ = Country.objects.get_or_create(
            code="RW",
            defaults={"name": "Rwanda", "native_name": "Rwanda", "max_levels": 5},
        )
        for level, (name, name_sw) in LEVEL_MAP.items():
            DivisionLevel.objects.get_or_create(
                country=country, level=level,
                defaults={"name": name, "name_sw": name_sw}
            )

        with transaction.atomic():
            if "provinces" in levels: self._sync_provinces(country)
            if "districts" in levels: self._sync_districts(country)
            if "sectors"   in levels: self._sync_sectors(country)
            if "cells"     in levels: self._sync_cells(country)
            if "villages"  in levels: self._sync_villages(country)

        self.stdout.write(self.style.SUCCESS("✓ Rwanda sync complete."))

    # ── HELPERS ───────────────────────────────────────────────────────────────

    def _load(self, filename):
        path = os.path.join(BASE_DIR, filename)
        if not os.path.exists(path):
            self.stdout.write(self.style.ERROR(
                f"  {filename} not found in data/RW/\n"
                f"  Run: python convert_rwanda.py"
                f" --src ./locations.json --out ./data/RW"
            ))
            return None
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def _build_map(self, country, level):
        """Return native_id → Division object for a given level."""
        return {
            d.native_id: d
            for d in Division.objects.filter(country=country, level=level)
            if d.native_id
        }

    # ── PROVINCES ─────────────────────────────────────────────────────────────

    def _sync_provinces(self, country):
        self.stdout.write("Syncing provinces...")
        data = self._load("provinces.json")
        if data is None: return
        for item in data:
            obj, created = Division.objects.update_or_create(
                country=country, native_id=item["native_id"], level=1,
                defaults={"name": item["name"], "parent": None,
                          "source": item["source"], "source_url": item["source_url"]},
            )
            self.stdout.write(f"  {'[+]' if created else '[~]'} {obj.name}")

    # ── DISTRICTS ─────────────────────────────────────────────────────────────

    def _sync_districts(self, country):
        self.stdout.write("Syncing districts...")
        data = self._load("districts.json")
        if data is None: return
        province_map = self._build_map(country, 1)
        ok = skipped = 0
        for item in data:
            parent = province_map.get(item["parent_province_id"])
            if not parent:
                skipped += 1
                continue
            Division.objects.update_or_create(
                country=country, native_id=item["native_id"], level=2,
                defaults={"name": item["name"], "parent": parent,
                          "source": item["source"], "source_url": item["source_url"]},
            )
            ok += 1
        self.stdout.write(f"  Synced {ok:,} districts." + (f" Skipped {skipped}." if skipped else ""))

    # ── SECTORS ───────────────────────────────────────────────────────────────

    def _sync_sectors(self, country):
        self.stdout.write("Syncing sectors...")
        data = self._load("sectors.json")
        if data is None: return
        district_map = self._build_map(country, 2)
        ok = skipped = 0
        for item in data:
            parent = district_map.get(item["parent_district_id"])
            if not parent:
                skipped += 1
                continue
            Division.objects.update_or_create(
                country=country, native_id=item["native_id"], level=3,
                defaults={"name": item["name"], "parent": parent,
                          "source": item["source"], "source_url": item["source_url"]},
            )
            ok += 1
        self.stdout.write(f"  Synced {ok:,} sectors." + (f" Skipped {skipped}." if skipped else ""))

    # ── CELLS ─────────────────────────────────────────────────────────────────

    def _sync_cells(self, country):
        self.stdout.write("Syncing cells...")
        data = self._load("cells.json")
        if data is None: return
        sector_map = self._build_map(country, 3)
        ok = skipped = 0
        for item in data:
            parent = sector_map.get(item["parent_sector_id"])
            if not parent:
                skipped += 1
                continue
            Division.objects.update_or_create(
                country=country, native_id=item["native_id"], level=4,
                defaults={"name": item["name"], "parent": parent,
                          "source": item["source"], "source_url": item["source_url"]},
            )
            ok += 1
        self.stdout.write(f"  Synced {ok:,} cells." + (f" Skipped {skipped}." if skipped else ""))

    # ── VILLAGES ──────────────────────────────────────────────────────────────

    def _sync_villages(self, country):
        self.stdout.write("Syncing villages (bulk)...")
        data = self._load("villages.json")
        if data is None: return
        cell_map = self._build_map(country, 4)
        existing = set(
            Division.objects.filter(country=country, level=5)
            .values_list("native_id", flat=True)
        )
        to_create = []
        skipped = 0
        for item in data:
            if item["native_id"] in existing:
                continue
            parent = cell_map.get(item["parent_cell_id"])
            if not parent:
                skipped += 1
                continue
            to_create.append(Division(
                country=country,
                native_id=item["native_id"],
                name=item["name"],
                level=5,
                parent=parent,
                source=item["source"],
                source_url=item["source_url"],
            ))
        chunk = 500
        for i in range(0, len(to_create), chunk):
            Division.objects.bulk_create(to_create[i:i + chunk], ignore_conflicts=True)
            self.stdout.write(
                f"  Inserted chunk {i // chunk + 1}/{(len(to_create) - 1) // chunk + 1}..."
            )
        self.stdout.write(
            f"  Synced {len(to_create):,} villages." + (f" Skipped {skipped}." if skipped else "")
        )
