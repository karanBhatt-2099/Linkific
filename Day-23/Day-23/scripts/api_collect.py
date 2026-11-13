"""3 APIs: no auth, bearer-token auth, API-key-header auth. All paginated + rate limited."""
import os
import time

from scripts.common import http_get, log, save_raw


def fetch_all(url, page_size, params=None, headers=None, page_param="page",
              size_param="per_page", max_pages=5, pause=1):
    """Generic page-number pagination. Stops on empty/short page or max_pages."""
    records = []
    for page in range(1, max_pages + 1):
        q = {**(params or {}), page_param: page, size_param: page_size}
        data = http_get(url, q, headers).json()
        log.info("%s page %s -> %s items", url, page, len(data))
        records += data
        if len(data) < page_size:
            break
        time.sleep(pause)  # rate limiting: be polite between calls
    return records


def collect_posts():  # API 1: no auth
    save_raw("api_posts", fetch_all("https://jsonplaceholder.typicode.com/posts", 20,
                                    page_param="_page", size_param="_limit"))


def collect_github():  # API 2: Bearer token auth
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    save_raw("api_github", fetch_all("https://api.github.com/orgs/apache/repos", 100,
                                     headers=headers, max_pages=2))


def collect_crypto():  # API 3: API key in header
    key = os.getenv("COINGECKO_API_KEY")
    headers = {"x-cg-demo-api-key": key} if key else {}
    save_raw("api_crypto", fetch_all("https://api.coingecko.com/api/v3/coins/markets", 100,
                                     params={"vs_currency": "usd"}, headers=headers, max_pages=2))
