import csv
import json
import random
import string
import re
from decimal import Decimal

valid_chars = string.ascii_letters + string.digits
def gen_id():
    return ''.join(random.choice(valid_chars) for i in range(16))

def handle_class(c):
    return {
        "value": 'thrown' if ('Thrown' in c) else 'melee',
        "text": f'Class: {c}',
    }

def handle_range(r):
    value = None
    text = None

    if re.search("^\\d+m$", r):
        value = int(r.strip("m"))
    elif r == "":
        # Defaults are fine
        pass
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

    if d == "-":
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
        'Abundant': "abundant",
}
def handle_rarity(d):
    return "extremely-rare" if d == "" else rarity_map[d]

def weapon_to_json(row):
    r = handle_range(row["Range"])
    damage = handle_damage(row["Damage"])
    return json.dumps({
          "_id": gen_id(),
          "name": row["Name"],
          "type": "weapon",
          "data": {
            "craftsmanship": "common",
            "description": (f'<p>{r["text"]}</p>\n' if r["text"] else '') +
                           f'<p>Source: {row["Source"]}</p>' +
                           (f'\n<p>Page: {row["Book and Page#"]}</p>' if row["Book and Page#"] else ''),
            "availability": handle_rarity(row["Availability"]),
            "weight": 0 if row["Wt"] == "" else float(row["Wt"]),
            "class": "thrown",
            "range": r["value"],
            "originalRange": r["orig"],
            "rateOfFire": {
              "single": 0,
              "burst": 0,
              "full": 0,
            },
            "damage": damage["value"],
            "originalDamage": damage["orig"],
            "damageType": damage["type"],
            "penetration": row["Pen"],
            "clip": {
              "max": 0,
              "value": 0, 
            },
            "reload": "",
            "special": row["Qualities"],
            "attack": 0,
            "source": row["Source"],
            "type": row["Type"],
          },
          "flags": {},
          "img": "icons/svg/mystery-man.svg",
          "effects": []
        })

def ammo_to_json(row):
    return json.dumps({
          "_id": gen_id(),
          "name": row["Name"],
          "type": "ammunition",
          "data": {
            "craftsmanship": "common",
            "description": f'<p>Source: {row["Source"]}</p>' +
                           (f'\n<p>Page: {row["Book and page#"]}</p>' if row["Book and page#"] else ''),
            "availability": handle_rarity(row["Rarity"]),
            "weight": 0,
            "quantity": 0,
            "effect": {
                "damage": {
                    "modifier": "Unknown",
                    "type": "impact",
                },
                "special": row["Affect"],
                "penetration": 0,
                "attack": {
                    "modifier": 0,
                }
            },
            "weapon": row["Weapons that can use said Ammunition"],
            "source": row["Source"]
          },
          "flags": {},
          "img": "icons/svg/mystery-man.svg",
          "effects": []
        })

def tool_to_json(row):
    return json.dumps({
          "_id": gen_id(),
          "name": row["Name"],
          "type": "tool",
          "data": {
            "description": f'<p>Weight: Not in the data sheet</p>' +
                           f'\n<p>Source: {row["Source"]}</p>' +
                           (f'\n<p>Page: {row["Book and page#"]}</p>' if row["Book and page#"] else ''),
            "craftsmanship": "common",
            "availability": handle_rarity(row["Rarity"]),
            "weight": 0,
            "shortDescription": row["Effect"],
            "source": row["Source"]
          },
          "flags": {},
          "img": "icons/svg/mystery-man.svg",
          "effects": []
        })

def gear_to_json(row):
    return json.dumps({
          "_id": gen_id(),
          "name": row["Name"],
          "type": "gear",
          "data": {
            "description": f'<p>Weight: Not in the data sheet</p>' +
                           f'\n<p>Source: {row["Source"]}</p>' +
                           (f'\n<p>Page: {row["Book and page#"]}</p>' if row["Book and page#"] else ''),
            "craftsmanship": "common",
            "availability": handle_rarity(row["Rarity"]),
            "weight": 0,
            "shortDescription": row["Effects"],
            "source": row["Source"]
          },
          "flags": {},
          "img": "icons/svg/mystery-man.svg",
          "effects": []
        })

def cybernetics_to_json(row):
    return json.dumps({
          "_id": gen_id(),
          "name": row["Name"],
          "type": "cybernetic",
          "data": {
            "craftsmanship": "common",
            "description": f'<p>{row["Effects"]}</p>' +
                           f'\n<p>Weight: Not in the data sheet</p>' +
                           f'\n<p>Source: {row["Source"]}</p>' +
                           (f'\n<p>Page: {row["Book and page#"]}</p>' if row["Book and page#"] else ''),
            "availability": handle_rarity(row["Rarity"]),
            "weight": 0,
            "installed": False,
            "source": row["Source"],
          },
          "flags": {},
          "img": "icons/svg/mystery-man.svg",
          "effects": []
        })

with open("./cybernetics.csv") as talents_file:
    reader = csv.DictReader(talents_file)
    with open("./packs/dh-cybernetics.db", "a") as output_file:
        for row in reader:
            output = cybernetics_to_json(row)
            output_file.write(output + "\n")
