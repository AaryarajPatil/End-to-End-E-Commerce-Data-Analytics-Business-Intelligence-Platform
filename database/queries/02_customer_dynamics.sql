-- ==============================================================================
-- Query Suite 2: Customer Retention, Repeat Purchases & RFM Segmentation
-- Database: olist_ecommerce_db
-- Author: Aaryaraj Patil
-- Concepts: Multi-table CTEs, Window Functions (ROW_NUMBER, NTILE, LAG)
-- ==============================================================================

USE olist_ecommerce_db;

-- ------------------------------------------------------------------------------
-- 2.1 Customer Purchase Frequency Distribution & Repeat Buyer Rate
-- ------------------------------------------------------------------------------
WITH customer_order_counts AS (
    SELECT 
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS order_count,
        ROUND(SUM(p.payment_value), 2) AS lifetime_spend
    FROM dim_customers c
    JOIN fact_orders o ON c.customer_id = o.customer_id
    JOIN fact_order_payments p ON o.order_id = p.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
)
SELECT 
    CASE 
        WHEN order_count = 1 THEN '1 Order (One-Time Buyer)'
        WHEN order_count = 2 THEN '2 Orders (Repeat Buyer)'
        WHEN order_count BETWEEN 3 AND 5 THEN '3-5 Orders (Loyal Buyer)'
        ELSE '6+ Orders (VIP Power Buyer)'
    END AS customer_segment,
    COUNT(customer_unique_id) AS total_customers,
    ROUND(COUNT(customer_unique_id) / (SELECT COUNT(*) FROM customer_order_counts) * 100, 2) AS pct_of_customer_base,
    ROUND(SUM(lifetime_spend), 2) AS total_revenue_generated,
    ROUND(AVG(lifetime_spend), 2) AS avg_revenue_per_customer
FROM customer_order_counts
GROUP BY 
    CASE 
        WHEN order_count = 1 THEN '1 Order (One-Time Buyer)'
        WHEN order_count = 2 THEN '2 Orders (Repeat Buyer)'
        WHEN order_count BETWEEN 3 AND 5 THEN '3-5 Orders (Loyal Buyer)'
        ELSE '6+ Orders (VIP Power Buyer)'
    END
ORDER BY total_customers DESC;


-- ------------------------------------------------------------------------------
-- 2.2 Time to Second Purchase (Days Between Consecutive Orders)
-- ------------------------------------------------------------------------------
WITH ordered_customer_purchases AS (
    SELECT 
        c.customer_unique_id,
        o.order_id,
        o.order_purchase_timestamp,
        ROW_NUMBER() OVER (
            PARTITION BY c.customer_unique_id 
            ORDER BY o.order_purchase_timestamp
        ) AS purchase_sequence,
        LAG(o.order_purchase_timestamp, 1) OVER (
            PARTITION BY c.customer_unique_id 
            ORDER BY o.order_purchase_timestamp
        ) AS previous_purchase_timestamp
    FROM dim_customers c
    JOIN fact_orders o ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
)
SELECT 
    ROUND(AVG(DATEDIFF(order_purchase_timestamp, previous_purchase_timestamp)), 1) AS avg_days_to_second_purchase,
    MIN(DATEDIFF(order_purchase_timestamp, previous_purchase_timestamp)) AS min_days_between_purchases,
    MAX(DATEDIFF(order_purchase_timestamp, previous_purchase_timestamp)) AS max_days_between_purchases,
    COUNT(*) AS total_second_orders
FROM ordered_customer_purchases
WHERE purchase_sequence = 2;


-- ------------------------------------------------------------------------------
-- 2.3 SQL RFM Segmentation (Recency, Frequency, Monetary Score using NTILE)
-- ------------------------------------------------------------------------------
WITH rfm_base AS (
    SELECT 
        c.customer_unique_id,
        DATEDIFF('2018-09-03', MAX(o.order_purchase_timestamp)) AS recency_days,
        COUNT(DISTINCT o.order_id) AS frequency,
        ROUND(SUM(p.payment_value), 2) AS monetary
    FROM dim_customers c
    JOIN fact_orders o ON c.customer_id = o.customer_id
    JOIN fact_order_payments p ON o.order_id = p.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
),
rfm_scores AS (
    SELECT 
        customer_unique_id,
        recency_days,
        frequency,
        monetary,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
    FROM rfm_base
)
SELECT 
    customer_unique_id,
    recency_days,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    CONCAT(r_score, f_score, m_score) AS rfm_combined_score,
    CASE 
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 3 AND f_score < 3 THEN 'Potential Loyalists'
        WHEN r_score < 3 AND f_score >= 3 THEN 'At Risk / Churning'
        WHEN r_score < 2 AND f_score < 2 THEN 'Lost Customers'
        ELSE 'Needs Attention'
    END AS rfm_segment
FROM rfm_scores
LIMIT 100;
