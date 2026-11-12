# Power BI Data Model Architecture & Star Schema Design
**Platform:** Olist Brazilian E-Commerce Analytics  
**Author:** Aaryaraj Patil  

---

## 1. Architectural Overview & Modeling Principles

In enterprise Business Intelligence, optimal query performance and DAX calculation accuracy depend on a clean **Star Schema** (Kimball dimensional modeling methodology).

```
                      +-------------------+
                      |     Dim_Date      |
                      +-------------------+
                               | (1)
                               |
                               | (*)
+-------------------+ (1)      |      (*) (1) +-------------------+
|   dim_customers   |----------+-------------|    dim_sellers    |
+-------------------+          |              +-------------------+
                               | (*)
                               v
                      +-------------------+
                      |    fact_orders    |
                      +-------------------+
                         | (*)        | (*)
                         |            |
                         v            v
           +---------------------+   +---------------------+
           |   fact_order_items  |   | fact_order_payments |
           +---------------------+   +---------------------+
                         | (*)
                         |
                         | (1)
           +---------------------+
           |    dim_products     |
           +---------------------+
```

### Table Roles & Relationships

| Dimension Table (1) | Fact Table (*) | Primary Key | Foreign Key | Cardinality | Filter Direction |
| :--- | :--- | :--- | :--- | :---: | :---: |
| `Dim_Date` | `fact_orders` | `Date` | `order_purchase_date` | 1 : Many | Single |
| `dim_customers` | `fact_orders` | `customer_id` | `customer_id` | 1 : Many | Single |
| `dim_products` | `fact_order_items` | `product_id` | `product_id` | 1 : Many | Single |
| `dim_sellers` | `fact_order_items` | `seller_id` | `seller_id` | 1 : Many | Single |
| `fact_orders` | `fact_order_items` | `order_id` | `order_id` | 1 : Many | Single |
| `fact_orders` | `fact_order_payments` | `order_id` | `order_id` | 1 : Many | Single |
| `fact_orders` | `fact_order_reviews` | `order_id` | `order_id` | 1 : Many | Single |

---

## 2. Dedicated Calendar Table (`Dim_Date`)

Power BI Time Intelligence functions (`TOTALYTD`, `SAMEPERIODLASTYEAR`, `DATEADD`) require an unbroken, continuous Date dimension marked as an official Date Table.

### DAX Script to Generate `Dim_Date`:
```dax
Dim_Date = 
VAR MinYear = 2016
VAR MaxYear = 2018
VAR BaseCalendar = CALENDAR(DATE(MinYear, 1, 1), DATE(MaxYear, 12, 31))
RETURN
    GENERATE(
        BaseCalendar,
        VAR CurrentDate = [Date]
        RETURN ROW(
            "Year", YEAR(CurrentDate),
            "Year Quarter", "Q" & FORMAT(CurrentDate, "Q") & "-" & YEAR(CurrentDate),
            "Quarter", "Q" & FORMAT(CurrentDate, "Q"),
            "Month Number", MONTH(CurrentDate),
            "Month Name", FORMAT(CurrentDate, "mmmm"),
            "Month Short", FORMAT(CurrentDate, "mmm"),
            "Year Month", FORMAT(CurrentDate, "yyyy-mm"),
            "Year Month Sort", YEAR(CurrentDate) * 100 + MONTH(CurrentDate),
            "Day of Month", DAY(CurrentDate),
            "Day of Week Number", WEEKDAY(CurrentDate, 2), -- 1=Monday, 7=Sunday
            "Day of Week Name", FORMAT(CurrentDate, "dddd"),
            "Is Weekend", IF(WEEKDAY(CurrentDate, 2) IN {6, 7}, "Weekend", "Weekday")
        )
    )
```

---

## 3. Power BI Performance Best Practices Applied

1. **Disable Auto Date/Time:** Turn off `Auto Date/Time for new files` in Power BI Options to prevent hidden in-memory date hierarchy tables from consuming RAM.
2. **Strict Single-Direction Filtering:** All relationships filter from Dimension (1) to Fact (*). Bi-directional cross-filtering is strictly avoided to eliminate ambiguity and performance bottlenecks.
3. **Sort By Column:** Ensure `Month Short` is sorted by `Month Number`, and `Year Month` is sorted by `Year Month Sort` to guarantee correct chronological order in charts.
4. **Data Types & Decimal Places:** All currency fields (`price`, `freight_value`, `payment_value`) are formatted as `Fixed Decimal Number` (Currency BRL) to minimize precision floating-point storage overhead.
