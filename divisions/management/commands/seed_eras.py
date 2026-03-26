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
        {"name": "Republic of Kenya",                    "era_type": "current",
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
        {"name": "United Republic of Tanzania",          "era_type": "current", "started": "1964",
            "ended": "",     "notes": "Union of Tanganyika and Zanzibar, 26 April 1964"},
    ],
    "UG": [
        {"name": "Bunyoro-Kitara Kingdom",               "era_type": "precolonial",  "started": "~1300",
            "ended": "1899", "notes": "One of the oldest kingdoms in East Africa, traces origins to the Bachwezi dynasty. Once the dominant power in the Great Lakes region. Capital at Hoima. Lost 'lost counties' to Buganda in colonial era. Abolished 1967, restored 1993. Current ruler: Omukama Solomon Gafabusa Iguru I"},
        {"name": "Buganda Kingdom",                      "era_type": "precolonial",  "started": "~1300",
            "ended": "1894", "notes": "Largest and most influential kingdom; 52 clans under the Kabaka. Capital at Mengo (Kampala). Abolished by Milton Obote in 1967 (republican constitution). Restored 1993 by Museveni as cultural institution. Lukiiko (parliament) still functions. Current ruler: Kabaka Ronald Muwenda Mutebi II"},
        {"name": "Ankole Kingdom",                       "era_type": "precolonial",  "started": "~1500",
            "ended": "1901", "notes": "Hima-Iru kingdom in southwest Uganda; ruled by the Omugabe. Capital at Mbarara. Abolished 1967. NOT officially restored due to Bairu (farmers) vs Bahima (pastoralists) disagreements. Restoration remains politically sensitive"},
        {"name": "Toro Kingdom",                         "era_type": "precolonial",  "started": "~1830",
            "ended": "1900", "notes": "Founded c. 1830 when Prince Kaboyo broke away from Bunyoro. Capital at Kabarole (Fort Portal). Abolished 1967, restored 1993. Current ruler: Omukama Oyo Nyimba Kabamba Iguru Rukidi IV, crowned at age 3 in 1995"},
        {"name": "Busoga Chieftainships",                "era_type": "precolonial",  "started": "~1500",
            "ended": "1906", "notes": "Confederation of chieftainships east of the Nile near Jinja; Kyabazinga title rotates among clan chiefs. Not a centralized kingdom. Abolished 1967, restored 1995. Current ruler: Kyabazinga William Wilberforce Gabula Nadiope IV"},
        {"name": "Acholi Chiefdoms",                     "era_type": "precolonial",  "started": "~1600",
            "ended": "1911", "notes": "Luo-speaking chiefdoms in northern Uganda; rwodi (chiefs) led independent polities. Major center at Gulu. Fiercely resisted British pacification"},
        {"name": "Lango Chiefdoms",                      "era_type": "precolonial",  "started": "~1600",
            "ended": "1911", "notes": "Nilotic people of north-central Uganda; non-centralized society led by clan elders (won). Centered around Lira"},
        {"name": "Teso Chiefdoms",                       "era_type": "precolonial",  "started": "~1600",
            "ended": "1908", "notes": "Eastern Nilotic (Ateker) people of eastern Uganda; age-set based society. Main center at Soroti"},
        {"name": "Uganda Protectorate",                  "era_type": "colonial",
            "started": "1894",     "ended": "1962", "colonial_power": "british",
            "notes": "Established as British protectorate 1894; expanded through agreements with kingdoms (Buganda 1900, Bunyoro 1933, Ankole 1901, Toro 1900). Capital at Entebbe"},
        {"name": "Republic of Uganda",                   "era_type": "current",
            "started": "1962",     "ended": "",     "notes": "Independence 9 October 1962. Kingdoms abolished 1967 by Obote, restored (except Ankole) 1993 by Museveni as cultural institutions"},
    ],
    "RW": [
        {"name": "Kingdom of Rwanda",                    "era_type": "precolonial",  "started": "~1081",
            "ended": "1884", "notes": "Tutsi monarchy, one of the most centralised precolonial states in Africa"},
        {"name": "German East Africa (Rwanda)",          "era_type": "colonial",     "started": "1884",
         "ended": "1916", "colonial_power": "german", "notes": "Ruanda-Urundi territory"},
        {"name": "Belgian Ruanda-Urundi",                "era_type": "colonial",     "started": "1916",
            "ended": "1962", "colonial_power": "belgian", "notes": "League of Nations mandate then UN Trust Territory"},
        {"name": "Republic of Rwanda",                   "era_type": "current",
            "started": "1962",     "ended": "",     "notes": "Independence 1 July 1962"},
    ],
    "BI": [
        {"name": "Kingdom of Burundi",                   "era_type": "precolonial",
            "started": "~1680",    "ended": "1884", "notes": "Ganwa monarchy with mwami (king)"},
        {"name": "German East Africa (Burundi)",         "era_type": "colonial",     "started": "1884",
         "ended": "1916", "colonial_power": "german", "notes": "Part of Ruanda-Urundi"},
        {"name": "Belgian Ruanda-Urundi",                "era_type": "colonial",
            "started": "1916",     "ended": "1962", "colonial_power": "belgian"},
        {"name": "Kingdom of Burundi (post-independence)", "era_type": "independence",
            "started": "1962",     "ended": "1966", "notes": "Constitutional monarchy at independence; Mwami Mwambutsa IV then Ntare V"},
        {"name": "Republic of Burundi",                  "era_type": "current",
            "started": "1966",     "ended": "",     "notes": "Republic declared 28 November 1966 after coup by Michel Micombero"},
    ],
    "CD": [
        {"name": "Kingdom of Kongo",                     "era_type": "precolonial",  "started": "~1390",
            "ended": "1914", "notes": "Central African kingdom in western Congo basin; capital M'banza-Kongo (modern Angola). Decline after Portuguese contact 1483"},
        {"name": "Luba Empire",                          "era_type": "precolonial",  "started": "~1585",
            "ended": "1889", "notes": "Katanga/Kasai region; founded by Kongolo Mwamba, expanded by Kalala Ilunga. Collapsed under Tippu Tip and Belgian pressure"},
        {"name": "Lunda Empire",                         "era_type": "precolonial",  "started": "~1665",
            "ended": "1887", "notes": "Southern Congo and Zambia/Angola; offshoot of Luba Empire. Mwata Yamvo dynasty controlled copper and salt trade"},
        {"name": "Kuba Kingdom",                         "era_type": "precolonial",  "started": "~1625",
            "ended": "1900", "notes": "Kasai region between Sankuru and Lulua rivers; renowned for art, textiles and Shyaam a-Mbul a Ngoong dynasty"},
        {"name": "Azande Kingdoms",                      "era_type": "precolonial",  "started": "~1750",
            "ended": "1912", "notes": "Northern Congo (Uele); warrior kingdoms led by Avongara dynasty. Resisted Mahdists and Belgians"},
        {"name": "Congo Free State",                     "era_type": "colonial",     "started": "1885",     "ended": "1908",
            "colonial_power": "belgian", "notes": "Personal property of King Leopold II — notorious for atrocities, rubber terror, estimated millions of deaths"},
        {"name": "Belgian Congo",                        "era_type": "colonial",
            "started": "1908",     "ended": "1960", "colonial_power": "belgian"},
        {"name": "Republic of the Congo (Léopoldville)", "era_type": "independence",
         "started": "1960",     "ended": "1964", "notes": "Independence 30 June 1960"},
        {"name": "Democratic Republic of the Congo (First Republic)", "era_type": "independence",
            "started": "1964",     "ended": "1971", "notes": "First use of current name; Kasa-Vubu presidency"},
        {"name": "Republic of Zaire",                    "era_type": "independence", "started": "1971",
            "ended": "1997", "notes": "Renamed by Mobutu Sese Seko, 27 October 1971"},
        {"name": "Democratic Republic of the Congo",     "era_type": "current",
            "started": "1997",     "ended": "",     "notes": "Renamed after fall of Mobutu; Laurent-Désiré Kabila"},
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
        {"name": "Republic of South Sudan",              "era_type": "current", "started": "2011",
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
        ("Kinshasa",     "Kingdom of Kongo",                  "Nshasa",
         "Kikongo",  "indigenous", "Original Teke fishing village on the Congo River; within Kongo kingdom sphere"),
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
        ("Matadi",       "Kingdom of Kongo",                  "Matadi",         "Kikongo",
         "indigenous", "Kongo kingdom port area — 'rocks' in Kikongo, near Inga rapids"),
        # Congo Free State-era names for additional cities
        ("Lubumbashi",   "Congo Free State",                  "Elisabethville",
         "French",   "colonial",   "Founded 1910 as mining town — named after Queen Elisabeth of Belgium"),
        ("Bukavu",       "Congo Free State",                  "Costermansville",
         "French",   "colonial",   "Named after Belgian vice-governor Paul Costermans (d. 1903)"),
        ("Kalemie",      "Congo Free State",                  "Albertville",
         "French",   "colonial",   "Named after King Albert I — Free State post founded 1891 on Lake Tanganyika"),
        ("Mbandaka",     "Congo Free State",                  "Coquilhatville",
         "French",   "colonial",   "Founded as Equateur Station 1883 — renamed after Camille-Aimé Coquilhat"),
        ("Kananga",      "Congo Free State",                  "Luluabourg",
         "French",   "colonial",   "Free State post on Lulua River, founded 1884"),
        ("Likasi",       "Congo Free State",                  "Jadotville",
         "French",   "colonial",   "Named after geologist Jules Jadot — copper mining town from 1917"),
        ("Isiro",        "Congo Free State",                  "Paulis",
         "French",   "colonial",   "Named after Belgian officer — Free State post in Uele district"),
        ("Boma",         "Congo Free State",                  "Boma",           "Kikongo",
         "indigenous", "Capital of the Congo Free State 1885–1908; oldest European settlement on lower Congo"),
        ("Boma",         "Kingdom of Kongo",                  "Boma",           "Kikongo",
         "indigenous", "Kongo kingdom trading settlement at mouth of the Congo"),
        ("Goma",         "Congo Free State",                  "Goma",           "Swahili",
         "colonial",   "Free State military post established near Lake Kivu"),
        ("Kolwezi",      "Belgian Congo",                     "Kolwezi",
         "French",   "colonial",   "Founded 1937 as Union Minière mining town in Katanga"),
        ("Kamina",       "Belgian Congo",                     "Kamina",
         "French",   "colonial",   "Major Belgian military base — Base Militaire de Kamina"),
        ("Gbadolite",    "Republic of Zaire",                 "Gbadolite",
         "Ngbandi",  "official",   "Mobutu's birthplace — transformed into 'Versailles of the jungle' with presidential palace"),
        # Pre-colonial names for key cities
        ("Lubumbashi",   "Luba Empire",                       "Lubumbashi",
         "Kiluba",   "indigenous", "From the Luba word — area was within Luba/Lunda copper-trading sphere"),
        ("Kananga",      "Luba Empire",                       "Kananga",
         "Kiluba",   "indigenous", "Luba heartland settlement on the Lulua River"),
        ("Mbuji-Mayi",   "Luba Empire",                       "Mbuji-Mayi",
         "Kiluba",   "indigenous", "'Goat water' in Kiluba — river crossing in Luba territory"),
        ("Kisangani",    "Azande Kingdoms",                   "Boyoma",
         "Lokele",   "indigenous", "Local name for the falls area — Arab-Swahili trading post before Stanley"),
        ("Isiro",        "Azande Kingdoms",                   "Isiro",
         "Zande",    "indigenous", "Azande settlement in the Uele region"),
    ],
    "UG": [
        # Colonial-era names
        ("Kampala",      "Uganda Protectorate",               "Kampala",
         "English",  "colonial",   "British fort established 1890 on Old Kampala Hill"),
        ("Entebbe",      "Uganda Protectorate",               "Entebbe",
         "English",  "colonial",   "Capital of the Protectorate 1894-1962"),
        ("Jinja",        "Uganda Protectorate",               "Ripon Falls",    "English",
         "colonial",   "Source of the Nile named after Earl de Grey and Ripon"),
        ("Fort Portal",  "Uganda Protectorate",               "Fort Portal",    "English",
         "colonial",   "Named after Sir Gerald Portal, British commissioner 1893"),
        ("Gulu",         "Uganda Protectorate",               "Gulu",           "Acholi",
         "colonial",   "British administrative post established 1910 in Acholi territory"),
        ("Masaka",       "Uganda Protectorate",               "Masaka",
         "English",  "colonial",   "British administrative centre in Buganda's southern reaches"),
        ("Mbarara",      "Uganda Protectorate",               "Mbarara",        "English",
         "colonial",   "British administrative centre for Ankole; garrison town from 1901"),
        ("Hoima",        "Uganda Protectorate",               "Hoima",          "English",
         "colonial",   "British administrative centre for Bunyoro after 1899 agreement"),
        ("Soroti",       "Uganda Protectorate",               "Soroti",         "English",
         "colonial",   "British post in Teso region, established early 1900s"),
        ("Lira",         "Uganda Protectorate",               "Lira",           "English",
         "colonial",   "British administrative post in Lango territory, established 1911"),
        ("Mbale",        "Uganda Protectorate",               "Mbale",          "English",
         "colonial",   "British administrative post at foot of Mount Elgon"),
        ("Arua",         "Uganda Protectorate",               "Arua",           "English",
         "colonial",   "British post in West Nile, established after 1914 — near Lugbara/Kakwa territory"),
        # Buganda Kingdom names
        ("Kampala",      "Buganda Kingdom",                   "Kasozi k'Empala",
         "Luganda",  "indigenous", "Hill of impala — Buganda royal seat from 1880s"),
        ("Entebbe",      "Buganda Kingdom",                   "Entebe",
         "Luganda",  "indigenous", "Means 'seat/throne' in Luganda — Lake Victoria peninsula"),
        ("Masaka",       "Buganda Kingdom",                   "Masaka",
         "Luganda",  "indigenous", "From 'omusaka' — a type of grass; Buganda's southern frontier"),
        ("Mukono",       "Buganda Kingdom",                   "Mukono",
         "Luganda",  "indigenous", "Buganda heartland; name may derive from 'omukono' (arm/hand)"),
        ("Mityana",      "Buganda Kingdom",                   "Mityana",
         "Luganda",  "indigenous", "Western Buganda; site of Ssekabaka Mwanga's exile route"),
        ("Mubende",      "Buganda Kingdom",                   "Mubende",
         "Luganda",  "indigenous", "Contested between Buganda and Bunyoro; site of Nakayima tree shrine"),
        # Bunyoro-Kitara Kingdom names
        ("Hoima",        "Bunyoro-Kitara Kingdom",            "Hoima",
         "Runyoro",  "indigenous", "Capital of Bunyoro kingdom; seat of the Omukama"),
        ("Mubende",      "Bunyoro-Kitara Kingdom",            "Mubende",
         "Runyoro",  "indigenous", "Sacred Bunyoro site — Nakayima witch tree; lost to Buganda in 1894 agreement"),
        # Ankole Kingdom names
        ("Mbarara",      "Ankole Kingdom",                    "Mbarara",
         "Runyankole", "indigenous", "Capital of Ankole; seat of the Omugabe. Name from 'emburara' (couch grass)"),
        ("Kabale",       "Ankole Kingdom",                    "Kabale",
         "Rukiga",   "indigenous", "Southern frontier of Ankole/Kigezi — 'small stone' in Rukiga"),
        # Toro Kingdom names
        ("Fort Portal",  "Toro Kingdom",                      "Kabarole",       "Rutooro",
         "indigenous", "Original Toro kingdom capital; name now used for the district"),
        ("Kasese",       "Toro Kingdom",                      "Kasese",
         "Rutooro",  "indigenous", "Toro kingdom territory at foot of Rwenzori Mountains"),
        # Busoga Chieftainships names
        ("Jinja",        "Busoga Chieftainships",             "Jinja",
         "Lusoga",   "indigenous", "Means 'stone' in Lusoga — flat rocks at Lake Victoria outlet; Busoga territory"),
        # Acholi Chiefdoms names
        ("Gulu",         "Acholi Chiefdoms",                  "Gulu",
         "Acholi",   "indigenous", "Major Acholi centre; meaning disputed — possibly 'back of the neck' or 'cooking pot'"),
        ("Kitgum",       "Acholi Chiefdoms",                  "Kitgum",
         "Acholi",   "indigenous", "Acholi chiefdom centre; name means 'crush/grind' in Acholi"),
        # Lango Chiefdoms names
        ("Lira",         "Lango Chiefdoms",                   "Lira",
         "Lango",    "indigenous", "Central Lango settlement; name possibly from 'lyira' (to draw water)"),
        # Teso Chiefdoms names
        ("Soroti",       "Teso Chiefdoms",                    "Soroti",
         "Ateso",    "indigenous", "Main Teso centre; name derived from the Teso word for a type of tree"),
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
        ("Murang'a",     "Kenya Colony and Protectorate",     "Fort Hall",      "English",  "colonial",
         "Colonial district HQ — named after a British fort; renamed Murang'a at independence"),
        ("Nyahururu",    "Kenya Colony and Protectorate",     "Thompson's Falls", "English",
         "colonial",   "Named after explorer Joseph Thomson; renamed Nyahururu post-independence"),
        ("Hola",         "Kenya Colony and Protectorate",     "Galole",         "Orma",
         "indigenous", "Tana River District HQ — renamed from Galole to Hola"),
        # Additional colonial-era names
        ("Thika",        "Kenya Colony and Protectorate",     "Thika",          "English",
         "colonial",   "British settler town; Blue Posts Hotel established 1908 at Thika Falls"),
        ("Nanyuki",      "Kenya Colony and Protectorate",     "Nanyuki",        "English",
         "colonial",   "British military garrison town on the equator, established 1907"),
        ("Kitale",       "Kenya Colony and Protectorate",     "Kitale",         "English",
         "colonial",   "Trans-Nzoia settler farming town; became district HQ 1930"),
        ("Malindi",      "British East Africa Protectorate",  "Malindi",        "Swahili",
         "colonial",   "Ancient Swahili port; Vasco da Gama pillar 1498; British administrative post"),
        ("Lamu",         "British East Africa Protectorate",  "Lamu",           "Swahili",
         "colonial",   "Swahili city-state — British declared protectorate over Lamu archipelago 1890"),
        # Additional pre-colonial names
        ("Malindi",      "Pre-colonial Kingdoms & Communities", "Malindi",      "Swahili",
         "indigenous", "Swahili sultanate and trading city since 9th century; allied with Portuguese against Mombasa"),
        ("Lamu",         "Pre-colonial Kingdoms & Communities", "Lamu",          "Swahili",
         "indigenous", "Independent Swahili city-state from 14th century; peak prosperity in 18th century ivory trade"),
        ("Machakos",     "Imperial British East Africa",      "Masaku",         "Kamba",
         "indigenous", "Named after Kamba chief Masaku; IBEA Company post established 1889 — first inland station"),
        ("Kiambu",       "Pre-colonial Kingdoms & Communities", "Kiambu",       "Kikuyu",
         "indigenous", "From Kikuyu 'kiambuu' — a type of fig tree; Kikuyu agricultural heartland"),
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
        # British-era names
        ("Dar es Salaam", "Tanganyika Territory (British)",   "Dar es Salaam",  "English",
         "colonial",   "Capital of British Tanganyika; main port and administrative centre"),
        ("Tanga",        "German East Africa",                "Tanga",          "Swahili",
         "indigenous", "Ancient Swahili port; site of Battle of Tanga 1914 (German victory)"),
        ("Tanga",        "Tanganyika Territory (British)",    "Tanga",          "English",
         "colonial",   "Major sisal-producing port under British administration"),
        ("Moshi",        "German East Africa",                "Moshi",          "Chagga",
         "indigenous", "Chagga settlement at foot of Kilimanjaro; German garrison from 1893"),
        ("Morogoro",     "German East Africa",                "Morogoro",       "Luguru",
         "indigenous", "Luguru people's territory; German administrative post by 1890s"),
        ("Lindi",        "German East Africa",                "Lindi",          "Swahili",
         "indigenous", "Swahili coast town; centre of Maji Maji Rebellion 1905-1907"),
        ("Zanzibar Urban/West", "Zanzibar Protectorate",      "Zanzibar",       "Arabic",
         "colonial",   "Sultanate seat; British protectorate 1890; world's shortest war 1896 (38 minutes)"),
        # Additional pre-colonial names
        ("Tabora",       "Pre-colonial Kingdoms & Communities", "Kazeh",
         "Arabic",   "indigenous", "Arab-Swahili caravan trading post — major inland emporium from 1820s"),
        ("Ujiji",        "Pre-colonial Kingdoms & Communities", "Ujiji",
         "Ha",       "indigenous", "Ancient Lake Tanganyika port; where Stanley found Livingstone 1871"),
        ("Kilwa Masoko", "Pre-colonial Kingdoms & Communities", "Kilwa Kisiwani",
         "Swahili",  "indigenous", "Sultante of Kilwa — wealthiest Swahili city-state 13th-15th century; UNESCO site"),
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
        # Additional Rwandan names
        ("Muhanga",      "Belgian Ruanda-Urundi",             "Gitarama",
         "French",   "colonial",   "Colonial-era name; served as interim capital during 1994 genocide"),
        ("Karongi",      "Belgian Ruanda-Urundi",             "Kibuye",
         "French",   "colonial",   "Colonial-era name; Lake Kivu lakeside town"),
        ("Nyagatare",    "Kingdom of Rwanda",                 "Nyagatare",
         "Kinyarwanda", "indigenous", "From 'akagatare' — open grassland; northeastern Rwanda cattle territory"),
        ("Huye",         "Belgian Ruanda-Urundi",             "Astrida",
         "French",   "colonial",   "Now Huye district — site of National University of Rwanda (1963)"),
        ("Nyanza",       "Kingdom of Rwanda",                 "Nyanza",
         "Kinyarwanda", "indigenous", "Royal capital of the Mwami — seat of the Rwandan monarchy; 'nyanza' means court"),
        ("Nyanza",       "Belgian Ruanda-Urundi",             "Nyanza",
         "French",   "colonial",   "Belgian-administered royal capital; king's palace preserved as museum"),
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
        # Additional Burundi names
        ("Bururi",       "Belgian Ruanda-Urundi",             "Bururi",
         "French",   "colonial",   "Belgian administrative post in southern highlands"),
        ("Bururi",       "Kingdom of Burundi",                "Bururi",
         "Kirundi",  "indigenous", "Southern highland territory of the mwami"),
        ("Muyinga",      "Belgian Ruanda-Urundi",             "Muyinga",
         "French",   "colonial",   "Belgian administrative post near Tanzanian border"),
        ("Kayanza",      "Belgian Ruanda-Urundi",             "Kayanza",
         "French",   "colonial",   "Belgian tea-growing highland administrative post"),
        ("Makamba",      "Belgian Ruanda-Urundi",             "Makamba",
         "French",   "colonial",   "Southern border post; Belgian administrative centre"),
        ("Bujumbura",    "German East Africa (Burundi)",      "Usumbura",
         "German",   "colonial",   "German military post established 1889 on Lake Tanganyika"),
        ("Gitega",       "German East Africa (Burundi)",      "Kitega",
         "German",   "colonial",   "German Residenz near the royal court"),
    ],
    "SS": [
        ("Juba",         "Anglo-Egyptian Sudan",              "Juba",           "Bari",
         "indigenous", "Bari people's settlement — British built administrative post 1922"),
        ("Juba",         "Mahdist State",                     "Gondokoro",
         "English",  "colonial",   "Older trading post nearby, abandoned for Juba"),
        ("Juba",         "Pre-colonial Communities",          "Jubek",
         "Bari",     "indigenous", "Bari name for the area — 'Jubek' means uncultivated land near the river"),
        ("Malakal",      "Anglo-Egyptian Sudan",              "Malakal",        "Shilluk",
         "indigenous", "Shilluk kingdom territory — British post established 1905"),
        ("Malakal",      "Pre-colonial Communities",          "Malakal",
         "Shilluk",  "indigenous", "Shilluk royal territory; seat near the Reth (king) of the Shilluk"),
        ("Wau",          "Anglo-Egyptian Sudan",              "Wau",            "Dinka",
         "indigenous", "Dinka name for the area — British administrative centre"),
        ("Wau",          "Pre-colonial Communities",          "Wau",
         "Fertit",   "indigenous", "Fertit people's settlement on Jur River; pre-colonial trading point"),
        ("Yambio",       "Anglo-Egyptian Sudan",              "Yambio",         "Zande",
         "indigenous", "Named after Azande chief Wando's son Yambio, ruled ~1870-1905"),
        ("Yambio",       "Pre-colonial Communities",          "Yambio",
         "Zande",    "indigenous", "Azande chiefdom centre — Yambio was last major Azande chief to resist Anglo-Egyptian forces"),
        # Additional South Sudan names
        ("Bor",          "Anglo-Egyptian Sudan",              "Bor",            "Dinka",
         "indigenous", "British post in Dinka Bor territory; Jonglei Province HQ"),
        ("Bor",          "Pre-colonial Communities",          "Bor",
         "Dinka",    "indigenous", "Major Dinka Bor section territory on White Nile"),
        ("Rumbek",       "Anglo-Egyptian Sudan",              "Rumbek",         "Dinka",
         "indigenous", "British administrative centre in Lakes region; Dinka Agar territory"),
        ("Torit",        "Anglo-Egyptian Sudan",              "Torit",          "Otuho",
         "indigenous", "Eastern Equatoria HQ; site of the 1955 mutiny that preceded civil war"),
        ("Aweil",        "Anglo-Egyptian Sudan",              "Aweil",          "Dinka",
         "indigenous", "British post in Northern Bahr el Ghazal; Dinka Malual territory"),
    ],
}


class Command(BaseCommand):
    help = "Seed Era and DivisionName data for all 7 Mipaka countries"

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            self._seed_eras()
            self._seed_names()
        self.stdout.write(self.style.SUCCESS(
            "Era and historical name seed complete."))

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
                    f"  {'[+]' if created else '[~]'} {current_name} -> '{hist_name}' ({era_name})")
