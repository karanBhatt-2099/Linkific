import logging

from scrapers.utils import PoliteSession

log = logging.getLogger("scraper.tables")

URL = "https://www.scrapethissite.com/pages/forms/"


def extract_table(table) -> list[dict]:
    """Generic HTML <table> -> list of dicts keyed by header text."""
    headers = [" ".join(th.get_text().split()) for th in table.select("tr th")]
    rows = []
    for tr in table.select("tr"):
        cells = [" ".join(td.get_text().split()) for td in tr.find_all("td")]
        if cells:
            rows.append(dict(zip(headers, cells)))
    return rows


def scrape(query: str = "", max_pages: int = 3, **_) -> list[dict]:
    sess = PoliteSession()
    rows = []
    for page in range(1, max_pages + 1):
        params = {"page_num": page}
        if query:
            params["q"] = query
        soup = sess.soup(URL, params=params)
        table = soup.select_one("table.table")
        page_rows = extract_table(table) if table else []
        if not page_rows:
            break
        log.info("Page %d: %d rows", page, len(page_rows))
        rows.extend(page_rows)
    return rows
