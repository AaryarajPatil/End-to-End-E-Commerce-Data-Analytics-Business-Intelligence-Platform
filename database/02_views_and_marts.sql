-- ==============================================================================
-- Project: End-to-End E-Commerce Data Analytics Platform (Olist)
-- File: database/02_views_and_marts.sql
-- Description: Analytical views and summarized data marts for Power BI & SQL reporting.
-- Author: Aaryaraj Patil
-- ==============================================================================

USE olist_ecommerce_db;

-- ------------------------------------------------------------------------------
-- 1. VIEW: vw_order_summary
-- Aggregates item and payment metrics at the single order grain.
-- ------------------------------------------------------------------------------
DROP VIEW IF EXISTS vw_order_summary;
CREATE VIEW vw_order_summary AS
SELECT 
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    o.order_status,
    o.order_purchase_timestamp,
    DATE(o.order_purchase_timestamp) AS order_date,
    DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m-01') AS order_month,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp) AS actual_delivery_days,
    DATEDIFF(o.order_estimated_delivery_date, o.order_purchase_timestamp) AS estimated_delivery_days,
    CASE 
        WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 
        ELSE 0 
    END AS is_delayed,
    COALESCE(i.total_items, 0) AS total_items,
    COALESCE(i.total_item_value, 0.0) AS total_item_value,
    COALESCE(i.total_freight_value, 0.0) AS total_freight_value,
    COALESCE(i.total_item_value + i.total_freight_value, 0.0) AS total_order_value,
    COALESCE(p.total_payment_value, 0.0) AS total_payment_value,
    r.avg_review_score
FROM fact_orders o
JOIN dim_customers c ON o.customer_id = c.customer_id
LEFT JOIN (
    SELECT 
        order_id,
        COUNT(order_item_id) AS total_items,
        SUM(price) AS total_item_value,
        SUM(freight_value) AS total_freight_value
    FROM fact_order_items
    GROUP BY order_id
) i ON o.order_id = i.order_id
LEFT JOIN (
    SELECT 
        order_id,
        SUM(payment_value) AS total_payment_value
    FROM fact_order_payments
    GROUP BY order_id
) p ON o.order_id = p.order_id
LEFT JOIN (
    SELECT 
        order_id,
        AVG(review_score) AS avg_review_score
    FROM fact_order_reviews
    GROUP BY order_id
) r ON o.order_id = r.order_id;

-- ------------------------------------------------------------------------------
-- 2. VIEW: vw_monthly_sales_kpi
-- Monthly GMV, order volume, average order value, and on-time delivery rate.
-- ------------------------------------------------------------------------------
DROP VIEW IF EXISTS vw_monthly_sales_kpi;
CREATE VIEW vw_monthly_sales_kpi AS
SELECT 
    DATE_FORMAT(order_purchase_timestamp, '%Y-%m') AS year_month,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_unique_id) AS total_unique_customers,
    SUM(total_order_value) AS gross_merchandise_value,
    ROUND(AVG(total_order_value), 2) AS average_order_value,
    ROUND(SUM(total_freight_value), 2) AS total_freight_revenue,
    ROUND(AVG(actual_delivery_days), 1) AS avg_delivery_days,
    ROUND(SUM(is_delayed) / COUNT(order_id) * 100, 2) AS delayed_order_percentage,
    ROUND(AVG(avg_review_score), 2) AS avg_monthly_review_score
FROM vw_order_summary
WHERE order_status = 'delivered'
GROUP BY DATE_FORMAT(order_purchase_timestamp, '%Y-%m');

-- ------------------------------------------------------------------------------
-- 3. VIEW: vw_product_category_performance
-- Category-level sales, item count, revenue share, and average review score.
-- ------------------------------------------------------------------------------
DROP VIEW IF EXISTS vw_product_category_performance;
CREATE VIEW vw_product_category_performance AS
SELECT 
    COALESCE(p.product_category_name_english, 'Unknown') AS category_name,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    COUNT(oi.order_item_id) AS total_items_sold,
    ROUND(SUM(oi.price), 2) AS total_revenue,
    ROUND(AVG(oi.price), 2) AS avg_item_price,
    ROUND(AVG(oi.freight_value), 2) AS avg_freight_per_item,
    ROUND(AVG(r.review_score), 2) AS avg_category_review_score
FROM fact_order_items oi
JOIN dim_products p ON oi.product_id = p.product_id
JOIN fact_orders o ON oi.order_id = o.order_id
LEFT JOIN fact_order_reviews r ON oi.order_id = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY COALESCE(p.product_category_name_english, 'Unknown');

-- ------------------------------------------------------------------------------
-- 4. VIEW: vw_seller_performance
-- Seller fulfillment metrics, total revenue generated, and ratings.
-- ------------------------------------------------------------------------------
DROP VIEW IF EXISTS vw_seller_performance;
CREATE VIEW vw_seller_performance AS
SELECT 
    s.seller_id,
    s.seller_city,
    s.seller_state,
    COUNT(DISTINCT oi.order_id) AS orders_fulfilled,
    COUNT(oi.order_item_id) AS total_units_sold,
    ROUND(SUM(oi.price), 2) AS total_revenue,
    ROUND(AVG(oi.price), 2) AS average_selling_price,
    ROUND(AVG(r.review_score), 2) AS avg_seller_rating,
    SUM(CASE WHEN o.order_delivered_carrier_date > oi.shipping_limit_date THEN 1 ELSE 0 END) AS late_carrier_handoffs
FROM dim_sellers s
JOIN fact_order_items oi ON s.seller_id = oi.seller_id
JOIN fact_orders o ON oi.order_id = o.order_id
LEFT JOIN fact_order_reviews r ON oi.order_id = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY s.seller_id, s.seller_city, s.seller_state;

-- ------------------------------------------------------------------------------
-- 5. VIEW: vw_customer_rfm_source
-- Source features for Recency, Frequency, and Monetary calculation.
-- ------------------------------------------------------------------------------
DROP VIEW IF EXISTS vw_customer_rfm_source;
CREATE VIEW vw_customer_rfm_source AS
SELECT 
    c.customer_unique_id,
    MAX(o.order_purchase_timestamp) AS latest_order_date,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(p.payment_value), 2) AS total_spend,
    c.customer_state,
    c.customer_city
FROM dim_customers c
JOIN fact_orders o ON c.customer_id = o.customer_id
JOIN fact_order_payments p ON o.order_id = p.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_unique_id, c.customer_state, c.customer_city;
