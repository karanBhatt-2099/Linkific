"""Format handling: JSON, XML, Parquet, Avro, CSV + conversions.
Run the demo:  python -m src.formats
"""
import json
import os
import xml.etree.ElementTree as ET

import fastavro
import pandas as pd

from src.config import CONVERTED_DIR, FILES_DIR, SFTP_LOCAL_DIR
from src.utils import log


# ---------- readers ----------
def json_to_df(data):
    """list/dict of (possibly nested) JSON -> flat DataFrame."""
    return pd.json_normalize(data)


def xml_to_df(path):
    """<root><row><col>v</col></row>...</root> -> DataFrame."""
    root = ET.parse(path).getroot()
    return pd.DataFrame([{child.tag: child.text for child in row} for row in root])


def parquet_to_df(path):
    return pd.read_parquet(path)


def avro_to_df(path):
    with open(path, "rb") as f:
        return pd.DataFrame(list(fastavro.reader(f)))


# ---------- writers ----------
def df_to_avro(df, path, name="record"):
    df = df.copy()
    avro_types = {"int64": "long", "float64": "double", "bool": "boolean"}
    fields = []
    for col in df.columns:
        if df[col].dtype.name not in avro_types:  # dates, objects -> string
            df[col] = df[col].map(lambda v: None if pd.isna(v) else str(v))
        fields.append({"name": col, "type": ["null", avro_types.get(df[col].dtype.name, "string")]})
    schema = fastavro.parse_schema({"type": "record", "name": name, "fields": fields})
    records = df.astype(object).where(df.notna(), None).to_dict("records")
    with open(path, "wb") as f:
        fastavro.writer(f, schema, records)


def convert_all(df, name, out_dir=CONVERTED_DIR):
    """Write the same DataFrame as csv, json, parquet and avro."""
    os.makedirs(out_dir, exist_ok=True)
    df.to_csv(f"{out_dir}/{name}.csv", index=False)
    df.to_json(f"{out_dir}/{name}.json", orient="records", indent=2, date_format="iso")
    df.to_parquet(f"{out_dir}/{name}.parquet", index=False)
    df_to_avro(df, f"{out_dir}/{name}.avro", name)
    log.info("Converted '%s' -> csv, json, parquet, avro in %s", name, out_dir)


# ---------- demo ----------
if __name__ == "__main__":
    with open(f"{FILES_DIR}/orders.json") as f:
        orders = json_to_df(json.load(f))
    print("JSON -> DataFrame:\n", orders, "\n")

    customers = xml_to_df(f"{SFTP_LOCAL_DIR}/customers.xml")
    print("XML -> DataFrame:\n", customers, "\n")

    convert_all(orders, "demo_orders")
    convert_all(customers, "demo_customers")

    print("Parquet -> DataFrame:\n", parquet_to_df(f"{CONVERTED_DIR}/demo_orders.parquet"), "\n")
    print("Avro -> DataFrame:\n", avro_to_df(f"{CONVERTED_DIR}/demo_customers.avro"))
