"""API 4: OpenWeather (needs a free key).
Shows API key passed as a query parameter + .env secrets."""
import os
import pandas as pd
from dotenv import load_dotenv
from client import get

load_dotenv()
URL = "https://api.openweathermap.org/data/2.5/weather"
CITIES = ["Mumbai", "Delhi", "London", "New York", "Tokyo", "Sydney"]


def main():
    print("== OpenWeather ==")
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        print("Missing OPENWEATHER_API_KEY in .env - skipping.")
        return

    rows = []
    for city in CITIES:
        r = get(URL, params={"q": city, "appid": api_key, "units": "metric"})
        if r is None:
            continue
        d = r.json()
        rows.append({
            "city": d["name"],
            "country": d["sys"]["country"],
            "temp_c": d["main"]["temp"],
            "humidity": d["main"]["humidity"],
            "weather": d["weather"][0]["description"],   # list -> dict
            "wind_speed": d["wind"]["speed"],
        })
        print(f"  {city}: {rows[-1]['temp_c']} C")

    pd.DataFrame(rows).to_csv("data/processed/weather.csv", index=False)
    print(f"Saved {len(rows)} cities")


if __name__ == "__main__":
    main()
