# Data Visualization: Matplotlib, Seaborn, Plotly

Beginner-friendly notebooks with short, simple code. Every notebook runs top to bottom with no internet and no external data (datasets are created inside the notebooks).

## Setup
```bash
pip install matplotlib seaborn plotly pandas numpy scipy jupyter
jupyter notebook
```

## Project structure
| File | What it covers |
|---|---|
| `01_matplotlib_basics.ipynb` | Line, bar, scatter, histogram, pie, subplots, customization |
| `02_seaborn_statistical_plots.ipynb` | Distributions, categorical plots, heatmaps, pair plots, statistical annotations |
| `03_plotly_interactive.ipynb` | Interactive charts, 3D, animation, HTML export |
| `04_best_practices.ipynb` | Bad vs good chart examples, colors, labeling |
| `05_practice_sales_dashboard.ipynb` | Sales dashboards, time series, comparisons |
| `html_exports/` | Interactive dashboards: open in any browser |
| `images/` | Saved PNG charts |

## Chart guide: which chart should I use?
| I want to show... | Use this chart | Library call |
|---|---|---|
| A trend over time | Line / area | `plt.plot`, `px.line` |
| Compare categories | Bar (horizontal for long names) | `plt.bar`, `plt.barh`, `sns.barplot` |
| Compare groups across categories | Grouped bar | `plt.bar` with offsets, `hue=` |
| Parts of a total (2-5 parts) | Stacked bar, pie, donut | `plt.pie`, `px.pie` |
| Relationship of 2 numbers | Scatter | `plt.scatter`, `sns.scatterplot` |
| Relationship + 3rd number | Bubble chart | `plt.scatter(s=...)` |
| Trend line in scatter | Regression plot | `sns.regplot` |
| Shape of one variable | Histogram, KDE, ECDF | `plt.hist`, `sns.histplot`, `sns.kdeplot`, `sns.ecdfplot` |
| Spread and outliers | Box plot | `plt.boxplot`, `sns.boxplot`, `px.box` |
| Spread + shape by group | Violin plot | `sns.violinplot` |
| Every data point by group | Strip / swarm | `sns.stripplot`, `sns.swarmplot` |
| Counts of categories | Count plot | `sns.countplot` |
| Value uncertainty | Error bars | `plt.errorbar` |
| Correlations / 2D tables | Heatmap | `sns.heatmap`, `px.imshow` |
| All numeric columns at once | Pair plot | `sns.pairplot` |
| Compare subsets side by side | Facet grid | `sns.FacetGrid` |
| Two variables + their histograms | Joint plot | `sns.jointplot` |
| Hierarchy | Treemap, sunburst | `px.treemap`, `px.sunburst` |
| 3 numeric dimensions | 3D scatter / surface | `px.scatter_3d`, `go.Surface` |
| Change over time (animated) | Animated scatter / bar | `animation_frame=` |
| Stock-style data | Candlestick | `go.Candlestick` |
| Many charts together | Subplots / dashboard | `plt.subplots`, `make_subplots` |

## Deliverables checklist
- **30+ chart types**: line, bar, horizontal bar, grouped bar, stacked bar, scatter, bubble, histogram, pie, donut, area, box, error bars, KDE, ECDF, count, violin, strip, swarm, regression, joint, correlation heatmap, pivot heatmap, pair plot, facet grid, treemap, sunburst, 3D scatter, 3D surface, animated scatter, animated bar, range-slider line, candlestick, moving-average line.
- **Interactive dashboards** (`html_exports/`):
  - `sales_dashboard.html`: 4-panel dashboard
  - `dashboard_with_filter.html`: dropdown to filter by region
  - `animated_revenue.html`: play/slider animation by month
  - `scatter.html`, `combined.html`: simple exports
- **Statistical visualizations**: distributions, correlation (r, p-value) annotation, t-test, group means, heatmaps, pair plots.
- **README with chart guide**: this file.

## Best practices summary
1. Pick the chart that matches the question (see table above).
2. Start bar charts at zero.
3. Use few colors; highlight the one thing that matters.
4. Use colorblind-safe palettes (`sns.color_palette('colorblind')`).
5. Title = the message; label axes with units; cite the source.
6. Remove clutter (extra gridlines, borders, 3D effects).
7. Do not use pie charts with more than 5 slices.

## Tips
- Interactive charts need to be opened in Jupyter or a browser (the HTML files work offline).
- To re-run: *Kernel > Restart & Run All*.
