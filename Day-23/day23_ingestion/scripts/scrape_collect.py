"""Web scraping: static HTML (BeautifulSoup) and dynamic JS content (call the JSON endpoint the page uses)."""
import time

from bs4 import BeautifulSoup

from scripts.common import http_get, save_raw


def scrape_books(max_pages=3):  # static HTML, paginated
    books = []
    for page in range(1, max_pages + 1):
        html = http_get(f"https://books.toscrape.com/catalogue/page-{page}.html").content
        soup = BeautifulSoup(html, "html.parser")
        for b in soup.select("article.product_pod"):
            books.append({
                "title": b.h3.a["title"],
                "price": b.select_one(".price_color").text,
                "rating": b.p["class"][1],
                "in_stock": "In stock" in b.select_one(".availability").text,
            })
        time.sleep(1)
    save_raw("scrape_books", books)


def scrape_quotes(max_pages=5):
    """Dynamic content: quotes.toscrape.com/scroll renders via JavaScript, so a plain HTML
    fetch is empty. Easiest fix = call the same JSON endpoint the JavaScript calls
    (found in the browser's Network tab). Use Playwright only if no such endpoint exists."""
    quotes = []
    for page in range(1, max_pages + 1):
        data = http_get("https://quotes.toscrape.com/api/quotes", {"page": page}).json()
        quotes += data["quotes"]
        if not data["has_next"]:
            break
        time.sleep(1)
    save_raw("scrape_quotes", quotes)
