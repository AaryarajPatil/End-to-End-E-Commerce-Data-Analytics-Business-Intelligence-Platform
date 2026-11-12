-- ==============================================================================
-- Query Suite 3: Product Category Pareto Analysis & Seller Performance Ranking
-- Database: olist_ecommerce_db
-- Author: Aaryaraj Patil
-- Concepts: Pareto 80/20 Rule, Window Sum, Dense Rank, Case Aggregations
-- ==============================================================================

USE olist_ecommerce_db;

-- ------------------------------------------------------------------------------
-- 3.1 Product Category Pareto Analysis (80/20 Revenue Contribution Rule)
-- ------------------------------------------------------------------------------
WITH category_revenue AS (
    SELECT 
        COALESCE(p.product_category_name_english, 'Unknown') AS category_name,
        COUNT(oi.order_item_id) AS items_sold,
        ROUND(SUM(oi.price), 2) AS category_revenue
    FROM fact_order_items oi
    JOIN dim_products p ON oi.product_id = p.product_id
    JOIN fact_orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY COALESCE(p.product_category_name_english, 'Unknown')
),
category_ranking AS (
    SELECT 
        category_name,
        items_sold,
        category_revenue,
        SUM(category_revenue) OVER () AS total_ecommerce_revenue,
        SUM(category_revenue) OVER (ORDER BY category_revenue DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_category_revenue
    FROM category_revenue
)
SELECT 
    category_name,
    items_sold,
    category_revenue,
    ROUND((category_revenue / total_ecommerce_revenue) * 100, 2) AS pct_of_total_revenue,
    ROUND((cumulative_category_revenue / total_ecommerce_revenue) * 100, 2) AS cumulative_revenue_pct,
    CASE 
        WHEN (cumulative_category_revenue / total_ecommerce_revenue) <= 0.80 THEN 'Top 80% Core Driver (Pareto Head)'
        ELSE 'Long Tail Product (Pareto Tail)'
    END AS pareto_classification
FROM category_ranking
ORDER BY category_revenue DESC;


-- ------------------------------------------------------------------------------
-- 3.2 Top Sellers & SLA Fulfillment Performance
-- ------------------------------------------------------------------------------
WITH seller_metrics AS (
    SELECT 
        s.seller_id,
        s.seller_city,
        s.seller_state,
        COUNT(DISTINCT oi.order_id) AS orders_handled,
        COUNT(oi.order_item_id) AS total_items_sold,
        ROUND(SUM(oi.price), 2) AS total_gross_sales,
        ROUND(AVG(r.review_score), 2) AS avg_review_score,
        SUM(CASE WHEN o.order_delivered_carrier_date > oi.shipping_limit_date THEN 1 ELSE 0 END) AS late_dispatches
    FROM dim_sellers s
    JOIN fact_order_items oi ON s.seller_id = oi.seller_id
    JOIN fact_orders o ON oi.order_id = o.order_id
    LEFT JOIN fact_order_reviews r ON oi.order_id = r.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY s.seller_id, s.seller_city, s.seller_state
)
SELECT 
    seller_id,
    seller_city,
    seller_state,
    orders_handled,
    total_items_sold,
    total_gross_sales,
    avg_review_score,
    late_dispatches,
    ROUND((late_dispatches / total_items_sold) * 100, 2) AS late_dispatch_rate_pct,
    DENSE_RANK() OVER (ORDER BY total_gross_sales DESC) AS sales_rank
FROM seller_metrics
WHERE orders_handled >= 10
ORDER BY total_gross_sales DESC
LIMIT 50;
