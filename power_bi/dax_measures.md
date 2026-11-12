# Comprehensive DAX Measure Catalog
**Project:** Olist E-Commerce Data Analytics & Business Intelligence Platform  
**Author:** Aaryaraj Patil  
**Target Tool:** Microsoft Power BI Desktop  

---

## 1. Core Sales & Volume Measures

### 1.1 Total Delivered Orders
```dax
Total Orders = 
CALCULATE(
    DISTINCTCOUNT(fact_orders[order_id]),
    fact_orders[order_status] = "delivered"
)
```

### 1.2 Gross Merchandise Value (GMV / Revenue)
```dax
Total Revenue = 
CALCULATE(
    SUM(fact_order_items[price]) + SUM(fact_order_items[freight_value]),
    fact_orders[order_status] = "delivered"
)
```

### 1.3 Total Item Sales (Excluding Freight)
```dax
Merchandise Sales = 
CALCULATE(
    SUM(fact_order_items[price]),
    fact_orders[order_status] = "delivered"
)
```

### 1.4 Total Freight Incurred
```dax
Total Freight = 
CALCULATE(
    SUM(fact_order_items[freight_value]),
    fact_orders[order_status] = "delivered"
)
```

### 1.5 Total Units Sold
```dax
Total Items Sold = 
CALCULATE(
    COUNT(fact_order_items[order_item_id]),
    fact_orders[order_status] = "delivered"
)
```

### 1.6 Average Order Value (AOV)
```dax
Average Order Value = 
DIVIDE([Total Revenue], [Total Orders], 0)
```

### 1.7 Average Basket Size (Items Per Order)
```dax
Average Basket Size = 
DIVIDE([Total Items Sold], [Total Orders], 0)
```

---

## 2. Time Intelligence & Growth Measures

### 2.1 Revenue Prior Month (PM)
```dax
Revenue Prior Month = 
CALCULATE(
    [Total Revenue],
    DATEADD(Dim_Date[Date], -1, MONTH)
)
```

### 2.2 Month-over-Month (MoM) Revenue Growth %
```dax
Revenue MoM Growth % = 
VAR CurrentRev = [Total Revenue]
VAR PriorRev = [Revenue Prior Month]
RETURN
    DIVIDE(CurrentRev - PriorRev, PriorRev, 0)
```

### 2.3 Year-to-Date (YTD) Revenue
```dax
Revenue YTD = 
TOTALYTD([Total Revenue], Dim_Date[Date])
```

### 2.4 Same Period Last Year (SPLY) Revenue
```dax
Revenue SPLY = 
CALCULATE(
    [Total Revenue],
    SAMEPERIODLASTYEAR(Dim_Date[Date])
)
```

### 2.5 Year-over-Year (YoY) Revenue Growth %
```dax
Revenue YoY Growth % = 
VAR CurrentRev = [Total Revenue]
VAR PriorYearRev = [Revenue SPLY]
RETURN
    DIVIDE(CurrentRev - PriorYearRev, PriorYearRev, 0)
```

### 2.6 3-Month Moving Average Revenue
```dax
Revenue 3M Moving Avg = 
AVERAGEX(
    DATESINPERIOD(Dim_Date[Date], LASTDATE(Dim_Date[Date]), -3, MONTH),
    [Total Revenue]
)
```

---

## 3. Delivery & Logistics Measures

### 3.1 Average Actual Delivery Days
```dax
Avg Actual Delivery Days = 
AVERAGEX(
    FILTER(fact_orders, fact_orders[order_status] = "delivered" && NOT(ISBLANK(fact_orders[order_delivered_customer_date]))),
    DATEDIFF(fact_orders[order_purchase_timestamp], fact_orders[order_delivered_customer_date], DAY)
)
```

### 3.2 Average Estimated Delivery Days
```dax
Avg Estimated Delivery Days = 
AVERAGEX(
    FILTER(fact_orders, fact_orders[order_status] = "delivered"),
    DATEDIFF(fact_orders[order_purchase_timestamp], fact_orders[order_estimated_delivery_date], DAY)
)
```

### 3.3 Delayed Orders Count
```dax
Delayed Orders = 
CALCULATE(
    COUNTROWS(fact_orders),
    fact_orders[order_status] = "delivered",
    fact_orders[order_delivered_customer_date] > fact_orders[order_estimated_delivery_date]
)
```

### 3.4 Delayed Order Percentage
```dax
Delayed Order % = 
DIVIDE([Delayed Orders], [Total Orders], 0)
```

### 3.5 On-Time Delivery Rate %
```dax
On-Time Delivery Rate % = 
1 - [Delayed Order %]
```

### 3.6 Freight-to-Price Ratio %
```dax
Freight Ratio % = 
DIVIDE([Total Freight], [Merchandise Sales], 0)
```

---

## 4. Customer Intelligence Measures

### 4.1 Total Unique Customers
```dax
Unique Customers = 
CALCULATE(
    DISTINCTCOUNT(dim_customers[customer_unique_id]),
    fact_orders[order_status] = "delivered"
)
```

### 4.2 Repeat Customers Count
```dax
Repeat Customers = 
VAR CustomerOrders = 
    ADDCOLUMNS(
        VALUES(dim_customers[customer_unique_id]),
        "OrderCount", [Total Orders]
    )
RETURN
    COUNTROWS(FILTER(CustomerOrders, [OrderCount] > 1))
```

### 4.3 Repeat Customer Rate %
```dax
Repeat Customer Rate % = 
DIVIDE([Repeat Customers], [Unique Customers], 0)
```

### 4.4 Average Customer Lifetime Spend
```dax
Avg Customer Spend = 
DIVIDE([Total Revenue], [Unique Customers], 0)
```

---

## 5. Customer Satisfaction & Review Measures

### 5.1 Average Customer Review Score
```dax
Avg Review Score = 
AVERAGE(fact_order_reviews[review_score])
```

### 5.2 5-Star Review Percentage
```dax
5-Star Review % = 
DIVIDE(
    CALCULATE(COUNTROWS(fact_order_reviews), fact_order_reviews[review_score] = 5),
    COUNTROWS(fact_order_reviews),
    0
)
```

### 5.3 1-Star Review Percentage
```dax
1-Star Review % = 
DIVIDE(
    CALCULATE(COUNTROWS(fact_order_reviews), fact_order_reviews[review_score] = 1),
    COUNTROWS(fact_order_reviews),
    0
)
```

### 5.4 Net Promoter Score (NPS-Proxy)
```dax
Net Review Score = 
([5-Star Review %] - [1-Star Review %]) * 100
```

---

## 6. Product & Seller Measures

### 6.1 Active Marketplace Sellers
```dax
Active Sellers = 
CALCULATE(
    DISTINCTCOUNT(fact_order_items[seller_id]),
    fact_orders[order_status] = "delivered"
)
```

### 6.2 Seller Late Carrier Dispatch Rate %
```dax
Late Dispatch Rate % = 
VAR LateHandoffs = 
    CALCULATE(
        COUNTROWS(fact_order_items),
        RELATED(fact_orders[order_delivered_carrier_date]) > fact_order_items[shipping_limit_date]
    )
RETURN
    DIVIDE(LateHandoffs, [Total Items Sold], 0)
```
