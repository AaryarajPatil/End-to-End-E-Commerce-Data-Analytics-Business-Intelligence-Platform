-- ==============================================================================
-- Query Suite 4: Logistics Bottlenecks, Delivery Delays & Regional Freight Costs
-- Database: olist_ecommerce_db
-- Author: Aaryaraj Patil
-- Concepts: Multi-table Joins, Date Arithmetic, Conditional Flagging
-- ==============================================================================

USE olist_ecommerce_db;

-- ------------------------------------------------------------------------------
-- 4.1 State-Level Delivery Performance & Delay Risk Heatmap
-- ------------------------------------------------------------------------------
SELECT 
    c.customer_state,
    COUNT(o.order_id) AS total_delivered_orders,
    ROUND(AVG(DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp)), 1) AS avg_actual_delivery_days,
    ROUND(AVG(DATEDIFF(o.order_estimated_delivery_date, o.order_purchase_timestamp)), 1) AS avg_estimated_delivery_days,
    ROUND(AVG(DATEDIFF(o.order_delivered_customer_date, o.order_estimated_delivery_date)), 1) AS avg_delay_variance_days,
    SUM(CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 ELSE 0 END) AS delayed_orders_count,
    ROUND(
        (SUM(CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 ELSE 0 END) / COUNT(o.order_id)) * 100, 
        2
    ) AS delayed_order_percentage
FROM fact_orders o
JOIN dim_customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
GROUP BY c.customer_state
ORDER BY delayed_order_percentage DESC;


-- ------------------------------------------------------------------------------
-- 4.2 Logistics Breakdown: Seller Processing Time vs Carrier Transit Time
-- ------------------------------------------------------------------------------
SELECT 
    DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') AS order_month,
    COUNT(o.order_id) AS orders_analyzed,
    -- Seller preparation days (Approval to Carrier handoff)
    ROUND(AVG(TIMESTAMPDIFF(HOUR, o.order_approved_at, o.order_delivered_carrier_date) / 24.0), 1) AS avg_seller_handling_days,
    -- Carrier transit days (Carrier handoff to Customer delivery)
    ROUND(AVG(TIMESTAMPDIFF(HOUR, o.order_delivered_carrier_date, o.order_delivered_customer_date) / 24.0), 1) AS avg_carrier_transit_days,
    -- Total end-to-end days
    ROUND(AVG(TIMESTAMPDIFF(HOUR, o.order_purchase_timestamp, o.order_delivered_customer_date) / 24.0), 1) AS avg_total_delivery_days
FROM fact_orders o
WHERE o.order_status = 'delivered'
  AND o.order_approved_at IS NOT NULL
  AND o.order_delivered_carrier_date IS NOT NULL
  AND o.order_delivered_customer_date IS NOT NULL
GROUP BY DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m')
ORDER BY order_month;


-- ------------------------------------------------------------------------------
-- 4.3 Freight Cost Burden as % of Product Value Across Brazilian Regions
-- ------------------------------------------------------------------------------
SELECT 
    c.customer_state,
    ROUND(AVG(oi.price), 2) AS avg_product_price,
    ROUND(AVG(oi.freight_value), 2) AS avg_freight_value,
    ROUND((SUM(oi.freight_value) / SUM(oi.price)) * 100, 2) AS freight_to_price_ratio_pct,
    ROUND(AVG(r.review_score), 2) AS avg_review_score
FROM fact_order_items oi
JOIN fact_orders o ON oi.order_id = o.order_id
JOIN dim_customers c ON o.customer_id = c.customer_id
LEFT JOIN fact_order_reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY freight_to_price_ratio_pct DESC;
