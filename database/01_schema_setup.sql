-- ==============================================================================
-- Project: End-to-End E-Commerce Data Analytics Platform (Olist)
-- File: database/01_schema_setup.sql
-- Description: Creates the normalized relational schema (Star/Snowflake hybrid),
--              table definitions, primary keys, foreign keys, and indexes.
-- Author: Aaryaraj Patil
-- ==============================================================================

-- Create database with modern UTF-8 support
CREATE DATABASE IF NOT EXISTS olist_ecommerce_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE olist_ecommerce_db;

-- ------------------------------------------------------------------------------
-- 1. DIMENSION TABLE: dim_geolocation
-- Aggregated to the zip-code prefix level to avoid Cartesian product joins.
-- ------------------------------------------------------------------------------
DROP TABLE IF EXISTS dim_geolocation;
CREATE TABLE dim_geolocation (
    zip_code_prefix INT NOT NULL,
    geolocation_lat DECIMAL(10, 8) NULL,
    geolocation_lng DECIMAL(11, 8) NULL,
    geolocation_city VARCHAR(100) NOT NULL,
    geolocation_state CHAR(2) NOT NULL,
    PRIMARY KEY (zip_code_prefix),
    INDEX idx_geo_state (geolocation_state),
    INDEX idx_geo_city (geolocation_city)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------------------------
-- 2. DIMENSION TABLE: dim_customers
-- Captures both transaction-level customer_id and real person customer_unique_id.
-- ------------------------------------------------------------------------------
DROP TABLE IF EXISTS dim_customers;
CREATE TABLE dim_customers (
    customer_id VARCHAR(32) NOT NULL,
    customer_unique_id VARCHAR(32) NOT NULL,
    customer_zip_code_prefix INT NOT NULL,
    customer_city VARCHAR(100) NOT NULL,
    customer_state CHAR(2) NOT NULL,
    PRIMARY KEY (customer_id),
    INDEX idx_cust_unique (customer_unique_id),
    INDEX idx_cust_zip (customer_zip_code_prefix),
    INDEX idx_cust_state (customer_state)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------------------------
-- 3. DIMENSION TABLE: dim_sellers
-- Information about merchants and marketplace sellers.
-- ------------------------------------------------------------------------------
DROP TABLE IF EXISTS dim_sellers;
CREATE TABLE dim_sellers (
    seller_id VARCHAR(32) NOT NULL,
    seller_zip_code_prefix INT NOT NULL,
    seller_city VARCHAR(100) NOT NULL,
    seller_state CHAR(2) NOT NULL,
    PRIMARY KEY (seller_id),
    INDEX idx_seller_zip (seller_zip_code_prefix),
    INDEX idx_seller_state (seller_state)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------------------------
-- 4. DIMENSION TABLE: dim_products
-- Product catalog enriched with translated English category names.
-- ------------------------------------------------------------------------------
DROP TABLE IF EXISTS dim_products;
CREATE TABLE dim_products (
    product_id VARCHAR(32) NOT NULL,
    product_category_name VARCHAR(100) NULL,
    product_category_name_english VARCHAR(100) NULL,
    product_name_length INT NULL,
    product_description_length INT NULL,
    product_photos_qty INT NULL,
    product_weight_g DECIMAL(10, 2) NULL,
    product_length_cm DECIMAL(10, 2) NULL,
    product_height_cm DECIMAL(10, 2) NULL,
    product_width_cm DECIMAL(10, 2) NULL,
    PRIMARY KEY (product_id),
    INDEX idx_prod_category (product_category_name_english)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------------------------
-- 5. FACT TABLE: fact_orders
-- Central fact table recording order lifecycle status and timestamps.
-- ------------------------------------------------------------------------------
DROP TABLE IF EXISTS fact_orders;
CREATE TABLE fact_orders (
    order_id VARCHAR(32) NOT NULL,
    customer_id VARCHAR(32) NOT NULL,
    order_status VARCHAR(20) NOT NULL,
    order_purchase_timestamp DATETIME NOT NULL,
    order_approved_at DATETIME NULL,
    order_delivered_carrier_date DATETIME NULL,
    order_delivered_customer_date DATETIME NULL,
    order_estimated_delivery_date DATETIME NOT NULL,
    PRIMARY KEY (order_id),
    INDEX idx_orders_customer (customer_id),
    INDEX idx_orders_status (order_status),
    INDEX idx_orders_purchase_date (order_purchase_timestamp),
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) 
        REFERENCES dim_customers(customer_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------------------------
-- 6. FACT TABLE: fact_order_items
-- Grain: One record per line item ordered.
-- ------------------------------------------------------------------------------
DROP TABLE IF EXISTS fact_order_items;
CREATE TABLE fact_order_items (
    order_id VARCHAR(32) NOT NULL,
    order_item_id INT NOT NULL,
    product_id VARCHAR(32) NOT NULL,
    seller_id VARCHAR(32) NOT NULL,
    shipping_limit_date DATETIME NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    freight_value DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (order_id, order_item_id),
    INDEX idx_items_product (product_id),
    INDEX idx_items_seller (seller_id),
    CONSTRAINT fk_items_order FOREIGN KEY (order_id) 
        REFERENCES fact_orders(order_id) ON DELETE CASCADE,
    CONSTRAINT fk_items_product FOREIGN KEY (product_id) 
        REFERENCES dim_products(product_id),
    CONSTRAINT fk_items_seller FOREIGN KEY (seller_id) 
        REFERENCES dim_sellers(seller_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------------------------
-- 7. FACT TABLE: fact_order_payments
-- Grain: One record per payment transaction / installment split.
-- ------------------------------------------------------------------------------
DROP TABLE IF EXISTS fact_order_payments;
CREATE TABLE fact_order_payments (
    order_id VARCHAR(32) NOT NULL,
    payment_sequential INT NOT NULL,
    payment_type VARCHAR(20) NOT NULL,
    payment_installments INT NOT NULL,
    payment_value DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (order_id, payment_sequential),
    INDEX idx_payments_type (payment_type),
    CONSTRAINT fk_payments_order FOREIGN KEY (order_id) 
        REFERENCES fact_orders(order_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------------------------
-- 8. FACT TABLE: fact_order_reviews
-- Grain: One record per customer review submission.
-- Uses an auto-increment surrogate key to handle duplicated review IDs across orders.
-- ------------------------------------------------------------------------------
DROP TABLE IF EXISTS fact_order_reviews;
CREATE TABLE fact_order_reviews (
    surrogate_review_id INT AUTO_INCREMENT PRIMARY KEY,
    review_id VARCHAR(32) NOT NULL,
    order_id VARCHAR(32) NOT NULL,
    review_score TINYINT NOT NULL,
    review_comment_title VARCHAR(255) NULL,
    review_comment_message TEXT NULL,
    review_creation_date DATETIME NOT NULL,
    review_answer_timestamp DATETIME NOT NULL,
    INDEX idx_reviews_order (order_id),
    INDEX idx_reviews_score (review_score),
    INDEX idx_reviews_review_id (review_id),
    CONSTRAINT fk_reviews_order FOREIGN KEY (order_id) 
        REFERENCES fact_orders(order_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
