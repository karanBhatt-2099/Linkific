"""Local files: CSV, JSON, Excel."""
import json

import pandas as pd

from src.config import FILES_DIR
from src.formats import json_to_df
from src.utils import save_raw


def csv_customers():
    save_raw(pd.read_csv(f"{FILES_DIR}/crm_customers.csv"), "csv_customers", "csv_file")


def file_orders():
    with open(f"{FILES_DIR}/orders.json") as f:
        save_raw(json_to_df(json.load(f)), "file_orders", "json_file")


def file_targets():
    save_raw(pd.read_excel(f"{FILES_DIR}/targets.xlsx"), "file_targets", "excel_file")
