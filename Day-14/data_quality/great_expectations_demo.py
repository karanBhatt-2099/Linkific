"""Great Expectations basics (v1.x).  pip install great_expectations pandas
Run from the project root:  python data_quality/great_expectations_demo.py"""
import pandas as pd
import great_expectations as gx

df = pd.read_csv("data/orders.csv")

# 1. Create context and connect the DataFrame
context = gx.get_context()
source = context.data_sources.add_pandas("my_pandas")
asset = source.add_dataframe_asset("orders")
batch_def = asset.add_batch_definition_whole_dataframe("whole")
batch = batch_def.get_batch(batch_parameters={"dataframe": df})

# 2. Define expectations
expectations = [
    gx.expectations.ExpectColumnValuesToNotBeNull(column="order_id"),
    gx.expectations.ExpectColumnValuesToBeUnique(column="order_id"),
    gx.expectations.ExpectColumnValuesToNotBeNull(column="price"),
    gx.expectations.ExpectColumnValuesToBeBetween(column="quantity", min_value=1, max_value=100),
    gx.expectations.ExpectColumnValuesToBeInSet(column="country", value_set=["India", "USA", "UK", "Germany"]),
]

# 3. Validate and print results
for exp in expectations:
    result = batch.validate(exp)
    print("PASS" if result.success else "FAIL", "-", exp.__class__.__name__, "on", exp.column)
