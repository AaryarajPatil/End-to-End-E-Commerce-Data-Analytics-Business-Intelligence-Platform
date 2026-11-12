# Relational Database Schema & Entity-Relationship (ER) Documentation
**Database:** `olist_ecommerce_db` (MySQL 8.0)  
**Author:** Aaryaraj Patil  

---

## 1. Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    DIM_GEOLOCATION ||--o{ DIM_CUSTOMERS : "locates (lookup)"
    DIM_GEOLOCATION ||--o{ DIM_SELLERS : "locates (lookup)"
    DIM_CUSTOMERS ||--o{ FACT_ORDERS : "places (1:N)"
    FACT_ORDERS ||--|{ FACT_ORDER_ITEMS : "contains (1:N)"
    DIM_PRODUCTS ||--o{ FACT_ORDER_ITEMS : "catalogued_in (1:N)"
    DIM_SELLERS ||--o{ FACT_ORDER_ITEMS : "fulfills (1:N)"
    FACT_ORDERS ||--o{ FACT_ORDER_PAYMENTS : "settled_by (1:N)"
    FACT_ORDERS ||--o{ FACT_ORDER_REVIEWS : "reviewed_in (1:N)"

    DIM_GEOLOCATION {
        int zip_code_prefix PK
        decimal geolocation_lat
        decimal geolocation_lng
        string geolocation_city
        string geolocation_state
    }

    DIM_CUSTOMERS {
        string customer_id PK
        string customer_unique_id
        int customer_zip_code_prefix
        string customer_city
        string customer_state
    }

    DIM_SELLERS {
        string seller_id PK
        int seller_zip_code_prefix
        string seller_city
        string seller_state
    }

    DIM_PRODUCTS {
        string product_id PK
        string product_category_name
        string product_category_name_english
        int product_name_length
        int product_description_length
        int product_photos_qty
        decimal product_weight_g
        decimal product_length_cm
        decimal product_height_cm
        decimal product_width_cm
    }

    FACT_ORDERS {
        string order_id PK
        string customer_id FK
        string order_status
        datetime order_purchase_timestamp
        datetime order_approved_at
        datetime order_delivered_carrier_date
        datetime order_delivered_customer_date
        datetime order_estimated_delivery_date
    }

    FACT_ORDER_ITEMS {
        string order_id PK,FK
        int order_item_id PK
        string product_id FK
        string seller_id FK
        datetime shipping_limit_date
        decimal price
        decimal freight_value
    }

    FACT_ORDER_PAYMENTS {
        string order_id PK,FK
        int payment_sequential PK
        string payment_type
        int payment_installments
        decimal payment_value
    }

    FACT_ORDER_REVIEWS {
        int surrogate_review_id PK
        string review_id
        string order_id FK
        int review_score
        string review_comment_title
        text review_comment_message
        datetime review_creation_date
        datetime review_answer_timestamp
    }
```

---

## 2. Table Specifications & Cardinality

### 1. `dim_customers`
- **Primary Key:** `customer_id` (VARCHAR 32)
- **Business Key:** `customer_unique_id` (VARCHAR 32)
- **Indexes:** `idx_cust_unique`, `idx_cust_zip`, `idx_cust_state`
- **Volume:** 99,441 records

### 2. `dim_sellers`
- **Primary Key:** `seller_id` (VARCHAR 32)
- **Indexes:** `idx_seller_zip`, `idx_seller_state`
- **Volume:** 3,095 records

### 3. `dim_products`
- **Primary Key:** `product_id` (VARCHAR 32)
- **Indexes:** `idx_prod_category`
- **Volume:** 32,951 records

### 4. `dim_geolocation`
- **Primary Key:** `zip_code_prefix` (INT)
- **Indexes:** `idx_geo_state`, `idx_geo_city`
- **Aggregation:** 19,015 distinct Brazilian postal prefixes (median centroid coordinates).

### 5. `fact_orders`
- **Primary Key:** `order_id` (VARCHAR 32)
- **Foreign Keys:** `customer_id` -> `dim_customers(customer_id)`
- **Indexes:** `idx_orders_customer`, `idx_orders_status`, `idx_orders_purchase_date`
- **Volume:** 99,441 records

### 6. `fact_order_items`
- **Composite Primary Key:** `(order_id, order_item_id)`
- **Foreign Keys:** 
  - `order_id` -> `fact_orders(order_id)`
  - `product_id` -> `dim_products(product_id)`
  - `seller_id` -> `dim_sellers(seller_id)`
- **Volume:** 112,650 records

### 7. `fact_order_payments`
- **Composite Primary Key:** `(order_id, payment_sequential)`
- **Foreign Keys:** `order_id` -> `fact_orders(order_id)`
- **Volume:** 103,886 records

### 8. `fact_order_reviews`
- **Surrogate Primary Key:** `surrogate_review_id` (INT AUTO_INCREMENT)
- **Foreign Keys:** `order_id` -> `fact_orders(order_id)`
- **Indexes:** `idx_reviews_order`, `idx_reviews_score`, `idx_reviews_review_id`
- **Volume:** 99,224 records
