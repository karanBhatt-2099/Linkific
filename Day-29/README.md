# Orders ETL: Snowflake + Airflow (Docker)

Small end-to-end ETL pipeline with documentation, tests, optimisation notes and presentation materials.

**Quick start** (details in `docs/user_guide.md`)
```bash
cp .env.example .env            # add Snowflake credentials
pip install -r requirements.txt
python scripts/setup_snowflake.py
python scripts/generate_sample_data.py
docker compose up --build -d    # Airflow at http://localhost:8080, trigger DAG `orders_etl`
python -m pytest                # tests
```

| Folder | Contents |
|---|---|
| `dags/` | Airflow DAG `orders_etl` |
| `etl/` | extract, transform, quality, load, pipeline modules |
| `sql/` | DDL, MERGE, incremental mart |
| `scripts/` | setup, sample data, CLI runner, benchmarks |
| `tests/` | unit, edge-case, data-quality, performance, e2e |
| `dashboard/` | Streamlit dashboard |
| `docs/` | architecture, data dictionary, ETL docs, user guide, optimisation, test results |
| `presentation/` | demo script, slides (Marp markdown), data-flow walkthrough |

**Status:** all tests that can run without Snowflake/Airflow pass (35). The Snowflake end-to-end test, DAG import test and Docker run have not been executed yet; see `docs/test_results.md`.
