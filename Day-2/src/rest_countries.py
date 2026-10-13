
import os
import pandas as pd
from client import get

URL = "https://api.restcountries.com/countries/v5"


def main():
    print("== REST Countries ==")

    headers = {"Authorization": "Bearer rc_live_demo"}
    params = {
        "limit": 100,
        "response_fields": "names.common,capitals,region,population,geography.area,languages,currencies"
    }

    r = get(URL, headers=headers, params=params)

    if r is None or not r.ok:
        print("Failed to fetch countries")
        return

    data = r.json()
    countries = data.get("data", {}).get("objects", [])

    if not countries:
        print("No country data found:", data.get("errors"))
        return

    rows = []

    for c in countries:
        capitals = c.get("capitals") or []
        capital_names = [
            x.get("name", "N/A") if isinstance(x, dict) else str(x)
            for x in capitals
        ]

        rows.append({
            "name": c.get("names", {}).get("common", "N/A"),
            "capital": ", ".join(capital_names) or "N/A",
            "region": c.get("region", "N/A"),
            "population": c.get("population", 0),
            "area": c.get("geography", {}).get("area", 0),
            "languages": str(c.get("languages", [])),
            "currencies": str(c.get("currencies", {}))
        })

    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("data/raw", exist_ok=True)

    df = pd.DataFrame(rows).sort_values(
        "population", ascending=False
    )

    df.to_csv("data/processed/countries.csv", index=False)
    df.to_json("data/raw/countries.json", orient="records", indent=2)

    print(f"Saved {len(df)} countries")
    print(df.head().to_string(index=False))


if __name__ == "__main__":
    main()
