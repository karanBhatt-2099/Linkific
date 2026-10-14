import logging
from urllib.parse import urljoin

from scrapers.utils import PoliteSession

log = logging.getLogger("scraper.books")

START_URL = "https://books.toscrape.com/catalogue/page-1.html"
RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def parse_listing(soup, page_url) -> list[dict]:
    items = []
    for art in soup.select("article.product_pod"):
        a = art.select_one("h3 a")
        items.append({
            "title": a["title"],
            "url": urljoin(page_url, a["href"]),
            "price": art.select_one("p.price_color").get_text(strip=True),
            "rating": RATINGS.get(art.select_one("p.star-rating")["class"][1]),
            "in_stock": "in stock" in art.select_one("p.availability").get_text().lower(),
        })
    return items


def parse_detail(soup) -> dict:
    info = {tr.th.get_text(strip=True): tr.td.get_text(strip=True)
            for tr in soup.select("table.table-striped tr")}
    crumbs = soup.select("ul.breadcrumb li a")
    desc = soup.select_one("#product_description ~ p")
    return {
        "upc": info.get("UPC"),
        "category": crumbs[-1].get_text(strip=True) if len(crumbs) >= 3 else None,
        "description": desc.get_text(strip=True) if desc else None,
    }


def scrape(max_pages: int = 3, details: bool = True, **_) -> list[dict]:
    sess = PoliteSession()
    url, page, books = START_URL, 1, []
    while url and page <= max_pages:
        log.info("Page %d: %s", page, url)
        soup = sess.soup(url)
        books.extend(parse_listing(soup, url))
        nxt = soup.select_one("li.next a")
        url = urljoin(url, nxt["href"]) if nxt else None
        page += 1
    if details:
        for b in books:
            try:
                b.update(parse_detail(sess.soup(b["url"])))
            except Exception as e:
                log.warning("Detail failed for %s: %s", b["url"], e)
    return books
