
from client import get


# 1. Page-number pagination
def page_number(url, max_pages=3):
    results = []

    for page in range(1, max_pages + 1):
        r = get(url, params={"_page": page, "_limit": 10})

        if r is None or not r.ok or not r.json():
            break

        results.extend(r.json())

    return results


# 2. Link-header pagination
def link_header(url, max_pages=3):
    results = []

    for _ in range(max_pages):
        r = get(url, params={"per_page": 10})

        if r is None or not r.ok:
            break

        results.extend(r.json())
        url = r.links.get("next", {}).get("url")

        if not url:
            break

    return results


# 3. Cursor-based pagination (template)
def cursor_based(url, headers=None):
    results = []
    cursor = None

    while True:
        params = {"cursor": cursor} if cursor else None
        r = get(url, headers=headers, params=params)

        if r is None or not r.ok:
            break

        data = r.json()
        results.extend(data["items"])
        cursor = data.get("next_cursor")

        if not cursor:
            break

    return results


if __name__ == "__main__":
    posts = page_number(
        "https://jsonplaceholder.typicode.com/posts"
    )
    print("Page-number:", len(posts), "items")

    issues = link_header(
        "https://api.github.com/repos/psf/requests/issues"
    )
    print("Link-header:", len(issues), "items")
