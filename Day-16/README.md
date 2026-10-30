House Market Dashboard: Power BI Guide (Day 12)

An interactive Power BI report analysing house sales across four Danish regions: Zealand, Jutland, Fyn & islands and Bornholm. The project covers the full basic workflow: setup, data connection, Power Query cleaning, data modelling, DAX measures and dashboard building.

Contents
Project Overview
Learning Objectives
Prerequisites
Project Structure
Step-by-Step Guide
Data Model and Measures
Dashboard Pages
Key Insights
Known Issues and Next Steps
Project Overview
Item	Details
Tool	Power BI Desktop
Data source	Excel / CSV file of house sales
Key fields	region, sales_type, offer price, purchase_price, age, area (sqm), sales date
Output	2-page interactive dashboard (.pbix)
Learning Objectives
Set up Power BI
Connect data sources
Create data models
Build basic reports
Prerequisites
Windows PC (Power BI Desktop is Windows only)
Power BI Desktop installed (free), from the Microsoft Store or the website installer
The source Excel or CSV file
Project Structure
day12-powerbi/
├── data/                  # Source Excel / CSV file
├── House_Market.pbix      # Power BI report file
├── screenshots/           # Dashboard images
└── README.md              # This guide
Step-by-Step Guide
1. Understand the interface
Area	Purpose
Report view	Canvas where visuals are built
Table view	Inspect rows and columns
Model view	Create and manage relationships
Visualizations pane	Choose chart types and set field wells
Data pane	Tables, columns and measures
Filters pane	Visual, page and report level filters
2. Connect data
Open Power BI Desktop and start a blank report.
Go to Home > Get Data > Excel or Text/CSV.
Select the file and preview it in the Navigator.
Click Transform Data to open Power Query.
3. Transform data in Power Query
Task	How
Remove columns	Select the columns, right-click, then Remove Columns
Filter rows	Use the dropdown on a column header to remove blanks and invalid values
Change data types	Transform > Data Type (Date, Decimal Number, Whole Number, Text)
Split columns	Transform > Split Column (for example, split a date into Year, Quarter, Month, Day)
Merge columns	Transform > Merge Columns
Append queries	Home > Append Queries (stacks rows from tables with the same structure)
Merge queries	Home > Merge Queries (joins tables on a common key, like a SQL join)

When finished, click Close & Apply. All steps are saved under Applied Steps, so they re-run automatically on refresh.

4. Build the data model
Open Model view.
Confirm or create relationships, with one-to-many from dimension tables to the fact table.
Prefer single-direction filtering unless both directions are needed.
Create a blank table named Measures Table to hold all DAX measures. Hide or delete the placeholder Column1.
5. Create measures

Go to Modeling > New Measure and add the measures below.

Measure	Purpose
Average Price SQMT	Average price per square metre
Last 12 Months Sales	Rolling 12-month sales total
Median Sales Price	Median price by region
Offer to SQM ratio	Offer price relative to area
Sales by Region	Total sales split by region
TotalYTD Sales	Year-to-date sales
Units Sold (latest quarter)	Count of sales in the newest quarter
YOY Sales Growth	Year-over-year growth

Example DAX patterns (adjust table and column names to your model):

DAX
Total Sales = SUM(Sales[purchase_price])

TotalYTD Sales = TOTALYTD([Total Sales], 'Date'[Date])

Median Sales Price = MEDIAN(Sales[purchase_price])

YOY Sales Growth =
VAR PrevYear = CALCULATE([Total Sales], SAMEPERIODLASTYEAR('Date'[Date]))
RETURN DIVIDE([Total Sales] - PrevYear, PrevYear)
6. Build visualizations
Tables and matrices for detailed records
Charts (bar, area, scatter, funnel, donut) for comparisons and trends
Cards and KPIs for headline numbers
Slicers for interactive filtering
Format with a consistent theme, titles and a header banner
7. Save and share

Save as .pbix. Optionally publish via Home > Publish to the Power BI Service.

Dashboard Pages
Page 1: House Market Overview
Visual	Type	Insight
Median Sales Price by region	Bar chart	Zealand highest (about 2.7M), Bornholm lowest (about 1.2M)
Units Sold (New & Quarter)	Card	77 units
Last 12 Months Sales	Card	13bn
Offer Price vs purchase_price	Scatter plot	Strong positive linear relationship
YOY Sales Growth by Sales Type	Area chart	Auction +0.29; regular and other sale about -0.21; family sale about -0.75
Page 2: Sales Performance
Visual	Type	Insight
Sales by Region	Funnel	Zealand 95bn, Jutland 81bn, Fyn & islands 15bn, Bornholm 1bn
Key influencers	AI visual	Age group 16 to 45 linked to an average purchase_price decrease of about 512.9K
Sales detail	Table	Year, Quarter, Month, Day and TotalYTD Sales
Offer to SQM ratio by sales_type	Bar chart	Regular 14.9K, other 13.7K, family 11.9K, auction 11.1K
Average Price SQMT by region	Donut	Zealand 20.85K (about 35%), Fyn & islands 13.62K, Jutland about 13K, Bornholm 10.6K
Key Insights
Zealand leads on total sales, median price and price per sqm.
Bornholm is the smallest market on every measure.
Auction is the only sales type that grew year over year; family sales fell the most.
Offer and purchase prices are tightly correlated.
Regular sales have the highest offer-to-sqm ratio; auctions the lowest.
Known Issues and Next Steps
Fix label typos ("Chain" should be "Change", "Quater" should be "Quarter").
Improve donut chart labels, which are truncated.
Add slicers for Year, Region and Sales Type.
Hide the unused Column1 in the Measures Table.
Publish to the Power BI Service and set up scheduled refresh.
Learn more DAX (calculated columns vs measures, time intelligence).
Deliverables Checklist
 Power BI Desktop setup
 Data sources connected
 Data model with relationships
 Interactive dashboard
 README with Power BI guide