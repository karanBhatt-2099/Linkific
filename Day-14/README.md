# Day 14 – Big Data, PySpark & Data Quality

## Project Structure
```
day14/
├── README.md                  # concepts + how to run
├── requirements.txt
├── spark_setup.py             # PySpark setup + SparkSession
├── generate_data.py           # creates 500k-row orders.csv (with bad rows) + customers.csv
├── pyspark_operations.py      # select, filter, groupBy, join, window, UDF
├── process_large_csv.py       # read -> clean -> aggregate -> save cleaned CSV
├── data/                      # generated CSVs
├── output/                    # cleaned CSVs + DQ reports (JSON)
└── data_quality/
    ├── dq_framework.py            # small reusable DQ framework
    ├── validation_suite.py        # runs checks on raw vs cleaned data
    ├── assert_examples.py         # simple assert-based validation
    └── great_expectations_demo.py # Great Expectations basics
```

## How to Run (from the day14 folder)
```bash
pip install -r requirements.txt     # needs Java 8/11/17/21 installed
python generate_data.py             # 1. create data
python spark_setup.py               # 2. test Spark
python pyspark_operations.py        # 3. PySpark operations
python process_large_csv.py         # 4. process large CSV
python data_quality/validation_suite.py          # 5. DQ framework (raw FAIL, clean PASS)
python data_quality/assert_examples.py           # 6. assert checks
python data_quality/great_expectations_demo.py   # 7. Great Expectations
```

---

## 1. Big Data Concepts (Theory)

### The 3 V's
| V | Meaning | Example |
|---|---------|---------|
| **Volume** | Amount of data (TBs–PBs) | Years of e-commerce transactions |
| **Velocity** | Speed data arrives / must be processed | Clickstream, UPI payments, sensors |
| **Variety** | Different formats | Structured (SQL), semi-structured (JSON), unstructured (images, text) |

### Distributed Storage
Data is split into blocks and stored across many machines, with copies (replication) for fault tolerance.
Examples: **HDFS**, **Amazon S3**, **Azure Data Lake**, **Google Cloud Storage**.
Columnar formats like **Parquet** make reads fast and small.

### Distributed Processing
A big job is split into small tasks that run in parallel on many machines, then results are combined.
- **MapReduce** – older, disk-based, slow.
- **Spark** – newer, in-memory, much faster.
Components: *Driver* (plans the job), *Executors/Workers* (do the work), *Cluster Manager* (allocates machines).

### When Are Big Data Tools Needed?
- Data does not fit in one machine's memory/disk (rule of thumb: > tens of GB).
- Pandas/SQL is too slow or crashes.
- Data arrives continuously (streaming).
- Need to scale out by adding machines.

**Not needed** when data is small (MBs–few GBs) – pandas is simpler and faster.

---

## 2. Apache Spark
**Apache Spark** is an open-source engine for fast, distributed data processing. It supports Python (PySpark), SQL, Scala, Java and has libraries for SQL, streaming and ML.

- **Install:** `pip install pyspark`
- **SparkSession:** the entry point to Spark (`SparkSession.builder.getOrCreate()`).
- **DataFrame:** distributed table with named columns.
- **Lazy evaluation:** transformations (`filter`, `select`) build a plan; *actions* (`show`, `count`, `write`) run it.

## 3. PySpark Operations (see `pyspark_operations.py`)
| Operation | Code |
|-----------|------|
| Select | `df.select("a","b")` |
| Filter | `df.filter(F.col("price") > 500)` |
| GroupBy | `df.groupBy("cat").agg(F.sum("x"))` |
| Join | `df1.join(df2, on="id", how="inner")` |
| Window | `F.rank().over(Window.partitionBy("cat").orderBy(F.desc("rev")))` |
| UDF | `F.udf(my_function, StringType())` (prefer built-in functions; UDFs are slower) |

## 4. Data Quality
### Dimensions
| Dimension | Question | Example check |
|-----------|----------|---------------|
| Completeness | Is data missing? | `price` not null |
| Uniqueness | Any duplicates? | `order_id` unique |
| Validity | Is it in allowed format/range? | `quantity` 1–100, country in list |
| Accuracy | Does it match reality? | Price matches source system |
| Consistency | Same across systems? | Totals match between tables |
| Timeliness | Is it fresh? | Latest order date is today |

### Validation Tools
- **Assert statements** – simplest; stop the program on failure.
- **Custom framework** (`dq_framework.py`) – chainable checks + report (console + JSON).
- **Great Expectations** – industry-standard library; you declare "expectations" and it validates them.

### Validation Report (sample output)
```
=== Data Quality Report: orders_raw (500000 rows) ===
CHECK                 COLUMN          FAILED  STATUS
not_null              order_id             0  PASS
unique                order_id          4925  FAIL
not_null              price             5079  FAIL
range[1,100]          quantity          5009  FAIL
in_set                country           5089  FAIL
Summary: 4/8 checks passed
```
After cleaning (`process_large_csv.py`), the same suite gives **8/8 PASS**.

## Key Learnings
1. Use Spark only when data is too big for one machine.
2. Spark is lazy – nothing runs until an action is called.
3. Prefer built-in Spark functions over UDFs.
4. Always validate data **before** and **after** cleaning.
5. Save big data as Parquet (on Windows, Spark writes need winutils.exe, so we used pandas CSV).
