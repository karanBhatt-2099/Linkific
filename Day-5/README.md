## Folder structure

```
pandas_day_task/
├── pandas_operations.ipynb        # Main notebook (5 cells, one per topic)
├── README.md                      # This file: pandas patterns cheat sheet
├── requirements.txt
├── data/
│   ├── make_data.py               # Creates the messy practice datasets
│   ├── messy_sales.csv            # Project 1 input
│   ├── messy_customers.csv        # Project 2 input
│   ├── messy_employees.csv        # Project 3 input
│   ├── customers_small.csv / orders_small.csv   # Merge examples
│   └── tips.csv                   # Real dataset (restaurant tips, 244 rows)
└── projects/
    ├── project1_clean_sales.py            # Cleaning project 1
    ├── project2_customer_analytics.py     # Cleaning project 2 + customer analytics
    ├── project3_clean_employees.py        # Cleaning project 3
    ├── groupby_examples.py                # Groupby / pivot / crosstab / transform / filter
    ├── project4_time_series.py            # Time series manipulation
    ├── project5_multilevel_aggregation.py # Multi-level aggregations
    └── real_dataset_analysis.py           # Real dataset analysis (tips)
```

## How to run

```bash
pip install -r requirements.txt
cd pandas_day_task

jupyter notebook pandas_operations.ipynb     # open and run all cells

# Scripts (run from the pandas_day_task folder, in this order):
python projects/project1_clean_sales.py      # creates data/clean_sales.csv
python projects/project2_customer_analytics.py
python projects/project3_clean_employees.py
python projects/groupby_examples.py          # needs clean_sales.csv
python projects/project4_time_series.py      # needs clean_sales.csv
python projects/project5_multilevel_aggregation.py
python projects/real_dataset_analysis.py
```

## Deliverables checklist

- [x] Pandas operations notebook: `pandas_operations.ipynb`
- [x] 3 data cleaning projects: projects 1, 2 and 3
- [x] Groupby and aggregation examples: `groupby_examples.py` and notebook cell 4
- [x] Real dataset analysis: `real_dataset_analysis.py`
- [x] README with pandas patterns: below

---

## Pandas patterns cheat sheet

### Create / read / write
```python
df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
pd.read_csv("f.csv");  pd.read_excel("f.xlsx");  pd.read_json("f.json")
pd.read_sql("SELECT * FROM t", conn)
df.to_csv("out.csv", index=False)
```

### Look at data
```python
df.head()   df.tail()   df.info()   df.describe()   df.shape   df.dtypes
df["col"].value_counts()
```

### Select and filter
```python
df["col"]                      # one column
df[["a", "b"]]                 # several columns
df.loc[0:2, ["a", "b"]]        # by label
df.iloc[0]                     # by position
df[df["age"] > 30]             # condition
df[(df["a"] > 1) & (df["b"] == "x")]   # AND  (use | for OR)
df[df["city"].isin(["A", "B"])]
```

### Cleaning
```python
df.isna().sum()                          # count missing
df.dropna(subset=["col"])                # drop rows with missing col
df["col"] = df["col"].fillna(0)          # fill missing
df = df.drop_duplicates()
df["col"] = df["col"].str.strip().str.title()
df["num"] = pd.to_numeric(df["num"], errors="coerce")
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.rename(columns={"old": "new"})
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
df = df.reset_index(drop=True);  df = df.set_index("col")
```
> Tip: assign back (`df["c"] = df["c"].fillna(0)`). Avoid `inplace=True`; it is unreliable in pandas 3.

### Transform
```python
df["new"] = df["a"] * 2
df["new"] = df["a"].apply(lambda x: x + 1)
df["new"] = df["code"].map({"A": 1, "B": 2})
df["col"] = df["col"].replace({"old": "new"})
df.sort_values("col", ascending=False)
df["rank"] = df["col"].rank(ascending=False)
pd.cut(df["age"], bins=[0, 30, 60, 100], labels=["Y", "M", "O"])   # fixed bins
pd.qcut(df["val"], q=4)                                            # equal-size bins
df.pivot(index="id", columns="k", values="v")                      # long -> wide
df.melt(id_vars="id", var_name="k", value_name="v")                # wide -> long
```

### Group and aggregate
```python
df.groupby("a")["b"].mean()
df.groupby("a")["b"].agg(["count", "sum", "mean"])
df.groupby("a").agg(total=("b", "sum"), n=("b", "count"))   # named aggregations
df.groupby(["a", "c"])["b"].sum()                           # multi-level
pd.pivot_table(df, values="b", index="a", columns="c", aggfunc="sum")
pd.crosstab(df["a"], df["c"])
df["avg"] = df.groupby("a")["b"].transform("mean")          # same length as df
df.groupby("a").filter(lambda g: len(g) > 5)                # keep big groups
```

### Merge / join / concat
```python
pd.merge(left, right, on="id", how="inner")   # inner | left | right | outer
left.join(right, how="left")                  # join on index
pd.concat([df1, df2], ignore_index=True)      # stack rows
```

### Time series
```python
df["month"] = df["date"].dt.month
ts = df.set_index("date").sort_index()
ts["value"].resample("ME").sum()              # monthly totals
ts["value"].rolling(3).mean()                 # moving average
ts["value"].pct_change()                      # growth rate
```

