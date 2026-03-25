import json
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from divisions.models import Country, Division, DivisionLevel

BASE_DIR = os.path.join(os.path.dirname(__file__),
                        "..", "..", "..", "data", "CD")

LEVEL_MAP = {
    1: ("Province",  "Province"),
    2: ("Territory / City", "Territoire / Ville"),
}

# Historical levels — all provinces at 100, all districts at 101
HISTORICAL_LEVEL_MAP = {
    100: ("Historical Province", "Province historique"),
    101: ("Historical District", "District historique"),
}

# All available --levels choices
ALL_LEVEL_CHOICES = [
    "provinces", "territories", "cities",
    "provinces_1997", "provinces_1933", "provinces_1966", "provinces_1988",
    "districts_1910", "districts_1933", "districts_1954", "districts_2008",
]


class Command(BaseCommand):
    help = "Sync DRC administrative divisions from local JSON files (data/CD/)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--levels", nargs="+", type=str,
            choices=ALL_LEVEL_CHOICES,
            default=["provinces", "territories"],
        )

    def handle(self, *args, **options):
        levels = options["levels"]

        country, _ = Country.objects.get_or_create(
            code="CD",
            defaults={"name": "Democratic Republic of Congo",
                      "native_name": "République Démocratique du Congo",
                      "max_levels": 2},
        )
        for level, (name, name_sw) in LEVEL_MAP.items():
            DivisionLevel.objects.get_or_create(
                country=country, level=level,
                defaults={"name": name, "name_sw": name_sw}
            )

        with transaction.atomic():
            # ── Current data ──
            if "provinces" in levels:
                self._sync_provinces(country)
            if "territories" in levels:
                self._sync_territories(country)
            if "cities" in levels:
                self._sync_cities(country)

            # ── Historical provinces (all at level 100) ──
            province_eras = [
                ("provinces_1997", "provinces_1997.json", "1997–2015"),
                ("provinces_1933", "provinces_1933.json", "Belgian Congo 1933–1960"),
                ("provinces_1966", "provinces_1966.json",
                 "Post-independence 1966–1971"),
                ("provinces_1988", "provinces_1988.json", "Zaire 1971–1997"),
            ]
            for key, filename, label in province_eras:
                if key in levels:
                    self._sync_historical_provinces(country, filename, label)

            # ── Historical districts (all at level 101) ──
            district_eras = [
                ("districts_1910", "districts_1910.json",
                 "Congo Free State / Early Belgian Congo 1910"),
                ("districts_1933", "districts_1933.json",
                 "Belgian Congo 1933–1960"),
                ("districts_1954", "districts_1954.json",
                 "Late Belgian Congo 1954–1960"),
                ("districts_2008", "districts_2008.json",
                 "Pre-2015 DRC 1966–2015"),
            ]
            for key, filename, label in district_eras:
                if key in levels:
                    self._sync_historical_districts(country, filename, label)

        self.stdout.write(self.style.SUCCESS("DRC sync complete."))

    # ── Helpers ────────────────────────────────────────────────────────────

    def _load(self, filename):
        path = os.path.join(BASE_DIR, filename)
        if not os.path.exists(path):
            self.stdout.write(self.style.ERROR(
                f"  {filename} not found in data/CD/"))
            return None
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _build_description(item):
        """Build a description string from common item fields."""
        desc_parts = [item.get("notes", "")]
        if item.get("era"):
            desc_parts.append(
                f"Era: {item['era']} ({item.get('era_years', '')})")
        if item.get("capital"):
            desc_parts.append(f"Capital: {item['capital']}")
        if item.get("successor_provinces"):
            desc_parts.append(
                f"Successors: {', '.join(item['successor_provinces'])}")
        return ". ".join(p for p in desc_parts if p)

    # ── Current data ──────────────────────────────────────────────────────

    def _sync_provinces(self, country):
        self.stdout.write("Syncing DRC provinces...")
        data = self._load("provinces.json")
        if data is None:
            return
        for item in data:
            obj, created = Division.objects.update_or_create(
                country=country, native_id=item["native_id"], level=1,
                defaults={"name": item["name"], "parent": None,
                          "source": item["source"],
                          "source_url": item["source_url"]},
            )
            self.stdout.write(f"  {'[+]' if created else '[~]'} {obj.name}")

    def _sync_territories(self, country):
        self.stdout.write("Syncing DRC territories...")
        data = self._load("territories.json")
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
                          "source": item["source"],
                          "source_url": item["source_url"]},
            )
            ok += 1
        self.stdout.write(
            f"  Synced {ok:,} territories."
            + (f" Skipped {skipped}." if skipped else ""))

    def _sync_cities(self, country):
        """Load 33 DRC cities as level-2 divisions with coordinates."""
        self.stdout.write("Syncing DRC cities...")
        data = self._load("cities.json")
        if data is None:
            return
        # Build province lookup by name (for linking cities to parents)
        province_map = {
            d.name: d
            for d in Division.objects.filter(country=country, level=1)
        }
        ok = skipped = 0
        for item in data:
            parent = None
            pname = item.get("province_name")
            if pname:
                parent = province_map.get(pname)
                if not parent:
                    self.stdout.write(self.style.WARNING(
                        f"  [!] Province '{pname}' not found for "
                        f"city {item['name']} — saving without parent"))

            desc = item.get("description", "")
            if not desc:
                parts = [
                    f"Provincial city with {item.get('communes', '?')} communes"]
                if item.get("is_capital"):
                    parts.append("Provincial capital")
                desc = ". ".join(parts)

            Division.objects.update_or_create(
                country=country, native_id=item["native_id"], level=2,
                defaults={
                    "name": item["name"],
                    "parent": parent,
                    "latitude": item.get("latitude"),
                    "longitude": item.get("longitude"),
                    "description": desc,
                    "source": item.get("source", "Wikipedia"),
                    "source_url": item.get("source_url", ""),
                },
            )
            ok += 1
        self.stdout.write(f"  Synced {ok} cities.")

    # ── Historical data ───────────────────────────────────────────────────

    def _sync_historical_provinces(self, country, filename, label):
        """Load historical provinces (level 100) from a JSON file."""
        self.stdout.write(f"Syncing historical provinces ({label})...")
        data = self._load(filename)
        if data is None:
            return
        DivisionLevel.objects.get_or_create(
            country=country, level=100,
            defaults={"name": "Historical Province",
                      "name_sw": "Province historique"},
        )
        for item in data:
            description = self._build_description(item)
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

    def _sync_historical_districts(self, country, filename, label):
        """Load historical districts (level 101) from a JSON file."""
        self.stdout.write(f"Syncing historical districts ({label})...")
        data = self._load(filename)
        if data is None:
            return
        DivisionLevel.objects.get_or_create(
            country=country, level=101,
            defaults={"name": "Historical District",
                      "name_sw": "District historique"},
        )
        # Build province lookup from level 100 (by name) for parent linking
        province_map = {
            d.name: d
            for d in Division.objects.filter(country=country, level=100)
        }
        ok = skipped = 0
        for item in data:
            parent = None
            pname = item.get("parent_province")
            if pname:
                parent = province_map.get(pname)
                if not parent:
                    self.stdout.write(self.style.WARNING(
                        f"  [!] Province '{pname}' not found for "
                        f"{item['name']} — saving without parent"))

            description = self._build_description(item)
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
            f"  Synced {ok} districts from {filename}."
            + (f" Skipped {skipped}." if skipped else ""))
