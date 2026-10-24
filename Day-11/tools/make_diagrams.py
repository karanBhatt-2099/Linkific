import html, os

ROW_H, HEAD_H = 22, 28
COLORS = {  # kind: (fill, stroke)
    "fact":      ("#f8cecc", "#b85450"),
    "dim":       ("#dae8fc", "#6c8ebf"),
    "conformed": ("#d5e8d4", "#82b366"),
    "sub":       ("#fff2cc", "#d6b656"),
}

def height(t): return HEAD_H + ROW_H * len(t["rows"])

def clip(t, tx, ty):
    """point where the line from t's center towards (tx,ty) leaves t's rectangle"""
    cx, cy = t["x"] + t["w"] / 2, t["y"] + height(t) / 2
    dx, dy = tx - cx, ty - cy
    hw, hh = t["w"] / 2, height(t) / 2
    if dx == 0 and dy == 0: return cx, cy
    s = min(hw / abs(dx) if dx else 1e9, hh / abs(dy) if dy else 1e9)
    return cx + dx * s, cy + dy * s

def centre(t): return t["x"] + t["w"] / 2, t["y"] + height(t) / 2

def build(name, title, subtitle, tables, edges, legend, out_dir):
    W = max(t["x"] + t["w"] for t in tables.values()) + 60
    H = max(t["y"] + height(t) for t in tables.values()) + 100
    # ---------------- draw.io XML ----------------
    x = ['<mxfile host="app.diagrams.net"><diagram name="%s" id="%s">' % (html.escape(title), name),
         '<mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" '
         'fold="1" page="1" pageScale="1" pageWidth="%d" pageHeight="%d" math="0" shadow="0"><root>' % (W, H),
         '<mxCell id="0"/><mxCell id="1" parent="0"/>',
         '<mxCell id="title" value="%s" style="text;html=1;fontSize=20;fontStyle=1;align=left;" vertex="1" parent="1">'
         '<mxGeometry x="30" y="10" width="700" height="30" as="geometry"/></mxCell>' % html.escape(title),
         '<mxCell id="subtitle" value="%s" style="text;html=1;fontSize=12;align=left;fontColor=#555555;" vertex="1" parent="1">'
         '<mxGeometry x="30" y="40" width="900" height="24" as="geometry"/></mxCell>' % html.escape(subtitle)]
    for tid, t in tables.items():
        f, s = COLORS[t["kind"]]
        x.append('<mxCell id="%s" value="%s" style="swimlane;fontStyle=1;childLayout=stackLayout;horizontal=1;startSize=%d;'
                 'horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=0;marginBottom=0;'
                 'fillColor=%s;strokeColor=%s;fontSize=13;fontColor=#000000;" vertex="1" parent="1">'
                 '<mxGeometry x="%d" y="%d" width="%d" height="%d" as="geometry"/></mxCell>'
                 % (tid, html.escape(t["title"]), HEAD_H, f, s, t["x"], t["y"], t["w"], height(t)))
        for i, (tag, col, typ) in enumerate(t["rows"]):
            txt = "%-3s %s : %s" % (tag, col, typ)
            bold = "fontStyle=1;" if tag in ("PK", "SK") else ""
            x.append('<mxCell id="%s_r%d" value="%s" style="text;strokeColor=%s;strokeWidth=0.5;fillColor=#ffffff;align=left;'
                     'verticalAlign=middle;spacingLeft=6;spacingRight=4;overflow=hidden;rotatable=0;fontSize=11;'
                     'fontFamily=Courier New;whiteSpace=nowrap;%s" vertex="1" parent="%s">'
                     '<mxGeometry y="%d" width="%d" height="%d" as="geometry"/></mxCell>'
                     % (tid, i, html.escape(txt), s, bold, tid, HEAD_H + i * ROW_H, t["w"], ROW_H))
    for i, (a, b) in enumerate(edges):
        x.append('<mxCell id="e%d" style="edgeStyle=none;html=1;rounded=0;startArrow=ERmany;startFill=0;endArrow=ERone;'
                 'endFill=0;strokeWidth=1.5;strokeColor=#444444;" edge="1" parent="1" source="%s" target="%s">'
                 '<mxGeometry relative="1" as="geometry"/></mxCell>' % (i, a, b))
    # legend
    lx, ly = 30, H - 40
    for i, (label, kind) in enumerate(legend):
        f, s = COLORS[kind]
        x.append('<mxCell id="lg%d" value="%s" style="rounded=0;fillColor=%s;strokeColor=%s;fontSize=11;" vertex="1" parent="1">'
                 '<mxGeometry x="%d" y="%d" width="170" height="24" as="geometry"/></mxCell>' % (i, html.escape(label), f, s, lx + i * 185, ly))
    x.append('</root></mxGraphModel></diagram></mxfile>')
    open(os.path.join(out_dir, name + ".drawio"), "w", encoding="utf-8").write("\n".join(x))

    # ---------------- SVG preview ----------------
    v = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" font-family="Arial, sans-serif">' % (W, H, W, H),
         '<rect width="100%" height="100%" fill="#ffffff"/>',
         '<text x="30" y="32" font-size="20" font-weight="bold">%s</text>' % html.escape(title),
         '<text x="30" y="54" font-size="12" fill="#555">%s</text>' % html.escape(subtitle)]
    for a, b in edges:
        ta, tb = tables[a], tables[b]
        x1, y1 = clip(ta, *centre(tb)); x2, y2 = clip(tb, *centre(ta))
        v.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#444" stroke-width="1.5"/>' % (x1, y1, x2, y2))
        L = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** .5 or 1
        for (px, py, ux, uy, lab) in ((x1, y1, (x2 - x1) / L, (y2 - y1) / L, "N"), (x2, y2, (x1 - x2) / L, (y1 - y2) / L, "1")):
            v.append('<text x="%.1f" y="%.1f" font-size="12" font-weight="bold" fill="#c00" text-anchor="middle">%s</text>'
                     % (px + ux * 14, py + uy * 14 + 4, lab))
    for tid, t in tables.items():
        f, s = COLORS[t["kind"]]
        h = height(t)
        v.append('<rect x="%d" y="%d" width="%d" height="%d" fill="#fff" stroke="%s" stroke-width="1.5"/>' % (t["x"], t["y"], t["w"], h, s))
        v.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="%s" stroke-width="1.5"/>' % (t["x"], t["y"], t["w"], HEAD_H, f, s))
        v.append('<text x="%d" y="%d" font-size="13" font-weight="bold" text-anchor="middle">%s</text>' % (t["x"] + t["w"] / 2, t["y"] + 19, html.escape(t["title"])))
        for i, (tag, col, typ) in enumerate(t["rows"]):
            y = t["y"] + HEAD_H + i * ROW_H
            v.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="0.5"/>' % (t["x"], y, t["x"] + t["w"], y, s))
            wt = ' font-weight="bold"' if tag in ("PK", "SK") else ""
            v.append('<text x="%d" y="%d" font-size="11" font-family="Courier New, monospace"%s xml:space="preserve">%s</text>'
                     % (t["x"] + 6, y + 15, wt, html.escape("%-3s %s : %s" % (tag, col, typ))))
    for i, (label, kind) in enumerate(legend):
        f, s = COLORS[kind]
        v.append('<rect x="%d" y="%d" width="170" height="24" fill="%s" stroke="%s"/><text x="%d" y="%d" font-size="11" text-anchor="middle">%s</text>'
                 % (30 + i * 185, H - 40, f, s, 30 + i * 185 + 85, H - 24, html.escape(label)))
    v.append('<text x="%d" y="%d" font-size="11" fill="#c00">N = many, 1 = one  (fact N : 1 dimension)</text>' % (30, H - 52))
    v.append('</svg>')
    open(os.path.join(out_dir, name + ".svg"), "w", encoding="utf-8").write("\n".join(v))

def T(title, kind, x, y, rows, w=270): return dict(title=title, kind=kind, x=x, y=y, rows=rows, w=w)

# ---------- column definitions (full, match the SQL exactly) ----------
DATE = [("PK","date_key","INT"),("","full_date","DATE"),("","day_of_month","SMALLINT"),("","day_of_week","SMALLINT"),
        ("","day_name","VARCHAR(10)"),("","week_of_year","SMALLINT"),("","month_number","SMALLINT"),("","month_name","VARCHAR(10)"),
        ("","quarter","SMALLINT"),("","year","SMALLINT"),("","is_weekend","BOOLEAN")]
CUST = [("PK","customer_key","INT  (surrogate)"),("NK","customer_id","VARCHAR(10)"),("","full_name","VARCHAR(100)"),("","email","VARCHAR(100)"),
        ("","city","VARCHAR(50)"),("","state","VARCHAR(50)"),("","country","VARCHAR(50)"),("","segment","VARCHAR(20)"),
        ("","effective_date","DATE"),("","end_date","DATE"),("","is_current","BOOLEAN")]
PROD = [("PK","product_key","INT  (surrogate)"),("NK","product_id","VARCHAR(10)"),("","product_name","VARCHAR(100)"),("","category","VARCHAR(50)"),
        ("","subcategory","VARCHAR(50)"),("","brand","VARCHAR(50)"),("","unit_cost","NUMERIC(12,2)"),("","unit_price","NUMERIC(12,2)")]
STORE = [("PK","store_key","INT  (surrogate)"),("NK","store_id","VARCHAR(10)"),("","store_name","VARCHAR(100)"),("","city","VARCHAR(50)"),
         ("","state","VARCHAR(50)"),("","region","VARCHAR(20)"),("","store_type","VARCHAR(20)")]
FACT = [("PK","sales_key","BIGINT"),("FK","date_key","INT"),("FK","customer_key","INT"),("FK","product_key","INT"),("FK","store_key","INT"),
        ("DD","order_id","VARCHAR(12)"),("DD","order_line_number","SMALLINT"),("M","quantity","INT"),("M","unit_price","NUMERIC(12,2)"),
        ("M","discount_amount","NUMERIC(12,2)"),("M","sales_amount","NUMERIC(12,2)"),("M","cost_amount","NUMERIC(12,2)"),("M","profit_amount","NUMERIC(12,2)")]
INV = [("PK","inventory_key","BIGINT"),("FK","date_key","INT"),("FK","product_key","INT"),("FK","store_key","INT"),
       ("M","quantity_on_hand","INT"),("M","reorder_level","INT")]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "diagrams")
os.makedirs(out, exist_ok=True)
LEG_STAR = [("Fact table (events + measures)", "fact"), ("Dimension table (context)", "dim")]
KEYS = "PK=primary key  FK=foreign key  NK=natural key  DD=degenerate dimension  M=measure"

# 1) STAR -----------------------------------------------------------------
build("01_star_schema", "Sales Data Warehouse - STAR Schema",
      "Grain: one row per product line on one order.   " + KEYS,
      {"dim_date": T("dw.dim_date", "dim", 30, 90, DATE),
       "dim_customer": T("dw.dim_customer (SCD Type 2 ready)", "dim", 700, 90, CUST, 300),
       "fact_sales": T("dw.fact_sales", "fact", 365, 190, FACT),
       "dim_product": T("dw.dim_product", "dim", 30, 480, PROD),
       "dim_store": T("dw.dim_store", "dim", 700, 480, STORE, 300)},
      [("fact_sales", "dim_date"), ("fact_sales", "dim_customer"), ("fact_sales", "dim_product"), ("fact_sales", "dim_store")],
      LEG_STAR, out)

# 2) SNOWFLAKE ------------------------------------------------------------
build("02_snowflake_schema", "Sales Data Warehouse - SNOWFLAKE Schema",
      "Product and store dimensions are normalized into sub-tables (more joins, less repeated text).",
      {"dim_date": T("dw.dim_date", "conformed", 30, 90, [r for r in DATE if r[1] in ("date_key","full_date","month_name","quarter","year")], 230),
       "dim_customer": T("dw.dim_customer", "conformed", 30, 270, [r for r in CUST if r[1] in ("customer_key","customer_id","full_name","city","segment")], 275),
       "fact": T("dw_snowflake.fact_sales", "fact", 340, 150,
                 [("PK","sales_key","BIGINT"),("FK","date_key","INT"),("FK","customer_key","INT"),("FK","product_key","INT"),("FK","store_key","INT"),
                  ("DD","order_id","VARCHAR(12)"),("M","quantity","INT"),("M","sales_amount","NUMERIC"),("M","profit_amount","NUMERIC")], 230),
       "dim_product": T("dw_snowflake.dim_product", "dim", 640, 60,
                 [("PK","product_key","INT"),("NK","product_id","VARCHAR(10)"),("","product_name","VARCHAR(100)"),("","brand","VARCHAR(50)"),("FK","subcategory_key","INT")], 250),
       "dim_subcategory": T("dw_snowflake.dim_subcategory", "sub", 960, 60,
                 [("PK","subcategory_key","INT"),("","subcategory_name","VARCHAR(50)"),("FK","category_key","INT")], 250),
       "dim_category": T("dw_snowflake.dim_category", "sub", 1270, 60,
                 [("PK","category_key","INT"),("","category_name","VARCHAR(50)")], 260),
       "dim_store": T("dw_snowflake.dim_store", "dim", 640, 330,
                 [("PK","store_key","INT"),("NK","store_id","VARCHAR(10)"),("","store_name","VARCHAR(100)"),("","city","VARCHAR(50)"),("FK","region_key","INT")], 250),
       "dim_region": T("dw_snowflake.dim_region", "sub", 960, 330,
                 [("PK","region_key","INT"),("","region_name","VARCHAR(20)")], 220)},
      [("fact", "dim_date"), ("fact", "dim_customer"), ("fact", "dim_product"), ("fact", "dim_store"),
       ("dim_product", "dim_subcategory"), ("dim_subcategory", "dim_category"), ("dim_store", "dim_region")],
      [("Fact table", "fact"), ("Dimension", "dim"), ("Normalized sub-dimension", "sub"), ("Shared with star (dw schema)", "conformed")], out)

# 3) GALAXY ---------------------------------------------------------------
build("03_galaxy_schema", "Sales Data Warehouse - GALAXY (Fact Constellation) Schema",
      "Two fact tables share CONFORMED dimensions (date, product, store). dim_customer is used only by sales.",
      {"fact_sales": T("dw.fact_sales  (transaction fact)", "fact", 30, 120,
                 [("PK","sales_key","BIGINT"),("FK","date_key","INT"),("FK","customer_key","INT"),("FK","product_key","INT"),("FK","store_key","INT"),
                  ("DD","order_id","VARCHAR(12)"),("M","quantity","INT"),("M","sales_amount","NUMERIC"),("M","profit_amount","NUMERIC")], 250),
       "dim_customer": T("dw.dim_customer", "dim", 30, 420, [r for r in CUST if r[1] in ("customer_key","customer_id","full_name","city","segment")], 250),
       "dim_date": T("dw.dim_date  (CONFORMED)", "conformed", 400, 70, [r for r in DATE if r[1] in ("date_key","full_date","month_name","quarter","year")], 260),
       "dim_product": T("dw.dim_product  (CONFORMED)", "conformed", 400, 260, [r for r in PROD if r[1] in ("product_key","product_id","product_name","category","brand")], 260),
       "dim_store": T("dw.dim_store  (CONFORMED)", "conformed", 400, 450, [r for r in STORE if r[1] in ("store_key","store_id","store_name","region")], 260),
       "fact_inventory": T("dw.fact_inventory  (periodic snapshot fact)", "fact", 830, 200, INV, 270)},
      [("fact_sales", "dim_date"), ("fact_sales", "dim_customer"), ("fact_sales", "dim_product"), ("fact_sales", "dim_store"),
       ("fact_inventory", "dim_date"), ("fact_inventory", "dim_product"), ("fact_inventory", "dim_store")],
      [("Fact table", "fact"), ("Conformed dimension", "conformed"), ("Dimension (one fact only)", "dim")], out)

# 4) FULL ER DIAGRAM ------------------------------------------------------
build("04_data_warehouse_erd", "Sales Data Warehouse - Physical ER Diagram (schema dw)",
      "Exactly mirrors sql/01_ddl.   " + KEYS,
      {"dim_date": T("dw.dim_date", "conformed", 30, 90, DATE, 250),
       "dim_customer": T("dw.dim_customer", "dim", 30, 400, CUST, 280),
       "fact_sales": T("dw.fact_sales", "fact", 400, 190, FACT, 270),
       "dim_product": T("dw.dim_product", "conformed", 790, 90, PROD, 280),
       "dim_store": T("dw.dim_store", "conformed", 790, 330, STORE, 280),
       "fact_inventory": T("dw.fact_inventory", "fact", 790, 560, INV, 280)},
      [("fact_sales", "dim_date"), ("fact_sales", "dim_customer"), ("fact_sales", "dim_product"), ("fact_sales", "dim_store"),
       ("fact_inventory", "dim_date"), ("fact_inventory", "dim_product"), ("fact_inventory", "dim_store")],
      [("Fact table", "fact"), ("Conformed dimension", "conformed"), ("Dimension", "dim")], out)
print("Diagrams written to", os.path.abspath(out))
