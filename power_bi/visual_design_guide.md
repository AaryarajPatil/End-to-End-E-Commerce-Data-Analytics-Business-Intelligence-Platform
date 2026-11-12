# Power BI Dashboard Visual Design & Configuration Guide
**Project:** End-to-End E-Commerce Data Analytics Platform (Olist)  
**Author:** Aaryaraj Patil  
**Target Resolution:** 16:9 (1920 x 1080 px or 1280 x 720 px)  

---

## 1. Corporate Design System & Visual Hierarchy

A clean, cohesive aesthetic ensures stakeholders can extract actionable insights within five seconds of landing on any page.

### Color Palette (Hex Codes)
| Element | Color Name | Hex Code | Purpose / Usage |
| :--- | :--- | :--- | :--- |
| **Primary** | Midnight Navy | `#0F172A` | Navigation bars, primary page titles, major card fonts |
| **Secondary** | Dark Slate | `#1E293B` | Card container borders, secondary axis labels |
| **Accent Primary**| Royal Electric | `#2563EB` | Revenue line graphs, primary bar charts, active buttons |
| **Accent Positive**| Emerald Green| `#10B981` | On-time delivery indicators, positive MoM growth |
| **Accent Warning** | Amber Orange | `#F59E0B` | Delayed warning alerts, moderate review scores |
| **Accent Danger**  | Crimson Red  | `#EF4444` | High logistics delays, 1-star reviews, negative growth |
| **Background**    | Pure Slate    | `#F8FAFC` | Clean canvas background |
| **Card Fill**     | Crisp White   | `#FFFFFF` | Visual container card backgrounds with subtle shadow |

### Typography Guidelines
- **Page Titles:** Segoe UI Semibold, 20 pt, `#0F172A`.
- **Card Callout Values:** Segoe UI Bold, 28–32 pt, `#0F172A`.
- **Card Category Labels:** Segoe UI, 10–11 pt, `#64748B`.
- **Axis Titles & Legends:** Segoe UI, 9–10 pt, `#475569`.

---

## 2. Page-by-Page Visual Configuration

---

### Page 1: Executive Overview
*Audience: C-Suite, VP of E-Commerce, Directors.*

1. **Top KPI Banner (4 Cards across top):**
   - Card 1: `[Total Revenue]` (formatted as Currency R$ Millions, e.g. R$15.82M).
   - Card 2: `[Total Orders]` (formatted with comma, e.g. 96,478).
   - Card 3: `[Average Order Value]` (e.g. R$164.03).
   - Card 4: `[On-Time Delivery Rate %]` (e.g. 91.89%, Green status conditional formatting).
2. **Main Visual (Center Left - Line & Clustered Column Chart):**
   - X-Axis: `Dim_Date[Year Month]`.
   - Column Y-Axis: `[Total Revenue]`.
   - Line Y-Axis: `[Revenue MoM Growth %]`.
3. **Product Contribution (Center Right - Treemap):**
   - Group: `dim_products[product_category_name_english]`.
   - Values: `[Total Revenue]`.
   - Top 10 filter applied.
4. **Bottom Bar (Bottom Left & Right):**
   - Bottom Left (Donut Chart): `[Total Revenue]` by `fact_order_payments[payment_type]`.
   - Bottom Right (Gauge Chart): Value = `[Avg Review Score]` (Min 1.0, Max 5.0, Target 4.5).

---

### Page 2: Sales Performance
*Audience: Sales Directors, Merchandising Managers.*

1. **Top Slicers:** `Year`, `Quarter`, `Customer State`, `Category`.
2. **Cumulative GMV Velocity (Area Chart):**
   - X-Axis: `Dim_Date[Date]`.
   - Y-Axis: `[Revenue YTD]`.
   - Legend: `Dim_Date[Year]`.
3. **Payment Method Analysis (Clustered Bar Chart):**
   - Y-Axis: `fact_order_payments[payment_type]`.
   - X-Axis: `[Total Revenue]`.
   - Tooltip: `[Average Installments]`, `[Transaction Share %]`.
4. **Credit Card Installment Distribution (Clustered Column Chart):**
   - X-Axis: `fact_order_payments[payment_installments]` (1 to 24).
   - Y-Axis: `COUNTROWS(fact_order_payments)`.

---

### Page 3: Customer Intelligence & RFM
*Audience: Retention Marketing, CRM Managers.*

1. **KPI Cards:** `[Unique Customers]`, `[Repeat Customer Rate %]`, `[Avg Customer Spend]`.
2. **Customer Acquisition Growth (Line Chart):**
   - X-Axis: `Dim_Date[Year Month]`.
   - Y-Axis: `DISTINCTCOUNT(dim_customers[customer_unique_id])`.
3. **RFM Segment Matrix (Stacked Bar Chart):**
   - Y-Axis: `RFM Segment` (Champions, Loyal, At Risk, Hibernating, etc.).
   - X-Axis: Total Spend and Customer Volume.
4. **State-by-State Customer Density (Map / Filled Map):**
   - Location: `dim_customers[customer_state]`.
   - Bubble Size: `[Total Orders]`.
   - Color Saturation: `[Total Revenue]`.

---

### Page 4: Product & Seller Analytics
*Audience: Marketplace Operations, Category Managers.*

1. **Category Pareto 80/20 Curve (Line & Clustered Column):**
   - X-Axis: `dim_products[product_category_name_english]` (sorted descending by revenue).
   - Column: `[Total Revenue]`.
   - Line: `[Pareto Cumulative Revenue %]` with 80% reference threshold line.
2. **Top 10 Sellers Leaderboard (Table with Data Bars):**
   - Columns: `seller_id`, `seller_state`, `[Total Revenue]`, `[Total Items Sold]`, `[Avg Review Score]`, `[Late Dispatch Rate %]`.
3. **Price vs Freight Elasticity (Scatter Chart):**
   - X-Axis: Average Item Price.
   - Y-Axis: Average Freight Value.
   - Size: Total Quantity Sold.
   - Legend: Product Category.

---

### Page 5: Delivery & Logistics
*Audience: Supply Chain Directors, Logistics Partners.*

1. **Delivery KPI Ribbon:** `[Avg Actual Delivery Days]` (12.5 days), `[Avg Estimated Delivery Days]` (24.4 days), `[Delayed Orders]` (7,827), `[Delayed Order %]` (8.11%).
2. **Logistics Delay Breakdown (Decomposition Tree):**
   - Root: `[Delayed Orders]`.
   - Explain by: `Customer Region` -> `Customer State` -> `Product Category` -> `Seller State`.
3. **Estimated vs Actual Variance by State (Clustered Bar Chart):**
   - Y-Axis: `dim_customers[customer_state]`.
   - Bars: `[Avg Actual Delivery Days]` vs `[Avg Estimated Delivery Days]`.
4. **Interstate vs Intrastate Delivery Performance (Donut Chart):**
   - Comparison of delivery speed when seller and buyer reside in the same state vs different states.

---

### Page 6: Customer Satisfaction & Reviews
*Audience: Customer Experience (CX) Leads, Quality Assurance.*

1. **Star Rating Breakdown (Stacked Horizontal Bar):**
   - Segments: 5 Stars (57.8%), 4 Stars (19.3%), 3 Stars (8.2%), 2 Stars (3.2%), 1 Star (11.5%).
2. **Delivery Delay vs Review Score (Clustered Column Chart):**
   - X-Axis: Delivery Status (`Delivered On-Time` vs `Delivered Late`).
   - Y-Axis: Average Review Score (On-Time = 4.30 vs Delayed = 2.15).
3. **Freight Burden Impact on Rating (Line Chart):**
   - X-Axis: Freight as % of Price (0-10%, 10-25%, 25-50%, >50%).
   - Y-Axis: Average Review Score.

---

### Page 7: Geographic Sales Analysis
*Audience: Expansion Strategy, Regional Business Developers.*

1. **Brazilian Regional Choropleth Map (Filled Map):**
   - Location: Brazilian State Code (SP, RJ, MG, RS, PR, etc.).
   - Tooltip: State Name, Total GMV, Total Orders, Average Freight Cost, Delayed Order Rate.
2. **Top Origin-Destination Freight Corridors (Matrix Visual):**
   - Rows: `Seller State`.
   - Columns: `Customer State`.
   - Values: Total Order Volume and Average Delivery Days.
3. **Regional Revenue Share (Donut / Treemap):**
   - Southeast (SE ~70% of total GMV), South (S ~15%), Northeast (NE), Central-West (CW), North (N).

---

## 3. Step-by-Step Power BI Desktop Configuration Guide

1. **Data Ingestion:**
   - Launch Power BI Desktop.
   - Click **Get Data** -> Select **MySQL Database** (enter `localhost:3306` and `olist_ecommerce_db`) OR select **Folder / Text/CSV** and select the curated files exported by `python src/export_analytical_data.py`.
2. **Verify Data Model:**
   - Navigate to the **Model View** (left navigation tab).
   - Ensure the Star Schema matches `power_bi/data_model_architecture.md`.
   - Drag `customer_id` from `dim_customers` to `fact_orders[customer_id]`.
   - Drag `product_id` from `dim_products` to `fact_order_items[product_id]`.
   - Drag `seller_id` from `dim_sellers` to `fact_order_items[seller_id]`.
   - Drag `order_id` from `fact_orders` to `fact_order_items[order_id]`.
   - Drag `order_id` from `fact_orders` to `fact_order_payments[order_id]`.
   - Drag `order_id` from `fact_orders` to `fact_order_reviews[order_id]`.
3. **Create DAX Measures Table:**
   - On the Home Ribbon, click **Enter Data**, name the table `_DAX Measures`, and click Load.
   - Right-click `_DAX Measures` -> Select **New Measure**, and paste each measure from `power_bi/dax_measures.md`.
4. **Create Dim_Date Table:**
   - Click **Modeling Ribbon** -> **New Table**, and paste the calendar DAX formula.
   - Right-click `Dim_Date` -> Select **Mark as Date Table**.
5. **Set Up Slicers & Page Navigation:**
   - Add a date range slider linked to `Dim_Date[Date]`.
   - Add buttons for page navigation with hover state animations.
