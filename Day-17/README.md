# Power BI: Advanced DAX Sales Dashboard

A Power BI project that practises DAX fundamentals, measures, time intelligence and an interactive sales dashboard.

## Contents

1. [Overview](#1-overview)
2. [Project files](#2-project-files)
3. [Data model](#3-data-model)
4. [Setup steps](#4-setup-steps)
5. [DAX library](#5-dax-library)
6. [Dashboard pages](#6-dashboard-pages)
7. [Advanced features](#7-advanced-features)
8. [Key insights](#8-key-insights)
9. [Troubleshooting](#9-troubleshooting)
10. [Status and next steps](#10-status-and-next-steps)

---

## 1. Overview

**Goal:** master DAX, create measures, build a dashboard and add drill-through.

**Dataset:** synthetic sales data from 2023 to 2025 with 3,500 orders, 20 products (5 categories), 60 customers (4 regions) and a date table.

**Tools:** Power BI Desktop (free), CSV files.

## 2. Project files

| File | Rows | Columns |
|---|---|---|
| `Sales.csv` (fact) | 3,500 | OrderID, OrderDate, CustomerID, ProductID, Quantity, UnitPrice, UnitCost, Discount |
| `Products.csv` | 20 | ProductID, ProductName, Category, UnitPrice, UnitCost |
| `Customers.csv` | 60 | CustomerID, CustomerName, Segment, Region, City |
| `Calendar.csv` | 1,096 | Date, Year, Quarter, MonthNumber, MonthName, YearMonth, WeekdayName |

## 3. Data model

Star schema with `Sales` as the fact table. All relationships are Many-to-One with single-direction filtering.

```
Calendar (1) ──< (*) Sales (*) >── (1) Products
                       │
                       (*)
                       │
                  (1) Customers
```

| From (many) | To (one) |
|---|---|
| `Sales[OrderDate]` | `Calendar[Date]` |
| `Sales[ProductID]` | `Products[ProductID]` |
| `Sales[CustomerID]` | `Customers[CustomerID]` |

## 4. Setup steps

1. Open Power BI Desktop and start a blank report.
2. **Home → Get Data → Text/CSV**, then load all four files.
3. In **Transform data**, set `Sales[OrderDate]` and `Calendar[Date]` to type **Date**, then **Close & Apply**.
4. In **Model view**, create the three relationships above.
5. Select `Calendar` → **Table tools → Mark as date table** → choose `Date`.
6. Select `Calendar[MonthName]` → **Column tools → Sort by column → MonthNumber**.
7. Create a **Measures** table (Home → Enter data, empty table) and add the DAX below with **Home → New measure**.
8. Format measures: `Profit Margin %`, `YoY Growth %` and `Revenue % of Category` as **Percentage**; the revenue and profit measures as **Currency** or **Whole number**.

## 5. DAX library

All measures live in the `Measures` table. Paste them in this order, since later ones refer to earlier ones.

### 5.1 Basic measures

```DAX
Total Revenue =
SUMX ( Sales, Sales[Quantity] * Sales[UnitPrice] * ( 1 - Sales[Discount] ) )

Total Cost =
SUMX ( Sales, Sales[Quantity] * Sales[UnitCost] )

Total Profit = [Total Revenue] - [Total Cost]

Profit Margin % = DIVIDE ( [Total Profit], [Total Revenue] )

Total Orders = DISTINCTCOUNT ( Sales[OrderID] )
```

### 5.2 Iterators: SUMX and AVERAGEX

```DAX
Avg Revenue per Customer =
AVERAGEX ( VALUES ( Customers[CustomerID] ), [Total Revenue] )
```

### 5.3 CALCULATE, FILTER, ALLEXCEPT

```DAX
Large Order Revenue =
CALCULATE (
    [Total Revenue],
    FILTER (
        Sales,
        Sales[Quantity] * Sales[UnitPrice] * ( 1 - Sales[Discount] ) > 50000
    )
)

Revenue % of Category =
DIVIDE (
    [Total Revenue],
    CALCULATE ( [Total Revenue], ALLEXCEPT ( Products, Products[Category] ) )
)
```

### 5.4 Time intelligence and advanced measures

```DAX
Revenue LY =
CALCULATE ( [Total Revenue], SAMEPERIODLASTYEAR ( 'Calendar'[Date] ) )

YoY Growth % =
DIVIDE ( [Total Revenue] - [Revenue LY], [Revenue LY] )

3M Moving Avg =
DIVIDE (
    CALCULATE (
        [Total Revenue],
        DATESINPERIOD ( 'Calendar'[Date], MAX ( 'Calendar'[Date] ), -3, MONTH )
    ),
    3
)
```

### 5.5 Optional extras

```DAX
Revenue YTD = TOTALYTD ( [Total Revenue], 'Calendar'[Date] )

Running Total =
CALCULATE (
    [Total Revenue],
    FILTER ( ALL ( 'Calendar'[Date] ), 'Calendar'[Date] <= MAX ( 'Calendar'[Date] ) )
)

Product Rank =
RANKX ( ALL ( Products[ProductName] ), [Total Revenue], , DESC, Dense )

YoY Color =
IF ( [YoY Growth %] >= 0, "#2E7D32", "#C62828" )
```

### 5.6 Measure summary

| # | Measure | Concept |
|---|---|---|
| 1 | Total Revenue | `SUMX` |
| 2 | Total Cost | `SUMX` |
| 3 | Total Profit | Measure built on measures |
| 4 | Profit Margin % | `DIVIDE` |
| 5 | Total Orders | `DISTINCTCOUNT` |
| 6 | Avg Revenue per Customer | `AVERAGEX` |
| 7 | Large Order Revenue | `CALCULATE` + `FILTER` |
| 8 | Revenue % of Category | `ALLEXCEPT` |
| 9 | Revenue LY | `SAMEPERIODLASTYEAR` |
| 10 | YoY Growth % | Growth formula |
| 11 | 3M Moving Avg | `DATESINPERIOD` |

### 5.7 Key concepts

- **Measure vs calculated column:** a column is computed row by row and stored in the table. A measure is computed when needed, based on the current filters.
- **Filter context:** slicers, axes and filters decide which rows a measure sees.
- **CALCULATE:** changes the filter context before evaluating an expression.
- **Date table:** time functions need a continuous Date table that is marked as the date table.

## 6. Dashboard pages

### Page 1: Sales Overview

| Visual | Fields |
|---|---|
| Cards | `Total Revenue`, `Total Cost`, `Total Profit`, `Profit Margin %`, `Total Orders` |
| KPI | Value `Total Revenue`, Trend axis `Calendar[Date]` (month), Target `Revenue LY` |
| Clustered column | X `Products[Category]`, Y `Total Revenue` |
| Donut | Legend `Customers[Region]`, Values `Total Revenue` |
| Slicers | `Calendar[Year]`, `Customers[Region]` |

### Page 2: Product Analysis

| Visual | Fields |
|---|---|
| Bar chart (Top N) | Y `ProductName`, X `Total Revenue` |
| Table | `ProductName`, `Category`, `Total Revenue`, `Total Profit`, `Profit Margin %`, `Revenue % of Category` |
| Card | `Large Order Revenue` |
| Treemap | Group `Category`, Values `Total Revenue` |
| Scatter | Values `ProductName`, X `Total Orders`, Y `Profit Margin %`, Size `Total Revenue` |

### Page 3: Trends (planned)

| Visual | Fields |
|---|---|
| Line chart | X `YearMonth`, Y `Total Revenue`, `Revenue LY` |
| Line chart | X `YearMonth`, Y `Total Revenue`, `3M Moving Avg` |
| Matrix | Rows `Year`, `Quarter`, `MonthName`; Values `Total Revenue`, `YoY Growth %` |

## 7. Advanced features

**Drill-through**
1. Add a page named `Product Details` with cards, a monthly line chart and a customer table.
2. Drag `Products[ProductName]` into the **Drill through** well.
3. On the product page, right-click a product, then choose **Drill through → Product Details**.

**Bookmarks and navigation**
1. **Insert → Buttons → Navigator → Page navigator**.
2. Stack a chart and a table, hide one in the **Selection pane**, then add the bookmarks `Chart View` and `Table View` (**View → Bookmarks**).
3. Add two buttons and set **Action → Type = Bookmark** for each.

**Conditional formatting**
- Table or matrix column dropdown → **Conditional formatting → Background color / Font color / Data bars**.
- For green and red growth: **Rules**, with `>= 0` green and `< 0` red.

## 8. Key insights

- Total revenue is **71.29M**, cost **47.59M**, profit **23.70M**, a margin of about **33%**.
- **Electronics** (about 34M) and **Furniture** (about 21M) bring most of the revenue.
- **Laptop** is the top product (about 14.6M).
- **North** (about 31%) and **East** (about 28%) are the strongest regions.
- Margins range from about 22% (Planner) to about 42% (Pen Set).
- Large orders (above 50,000) make up about 38% of revenue.

## 9. Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| "A single value for column 'Quantity' cannot be determined" | Row-by-row formula written as a plain measure | Use `SUMX` (as in `Total Revenue`) or a calculated column |
| "A column specified in `SAMEPERIODLASTYEAR` is not of type DATE" | `Calendar[Date]` loaded as text | Set `Calendar[Date]` and `Sales[OrderDate]` to Date, then mark as date table |
| Chart shows a single point under (Blank) | Relationship missing or inactive | Recreate `Sales[OrderDate]` to `Calendar[Date]`, Many-to-One, active |
| Year slicer shows (Blank) | Some sales dates not matching the Calendar | Check Date types and the relationship |
| KPI shows "Goal: (Blank)" | No previous year for 2023 | Select 2024 or 2025 in the Year slicer |
| Margin shows 0.33 | Measure not formatted | Set **Measure tools → Format → Percentage** |
| Orders card shows 4K | Display units on Auto | Set **Display units** to **None** |
| `Revenue % of Category` looks like share of total | Category not in the visual | Add `Products[Category]` to the table |

## 10. Status and next steps

| Deliverable | Status |
|---|---|
| CSV datasets | Done |
| Data model and date table | Done |
| 10+ DAX measures | Done (11) |
| Time intelligence examples | Done |
| Dashboard (2 pages) | In progress |
| Drill-through | Pending |
| Bookmarks and navigation | Pending |
| Conditional formatting | Pending |
