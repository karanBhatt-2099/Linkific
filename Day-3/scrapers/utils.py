import logging
import time
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

import config

log = logging.getLogger("scraper")


class PoliteSession:
    def __init__(self, delay: float = config.REQUEST_DELAY):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": config.USER_AGENT})
        self.delay = delay
        self._robots = {}
        self._last = 0.0

    # ---- robots.txt -------------------------------------------------
    def _parser(self, url):
        p = urlparse(url)
        root = f"{p.scheme}://{p.netloc}"
        if root not in self._robots:
            rp = RobotFileParser()
            rp.set_url(root + "/robots.txt")
            try:
                rp.read()
            except Exception as e:  # network problem -> log and continue
                log.warning("Could not read robots.txt for %s: %s", root, e)
                rp = None
            self._robots[root] = rp
        return self._robots[root]

    def allowed(self, url) -> bool:
        rp = self._parser(url)
        return True if rp is None else rp.can_fetch(config.USER_AGENT, url)

    # ---- rate limiting ----------------------------------------------
    def _wait(self, url):
        rp = self._parser(url)
        crawl_delay = rp.crawl_delay(config.USER_AGENT) if rp else None
        gap = max(self.delay, float(crawl_delay or 0))
        elapsed = time.time() - self._last
        if elapsed < gap:
            time.sleep(gap - elapsed)

    # ---- requests ---------------------------------------------------
    def request(self, method, url, **kwargs):
        if not self.allowed(url):
            raise PermissionError(f"Blocked by robots.txt: {url}")
        kwargs.setdefault("timeout", config.TIMEOUT)
        for attempt in range(1, config.MAX_RETRIES + 1):
            self._wait(url)
            try:
                resp = self.session.request(method, url, **kwargs)
                self._last = time.time()
                resp.raise_for_status()
                return resp
            except requests.RequestException as e:
                self._last = time.time()
                status = getattr(getattr(e, "response", None), "status_code", None)
                client_error = status is not None and 400 <= status < 500 and status != 429
                log.warning("Attempt %d/%d failed for %s: %s", attempt, config.MAX_RETRIES, url, e)
                if client_error or attempt == config.MAX_RETRIES:
                    raise
                time.sleep(2 ** attempt)

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)

    def soup(self, url, **kwargs) -> BeautifulSoup:
        # use .content so bs4 detects encoding itself (avoids "Â£" artefacts)
        return BeautifulSoup(self.get(url, **kwargs).content, "html.parser")


def parse_quotes(soup: BeautifulSoup) -> list[dict]:
    """Shared by the login scraper and the Selenium scraper (quotes.toscrape.com)."""
    rows = []
    for q in soup.select("div.quote"):
        rows.append({
            "text": q.select_one("span.text").get_text(strip=True),
            "author": q.select_one("small.author").get_text(strip=True),
            "tags": ", ".join(t.get_text(strip=True) for t in q.select("a.tag")),
        })
    return rows
