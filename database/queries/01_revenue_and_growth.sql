-- ==============================================================================
-- Query Suite 1: Revenue Trends, MoM Growth & Average Order Value (AOV)
-- Database: olist_ecommerce_db
-- Author: Aaryaraj Patil
-- Concepts: CTEs, Window Functions (LAG, SUM OVER), Date Formatting
-- ==============================================================================

USE olist_ecommerce_db;

-- ------------------------------------------------------------------------------
-- 1.1 Monthly Revenue, MoM Growth % and Cumulative Revenue
-- ------------------------------------------------------------------------------
WITH monthly_revenue AS (
    SELECT 
        DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') AS order_month,
        COUNT(DISTINCT o.order_id) AS total_orders,
        COUNT(DISTINCT o.customer_id) AS total_customers,
        ROUND(SUM(oi.price), 2) AS merchandise_revenue,
        ROUND(SUM(oi.freight_value), 2) AS freight_revenue,
        ROUND(SUM(oi.price + oi.freight_value), 2) AS total_gross_revenue,
        ROUND(AVG(oi.price + oi.freight_value), 2) AS avg_item_gross_value
    FROM fact_orders o
    JOIN fact_order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m')
)
SELECT 
    order_month,
    total_orders,
    total_customers,
    total_gross_revenue,
    -- Lagged previous month revenue
    LAG(total_gross_revenue, 1) OVER (ORDER BY order_month) AS prev_month_revenue,
    -- Month-over-Month Revenue Growth Percentage
    ROUND(
        ((total_gross_revenue - LAG(total_gross_revenue, 1) OVER (ORDER BY order_month)) 
        / LAG(total_gross_revenue, 1) OVER (ORDER BY order_month)) * 100, 
        2
    ) AS mom_growth_pct,
    -- Running Cumulative Revenue
    ROUND(SUM(total_gross_revenue) OVER (ORDER BY order_month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS cumulative_revenue
FROM monthly_revenue
ORDER BY order_month;


-- ------------------------------------------------------------------------------
-- 1.2 Average Order Value (AOV) and Basket Size per Order
-- ------------------------------------------------------------------------------
WITH order_basket_summary AS (
    SELECT 
        o.order_id,
        DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') AS order_month,
        COUNT(oi.order_item_id) AS items_in_order,
        SUM(oi.price) AS order_items_price,
        SUM(oi.freight_value) AS order_freight,
        SUM(oi.price + oi.freight_value) AS order_total_value
    FROM fact_orders o
    JOIN fact_order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY o.order_id, DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m')
)
SELECT 
    order_month,
    COUNT(order_id) AS completed_orders,
    ROUND(AVG(items_in_order), 2) AS avg_items_per_order,
    ROUND(AVG(order_total_value), 2) AS average_order_value_aov,
    ROUND(MIN(order_total_value), 2) AS min_order_value,
    ROUND(MAX(order_total_value), 2) AS max_order_value
FROM order_basket_summary
GROUP BY order_month
ORDER BY order_month;
