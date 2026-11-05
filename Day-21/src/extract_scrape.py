"""Web scraping: first page of books.toscrape.com (a site built for practice)."""
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

from src.utils import save_raw


def web_books():
    r = requests.get("https://books.toscrape.com/", timeout=30)
    r.raise_for_status()
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "html.parser")
    rows = []
    for book in soup.select("article.product_pod"):
        price = re.sub(r"[^\d.]", "", book.select_one(".price_color").text)
        rows.append({
            "title": book.h3.a["title"],
            "price_gbp": float(price),
            "rating": book.select_one("p.star-rating")["class"][1],  # e.g. 'Three'
        })
    save_raw(pd.DataFrame(rows), "web_books", "books.toscrape.com")
