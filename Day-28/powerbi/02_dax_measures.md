# DAX Measures

Create a blank table called `_Measures` (Home → Enter data) and keep all measures there.

## Core measures
```dax
Total Revenue = SUM(fact_sales[revenue])

Total Cost = SUM(fact_sales[cost])

Total Profit = [Total Revenue] - [Total Cost]

Profit Margin % = DIVIDE([Total Profit], [Total Revenue])

Total Orders = COUNTROWS(fact_sales)

Units Sold = SUM(fact_sales[quantity])

Avg Order Value = DIVIDE([Total Revenue], [Total Orders])

Active Customers = DISTINCTCOUNT(fact_sales[customer_key])
```

## Time intelligence
```dax
Revenue LY = CALCULATE([Total Revenue], SAMEPERIODLASTYEAR(dim_date[full_date]))

YoY Growth % = DIVIDE([Total Revenue] - [Revenue LY], [Revenue LY])

Revenue MTD = TOTALMTD([Total Revenue], dim_date[full_date])

Revenue YTD = TOTALYTD([Total Revenue], dim_date[full_date])

Revenue Prev Month = CALCULATE([Total Revenue], PREVIOUSMONTH(dim_date[full_date]))

MoM Growth % = DIVIDE([Total Revenue] - [Revenue Prev Month], [Revenue Prev Month])
```

## Ranking and share
```dax
Revenue % of Total =
DIVIDE([Total Revenue], CALCULATE([Total Revenue], ALL(dim_product)))

Product Rank = RANKX(ALL(dim_product[product_name]), [Total Revenue])
```

## Helper measures
```dax
Discounted Orders = CALCULATE([Total Orders], fact_sales[discount] > 0)

Weekend Revenue = CALCULATE([Total Revenue], dim_date[is_weekend] = 1)

Margin Color =
IF([Profit Margin %] >= 0.30, "#12B5A5", "#E66C37")   -- use in conditional formatting
```

## Test each measure
Drop it in a Card visual and compare with the SQL result.
Total Revenue should be **15,994,288.45** (same as `sql/01_business_metrics.sql`).
