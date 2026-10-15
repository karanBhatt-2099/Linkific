# Web Scraping Project

BeautifulSoup + Selenium scrapers, cleaning, and storage (CSV / JSON / SQLite) with ethical-scraping defaults.

## Structure
```
web-scraping-project/
├── main.py                      # CLI entry point
├── config.py                    # paths, user-agent, delay, timeouts
├── requirements.txt
├── ETHICAL_SCRAPING_CHECKLIST.md
├── scrapers/
│   ├── utils.py                 # PoliteSession (robots.txt, rate limit, retries, UA)
│   ├── books_scraper.py         # product listings: pagination + detail links
│   ├── news_scraper.py          # news articles (Hacker News)
│   ├── jobs_scraper.py          # job postings
│   ├── table_scraper.py         # HTML tables + search form + pagination
│   ├── login_scraper.py         # POST form login (CSRF) then scrape
│   └── dynamic_scraper.py       # Selenium scraper for JS-rendered site
├── cleaning/
│   ├── clean.py                 # types, missing values, duplicates
│   └── aggregate.py             # merge sources into unified dataset
├── storage/
│   ├── files.py                 # CSV / JSON
│   └── database.py              # SQLite
└── data/
    ├── raw/                     # scraper output
    ├── clean/                   # cleaned + unified datasets
    └── scraped.db               # SQLite database
```

## Setup
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
`quotes_js` needs Google Chrome installed (Selenium 4 downloads the driver automatically).

## Run
```bash
python main.py scrape books jobs --max-pages 2   # specific scrapers
python main.py scrape all                        # every scraper
python main.py clean                             # data/raw -> data/clean
python main.py aggregate                         # data/clean/unified.csv
python main.py store                             # load clean data into SQLite
python main.py run-all                           # the whole pipeline
```

## Datasets produced
| Name | Source | Technique |
|---|---|---|
| books | books.toscrape.com | pagination, follow links |
| news | news.ycombinator.com | robots Crawl-delay honoured |
| jobs | realpython.github.io/fake-jobs | single page |
| hockey | scrapethissite.com | tables, GET form, pagination |
| quotes_login | quotes.toscrape.com/login | POST form + session |
| quotes_js | quotes.toscrape.com/js | Selenium (JavaScript) |
| unified | all of the above | aggregated + deduplicated |

## Querying the database
```python
from storage.database import query
print(query("SELECT category, ROUND(AVG(price_gbp),2) avg_price FROM books GROUP BY category"))
```
