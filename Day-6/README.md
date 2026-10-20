# Advanced Pandas Guide - Practice Project

Learn to **combine DataFrames, analyse time series, automate Excel and speed up pandas**
using one small sales dataset (customers, products, orders).

## Project structure

```
pandas_advanced_project/
├── data/
│   ├── sales_data.xlsx        <- YOUR Excel input (3 sheets: Customers, Products, Orders)
│   ├── customers.csv, products.csv, orders.csv
│   └── big_file.csv           (500,000 rows, for chunk processing)
├── scripts/
│   ├── 00_generate_data.py            create the sample data
│   ├── 01_merge_examples.py           merge / join / concat
│   ├── 03_excel_automation.py         read Excel -> formatted Excel report
│   ├── 04_performance_optimization.py dtypes, vectorization, query
│   └── 05_process_large_csv.py        chunk processing
├── notebooks/
│   └── 02_time_series_analysis.ipynb  time series (run cell by cell)
├── output/                    <- generated files appear here
├── run_all.py                 run every script in order
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt        # pandas numpy openpyxl xlsxwriter matplotlib jupyter
python run_all.py                      # runs all scripts
jupyter notebook notebooks/02_time_series_analysis.ipynb
```
Always run scripts **from the project root folder** (the paths are relative).

## Connect your own Excel file

1. Put your file in `data/` (or overwrite `data/sales_data.xlsx`).
2. Keep the sheet names `Customers`, `Products`, `Orders` and the same column names
   - or change the names at the top of `scripts/03_excel_automation.py`.
3. Run `python scripts/03_excel_automation.py` - the report is created in `output/sales_report.xlsx`.

---

## 1. Combining DataFrames

| Join | Keeps | Code |
|------|-------|------|
| inner | only keys found in **both** | `a.merge(b, on="id", how="inner")` |
| left  | all rows of the left table | `how="left"` |
| right | all rows of the right table | `how="right"` |
| outer | all rows of both | `how="outer"` |

```python
orders.merge(customers, on="customer_id", how="left")            # one key
orders.merge(cust, left_on="customer_id", right_on="cust_id")     # different key names
monthly.merge(targets, on=["region", "month"])                    # multi-key
a.merge(b, on="id", suffixes=("_old", "_new"))                    # same column names
a.merge(b, on="id", indicator=True)                               # where did each row come from?
a.merge(b, on="id", validate="one_to_one")                        # catch duplicate keys
orders.join(customers.set_index("customer_id"), on="customer_id") # join on index
pd.concat([df1, df2], ignore_index=True)                          # stack rows
pd.concat([df1, df2], axis=1)                                     # side by side
```

**Tip:** after a merge always check `len()` - unexpected extra rows usually mean duplicate keys.

## 2. Time series

```python
df["date"] = pd.to_datetime(df["date"])
s = df.set_index("date")["revenue"]          # DatetimeIndex
s["2024-03"]                                  # select a month
s.resample("W").sum()                         # D, W, ME (month end), YE (year end)
s.rolling(7).mean()                           # 7-day moving average
s.shift(1)                                    # previous row (lag)
s.pct_change()                                # growth %
pd.date_range("2025-01-01", periods=5, freq="D")
s.index.tz_localize("Asia/Kolkata").tz_convert("UTC")   # time zones
```

## 3. Excel automation

```python
pd.read_excel("file.xlsx", sheet_name=None)                 # all sheets -> dict
pd.read_excel("file.xlsx", sheet_name="Orders")             # one sheet

with pd.ExcelWriter("report.xlsx", engine="xlsxwriter") as writer:
    df1.to_excel(writer, sheet_name="Sheet A", index=False)
    df2.to_excel(writer, sheet_name="Sheet B", index=False)
    ws = writer.sheets["Sheet A"]
    ws.set_column(0, 0, 20)                  # column width
    ws.freeze_panes(1, 0)                    # freeze header
    ws.autofilter(0, 0, len(df1), 2)         # filter buttons
```
- `openpyxl` - read and edit existing `.xlsx` files
- `xlsxwriter` - create new, nicely formatted files (formats, charts, conditional formatting)

## 4. Performance

| Technique | Example | Result in this project |
|-----------|---------|-----------------------|
| Smaller dtypes | `astype("int8")`, `astype("float32")` | |
| Category for text | `df["city"].astype("category")` | 67 MB -> 6 MB |
| Vectorize | `df["a"] * df["b"]` instead of `apply(axis=1)` | ~800x faster |
| `np.where` | instead of `apply` for if/else | |
| Chunks | `pd.read_csv(f, chunksize=100_000)` | big files without memory errors |
| `query()` | `df.query("qty > 50 and city == 'Mumbai'")` | cleaner, similar speed |

**Rule of thumb:** avoid loops and `apply(axis=1)` whenever a vectorized expression exists.

## Practice ideas

1. Add a 4th table (e.g. `returns.csv`) and merge it into the full dataset.
2. Find the best-selling product per month using `resample` + `groupby`.
3. Add a new sheet to the Excel report with the 7-day rolling average.
4. Run script 05 on your own large CSV.

## Deliverables checklist

- [x] Multi-table merge examples - `scripts/01_merge_examples.py`
- [x] Time series analysis notebook - `notebooks/02_time_series_analysis.ipynb`
- [x] Excel automation script - `scripts/03_excel_automation.py` -> `output/sales_report.xlsx`
- [x] Performance optimization examples - `scripts/04_...py`, `scripts/05_...py`
- [x] README with advanced pandas guide - this file
