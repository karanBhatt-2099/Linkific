import logging
from urllib.parse import urljoin

from scrapers.utils import PoliteSession

log = logging.getLogger("scraper.news")

START_URL = "https://news.ycombinator.com/news"


def parse_page(soup, page_url) -> list[dict]:
    items = []
    for row in soup.select("tr.athing"):
        link = row.select_one("span.titleline > a")
        if not link:
            continue
        sub = row.find_next_sibling("tr")
        links = sub.select("a") if sub else []
        score = sub.select_one("span.score") if sub else None
        author = sub.select_one("a.hnuser") if sub else None
        age = sub.select_one("span.age") if sub else None
        site = row.select_one("span.sitestr")
        items.append({
            "id": row.get("id"),
            "title": link.get_text(strip=True),
            "url": urljoin(page_url, link["href"]),
            "site": site.get_text(strip=True) if site else None,
            "points": score.get_text(strip=True) if score else None,
            "author": author.get_text(strip=True) if author else None,
            "posted": age.get("title") if age else None,
            "comments": links[-1].get_text(strip=True) if links else None,
        })
    return items


def fetch_body(sess, url, max_chars=2000):
    """Best-effort article text from the linked page; returns None on any failure."""
    try:
        soup = sess.soup(url)
    except Exception as e:
        log.info("Skip body for %s: %s", url, e)
        return None
    paras = soup.select("article p") or soup.select("p")
    text = " ".join(p.get_text(" ", strip=True) for p in paras)
    return text[:max_chars] or None


def scrape(max_pages: int = 2, with_body: bool = False, **_) -> list[dict]:
    sess = PoliteSession()
    url, page, articles = START_URL, 1, []
    while url and page <= max_pages:
        log.info("Page %d: %s", page, url)
        soup = sess.soup(url)
        articles.extend(parse_page(soup, url))
        more = soup.select_one("a.morelink")
        url = urljoin(url, more["href"]) if more else None
        page += 1
    if with_body:
        for a in articles:
            if a["site"]:  # skip internal HN posts
                a["body"] = fetch_body(sess, a["url"])
    return articles
