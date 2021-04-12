import csv
import json
import random
import string
import re
from decimal import Decimal

valid_chars = string.ascii_letters + string.digits
def gen_id():
    return ''.join(random.choice(valid_chars) for i in range(16))

def handle_range(r):
    value = None
    text = None

    if re.search("^\\d+m$", r):
        value = int(r.strip("m"))
    elif re.search("^\\d+-\\d+m$", r):
        value = int(r.split("-")[1].strip("m"))
        text = f"Range: {r}"
    elif re.search("†", r):
        text = "Range: Depends on ammunition"
    else:
        text = f"Range: {r}"

    return {
        "orig": r,
        "value": value,
        "text": text,
    }

def handle_rof(rof):
    split = rof.split("/")
    single = split[0]
    burst = split[1]
    full = split[2]

    return {
        "orig": rof,
        "single": 1 if single == "S" else 0,
        "burst": 0 if burst == "-" else int(burst),
        "full": 0 if full == "-" else int(full),
    }

type_map = {
    "X": "explosive",
    "R": "rending",
    "I": "impact",
    "E": "energy",
}
def handle_damage(d):
    value = ""
    type = "impact"

    if re.search("†", d):
        value = d
    elif re.search("-", d):
        # Defaults are fine
        pass
    else:
        type_char = d[-1]
        type = type_map[type_char]
        value = d[0:-1]

    return {
        "orig": d,
        "value": value,
        "type": type,
    }

rarity_map = {
        'Unique': "unique",
        'Near Unique': "near-unique",
        'Extremely Rare': "extremely-rare",
        'Very Rare': "very-rare",
        'Rare': "rare",
        'Scarce': "scarce",
        'Average': "average",
        'Common': "common",
        'Plentiful': "plentiful",
}
def handle_rarity(d):
    return "extremely-rare" if d == "" else rarity_map[d]

def weapon_to_json(row):
    r = handle_range(row["Range"])
    rof = handle_rof(row["RoF"])
    damage = handle_damage(row["Damage"])
    clip = 0 if row["Clip"] == "-" else int(row["Clip"])
    # If any of these have a cross in them, add a note to the description
    cross = '†' in (row["Damage"] + row["Pen"] + row["Qualities"])
    return json.dumps({
          "_id": gen_id(),
          "name": row["Name"],
          "type": "weapon",
          "data": {
            "craftsmanship": "common",
            "description": (f'<p>{r["text"]}</p>\n' if r["text"] else '') +
                           f'<p>Source: {row["Source"]}</p>' +
                           (f'\n<p>Page: {row["Book and Page#"]}</p>' if row["Book and Page#"] else '') +
                           ("\n<p>† means: Depends on ammunition</p>" if cross else ''),
            "availability": handle_rarity(row["Rarity"]),
            "weight": 0 if row["Wt"] == "" else float(row["Wt"]),
            "class": row["Class"].lower(),
            "range": r["value"],
            "originalRange": r["orig"],
            "rateOfFire": {
              "single": rof["single"],
              "burst": rof["burst"],
              "full": rof["full"]
            },
            "originalRateOfFire": rof["orig"],
            "damage": damage["value"],
            "originalDamage": damage["orig"],
            "damageType": damage["type"],
            "penetration": row["Pen"],
            "clip": {
              "max": clip,
              "value": clip, 
            },
            "reload": row["Rld"],
            "special": row["Qualities"],
            "attack": 0,
            "source": row["Source"],
            "type": row["Type"],
          },
          "flags": {},
          "img": "icons/svg/mystery-man.svg",
          "effects": []
        })

with open("./ranged-weapons.csv") as talents_file:
    reader = csv.DictReader(talents_file)
    with open("./packs/dh-ranged-weapons.db", "a") as output_file:
        for row in reader:
            output = weapon_to_json(row)
            output_file.write(output + "\n")
