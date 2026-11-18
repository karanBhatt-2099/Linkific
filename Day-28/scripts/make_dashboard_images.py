"""Renders preview images of the 4 Power BI dashboard pages from warehouse.db"""
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

con = sqlite3.connect("data/warehouse.db")
BLUE, GREEN, ORANGE, GREY, BG = "#118DFF", "#12B5A5", "#E66C37", "#6B7280", "#F3F4F6"

def q(sql):
    return pd.read_sql(sql, con)

def new_page(title):
    fig = plt.figure(figsize=(16, 9), facecolor=BG)
    fig.text(0.03, 0.94, title, fontsize=22, fontweight="bold", color="#1F2937")
    fig.text(0.97, 0.94, "Overview | Trends | Products | Customers", fontsize=10, color=GREY, ha="right")
    return fig

def card(fig, x, label, value, color=BLUE):
    ax = fig.add_axes([x, 0.78, 0.14, 0.11]); ax.set_facecolor("white")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_color("#E5E7EB")
    ax.text(0.5, 0.62, value, ha="center", fontsize=20, fontweight="bold", color=color)
    ax.text(0.5, 0.22, label, ha="center", fontsize=10, color=GREY)

def panel(fig, rect, title):
    ax = fig.add_axes(rect); ax.set_facecolor("white")
    ax.set_title(title, loc="left", fontsize=11, fontweight="bold", color="#1F2937")
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    return ax

# ---------- data ----------
kpi = q("""SELECT SUM(revenue) r, SUM(revenue-cost) p, COUNT(*) o, AVG(revenue) a, COUNT(DISTINCT customer_key) c
           FROM fact_sales""").iloc[0]
monthly = q("""SELECT d.year, d.month, SUM(f.revenue) revenue, SUM(f.revenue-f.cost) profit
               FROM fact_sales f JOIN dim_date d ON f.date_key=d.date_key GROUP BY d.year, d.month""")
cat = q("""SELECT p.category, SUM(f.revenue) revenue, SUM(f.revenue-f.cost)*100.0/SUM(f.revenue) margin
           FROM fact_sales f JOIN dim_product p ON f.product_key=p.product_key
           GROUP BY p.category ORDER BY revenue""")
region = q("""SELECT c.region, SUM(f.revenue) revenue FROM fact_sales f
              JOIN dim_customer c ON f.customer_key=c.customer_key GROUP BY c.region ORDER BY revenue DESC""")
seg = q("""SELECT c.segment, SUM(f.revenue) revenue FROM fact_sales f
           JOIN dim_customer c ON f.customer_key=c.customer_key GROUP BY c.segment""")

# ---------- Page 1: Overview ----------
fig = new_page("Sales Overview")
card(fig, 0.03, "Total Revenue", f"${kpi.r/1e6:.2f}M")
card(fig, 0.20, "Total Profit", f"${kpi.p/1e6:.2f}M", GREEN)
card(fig, 0.37, "Profit Margin", f"{kpi.p/kpi.r*100:.1f}%", GREEN)
card(fig, 0.54, "Orders", f"{int(kpi.o):,}", ORANGE)
card(fig, 0.71, "Avg Order Value", f"${kpi.a:,.0f}")
fig.text(0.88, 0.84, "Slicers:\n[Year ▾]\n[Region ▾]\n[Segment ▾]", fontsize=10, color=GREY, va="center")

ax = panel(fig, [0.05, 0.08, 0.42, 0.60], "Monthly Revenue (2023 vs 2024)")
for yr, col in [(2023, GREY), (2024, BLUE)]:
    m = monthly[monthly.year == yr]
    ax.plot(m.month, m.revenue / 1e3, marker="o", color=col, label=str(yr))
ax.set_xticks(range(1, 13)); ax.set_ylabel("Revenue ($K)"); ax.legend(frameon=False)

ax = panel(fig, [0.55, 0.08, 0.18, 0.60], "Revenue by Category")
ax.barh(cat.category, cat.revenue / 1e6, color=BLUE); ax.set_xlabel("$M")

ax = panel(fig, [0.80, 0.08, 0.17, 0.60], "Revenue by Region")
ax.bar(region.region, region.revenue / 1e6, color=GREEN); ax.set_ylabel("$M")
fig.savefig("powerbi/images/page1_overview.png", dpi=110); plt.close(fig)

# ---------- Page 2: Sales Trends ----------
fig = new_page("Sales Trends")
m = monthly.sort_values(["year", "month"]).reset_index(drop=True)
m["mom"] = m.revenue.pct_change() * 100
m["cum"] = m.revenue.cumsum()
m["label"] = m.year.astype(str).str[2:] + "-" + m.month.astype(str).str.zfill(2)

ax = panel(fig, [0.05, 0.55, 0.43, 0.32], "Monthly Revenue")
ax.bar(m.label, m.revenue / 1e3, color=[GREY if y == 2023 else BLUE for y in m.year])
ax.tick_params(axis="x", rotation=90, labelsize=7); ax.set_ylabel("$K")

ax = panel(fig, [0.55, 0.55, 0.42, 0.32], "Cumulative Revenue")
ax.fill_between(m.label, m.cum / 1e6, color=BLUE, alpha=0.3); ax.plot(m.label, m.cum / 1e6, color=BLUE)
ax.tick_params(axis="x", rotation=90, labelsize=7); ax.set_ylabel("$M")

ax = panel(fig, [0.05, 0.08, 0.43, 0.35], "Month-over-Month Growth %")
ax.bar(m.label, m.mom, color=[GREEN if v >= 0 else ORANGE for v in m.mom.fillna(0)])
ax.axhline(0, color="black", lw=0.5); ax.tick_params(axis="x", rotation=90, labelsize=7)

qtr = q("""SELECT d.quarter, d.year, SUM(f.revenue) revenue FROM fact_sales f
           JOIN dim_date d ON f.date_key=d.date_key GROUP BY d.quarter, d.year""")
ax = panel(fig, [0.55, 0.08, 0.42, 0.35], "Quarterly Revenue: YoY")
for i, (yr, col) in enumerate([(2023, GREY), (2024, BLUE)]):
    s = qtr[qtr.year == yr]
    ax.bar(s.quarter + (i - 0.5) * 0.35, s.revenue / 1e6, width=0.35, color=col, label=str(yr))
ax.set_xticks([1, 2, 3, 4]); ax.set_xticklabels(["Q1", "Q2", "Q3", "Q4"]); ax.legend(frameon=False)
fig.savefig("powerbi/images/page2_sales_trends.png", dpi=110); plt.close(fig)

# ---------- Page 3: Products ----------
fig = new_page("Product Performance")
top = q("""SELECT p.product_name, SUM(f.revenue) revenue FROM fact_sales f
           JOIN dim_product p ON f.product_key=p.product_key GROUP BY p.product_name
           ORDER BY revenue DESC LIMIT 10""").iloc[::-1]
ax = panel(fig, [0.15, 0.08, 0.32, 0.78], "Top 10 Products by Revenue")
ax.barh(top.product_name, top.revenue / 1e3, color=BLUE); ax.set_xlabel("$K")

ax = panel(fig, [0.55, 0.50, 0.42, 0.36], "Profit Margin % by Category")
ax.bar(cat.category, cat.margin, color=GREEN); ax.set_ylim(0, 40)
for i, v in enumerate(cat.margin): ax.text(i, v + 0.8, f"{v:.1f}%", ha="center", fontsize=9)

disc = q("""SELECT discount*100 d, SUM(revenue-cost)*100.0/SUM(revenue) margin FROM fact_sales GROUP BY discount""")
ax = panel(fig, [0.55, 0.08, 0.42, 0.30], "Margin % by Discount Level")
ax.plot(disc.d.astype(int).astype(str) + "%", disc.margin, marker="o", color=ORANGE); ax.set_ylabel("Margin %")
fig.savefig("powerbi/images/page3_products.png", dpi=110); plt.close(fig)

# ---------- Page 4: Customers ----------
fig = new_page("Customer Insights")
ax = panel(fig, [0.05, 0.50, 0.28, 0.36], "Revenue by Segment")
ax.pie(seg.revenue, labels=seg.segment, autopct="%1.0f%%", colors=[BLUE, GREEN, ORANGE], startangle=90)

topc = q("""SELECT c.customer_name, SUM(f.revenue) revenue FROM fact_sales f
            JOIN dim_customer c ON f.customer_key=c.customer_key GROUP BY c.customer_name
            ORDER BY revenue DESC LIMIT 10""").iloc[::-1]
ax = panel(fig, [0.42, 0.10, 0.20, 0.76], "Top 10 Customers")
ax.barh(topc.customer_name, topc.revenue / 1e3, color=BLUE); ax.set_xlabel("$K")

heat = q("""SELECT c.segment, c.region, SUM(f.revenue)/1e6 revenue FROM fact_sales f
            JOIN dim_customer c ON f.customer_key=c.customer_key GROUP BY c.segment, c.region""")
pv = heat.pivot(index="segment", columns="region", values="revenue")
ax = panel(fig, [0.70, 0.50, 0.27, 0.36], "Segment x Region ($M)")
im = ax.imshow(pv.values, cmap="Blues")
ax.set_xticks(range(len(pv.columns))); ax.set_xticklabels(pv.columns)
ax.set_yticks(range(len(pv.index))); ax.set_yticklabels(pv.index)
for i in range(pv.shape[0]):
    for j in range(pv.shape[1]): ax.text(j, i, f"{pv.values[i, j]:.2f}", ha="center", va="center", fontsize=9)

spend = q("SELECT customer_key, SUM(revenue) s FROM fact_sales GROUP BY customer_key")
ax = panel(fig, [0.05, 0.08, 0.28, 0.30], "Customer Spend Distribution")
ax.hist(spend.s / 1e3, bins=25, color=GREEN); ax.set_xlabel("Total spend ($K)"); ax.set_ylabel("Customers")
fig.savefig("powerbi/images/page4_customers.png", dpi=110); plt.close(fig)
print("Images saved")
