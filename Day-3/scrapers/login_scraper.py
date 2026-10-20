import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scrapers.utils import PoliteSession, parse_quotes

log = logging.getLogger("scraper.login")

LOGIN_URL = "https://quotes.toscrape.com/login"


def scrape(max_pages: int = 2, username: str = "demo", password: str = "demo", **_) -> list[dict]:
    sess = PoliteSession()
    token = sess.soup(LOGIN_URL).select_one("input[name=csrf_token]")["value"]
    resp = sess.post(LOGIN_URL, data={"csrf_token": token, "username": username, "password": password})
    page = BeautifulSoup(resp.content, "html.parser")
    if not page.select_one("a[href='/logout']"):
        raise RuntimeError("Login failed")

    quotes, url, n = [], resp.url, 1
    while url and n <= max_pages:
        quotes.extend(parse_quotes(page))
        nxt = page.select_one("li.next a")
        url = urljoin(url, nxt["href"]) if nxt else None
        if url and n < max_pages:
            page = sess.soup(url)
        n += 1
    return quotes
