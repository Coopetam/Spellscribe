import json
import os

# This file is responsible for loading and validating spell data
# from spells.json at startup.
#
# Think of it as the librarian — it goes and fetches all the spell
# books, checks they're all intact, and hands them to the rest of
# the app in a clean, ready-to-use format.

# These are the fields every spell MUST have.
# If any are missing the loader will warn us instead of crashing silently.
REQUIRED_FIELDS = [
    "id",
    "name",
    "sigil",
    "sphere_level",
    "description",
    "valid_target",
    "crafting_cost",
    "sound"
]

def load_spells():
    """
    Reads spells.json and returns a list of spell dictionaries.
    If the file is missing or broken, returns an empty list
    and prints a helpful error message.
    """

    # Build the path to spells.json
    # os.path.dirname(__file__) means "the folder this file is in" (services/)
    # We go up one level (..) then into data/spells.json
    base_dir = os.path.dirname(__file__)
    spells_path = os.path.join(base_dir, "..", "data", "spells.json")

    # --- CHECK THE FILE EXISTS ---
    if not os.path.exists(spells_path):
        print(f"ERROR: spells.json not found at {spells_path}")
        print("The app will run but the grimoire will be empty.")
        return []

    # --- READ AND PARSE THE FILE ---
    try:
        with open(spells_path, "r", encoding="utf-8") as f:
            spells = json.load(f)
    except json.JSONDecodeError as e:
        # This means the JSON has a formatting error (missing comma, bracket etc.)
        print(f"ERROR: spells.json has a formatting error: {e}")
        print("Check your JSON for missing commas, quotes, or brackets.")
        return []

    # --- VALIDATE EACH SPELL ---
    # Loop through every spell and check it has all the required fields
    valid_spells = []

    for spell in spells:
        spell_name = spell.get("name", "UNKNOWN")
        missing = []

        for field in REQUIRED_FIELDS:
            if field not in spell:
                missing.append(field)

        if missing:
            # Warn us but don't crash — just skip the broken spell
            print(f"WARNING: Spell '{spell_name}' is missing fields: {missing}")
            print(f"  This spell will be skipped.")
        else:
            valid_spells.append(spell)

    # --- REPORT RESULTS ---
    print(f"Spell loader: {len(valid_spells)} of {len(spells)} spells loaded successfully.")

    for spell in valid_spells:
        level_numerals = {1: "I", 2: "II", 3: "III"}
        level = level_numerals.get(spell["sphere_level"], "?")
        print(f"  [{level}] {spell['name']}")

    return valid_spells