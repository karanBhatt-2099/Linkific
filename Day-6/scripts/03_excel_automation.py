"""Step 3: Excel automation - read Excel, process, write a formatted report.

INPUT : data/sales_data.xlsx   (replace with your own Excel if you like)
OUTPUT: output/sales_report.xlsx
"""
import pandas as pd

INPUT_FILE = "data/sales_data.xlsx"
OUTPUT_FILE = "output/sales_report.xlsx"


# 1. READ Excel (all sheets at once -> dict of DataFrames)
sheets = pd.read_excel(INPUT_FILE, sheet_name=None)
print("Sheets found:", list(sheets.keys()))

customers = sheets["Customers"]
products = sheets["Products"]
orders = sheets["Orders"]

# Reading just one sheet also works:
# orders = pd.read_excel(INPUT_FILE, sheet_name="Orders")


# 2. PROCESS: merge + summaries
df = (
    orders
    .merge(customers, on="customer_id")
    .merge(products, on="product_id")
)
df["revenue"] = df["quantity"] * df["price"]
df["month"] = df["order_date"].dt.to_period("M").astype(str)

by_region = df.groupby("region", as_index=False)["revenue"].sum()
by_category = df.groupby("category", as_index=False)["revenue"].sum()
by_month = df.groupby("month", as_index=False)["revenue"].sum()
top_customers = (
    df.groupby("customer_name", as_index=False)["revenue"].sum()
    .sort_values("revenue", ascending=False).head(10)
)

# 3. WRITE multiple sheets with ExcelWriter + format them
with pd.ExcelWriter(OUTPUT_FILE, engine="xlsxwriter",
                    datetime_format="yyyy-mm-dd") as writer:
    workbook = writer.book

    # Formats (reuse them everywhere)
    header = workbook.add_format({"bold": True, "font_name": "Arial", "bg_color": "#1F4E78",
                                  "font_color": "white", "border": 1, "align": "center"})
    money = workbook.add_format({"font_name": "Arial", "num_format": "#,##0"})
    text = workbook.add_format({"font_name": "Arial"})
    bold_money = workbook.add_format({"font_name": "Arial", "bold": True, "num_format": "#,##0",
                                      "top": 1})
    bold = workbook.add_format({"font_name": "Arial", "bold": True, "top": 1})

    def write_sheet(data, name, money_cols=()):
        """Write one DataFrame as a nicely formatted sheet."""
        data.to_excel(writer, sheet_name=name, index=False)
        ws = writer.sheets[name]
        for col_num, col_name in enumerate(data.columns):
            ws.write(0, col_num, col_name, header)                  # styled header
            width = max(len(str(col_name)), data[col_name].astype(str).str.len().max()) + 3
            fmt = money if col_name in money_cols else text
            ws.set_column(col_num, col_num, width, fmt)             # column width + format
        ws.freeze_panes(1, 0)                                       # freeze header row
        ws.autofilter(0, 0, len(data), len(data.columns) - 1)       # filter buttons
        return ws

    # --- Summary sheets ---
    ws = write_sheet(by_region, "By Region", money_cols=["revenue"])
    n = len(by_region)
    ws.write(n + 1, 0, "TOTAL", bold)
    ws.write_formula(n + 1, 1, f"=SUM(B2:B{n + 1})", bold_money, by_region["revenue"].sum())

    # Bar chart on the region sheet
    chart = workbook.add_chart({"type": "column"})
    chart.add_series({"name": "Revenue",
                      "categories": ["By Region", 1, 0, n, 0],
                      "values": ["By Region", 1, 1, n, 1]})
    chart.set_title({"name": "Revenue by Region"})
    chart.set_legend({"none": True})
    ws.insert_chart("D2", chart)

    write_sheet(by_category, "By Category", money_cols=["revenue"])

    ws = write_sheet(by_month, "By Month", money_cols=["revenue"])
    # Conditional formatting: colour scale on revenue
    ws.conditional_format(1, 1, len(by_month), 1, {"type": "3_color_scale"})

    write_sheet(top_customers, "Top 10 Customers", money_cols=["revenue"])

    # --- Raw data sheet ---
    write_sheet(df, "Full Data", money_cols=["revenue", "price"])

print("Report created ->", OUTPUT_FILE)
