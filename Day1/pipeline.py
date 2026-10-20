import csv
import json
from pathlib import Path

import requests

URL = "https://pokeapi.co/api/v2/pokemon/{}"
NAMES = ["ditto", "pikachu", "charizard", "bulbasaur", "squirtle",
         "ditto", "eevee", "snorlax", "notapokemon"]      # ditto = duplicate, last = fake name
OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(exist_ok=True)


def fetch(names):
    """Fetch every name. Failed calls are recorded, not fatal."""
    records, failures = [], []
    for name in names:
        try:
            response = requests.get(URL.format(name.strip().lower()), timeout=10)
            response.raise_for_status()
            records.append(response.json())
        except (requests.RequestException, ValueError) as err:
            failures.append(f"{name}: {type(err).__name__}")
    return records, failures


def extract(raw):
    """Keep only the fields we need."""
    return {
        "id": raw.get("id"),
        "name": raw.get("name"),
        "height_m": raw.get("height"),
        "weight_kg": raw.get("weight"),
        "types": ", ".join(t["type"]["name"] for t in raw.get("types", [])),
    }


def clean(rec):
    """Return a clean record, or None if it is invalid."""
    try:
        if not rec["name"] or rec["height_m"] <= 0 or rec["weight_kg"] <= 0:
            return None
        return {**rec, "name": rec["name"].strip().title(),
                "height_m": rec["height_m"] / 10,          # decimetres -> metres
                "weight_kg": rec["weight_kg"] / 10}        # hectograms -> kg
    except (TypeError, KeyError):
        return None


if __name__ == "__main__":
    raw, failures = fetch(NAMES)
    (OUT / "raw.json").write_text(json.dumps(raw, indent=2), encoding="utf-8")

    cleaned = [clean(extract(r)) for r in raw]
    valid = [r for r in cleaned if r]
    unique = {r["id"]: r for r in valid}.values()          # dict key = id removes duplicates

    with open(OUT / "pokemon_clean.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "height_m", "weight_kg", "types"])
        writer.writeheader()
        writer.writerows(unique)

    print(f"Fetched: {len(raw)} | API failures: {len(failures)} {failures}")
    print(f"Rejected: {len(raw) - len(valid)} | Duplicates removed: {len(valid) - len(unique)}")
    print(f"Saved: {len(unique)} records -> {OUT / 'pokemon_clean.csv'}")