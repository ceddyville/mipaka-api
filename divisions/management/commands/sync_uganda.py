import json
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from divisions.models import Country, Division, DivisionLevel

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data", "UG")

LEVEL_MAP = {
    1: ("Region",     "Mkoa"),
    2: ("District",   "Wilaya"),
    3: ("County",     "Kaunti"),
    4: ("Sub-county", ""),
    5: ("Parish",     ""),
    6: ("Village",    "Kijiji"),
}

ALL_LEVELS = ["regions", "districts", "counties", "subcounties", "parishes", "villages"]


class Command(BaseCommand):
    help = "Sync Uganda administrative divisions from local JSON files"

    def add_arguments(self, parser):
        parser.add_argument(
            "--levels", nargs="+", type=str,
            choices=ALL_LEVELS,
            default=["regions", "districts", "counties"],
            help="Which levels to sync (default: regions districts counties)",
        )
        parser.add_argument(
            "--skip-verification-flags", action="store_true",
            help="Also import county entries flagged as needing verification",
        )

    def handle(self, *args, **options):
        levels = options["levels"]
        skip_flags = options["skip_verification_flags"]

        country, _ = Country.objects.get_or_create(
            code="UG",
            defaults={"name": "Uganda", "native_name": "Uganda", "max_levels": 6},
        )
        for level, (name, name_sw) in LEVEL_MAP.items():
            DivisionLevel.objects.get_or_create(
                country=country, level=level,
                defaults={"name": name, "name_sw": name_sw}
            )

        with transaction.atomic():
            if "regions"     in levels: self._sync_regions(country)
            if "districts"   in levels: self._sync_districts(country)
            if "counties"    in levels: self._sync_counties(country, skip_flags)
            if "subcounties" in levels: self._sync_subcounties(country)
            if "parishes"    in levels: self._sync_parishes(country)
            if "villages"    in levels: self._sync_villages(country)

        self.stdout.write(self.style.SUCCESS("✓ Uganda sync complete."))

    # ── HELPERS ───────────────────────────────────────────────────────────────

    def _load(self, filename):
        path = os.path.join(BASE_DIR, filename)
        if not os.path.exists(path):
            return None
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def _missing(self, filename):
        self.stdout.write(self.style.ERROR(
            f"  {filename} not found in data/UG/.\n"
            f"  Run: python convert_uganda.py --src ./uganda-geo-data/src/Uganda/Data --out ./data/UG"
        ))

    # ── REGIONS ───────────────────────────────────────────────────────────────

    def _sync_regions(self, country):
        self.stdout.write("Syncing regions...")
        data = self._load("regions.json")
        if data is None: return self._missing("regions.json")
        for item in data:
            obj, created = Division.objects.update_or_create(
                country=country, native_id=item["id"], level=1,
                defaults={"name": item["name"], "parent": None,
                          "source": item["source"], "source_url": item["source_url"]},
            )
            self.stdout.write(f"  {'[+]' if created else '[~]'} {obj.name}")

    # ── DISTRICTS ─────────────────────────────────────────────────────────────

    def _sync_districts(self, country):
        self.stdout.write("Syncing districts...")
        data = self._load("districts.json")
        if data is None: return self._missing("districts.json")
        for region_data in data:
            try:
                region = Division.objects.get(country=country, native_id=region_data["id"], level=1)
            except Division.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  Region '{region_data['name']}' not found — run regions first"))
                continue
            for d in region_data.get("children", []):
                obj, created = Division.objects.update_or_create(
                    country=country, name=d["name"], level=2,
                    defaults={"parent": region, "source": region_data["source"],
                              "source_url": region_data["source_url"]},
                )
                self.stdout.write(f"  {'[+]' if created else '[~]'} {obj.name}")

    # ── COUNTIES ──────────────────────────────────────────────────────────────

    def _sync_counties(self, country, skip_flags=False):
        self.stdout.write("Syncing counties...")
        data = self._load("counties.json")
        if data is None: return self._missing("counties.json")
        skipped = 0
        for item in data:
            if item.get("needs_verification") and not skip_flags:
                skipped += 1
                self.stdout.write(self.style.WARNING(
                    f"  [?] Skipping '{item['name']}' — use --skip-verification-flags to force"
                ))
                continue
            try:
                parent = Division.objects.get(country=country, name=item["parent_district"], level=2)
            except Division.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  District '{item['parent_district']}' not found"))
                continue
            obj, created = Division.objects.update_or_create(
                country=country, native_id=item["id"], level=3,
                defaults={"name": item["name"], "parent": parent,
                          "source": item["source"], "source_url": item["source_url"]},
            )
            self.stdout.write(f"  {'[+]' if created else '[~]'} {obj.name} ({item['parent_district']})")
        if skipped:
            self.stdout.write(self.style.WARNING(f"  Skipped {skipped} entries pending verification."))

    # ── SUB-COUNTIES ──────────────────────────────────────────────────────────

    def _sync_subcounties(self, country):
        self.stdout.write("Syncing sub-counties...")
        data = self._load("subcounties.json")
        if data is None: return self._missing("subcounties.json")

        # Build county native_id → Division lookup
        county_map = {
            d.native_id: d
            for d in Division.objects.filter(country=country, level=3)
            if d.native_id
        }

        ok = skipped = 0
        for item in data:
            parent_native_id = item.get("parent_county_native_id")
            parent = county_map.get(parent_native_id)
            if not parent:
                # Fallback: try matching by name from counties.json
                skipped += 1
                continue
            Division.objects.update_or_create(
                country=country, native_id=item["native_id"], level=4,
                defaults={"name": item["name"], "parent": parent,
                          "source": item["source"], "source_url": item["source_url"]},
            )
            ok += 1
        self.stdout.write(f"  Synced {ok:,} sub-counties. Skipped {skipped} (unresolved parent).")

    # ── PARISHES ──────────────────────────────────────────────────────────────

    def _sync_parishes(self, country):
        self.stdout.write("Syncing parishes...")
        data = self._load("parishes.json")
        if data is None: return self._missing("parishes.json")

        # Build sub-county native_id → Division lookup
        subcounty_map = {
            d.native_id: d
            for d in Division.objects.filter(country=country, level=4)
            if d.native_id
        }

        ok = skipped = 0
        for item in data:
            parent = subcounty_map.get(item.get("parent_subcounty_native_id"))
            if not parent:
                skipped += 1
                continue
            Division.objects.update_or_create(
                country=country, native_id=item["native_id"], level=5,
                defaults={"name": item["name"], "parent": parent,
                          "source": item["source"], "source_url": item["source_url"]},
            )
            ok += 1
        self.stdout.write(f"  Synced {ok:,} parishes. Skipped {skipped} (unresolved parent).")

    # ── VILLAGES ──────────────────────────────────────────────────────────────

    def _sync_villages(self, country):
        self.stdout.write("Syncing villages...")
        data = self._load("villages.json")
        if data is None: return self._missing("villages.json")

        # Build parish native_id → Division lookup
        parish_map = {
            d.native_id: d
            for d in Division.objects.filter(country=country, level=5)
            if d.native_id
        }

        ok = skipped = 0
        # Villages can be 60k+ rows — use bulk_create for performance
        to_create = []
        existing_native_ids = set(
            Division.objects.filter(country=country, level=6)
            .values_list("native_id", flat=True)
        )

        for item in data:
            parent = parish_map.get(item.get("parent_parish_native_id"))
            if not parent:
                skipped += 1
                continue
            if item["native_id"] in existing_native_ids:
                ok += 1
                continue
            to_create.append(Division(
                country=country,
                native_id=item["native_id"],
                name=item["name"],
                level=6,
                parent=parent,
                source=item["source"],
                source_url=item["source_url"],
            ))
            ok += 1

        # Batch insert in chunks of 500
        chunk_size = 500
        for i in range(0, len(to_create), chunk_size):
            Division.objects.bulk_create(to_create[i:i + chunk_size], ignore_conflicts=True)
            self.stdout.write(f"  Inserted chunk {i // chunk_size + 1}/{(len(to_create) // chunk_size) + 1}...")

        self.stdout.write(f"  Synced {ok:,} villages. Skipped {skipped} (unresolved parent).")
