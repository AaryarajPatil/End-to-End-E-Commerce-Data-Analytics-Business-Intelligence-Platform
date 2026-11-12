-- ==============================================================================
-- Query Suite 5: Payment Installment Behaviors & Review Score Impact Analysis
-- Database: olist_ecommerce_db
-- Author: Aaryaraj Patil
-- Concepts: Grouping, Multi-Table Correlations, Aggregate Filtering
-- ==============================================================================

USE olist_ecommerce_db;

-- ------------------------------------------------------------------------------
-- 5.1 Payment Method Market Share, Average Installments & Total Volume
-- ------------------------------------------------------------------------------
SELECT 
    payment_type,
    COUNT(order_id) AS transaction_count,
    ROUND(COUNT(order_id) / (SELECT COUNT(*) FROM fact_order_payments) * 100, 2) AS transaction_share_pct,
    ROUND(SUM(payment_value), 2) AS total_payment_value,
    ROUND((SUM(payment_value) / (SELECT SUM(payment_value) FROM fact_order_payments)) * 100, 2) AS value_share_pct,
    ROUND(AVG(payment_value), 2) AS avg_transaction_value,
    ROUND(AVG(payment_installments), 1) AS avg_installments
FROM fact_order_payments
GROUP BY payment_type
ORDER BY total_payment_value DESC;


-- ------------------------------------------------------------------------------
-- 5.2 Direct Impact of Delivery Delay on Customer Review Scores
-- ------------------------------------------------------------------------------
WITH order_delivery_status AS (
    SELECT 
        o.order_id,
        r.review_score,
        CASE 
            WHEN o.order_delivered_customer_date IS NULL THEN 'Undelivered / In-Transit'
            WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date THEN 'Delivered On-Time or Early'
            ELSE 'Delivered Late (Delayed)'
        END AS delivery_punctuality
    FROM fact_orders o
    JOIN fact_order_reviews r ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
)
SELECT 
    delivery_punctuality,
    COUNT(order_id) AS total_reviews,
    ROUND(AVG(review_score), 2) AS average_review_score,
    SUM(CASE WHEN review_score = 5 THEN 1 ELSE 0 END) AS five_star_reviews,
    ROUND(SUM(CASE WHEN review_score = 5 THEN 1 ELSE 0 END) / COUNT(order_id) * 100, 2) AS five_star_rate_pct,
    SUM(CASE WHEN review_score = 1 THEN 1 ELSE 0 END) AS one_star_reviews,
    ROUND(SUM(CASE WHEN review_score = 1 THEN 1 ELSE 0 END) / COUNT(order_id) * 100, 2) AS one_star_rate_pct
FROM order_delivery_status
GROUP BY delivery_punctuality;


-- ------------------------------------------------------------------------------
-- 5.3 Installment Preference by Order Value Tier (Credit Card Orders)
-- ------------------------------------------------------------------------------
WITH order_tiers AS (
    SELECT 
        order_id,
        payment_installments,
        payment_value,
        CASE 
            WHEN payment_value < 50 THEN 'Low Ticket (< R$50)'
            WHEN payment_value BETWEEN 50 AND 150 THEN 'Medium Ticket (R$50 - R$150)'
            WHEN payment_value BETWEEN 150.01 AND 500 THEN 'High Ticket (R$150 - R$500)'
            ELSE 'Premium Ticket (> R$500)'
        END AS order_value_tier
    FROM fact_order_payments
    WHERE payment_type = 'credit_card'
)
SELECT 
    order_value_tier,
    COUNT(order_id) AS total_orders,
    ROUND(AVG(payment_installments), 1) AS avg_installments,
    ROUND(AVG(payment_value), 2) AS avg_order_value,
    SUM(CASE WHEN payment_installments > 6 THEN 1 ELSE 0 END) AS orders_over_6_installments,
    ROUND(SUM(CASE WHEN payment_installments > 6 THEN 1 ELSE 0 END) / COUNT(order_id) * 100, 2) AS pct_over_6_installments
FROM order_tiers
GROUP BY order_value_tier
ORDER BY avg_order_value ASC;
