# Dashboard Pages & Visuals

Preview images are in `powerbi/images/`.

## Page 1: Overview — `images/page1_overview.png`
| Visual | Fields |
|---|---|
| 5 Cards | Total Revenue, Total Profit, Profit Margin %, Total Orders, Avg Order Value |
| Line chart | Axis: dim_date[month]; Legend: dim_date[year]; Values: Total Revenue |
| Bar chart | Axis: dim_product[category]; Values: Total Revenue |
| Column chart | Axis: dim_customer[region]; Values: Total Revenue |
| 3 Slicers | Year, Region, Segment |

## Page 2: Sales Trends — `images/page2_sales_trends.png`
| Visual | Fields |
|---|---|
| Column chart | Axis: Year-Month; Values: Total Revenue |
| Area chart | Axis: Year-Month; Values: Revenue YTD |
| Column chart | Axis: Year-Month; Values: MoM Growth % |
| Clustered column | Axis: quarter; Legend: year; Values: Total Revenue |

## Page 3: Products — `images/page3_products.png`
| Visual | Fields |
|---|---|
| Bar chart (Top N = 10) | Axis: product_name; Values: Total Revenue |
| Column chart | Axis: category; Values: Profit Margin % |
| Line chart | Axis: discount; Values: Profit Margin % |

## Page 4: Customers — `images/page4_customers.png`
| Visual | Fields |
|---|---|
| Donut / Pie | Legend: segment; Values: Total Revenue |
| Bar chart (Top N = 10) | Axis: customer_name; Values: Total Revenue |
| Matrix (heatmap colors) | Rows: segment; Columns: region; Values: Total Revenue |
| Histogram-style column | Customer spend buckets |

## Page 5 (hidden): Drill-through — Product Detail
See below.
