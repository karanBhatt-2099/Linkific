from scrapers.utils import PoliteSession

URL = "https://realpython.github.io/fake-jobs/"


def parse_jobs(soup) -> list[dict]:
    jobs = []
    for card in soup.select("div.card-content"):
        links = card.select("footer a")
        time_tag = card.select_one("time")
        jobs.append({
            "title": card.select_one("h2.title").get_text(strip=True),
            "company": card.select_one("h3.company").get_text(strip=True),
            "location": card.select_one("p.location").get_text(strip=True),
            "date_posted": time_tag.get("datetime") if time_tag else None,
            "apply_url": links[-1]["href"] if links else None,
        })
    return jobs


def scrape(**_) -> list[dict]:
    return parse_jobs(PoliteSession().soup(URL))
