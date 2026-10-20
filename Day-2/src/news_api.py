"""API 5: News API (needs a free key).
Shows API key in a HEADER (the more secure place) + pagination."""
import os
import pandas as pd
from dotenv import load_dotenv
from client import get

load_dotenv()
URL = "https://newsapi.org/v2/everything"


def main(pages=2):
    print("== News API ==")
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        print("Missing NEWS_API_KEY in .env - skipping.")
        return

    headers = {"X-Api-Key": api_key}                 # key in header
    articles = []
    for page in range(1, pages + 1):
        r = get(URL, headers=headers,
                params={"q": "python programming", "pageSize": 20,
                        "page": page, "language": "en"})
        if r is None:
            break
        for a in r.json().get("articles", []):
            articles.append({
                "source": a["source"]["name"],
                "title": a["title"],
                "author": a["author"],
                "published_at": a["publishedAt"],
                "url": a["url"],
            })

    pd.DataFrame(articles).to_csv("data/processed/news.csv", index=False)
    print(f"Saved {len(articles)} articles")


if __name__ == "__main__":
    main()
