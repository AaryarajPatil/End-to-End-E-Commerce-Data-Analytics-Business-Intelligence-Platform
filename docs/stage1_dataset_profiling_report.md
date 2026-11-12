# Stage 1: Dataset Profiling & Verification Report
**Project:** End-to-End Brazilian E-Commerce Analytics & BI Platform (Olist)  
**Author:** Aaryaraj Patil  
**Date:** November 2026  

---

## 1. Executive Summary

The Brazilian E-Commerce Public Dataset provided by Olist contains information on **99,441 unique orders** placed between September 2016 and September 2018 across multiple marketplaces in Brazil. The data consists of **9 relational CSV files** capturing orders, order items, customer demographics, payments, product descriptions, seller data, customer reviews, category translations, and Brazilian geolocation points.

### File-Level Inventory & Metric Overview

| File Name | Records | Columns | Null Values | Duplicates | Key Candidate |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `olist_customers_dataset.csv` | 99,441 | 5 | 0 | 0 | `customer_id` (PK) |
| `olist_orders_dataset.csv` | 99,441 | 8 | 4,908 | 0 | `order_id` (PK) |
| `olist_order_items_dataset.csv` | 112,650 | 7 | 0 | 0 | `(order_id, order_item_id)` (Composite PK) |
| `olist_order_payments_dataset.csv` | 103,886 | 5 | 0 | 0 | `(order_id, payment_sequential)` (Composite PK) |
| `olist_order_reviews_dataset.csv` | 99,224 | 7 | 145,903 | 0 | `(review_id, order_id)` (Composite PK) |
| `olist_products_dataset.csv` | 32,951 | 9 | 2,448 | 0 | `product_id` (PK) |
| `olist_sellers_dataset.csv` | 3,095 | 4 | 0 | 0 | `seller_id` (PK) |
| `product_category_name_translation.csv` | 71 | 2 | 0 | 0 | `product_category_name` (PK) |
| `olist_geolocation_dataset.csv` | 1,000,163 | 5 | 0 | 261,831 | `geolocation_zip_code_prefix` (Lookup Dimension) |

---

## 2. In-Depth Table Analysis

### 2.1 Customers (`olist_customers_dataset.csv`)
- **Cardinality:** 99,441 rows.
- **Attributes:**
  - `customer_id` (VARCHAR 32): Unique key assigned per order transaction.
  - `customer_unique_id` (VARCHAR 32): Identifier representing the actual human individual (96,096 unique values).
  - `customer_zip_code_prefix` (INT): First 5 digits of Brazilian CEP.
  - `customer_city` (VARCHAR): City of residence (4,119 unique cities).
  - `customer_state` (VARCHAR 2): 27 Brazilian federal states/territories.
- **Data Engineering Takeaway:** To calculate customer retention, repeat purchase behavior, and RFM, analysts must group by `customer_unique_id`, not `customer_id`.

### 2.2 Orders (`olist_orders_dataset.csv`)
- **Cardinality:** 99,441 rows.
- **Status Breakdown:**
  - `delivered`: 96,478 (97.02%)
  - `shipped`: 1,107 (1.11%)
  - `canceled`: 625 (0.63%)
  - `unavailable`: 609 (0.61%)
  - `invoiced`: 314 (0.32%)
  - `processing`: 301 (0.30%)
  - `created`: 5 (0.01%)
  - `approved`: 2 (<0.01%)
- **Missing Value Context:**
  - `order_approved_at`: 160 missing (orders canceled or never confirmed).
  - `order_delivered_carrier_date`: 1,783 missing (orders canceled or in preparation).
  - `order_delivered_customer_date`: 2,965 missing (undelivered or in-transit orders).
- **Engineering Rule:** These nulls reflect real-world order lifecycle states; they should **never** be imputed with arbitrary fake dates.

### 2.3 Order Items (`olist_order_items_dataset.csv`)
- **Cardinality:** 112,650 rows across 98,666 distinct orders.
- **Attributes:**
  - `order_id`: References `orders.order_id`.
  - `order_item_id`: Sequential line item number within the order (1 to 21).
  - `product_id`: References `products.product_id`.
  - `seller_id`: References `sellers.seller_id`.
  - `shipping_limit_date`: Seller fulfillment SLA deadline.
  - `price`: Unit price of item in BRL (R$).
  - `freight_value`: Item-level shipping charge in BRL (R$).
- **Multi-Item Dynamics:** 112,650 items / 98,666 orders = ~1.14 items per order. 775 orders in `olist_orders_dataset.csv` have zero items because the customer canceled before item assignment.

### 2.4 Order Payments (`olist_order_payments_dataset.csv`)
- **Cardinality:** 103,886 payment transactions.
- **Payment Types:** `credit_card` (76,784), `boleto` (19,784), `voucher` (5,775), `debit_card` (1,529), `not_defined` (3).
- **Split Payments:** Customers frequently combine vouchers with credit cards or split payments over up to 24 monthly installments.

### 2.5 Order Reviews (`olist_order_reviews_dataset.csv`)
- **Cardinality:** 99,224 reviews.
- **Scores:** 1 to 5 integer rating.
  - 5 stars: ~57.8%
  - 4 stars: ~19.3%
  - 1 star: ~11.9%
  - 3 stars: ~8.2%
  - 2 stars: ~3.2%
- **Text Comments:** 88.34% of titles and 58.70% of messages are null, meaning customers predominantly express satisfaction via the star rating unless filing a specific complaint.

### 2.6 Products (`olist_products_dataset.csv`)
- **Cardinality:** 32,951 products.
- **Missing Values:** 610 products lack category and description length. 2 products lack weight and dimensions.
- **Category Inconsistencies:** 73 distinct Portuguese categories exist, but the official translation file covers only 71.
  - Missing translations: `portateis_cozinha_e_preparadores_de_alimentos` and `pc_gamer`.

### 2.7 Sellers (`olist_sellers_dataset.csv`)
- **Cardinality:** 3,095 sellers across 23 Brazilian states.
- 0 missing values, 0 duplicate rows.

### 2.8 Geolocation (`olist_geolocation_dataset.csv`)
- **Cardinality:** 1,000,163 records.
- **Duplicates:** 261,831 exact duplicate rows.
- **Many-to-One Prefix Mapping:** Multiple coordinates exist for a single `geolocation_zip_code_prefix` due to different street-level readings.
- **Missing Coverage:** 157 customer zip codes and 7 seller zip codes are missing from the raw geolocation table.

---

## 3. Referential Integrity Audit

Our programmatic integrity scan revealed:
1. **100% Match:** All `order_items.order_id` exist in `orders.order_id`.
2. **100% Match:** All `order_items.product_id` exist in `products.product_id`.
3. **100% Match:** All `order_items.seller_id` exist in `sellers.seller_id`.
4. **100% Match:** All `orders.customer_id` exist in `customers.customer_id`.
5. **100% Match:** All `payments.order_id` exist in `orders.order_id`.
6. **100% Match:** All `reviews.order_id` exist in `orders.order_id`.

---

## 4. Key Recommendations for Database & Pipeline Engineering

1. **Geolocation Consolidation:** Group raw geolocation data by `geolocation_zip_code_prefix` calculating median latitude and longitude and selecting the dominant city and state.
2. **Category Standardization:** Impute null categories as `'unknown'` and inject translations for `pc_gamer` and `portateis_cozinha_e_preparadores_de_alimentos`.
3. **Review De-duplication:** Some review records share identical `review_id` across different orders or items; generate an auto-incrementing surrogate primary key (`surrogate_review_id`) to ensure unique constraints are strictly honored.
