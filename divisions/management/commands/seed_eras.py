"""
Seed historical eras and well-known historical place names
for all 7 Mipaka countries.

Run: python manage.py seed_eras

This is a one-time seed for the Era table and key DivisionName entries.
Community contributions will extend the DivisionName data over time.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from divisions.models import Country, Era, Division, DivisionName


# ─────────────────────────────────────────────────────────────────────────────
# ERA DEFINITIONS PER COUNTRY
# ─────────────────────────────────────────────────────────────────────────────

ERAS = {
    "KE": [
        {"name": "Pre-colonial Kingdoms & Communities", "era_type": "precolonial",  "started": "pre-1885",
            "ended": "1895", "notes": "Included Maasai, Kikuyu, Luo, Mijikenda, Swahili coast city-states and others"},
        {"name": "Imperial British East Africa",         "era_type": "colonial",     "started": "1888",
            "ended": "1895", "colonial_power": "british", "notes": "Administered by Imperial British East Africa Company"},
        {"name": "British East Africa Protectorate",     "era_type": "colonial",
            "started": "1895",     "ended": "1920", "colonial_power": "british"},
        {"name": "Kenya Colony and Protectorate",        "era_type": "colonial",
            "started": "1920",     "ended": "1963", "colonial_power": "british"},
        {"name": "Republic of Kenya",                    "era_type": "independence",
            "started": "1963",     "ended": "",     "notes": "Independence 12 December 1963"},
    ],
    "TZ": [
        {"name": "Pre-colonial Kingdoms & Communities",  "era_type": "precolonial",  "started": "pre-1885",
            "ended": "1885", "notes": "Included Nyamwezi, Hehe, Chagga, Swahili coast sultanates"},
        {"name": "German East Africa",                   "era_type": "colonial",
            "started": "1885",     "ended": "1919", "colonial_power": "german"},
        {"name": "Tanganyika Territory (British)",       "era_type": "colonial",     "started": "1919",     "ended": "1961",
         "colonial_power": "british", "notes": "League of Nations mandate, then UN Trust Territory"},
        {"name": "Zanzibar Protectorate",                "era_type": "colonial",
            "started": "1890",     "ended": "1963", "colonial_power": "british"},
        {"name": "Republic of Tanganyika",
            "era_type": "independence", "started": "1961",     "ended": "1964"},
        {"name": "United Republic of Tanzania",          "era_type": "independence", "started": "1964",
            "ended": "",     "notes": "Union of Tanganyika and Zanzibar, 26 April 1964"},
    ],
    "UG": [
        {"name": "Buganda Kingdom",                      "era_type": "precolonial",  "started": "~1300",
            "ended": "1894", "notes": "Dominant kingdom; also Bunyoro-Kitara, Ankole, Toro, Busoga"},
        {"name": "Uganda Protectorate",                  "era_type": "colonial",
            "started": "1894",     "ended": "1962", "colonial_power": "british"},
        {"name": "Republic of Uganda",                   "era_type": "independence",
            "started": "1962",     "ended": "",     "notes": "Independence 9 October 1962"},
    ],
    "RW": [
        {"name": "Kingdom of Rwanda",                    "era_type": "precolonial",  "started": "~1081",
            "ended": "1884", "notes": "Tutsi monarchy, one of the most centralised precolonial states in Africa"},
        {"name": "German East Africa (Rwanda)",          "era_type": "colonial",     "started": "1884",
         "ended": "1916", "colonial_power": "german", "notes": "Ruanda-Urundi territory"},
        {"name": "Belgian Ruanda-Urundi",                "era_type": "colonial",     "started": "1916",
            "ended": "1962", "colonial_power": "belgian", "notes": "League of Nations mandate then UN Trust Territory"},
        {"name": "Republic of Rwanda",                   "era_type": "independence",
            "started": "1962",     "ended": "",     "notes": "Independence 1 July 1962"},
    ],
    "BI": [
        {"name": "Kingdom of Burundi",                   "era_type": "precolonial",
            "started": "~1680",    "ended": "1884", "notes": "Ganwa monarchy with mwami (king)"},
        {"name": "German East Africa (Burundi)",         "era_type": "colonial",     "started": "1884",
         "ended": "1916", "colonial_power": "german", "notes": "Part of Ruanda-Urundi"},
        {"name": "Belgian Ruanda-Urundi",                "era_type": "colonial",
            "started": "1916",     "ended": "1962", "colonial_power": "belgian"},
        {"name": "Kingdom of Burundi",                   "era_type": "independence",
            "started": "1962",     "ended": "1966", "notes": "Constitutional monarchy at independence"},
        {"name": "Republic of Burundi",                  "era_type": "independence",
            "started": "1966",     "ended": "",     "notes": "Republic declared 28 November 1966"},
    ],
    "CD": [
        {"name": "Pre-colonial Kingdoms",                "era_type": "precolonial",  "started": "pre-1885",
            "ended": "1885", "notes": "Kongo Kingdom, Luba Empire, Lunda Empire, Kuba Kingdom, Azande"},
        {"name": "Congo Free State",                     "era_type": "colonial",     "started": "1885",     "ended": "1908",
            "colonial_power": "belgian", "notes": "Personal property of King Leopold II — notorious for atrocities"},
        {"name": "Belgian Congo",                        "era_type": "colonial",
            "started": "1908",     "ended": "1960", "colonial_power": "belgian"},
        {"name": "Republic of the Congo (Léopoldville)", "era_type": "independence",
         "started": "1960",     "ended": "1964", "notes": "Independence 30 June 1960"},
        {"name": "Democratic Republic of the Congo",     "era_type": "independence",
            "started": "1964",     "ended": "1971", "notes": "First use of current name"},
        {"name": "Republic of Zaire",                    "era_type": "independence", "started": "1971",
            "ended": "1997", "notes": "Renamed by Mobutu Sese Seko, 27 October 1971"},
        {"name": "Democratic Republic of the Congo",     "era_type": "current",
            "started": "1997",     "ended": "",     "notes": "Renamed after fall of Mobutu"},
    ],
    "SS": [
        {"name": "Pre-colonial Communities",             "era_type": "precolonial",  "started": "pre-1821",
            "ended": "1821", "notes": "Dinka, Nuer, Azande, Shilluk, Bari and many others"},
        {"name": "Egyptian Sudan",                       "era_type": "colonial",
            "started": "1821",     "ended": "1885", "notes": "Ottoman-Egyptian rule"},
        {"name": "Mahdist State",                        "era_type": "colonial",     "started": "1885",
            "ended": "1899", "notes": "Independent Sudanese state under Muhammad Ahmad"},
        {"name": "Anglo-Egyptian Sudan",                 "era_type": "colonial",
            "started": "1899",     "ended": "1956", "colonial_power": "british"},
        {"name": "Republic of Sudan (unified)",          "era_type": "independence", "started": "1956",
         "ended": "2011", "notes": "South Sudan part of Sudan until independence"},
        {"name": "Republic of South Sudan",              "era_type": "independence", "started": "2011",
            "ended": "",     "notes": "Independence 9 July 2011 — world's newest country"},
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# KEY HISTORICAL PLACE NAMES (seed data — community will extend)
# ─────────────────────────────────────────────────────────────────────────────

HISTORICAL_NAMES = {
    # Format: (country_code, division_name_current, era_name, historical_name, language, name_type, etymology)
    "CD": [
        ("Kinshasa",     "Belgian Congo",                     "Léopoldville",
         "French",   "colonial",   "Named after King Leopold II of Belgium"),
        ("Kinshasa",     "Congo Free State",                  "Léopoldville",
         "French",   "colonial",   "Stanley's trading post, 1881"),
        ("Kinshasa",     "Pre-colonial Kingdoms",             "Nshasa",
         "Kikongo",  "indigenous", "Original Teke fishing village on the Congo River"),
        ("Kisangani",    "Belgian Congo",                     "Stanleyville",
         "French",   "colonial",   "Named after Henry Morton Stanley"),
        ("Kisangani",    "Congo Free State",                  "Stanleyville",
         "French",   "colonial",   "Stanley Falls Station, established 1883"),
        ("Lubumbashi",   "Belgian Congo",                     "Élisabethville",
         "French",   "colonial",   "Named after Queen Elisabeth of Belgium"),
        ("Lubumbashi",   "Republic of Zaire",                 "Lubumbashi",
         "Swahili",  "official",   "Renamed 1966 under authenticité policy"),
        ("Mbandaka",     "Belgian Congo",                     "Coquilhatville",
         "French",   "colonial",   "Named after Belgian officer Camille-Aimé Coquilhat"),
        ("Kananga",      "Belgian Congo",                     "Luluabourg",
         "French",   "colonial",   "Named after the Lulua River"),
        ("Mbuji-Mayi",   "Belgian Congo",
         "Bakwanga",       "Luba",     "colonial",   ""),
        ("Bandundu",     "Belgian Congo",                     "Banningville",
         "French",   "colonial",   "Named after Emile Banning, Belgian geographer"),
        ("Matadi",       "Congo Free State",                  "Matadi",         "Kikongo",
         "indigenous", "Means 'rocks' in Kikongo — port at rocky Congo River narrows"),
    ],
    "UG": [
        ("Kampala",      "Uganda Protectorate",               "Kampala",
         "English",  "colonial",   "British fort established 1890 on Old Kampala Hill"),
        ("Kampala",      "Buganda Kingdom",                   "Kasozi k'Empala",
         "Luganda",  "indigenous", "Hill of impala — Buganda royal seat from 1880s"),
        ("Entebbe",      "Uganda Protectorate",               "Entebbe",
         "English",  "colonial",   "Capital of the Protectorate 1894–1962"),
        ("Entebbe",      "Buganda Kingdom",                   "Entebe",
         "Luganda",  "indigenous", "Means 'seat/throne' in Luganda"),
        ("Jinja",        "Uganda Protectorate",               "Ripon Falls",    "English",
         "colonial",   "Source of the Nile named after Earl de Grey and Ripon"),
        ("Jinja",        "Buganda Kingdom",                   "Jinja",          "Lusoga",
         "indigenous", "Means 'stone' in Lusoga — flat rocks at Lake Victoria outlet"),
        ("Fort Portal",  "Uganda Protectorate",               "Fort Portal",    "English",
         "colonial",   "Named after Sir Gerald Portal, British commissioner 1893"),
        ("Fort Portal",  "Toro Kingdom",                      "Kabarole",       "Rutooro",
         "indigenous", "Original Toro kingdom name, now used for the district"),
        ("Gulu",         "Uganda Protectorate",               "Gulu",           "Acholi",
         "indigenous", "Acholi word, meaning disputed — possibly 'back of the neck'"),
        ("Masaka",       "Uganda Protectorate",               "Masaka",
         "Luganda",  "indigenous", "From 'omusaka' — a type of grass"),
    ],
    "KE": [
        ("Nairobi",      "British East Africa Protectorate",  "Nairobi",
         "English",  "colonial",   "British railway depot established 1899"),
        ("Nairobi",      "Pre-colonial Kingdoms & Communities", "Enkare Nyorobi",
         "Maasai",  "indigenous", "Place of cool waters — Maasai watering hole"),
        ("Mombasa",      "Kenya Colony and Protectorate",     "Mombasa",
         "English",  "colonial",   "Port city, major British East Africa hub"),
        ("Mombasa",      "Pre-colonial Kingdoms & Communities", "Mvita",          "Swahili",
         "indigenous", "Island of war in Swahili — old name still used for central constituency"),
        ("Kisumu",       "British East Africa Protectorate",  "Port Florence",  "English",
         "colonial",   "Named after Florence Preston, wife of railway engineer"),
        ("Kisumu",       "Pre-colonial Kingdoms & Communities", "Kisumo",
         "Dholuo",   "indigenous", "Place of barter/trading in Dholuo — Luo name for the lakeside market"),
        ("Nakuru",       "Kenya Colony and Protectorate",     "Nakuru",
         "English",  "colonial",   "British township from 1904"),
        ("Nakuru",       "Pre-colonial Kingdoms & Communities", "Nakuru",
         "Maasai",   "indigenous", "Dusty place in Maa — Maasai name for the lake area"),
        ("Eldoret",      "Kenya Colony and Protectorate",     "64",             "English",
         "colonial",   "Called '64' — 64 miles from Kisumu on railway mile-posts"),
        ("Eldoret",      "Pre-colonial Kingdoms & Communities", "Sisibo",
         "Nandi",    "indigenous", "Nandi people's name for the plateau area"),
        # Historical district/town name changes from Wikipedia Sub-counties_of_Kenya
        ("Murang'a",     "Kenya Colony and Protectorate",     "Fort Hall",      "English",  "colonial",
         "Colonial district HQ — named after a British fort; renamed Murang'a at independence"),
        ("Nyahururu",    "Kenya Colony and Protectorate",     "Thompson's Falls", "English",
         "colonial",   "Named after explorer Joseph Thomson; renamed Nyahururu post-independence"),
        ("Hola",         "Kenya Colony and Protectorate",     "Galole",         "Orma",
         "indigenous", "Tana River District HQ — renamed from Galole to Hola"),
    ],
    "TZ": [
        ("Dar es Salaam", "German East Africa",                "Dar es Salaam",  "Arabic",
         "colonial",   "Haven of peace in Arabic — Swahili Sultan founded 1866, Germans expanded"),
        ("Dar es Salaam", "Pre-colonial Kingdoms & Communities", "Mzizima",
         "Swahili",  "indigenous", "Healthy town in Swahili — original fishing village"),
        ("Dodoma",       "German East Africa",                "Dodoma",         "Gogo",
         "indigenous", "It has sunk in Kigogo — ox carts sank in swampy ground"),
        ("Arusha",       "German East Africa",                "Arusha-Chini",
         "German",   "colonial",   "Lower Arusha — German boma established 1900"),
        ("Arusha",       "Pre-colonial Kingdoms & Communities", "Ilkisonko",
         "Maasai",   "indigenous", "Maasai name for the area around Mount Meru"),
        ("Mwanza",       "German East Africa",                "Mwanza",
         "Sukuma",   "indigenous", "Named by Sukuma people — exact meaning disputed"),
        ("Tabora",       "German East Africa",                "Tabora",
         "Nyamwezi", "indigenous", "Major Nyamwezi and Arab trading centre from 1820s"),
        ("Bagamoyo",     "German East Africa",                "Bagamoyo",       "Swahili",
         "indigenous", "Lay down your heart in Swahili — start of slave route inland"),
    ],
    "RW": [
        ("Kigali",       "Belgian Ruanda-Urundi",             "Kigali",
         "French",   "colonial",   "Belgian administrative centre from 1907"),
        ("Kigali",       "Kingdom of Rwanda",                 "Kigali",
         "Kinyarwanda", "indigenous", "Hill of many in Kinyarwanda — always a trading hill"),
        ("Butare",       "Belgian Ruanda-Urundi",             "Astrida",
         "French",   "colonial",   "Named after Queen Astrid of Belgium"),
        ("Butare",       "Kingdom of Rwanda",                 "Butare",
         "Kinyarwanda", "indigenous", "Restored to original name at independence 1962"),
        ("Musanze",      "Belgian Ruanda-Urundi",             "Ruhengeri",
         "French",   "colonial",   "Colonial-era name, used until 2006"),
        ("Musanze",      "Republic of Rwanda",                "Musanze",
         "Kinyarwanda", "official",  "Renamed 2006 in post-genocide administrative reform"),
        ("Rubavu",       "Belgian Ruanda-Urundi",             "Gisenyi",
         "French",   "colonial",   "Colonial-era name, used until 2006"),
        ("Rusizi",       "Belgian Ruanda-Urundi",             "Cyangugu",
         "French",   "colonial",   "Colonial-era name for the southern lake town"),
    ],
    "BI": [
        ("Bujumbura",    "Belgian Ruanda-Urundi",             "Usumbura",
         "French",   "colonial",   "Belgian colonial capital from 1889"),
        ("Bujumbura",    "Kingdom of Burundi",                "Bujumbura",      "Kirundi",
         "indigenous", "Restored at independence 1962 — exact meaning disputed"),
        ("Gitega",       "Belgian Ruanda-Urundi",             "Kitega",
         "French",   "colonial",   "Colonial spelling of the royal capital"),
        ("Gitega",       "Kingdom of Burundi",                "Gitega",
         "Kirundi",  "indigenous", "Royal capital of the mwami (king)"),
        ("Ngozi",        "Belgian Ruanda-Urundi",             "Ngozi",
         "French",   "colonial",   "Administrative centre in Belgian period"),
        ("Rumonge",      "Republic of Burundi",               "Rumonge",        "Kirundi",
         "indigenous", "Became provincial capital 2015 when province created from Bururi"),
    ],
    "SS": [
        ("Juba",         "Anglo-Egyptian Sudan",              "Juba",           "Bari",
         "indigenous", "Bari people's settlement — British built administrative post 1922"),
        ("Juba",         "Mahdist State",                     "Gondokoro",
         "English",  "colonial",   "Older trading post nearby, abandoned for Juba"),
        ("Malakal",      "Anglo-Egyptian Sudan",              "Malakal",        "Shilluk",
         "indigenous", "Shilluk kingdom territory — British post established 1905"),
        ("Wau",          "Anglo-Egyptian Sudan",              "Wau",            "Dinka",
         "indigenous", "Dinka name for the area — British administrative centre"),
        ("Yambio",       "Anglo-Egyptian Sudan",              "Yambio",         "Zande",
         "indigenous", "Named after Azande chief Wando's son Yambio, ruled ~1870–1905"),
    ],
}


class Command(BaseCommand):
    help = "Seed Era and DivisionName data for all 7 Mipaka countries"

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            self._seed_eras()
            self._seed_names()
        self.stdout.write(self.style.SUCCESS(
            "✓ Era and historical name seed complete."))

    def _seed_eras(self):
        self.stdout.write("Seeding eras...")
        for country_code, eras in ERAS.items():
            try:
                country = Country.objects.get(code=country_code)
            except Country.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f"  Country {country_code} not found — run sync commands first"))
                continue
            for era_data in eras:
                era, created = Era.objects.get_or_create(
                    country=country,
                    name=era_data["name"],
                    defaults={
                        "era_type":       era_data.get("era_type", ""),
                        "colonial_power": era_data.get("colonial_power", ""),
                        "started":        era_data.get("started", ""),
                        "ended":          era_data.get("ended", ""),
                        "notes":          era_data.get("notes", ""),
                        "source":         "Wikipedia / Encyclopaedia Britannica",
                        "source_url":     "https://en.wikipedia.org",
                    }
                )
                self.stdout.write(
                    f"  {'[+]' if created else '[~]'} {country_code}: {era.name}")

    def _seed_names(self):
        self.stdout.write("\nSeeding historical place names...")
        for country_code, names in HISTORICAL_NAMES.items():
            try:
                country = Country.objects.get(code=country_code)
            except Country.DoesNotExist:
                continue

            for (current_name, era_name, hist_name, language, name_type, etymology) in names:
                # Find division by current name
                division = Division.objects.filter(
                    country=country, name__iexact=current_name
                ).first()
                if not division:
                    self.stdout.write(self.style.WARNING(
                        f"  Division '{current_name}' ({country_code}) not found — sync data first"))
                    continue

                # Find era
                era = Era.objects.filter(
                    country=country, name=era_name
                ).first()
                if not era:
                    self.stdout.write(self.style.WARNING(
                        f"  Era '{era_name}' ({country_code}) not found"))
                    continue

                _, created = DivisionName.objects.get_or_create(
                    division=division,
                    era=era,
                    language=language,
                    name_type=name_type,
                    defaults={
                        "name":       hist_name,
                        "etymology":  etymology,
                        "source":     "Wikipedia / Encyclopaedia Britannica",
                        "source_url": "https://en.wikipedia.org",
                    }
                )
                self.stdout.write(
                    f"  {'[+]' if created else '[~]'} {current_name} → '{hist_name}' ({era_name})")
