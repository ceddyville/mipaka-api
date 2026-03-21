import json
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from divisions.models import Country, Division, DivisionLevel

BASE_DIR = os.path.join(os.path.dirname(__file__),
                        "..", "..", "..", "data", "SS")

LEVEL_MAP = {
    1: ("State",  ""),
    2: ("County", ""),
    3: ("Payam",  ""),
}

# Historical levels
HISTORICAL_LEVEL_MAP = {
    100: ("State (2015–2020)", ""),
}


class Command(BaseCommand):
    help = "Sync South Sudan administrative divisions from local JSON files (data/SS/)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--levels", nargs="+", type=str,
            choices=["states", "counties", "payams", "states_2015"],
            default=["states", "counties"],
        )

    def handle(self, *args, **options):
        levels = options["levels"]

        country, _ = Country.objects.get_or_create(
            code="SS",
            defaults={"name": "South Sudan",
                      "native_name": "South Sudan", "max_levels": 3},
        )
        for level, (name, name_sw) in LEVEL_MAP.items():
            DivisionLevel.objects.get_or_create(
                country=country, level=level,
                defaults={"name": name, "name_sw": name_sw}
            )

        with transaction.atomic():
            if "states" in levels:
                self._sync_states(country)
            if "counties" in levels:
                self._sync_counties(country)
            if "payams" in levels:
                self._sync_payams(country)
            if "states_2015" in levels:
                self._sync_historical_states(country)

        self.stdout.write(self.style.SUCCESS("✓ South Sudan sync complete."))

    def _load(self, filename):
        path = os.path.join(BASE_DIR, filename)
        if not os.path.exists(path):
            self.stdout.write(self.style.ERROR(
                f"  {filename} not found in data/SS/\n"
                f"  Payams: download from https://data.humdata.org/dataset/cod-ab-ssd\n"
                f"  Then run: python convert_hdx.py --country SS --out ./data/SS"
            ))
            return None
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def _sync_states(self, country):
        self.stdout.write("Syncing states...")
        data = self._load("states.json")
        if data is None:
            return
        for item in data:
            obj, created = Division.objects.update_or_create(
                country=country, native_id=item["native_id"], level=1,
                defaults={"name": item["name"], "parent": None,
                          "source": item["source"], "source_url": item["source_url"]},
            )
            self.stdout.write(f"  {'[+]' if created else '[~]'} {obj.name}")

    def _sync_counties(self, country):
        self.stdout.write("Syncing counties...")
        data = self._load("counties.json")
        if data is None:
            return
        state_map = {d.native_id: d for d in Division.objects.filter(
            country=country, level=1) if d.native_id}
        ok = skipped = 0
        for item in data:
            parent = state_map.get(item.get("parent_state_id"))
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
            f"  Synced {ok:,} counties." + (f" Skipped {skipped}." if skipped else ""))

    def _sync_payams(self, country):
        self.stdout.write("Syncing payams...")
        data = self._load("payams.json")
        if data is None:
            return
        county_map = {d.native_id: d for d in Division.objects.filter(
            country=country, level=2) if d.native_id}
        ok = skipped = 0
        for item in data:
            parent = county_map.get(item.get("parent_county_id"))
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
            f"  Synced {ok:,} payams." + (f" Skipped {skipped}." if skipped else ""))

    # ── HISTORICAL DATA ───────────────────────────────────────────────────

    def _sync_historical_states(self, country):
        """Load 28 states (2015–2020) from states_2015.json."""
        self.stdout.write("Syncing historical states (2015–2020)...")
        data = self._load("states_2015.json")
        if data is None:
            return
        DivisionLevel.objects.get_or_create(
            country=country, level=100,
            defaults={"name": "State (2015–2020)", "name_sw": ""},
        )
        # Build lookup of current states by name for parent linking
        state_map = {
            d.name: d
            for d in Division.objects.filter(country=country, level=1)
        }
        for item in data:
            parent = state_map.get(item.get("parent_state"))

            desc_parts = [item.get("notes", "")]
            if item.get("era"):
                desc_parts.append(
                    f"Era: {item['era']} ({item.get('era_years', '')})")
            if item.get("region"):
                desc_parts.append(f"Region: {item['region']}")
            if item.get("parent_state"):
                desc_parts.append(
                    f"Carved from: {item['parent_state']}")
            description = ". ".join(p for p in desc_parts if p)

            obj, created = Division.objects.update_or_create(
                country=country, native_id=item["native_id"], level=100,
                defaults={
                    "name": item["name"],
                    "parent": parent,
                    "is_active": False,
                    "description": description,
                    "source": item.get("source", "Wikipedia"),
                    "source_url": item.get("source_url", ""),
                },
            )
            self.stdout.write(f"  {'[+]' if created else '[~]'} {obj.name}")
