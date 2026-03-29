"""
Convert Wikipedia "Divisions of Kenya" data into standardized JSON.

Source: https://en.wikipedia.org/wiki/Divisions_of_Kenya
The districts of Kenya were divided into 262 divisions (matarafa).
This script encodes the data manually extracted from Wikipedia.

Deduplication notes:
- Hulugho and Masalani appear in both Garissa and Ijara; kept under Ijara only
- Kapsokwony appears in both Bungoma and Mount Elgon; kept under Mount Elgon only
- Malindi/Magarini described under Kilifi split section; kept under Malindi District only
- Stray Gucha divisions (Etago, Kenyenya, etc.) found after Garissa on Wikipedia;
  assigned to Gucha district. Nyamache & Ogembo removed (already in Kisii Central).

Output: data/KE/divisions_admin.json
"""

import json
import os

# Divisions organized by parent district name.
# District names match those in districts_2007.json (or districts_1992.json for Mutomo).
DIVISIONS_BY_DISTRICT = {
    "Baringo": [
        "Kabarnet", "Kabartonjo", "Marigat", "Mochongoi",
        "Mogotio", "Nginyang", "Koibatek", "Tenges",
    ],
    "Bomet": ["Bomet", "Chepalungu", "Konoin"],
    "Bondo": ["Maranda", "Nyang'oma", "Rarieda", "Madiany", "Usigu"],
    "Bungoma": [
        # Kapsokwony removed — listed under Mount Elgon District
        "Cheptaisi", "Kanduyi", "Kimilili", "Mt. Elgon Forest",
        "Sirisia", "Tongareni", "Webuye", "Bumula",
    ],
    "Busia": [
        "Teso North", "Teso South", "Amukura", "Budalangi",
        "Butula", "Funyula", "Nambale", "Matayos",
    ],
    "Embu": [
        "Central", "Nembure", "Manyatta", "Runyenjes", "Kyeni",
        "Gachoka", "Mwea", "Makima", "Kiritiri", "Evurore", "Siakago",
    ],
    "Garissa": [
        # Hulugho and Masalani removed — listed under Ijara District
        "Bura", "Central Garissa", "Dadaab", "Galmagalla", "Jarajilla",
        "Mbalambala", "Modogashe", "Sankuri", "Danyere",
        "Shant-Abak", "Benane", "Liboi",
    ],
    "Gucha": [
        # Stray Wikipedia divisions found after Garissa section
        # Nyamache and Ogembo excluded (already in Kisii Central)
        "Etago", "Kenyenya", "Nyacheki", "Nyamarambe", "Sameta",
    ],
    "Homa Bay": ["Kendu Bay", "Mbita", "Ndhiwa", "Oyugis", "Rangwe"],
    "Ijara": ["Hulugho", "Ijara", "Masalani", "Sangailu"],
    "Isiolo": ["Central Isiolo", "Garba Tulla", "Merti", "Sericho"],
    "Kajiado": [
        "Central Kajiado", "Loitokitok", "Magadi", "Ngong", "Mashuru",
    ],
    "Kakamega": [
        "Butere", "Ikolomani", "Khwisero", "Lugari",
        "Lurambi", "Malava/Kabras", "Mumias", "Shinyalu",
    ],
    "Keiyo": ["Chepkorio", "Soy", "Metkei"],
    "Kericho": ["Belgut", "Bureti", "Kipkelion", "Ainamoi", "Soin", "Sigowet"],
    "Kiambu": [
        "Gatundu", "Githunguri", "Kiambaa", "Kikuyu",
        "Lari", "Limuru", "Thika-Juja",
    ],
    "Kilifi": [
        # Original Kilifi District divisions + Ganze/Kaloleni/Rabai (splits)
        # Malindi/Magarini excluded — listed under Malindi District
        "Bahari", "Kikambala", "Chonyi",
        "Ganze", "Bamba", "Vitengeni",
        "Kaloleni", "Rabai",
    ],
    "Kirinyaga": ["Gichugu", "Kirinyaga Central", "Mwea", "Ndia"],
    "Kisii Central": [
        "Bosongo", "Irianyi", "Kisii Municipality", "Marani",
        "Masaba", "Nyamache", "Ogembo", "Suneka",
    ],
    "Kisumu": [
        "Kisumu Township", "Kisumu Central", "Kisumu East",
        "Kisumu North", "Kisumu Southwest", "Kajulu East",
        "Kajulu West", "Central Kolwa", "East Kolwa", "West Kolwa",
    ],
    "Kitui": [
        "Central Kitui", "Kwa-Vonza", "Kyuso",
        "Mutito", "Mutomo", "Mwingi",
    ],
    "Kwale": ["Kinango", "Matuga", "Lunga Lunga", "Msambweni", "Samburu"],
    "Laikipia": ["Central Laikipia", "Mukogondo", "Ng'arua", "Rumuruti"],
    "Lamu": ["Amu", "Faza", "Kiunga", "Mpeketoni", "Witu"],
    "Machakos": [
        "Central Machakos", "Kangundo", "Kathiani",
        "Masinga", "Mwala", "Yatta",
    ],
    "Makueni": [
        "Kibwezi", "Kilome", "Makueni",
        "Mbooni", "Tsavo West National Park",
    ],
    "Malindi": ["Malindi", "Magarini"],
    "Mandera": [
        "Banissa", "Central Mandera", "Elwak",
        "Fino", "Rhamu", "Takaba",
    ],
    "Marakwet": ["Tot", "Tunyo", "Tirap", "Chepyemit", "Kapcherop"],
    "Marsabit": [
        "Central Marsabit", "Laisamis", "Loiyangalani",
        "Moyale", "North Horr", "Sololo",
    ],
    "Meru Central": [
        "Central Imenti", "Igembe", "Meru National Park",
        "Mount Kenya Forest", "North Imenti", "Ntonyiri",
        "South Imenti", "Tigania", "Timau",
    ],
    "Migori": ["Kehancha", "Migori", "Nyatike", "Rongo"],
    "Mombasa": ["Changamwe", "Kisauni", "Likoni", "Mvita"],
    "Mount Elgon": ["Kaptama", "Kapsokwony", "Kopsiro", "Cheptais"],
    "Murang'a": [
        "Gatanga", "Kandara", "Kangema", "Kigumo", "Kiharu", "Makuyu",
    ],
    "Mutomo": ["Ikutha", "Mutomo", "Mutha"],
    "Nairobi": [
        "Central Nairobi", "Dagoretti", "Embakasi", "Kasarani",
        "Lang'ata", "Makadara", "Westlands", "Pumwani",
    ],
    "Nakuru": [
        "Bahati", "Gilgil", "Mbogoini", "Molo", "Naivasha",
        "Nakuru Municipality", "Njoro", "Olenguruone",
        "Rongai", "Keringet",
    ],
    "Nandi": ["Aldai", "Kapsabet", "Kilibwoni", "Mosop", "Tindiret"],
    "Narok": [
        "Mara", "Mau", "Olokurto", "Osupuko",
        "Ololulunga", "Mulot", "Loita",
    ],
    "Nyamira": ["Borabu", "Ekerenyo", "Magombo", "Nyamira"],
    "Nyandarua": [
        "Kinangop", "Kipipiri", "Ndaragwa",
        "Ol Joro Orok", "Ol-Kalou",
    ],
    "Nyando": [
        "Muhoroni", "Upper Nyakach", "Lower Nyakach", "Nyando", "Miwani",
    ],
    "Nyeri": [
        "Aberdare Forest", "Kieni East", "Kieni West", "Mathira",
        "Mount Kenya Forest/National Park", "Mukurweini",
        "Nyeri Municipality", "Othaya", "Tetu",
    ],
    "Rachuonyo": [
        "West Karachuonyo", "East Karachuonyo", "Kasipul", "Kabondo",
    ],
    "Samburu": ["Baragoi", "Lorroki", "Wamba", "Waso"],
    "Siaya": [
        "Boro", "Karemo", "Ogongo", "Rarieda",
        "Ugunja", "Ukwala", "Yala",
    ],
    "Suba": ["Suba South", "Suba North"],
    "Taita-Taveta": [
        "Mwatate", "Taveta", "Tsavo East National Park",
        "Tsavo West National Park", "Voi", "Wundanyi",
    ],
    "Tana River": [
        "Bangale", "Bura", "Galole", "Garsen",
        "Kipini", "Madogo", "Wenje",
    ],
    "Teso": ["Chakol", "Amagoro", "Amukura", "Ang'urai"],
    "Tharaka": ["Chiakariga", "Gatunga", "Marimanti", "Nkondi", "Turima"],
    "Thika": [
        "Gatanga", "Gatundu", "Kamwangi", "Kakuzi",
        "Municipality", "Ruiru",
    ],
    "Trans Nzoia": [
        "Cherangani", "Kwanza", "Saboti", "Kitale", "Kiminini",
    ],
    "Turkana": [
        "Central", "Kakuma", "Katilu", "Kibish", "Lake Turkana",
        "Lokitaung", "Lokori", "Turkwel", "Lokichoggio",
    ],
    "Uasin Gishu": [
        "Ainabkoi", "Kesses", "Moiben", "Soy",
        "Eldoret", "Matunda", "Moi's Bridge",
    ],
    "Vihiga": [
        "Emuhaya", "Hamisi", "Sabatia", "Vihiga",
        "Mbale", "Majengo", "Chavakali",
    ],
    "Wajir": [
        "Buna", "Bute", "Central Wajir", "Griftu",
        "Habaswein", "Wajir-Bor",
    ],
    "West Pokot": [
        "Alale", "Chepareria", "Kacheliba", "Kapenguria", "Sigor",
    ],
}

SOURCE = "Wikipedia"
SOURCE_URL = "https://en.wikipedia.org/wiki/Divisions_of_Kenya"


def convert():
    records = []
    counter = 0

    for district_name in sorted(DIVISIONS_BY_DISTRICT.keys()):
        divisions = DIVISIONS_BY_DISTRICT[district_name]
        for div_name in divisions:
            counter += 1
            records.append({
                "id": f"KE-ADM-{counter:03d}",
                "native_id": f"ADM-{counter:03d}",
                "name": div_name,
                "level": 2,
                "level_name": "Division",
                "country": "KE",
                "parent_district": district_name,
                "status": "historical",
                "notes": f"Administrative division under {district_name} District",
                "source": SOURCE,
                "source_url": SOURCE_URL,
            })

    return records


def main():
    records = convert()
    out_dir = os.path.join(
        os.path.dirname(__file__), "..", "data", "KE"
    )
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "divisions_admin.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    # Count stats
    districts_with_data = len(DIVISIONS_BY_DISTRICT)
    total_divisions = len(records)
    print(f"✓ Wrote {total_divisions} divisions across "
          f"{districts_with_data} districts to {out_path}")


if __name__ == "__main__":
    main()
