
import argparse
import importlib
import logging
from datetime import datetime, timezone

import config
from cleaning.aggregate import aggregate
from cleaning.clean import clean_all
from storage.database import load_clean_into_db
from storage.files import save_both

SCRAPERS = {
    "books": "scrapers.books_scraper",
    "news": "scrapers.news_scraper",
    "jobs": "scrapers.jobs_scraper",
    "hockey": "scrapers.table_scraper",
    "quotes_login": "scrapers.login_scraper",
    "quotes_js": "scrapers.dynamic_scraper",   # needs Chrome + selenium
}
log = logging.getLogger("main")


def run_scrape(names, max_pages=None):
    names = list(SCRAPERS) if "all" in names else names
    for name in names:
        try:
            module = importlib.import_module(SCRAPERS[name])
            rows = module.scrape(**({"max_pages": max_pages} if max_pages else {}))
            stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
            for r in rows:
                r["scraped_at"] = stamp
            save_both(rows, config.RAW_DIR, name)
            log.info("%s: saved %d raw rows", name, len(rows))
        except Exception as e:
            log.error("%s failed: %s", name, e)


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scrape")
    s.add_argument("names", nargs="+", choices=[*SCRAPERS, "all"])
    s.add_argument("--max-pages", type=int)
    for c in ("clean", "aggregate", "store", "run-all"):
        sub.add_parser(c)
    args = p.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    if args.cmd == "scrape":
        run_scrape(args.names, args.max_pages)
    elif args.cmd == "clean":
        clean_all()
    elif args.cmd == "aggregate":
        aggregate()
    elif args.cmd == "store":
        log.info("Tables in %s: %s", config.DB_PATH.name, load_clean_into_db())
    else:  # run-all
        run_scrape(["all"])
        clean_all()
        aggregate()
        load_clean_into_db()


if __name__ == "__main__":
    main()
