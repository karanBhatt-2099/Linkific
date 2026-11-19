"""Streamlit dashboard over MART.DAILY_SALES.

Load-time design: queries hit the small pre-aggregated mart (not CORE), results are cached
for 5 minutes in Streamlit, and Snowflake's own result cache serves repeats for free.
"""
import pandas as pd
import streamlit as st

from etl.snowflake_client import get_connection

st.set_page_config(page_title="Orders Dashboard", layout="wide")
st.title("Orders Dashboard")


@st.cache_data(ttl=300, show_spinner="Loading from Snowflake...")
def load_mart() -> pd.DataFrame:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT ORDER_DATE, COUNTRY, CATEGORY, ORDERS, UNITS, GROSS_AMOUNT, "
                    "NET_REVENUE, CANCELLED_ORDERS FROM MART.DAILY_SALES")
        df = cur.fetch_pandas_all()
    df.columns = [c.lower() for c in df.columns]
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df


df = load_mart()
countries = st.sidebar.multiselect("Country", sorted(df["country"].unique()), default=None)
categories = st.sidebar.multiselect("Category", sorted(df["category"].unique()), default=None)
if countries:
    df = df[df["country"].isin(countries)]
if categories:
    df = df[df["category"].isin(categories)]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Net revenue", f"{df['net_revenue'].sum():,.0f}")
c2.metric("Orders", f"{int(df['orders'].sum()):,}")
c3.metric("Units", f"{int(df['units'].sum()):,}")
cancel = df["cancelled_orders"].sum() / max(df["orders"].sum(), 1)
c4.metric("Cancel rate", f"{cancel:.1%}")

st.subheader("Net revenue by day")
st.line_chart(df.groupby("order_date")["net_revenue"].sum())
left, right = st.columns(2)
left.subheader("By category")
left.bar_chart(df.groupby("category")["net_revenue"].sum())
right.subheader("By country")
right.bar_chart(df.groupby("country")["net_revenue"].sum())
