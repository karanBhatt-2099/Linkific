import os
from datetime import datetime

import requests
from airflow.decorators import dag, task
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.trigger_rule import TriggerRule

# ---- Change these two to use another Apify actor ----
ACTOR_ID = "apify~website-content-crawler"
RUN_INPUT = {
    "startUrls": [{"url": "https://docs.apify.com/academy"}],
    "maxCrawlPages": 5,
    "crawlerType": "cheerio",   # fastest / cheapest crawler
}


@dag(
    dag_id="03_apify_etl_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule="0 6 * * *",               # every day at 06:00
    catchup=False,
    default_args={"retries": 1},        # retry once if the API call fails
    tags=["day13", "etl", "apify"],
)
def apify_etl():

    # SQL operator (PostgresOperator replacement): create the target table
    create_table = SQLExecuteQueryOperator(
        task_id="create_table",
        conn_id="warehouse_db",
        sql="""
            CREATE TABLE IF NOT EXISTS apify_pages (
                url        TEXT PRIMARY KEY,
                title      TEXT,
                word_count INT,
                preview    TEXT,
                crawled_at TIMESTAMPTZ,
                loaded_at  TIMESTAMP DEFAULT NOW()
            );
        """,
    )

    @task
    def extract():
        """E: run the Apify actor and get its dataset items."""
        url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/run-sync-get-dataset-items"
        response = requests.post(
            url,
            json=RUN_INPUT,
            headers={"Authorization": f"Bearer {os.environ['APIFY_TOKEN']}"},
            params={"timeout": 240},    # actor timeout in seconds
            timeout=300,
        )
        response.raise_for_status()
        items = response.json()
        print(f"Extracted {len(items)} items")
        return items                    # saved automatically as XCom

    @task
    def transform(raw):
        """T: keep useful fields, compute word count, shorten text."""
        rows = []
        for item in raw:
            text = (item.get("text") or "").strip()
            rows.append({
                "url": item.get("url"),
                "title": (item.get("metadata") or {}).get("title"),
                "word_count": len(text.split()),
                "preview": text[:200],
                "crawled_at": (item.get("crawl") or {}).get("loadedTime"),
            })
        return rows

    @task
    def quality_check(rows):
        """Data quality checks: task fails (and load is skipped) if data is bad."""
        if not rows:
            raise ValueError("No rows extracted")
        urls = [r["url"] for r in rows]
        if any(not u for u in urls):
            raise ValueError("Row with missing url")
        if len(urls) != len(set(urls)):
            raise ValueError("Duplicate urls found")
        print(f"Quality checks passed for {len(rows)} rows")
        return rows

    @task
    def load(rows):
        """L: upsert into Postgres (re-running never creates duplicates)."""
        hook = PostgresHook(postgres_conn_id="warehouse_db")
        fields = list(rows[0].keys())
        hook.insert_rows(
            table="apify_pages",
            rows=[tuple(r[f] for f in fields) for r in rows],
            target_fields=fields,
            replace=True,
            replace_index="url",
        )
        print(f"Loaded {len(rows)} rows into apify_pages")

    # Trigger rule: runs at the end whether the pipeline succeeded or failed
    @task(trigger_rule=TriggerRule.ALL_DONE)
    def finish():
        print("ETL run finished - check task states in the UI")

    raw = extract()
    create_table >> raw
    loaded = load(quality_check(transform(raw)))
    loaded >> finish()


apify_etl()
