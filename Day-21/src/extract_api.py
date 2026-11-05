"""3 different REST APIs (all free, no API key)."""
import pandas as pd
import requests

from src.utils import save_raw


def get_json(url, params=None):
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def api_users():
    data = get_json("https://jsonplaceholder.typicode.com/users")
    df = pd.json_normalize(data).rename(columns={"address.city": "city"})
    save_raw(df[["id", "name", "email", "phone", "city"]], "api_users", "jsonplaceholder_api")


def api_weather():
    data = get_json(
        "https://api.open-meteo.com/v1/forecast",
        {"latitude": 19.07, "longitude": 72.88, "timezone": "Asia/Kolkata",
         "daily": "temperature_2m_max,temperature_2m_min"},
    )
    save_raw(pd.DataFrame(data["daily"]), "api_weather", "open_meteo_api")


def api_countries():
    data = get_json("https://api.worldbank.org/v2/country",
                    {"format": "json", "per_page": 300})
    if not isinstance(data, list) or len(data) < 2:   # guard: API sent an error instead of data
        raise ValueError(f"Unexpected API response: {str(data)[:200]}")
    rows = [{"country": c["name"],
             "capital": c["capitalCity"] or None,
             "region": c["region"]["value"],
             "income_level": c["incomeLevel"]["value"]}
            for c in data[1] if c["region"]["value"] != "Aggregates"]   # skip groups like "World"
    save_raw(pd.DataFrame(rows), "api_countries", "worldbank_api")
