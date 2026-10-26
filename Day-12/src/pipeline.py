"""Each ETL step as its own function, so main.py and the Airflow DAG share the same code.
Steps hand data to each other through the staging area (Parquet files)."""
from src.extract import api_extractor, db_extractor, file_extractor
from src.load import snowflake_loader as sf
from src.staging import read_stage, stage
from src.transform import transformations as T
from src.utils.logger import get_logger
from src.utils.state import get_watermark, reset_watermark, set_watermark

log = get_logger("pipeline")


# ---------- EXTRACT -> staging ----------
def extract_customers() -> None:
    stage(db_extractor.extract_customers(), "customers")


def extract_orders(full_refresh: bool = False) -> None:
    if full_refresh:
        reset_watermark()
        log.info("Full refresh requested: watermark reset")
    stage(db_extractor.extract_orders(get_watermark()), "orders")


def extract_order_items() -> None:
    stage(file_extractor.extract_order_items(), "order_items")


def extract_products() -> None:
    stage(api_extractor.extract_products(), "products")


# ---------- TRANSFORM (staging -> staging) ----------
def transform() -> None:
    customers = T.clean_customers(read_stage("customers"))
    orders = T.clean_orders(read_stage("orders"))
    items = T.clean_order_items(read_stage("order_items"))
    products = T.clean_products(read_stage("products"))
    fact = T.build_fact_sales(orders, items, customers, products)
    log.info("Fact rows built: %d", len(fact))

    stage(customers, "t_customers")
    stage(products, "t_products")
    stage(fact, "t_fact_sales")


# ---------- LOAD (staging -> Snowflake) ----------
def load() -> None:
    customers = read_stage("t_customers")
    products = read_stage("t_products")
    fact = read_stage("t_fact_sales")
    raw_orders = read_stage("orders")

    conn = sf.get_connection()
    try:
        sf.setup_objects(conn)
        sf.truncate_and_load(conn, products, "DIM_PRODUCTS")                 # full refresh
        sf.upsert(conn, customers, "DIM_CUSTOMERS", ["customer_id"])        # upsert
        sf.upsert(conn, fact, "FACT_SALES", ["order_item_id"])              # incremental upsert
        sf.refresh_daily_aggregate(conn)
    finally:
        conn.close()

    # Move the watermark only after everything loaded successfully
    if not raw_orders.empty:
        set_watermark(raw_orders["updated_at"].max())
        log.info("Watermark moved to %s", get_watermark())
    log.info("Load finished successfully")


def run_all(full_refresh: bool = False) -> None:
    """Run the whole pipeline in one process (used by `python main.py`)."""
    log.info("=== EXTRACT ===")
    extract_customers()
    extract_orders(full_refresh)
    extract_order_items()
    extract_products()
    log.info("=== TRANSFORM ===")
    transform()
    log.info("=== LOAD ===")
    load()
