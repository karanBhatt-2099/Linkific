import logging
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config
from scrapers.utils import PoliteSession, parse_quotes

log = logging.getLogger("scraper.dynamic")

URL = "https://quotes.toscrape.com/js/"
QUOTE = (By.CSS_SELECTOR, "div.quote")


def make_driver(headless: bool = True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument(f"--user-agent={config.USER_AGENT}")
    return webdriver.Chrome(options=opts)  # Selenium Manager fetches the driver


def static_html_has_data() -> bool:
    """Proves why Selenium is needed: plain requests gets an empty shell."""
    return bool(PoliteSession().soup(URL).select("div.quote"))


def scrape(max_pages: int = 3, headless: bool = True, **_) -> list[dict]:
    if not PoliteSession().allowed(URL):
        raise PermissionError(f"Blocked by robots.txt: {URL}")
    log.info("requests sees data without JS: %s", static_html_has_data())

    driver, quotes = make_driver(headless), []
    try:
        driver.get(URL)
        for page in range(1, max_pages + 1):
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(QUOTE))
            quotes.extend(parse_quotes(BeautifulSoup(driver.page_source, "html.parser")))
            nxt = driver.find_elements(By.CSS_SELECTOR, "li.next a")
            if not nxt or page == max_pages:
                break
            first = driver.find_element(*QUOTE)
            nxt[0].click()
            WebDriverWait(driver, 10).until(EC.staleness_of(first))  # old page content gone
            time.sleep(config.REQUEST_DELAY)
    finally:
        driver.quit()
    return quotes
