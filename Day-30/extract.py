"""Step 1: Pull product data from a public API and save it as CSV."""
import requests
import pandas as pd

URL = "https://dummyjson.com/products?limit=100"


def extract(path="products.csv"):
    response = requests.get(URL, timeout=30)
    response.raise_for_status()                      # fail loudly on API errors
    products = response.json()["products"]

    df = pd.DataFrame(products)[["id", "title", "category", "price", "stock", "rating"]]
    df.to_csv(path, index=False)
    print(f"Saved {len(df)} rows to {path}")


if __name__ == "__main__":
    extract()
