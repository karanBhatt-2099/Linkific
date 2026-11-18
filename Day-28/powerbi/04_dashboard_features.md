# Dashboard Features (Step-by-step)

## 1. Slicers and filters
- Insert **Slicer** → drag `dim_date[year]` → Format → Slicer settings → *Tile / Dropdown*.
- Repeat for `dim_customer[region]` and `dim_customer[segment]`.
- **Sync slicers**: View → Sync slicers → tick all pages for Year and Region.
- Filters pane: add a *Page-level filter* on Page 3 → `category` is not blank.

## 2. Drill-through (Product Detail page)
1. Add a new page called **Product Detail**.
2. Drag `dim_product[product_name]` into the *Drill through → Add drill-through fields* well.
3. Add visuals: Cards (Revenue, Profit, Orders), line chart of monthly revenue, table of top customers.
4. On Page 3, right-click any product bar → **Drill through → Product Detail**.
5. A back button appears automatically (top-left).

## 3. Bookmarks
Open **View → Bookmarks** and **Selection** panes.

| Bookmark | How to create |
|---|---|
| Reset Filters | Clear all slicers → View → Bookmarks → Add |
| Revenue View | On Page 2, show the revenue chart, hide the growth chart → Add bookmark |
| Growth View | Hide the revenue chart, show growth chart → Add bookmark |

Add two **Buttons** (Insert → Buttons → Blank) labelled *Revenue* and *Growth* → Action: Bookmark → pick the matching one.

## 4. Navigation
- Insert → Buttons → **Navigator → Page navigator** (auto-creates buttons for all pages).
- Copy the navigator to every page (or put it on a template page).
- Add a **Home** button (Insert → Buttons → Home icon) → Action: Page navigation → Overview.
- Hide the Product Detail page (right-click tab → Hide page) so it only opens through drill-through.

## 5. Final checks
- Titles and axis labels set on every visual
- Same colour palette on all pages (blue / green / orange)
- Totals match the SQL queries
- Save as `Day28_Sales_Dashboard.pbix` in this folder
