"""
Olist Dataset Profiling & Verification Script
Author: Aaryaraj Patil
Description:
    Inspects all nine Olist CSV files, computes row counts, null counts,
    duplicate rates, data types, and checks referential integrity across foreign keys.
"""

import os
import glob
import pandas as pd


def profile_datasets(data_dir: str):
    """
    Scans the given directory for CSV files and outputs a detailed profile
    for each dataset including missing values, duplicates, and data types.
    """
    csv_files = sorted(glob.glob(os.path.join(data_dir, "*.csv")))
    if not csv_files:
        print(f"[!] No CSV files found in {data_dir}")
        return

    print("=" * 80)
    print(f"OLIST DATASET PROFILING REPORT - FOUND {len(csv_files)} DATASETS")
    print("=" * 80)

    summary_list = []

    for file_path in csv_files:
        file_name = os.path.basename(file_path)
        df = pd.read_csv(file_path)
        row_count, col_count = df.shape
        dup_count = df.duplicated().sum()
        null_total = df.isnull().sum().sum()

        summary_list.append({
            "File": file_name,
            "Rows": f"{row_count:,}",
            "Cols": col_count,
            "Total Nulls": f"{null_total:,}",
            "Duplicate Rows": f"{dup_count:,}"
        })

        print(f"\n[FILE]: {file_name}")
        print(f"  Shape: {row_count:,} rows x {col_count} columns | Duplicates: {dup_count:,}")
        print("  Column Analysis:")
        null_series = df.isnull().sum()
        for col in df.columns:
            null_cnt = null_series[col]
            null_pct = (null_cnt / row_count) * 100 if row_count > 0 else 0
            n_unique = df[col].nunique()
            dtype = str(df[col].dtype)
            print(f"    - {col:35s} | Type: {dtype:8s} | Nulls: {null_cnt:6d} ({null_pct:5.2f}%) | Unique: {n_unique:6d}")

    summary_df = pd.DataFrame(summary_list)
    print("\n" + "=" * 80)
    print("EXECUTIVE SUMMARY TABLE")
    print("=" * 80)
    print(summary_df.to_string(index=False))


def check_referential_integrity(data_dir: str):
    """
    Validates foreign key relationships between the raw tables.
    """
    print("\n" + "=" * 80)
    print("REFERENTIAL INTEGRITY CHECKS")
    print("=" * 80)

    orders = pd.read_csv(os.path.join(data_dir, "olist_orders_dataset.csv"))
    items = pd.read_csv(os.path.join(data_dir, "olist_order_items_dataset.csv"))
    cust = pd.read_csv(os.path.join(data_dir, "olist_customers_dataset.csv"))
    sellers = pd.read_csv(os.path.join(data_dir, "olist_sellers_dataset.csv"))
    products = pd.read_csv(os.path.join(data_dir, "olist_products_dataset.csv"))
    reviews = pd.read_csv(os.path.join(data_dir, "olist_order_reviews_dataset.csv"))
    payments = pd.read_csv(os.path.join(data_dir, "olist_order_payments_dataset.csv"))
    translation = pd.read_csv(os.path.join(data_dir, "product_category_name_translation.csv"))

    # Orders -> Customers
    missing_cust = set(orders['customer_id']) - set(cust['customer_id'])
    print(f"[*] orders.customer_id -> customers.customer_id : {len(missing_cust)} unmatched")

    # Order Items -> Orders
    missing_items_orders = set(items['order_id']) - set(orders['order_id'])
    print(f"[*] order_items.order_id -> orders.order_id     : {len(missing_items_orders)} unmatched")

    # Order Items -> Products
    missing_items_prod = set(items['product_id']) - set(products['product_id'])
    print(f"[*] order_items.product_id -> products.product_id : {len(missing_items_prod)} unmatched")

    # Order Items -> Sellers
    missing_items_sellers = set(items['seller_id']) - set(sellers['seller_id'])
    print(f"[*] order_items.seller_id -> sellers.seller_id   : {len(missing_items_sellers)} unmatched")

    # Payments -> Orders
    missing_payments_orders = set(payments['order_id']) - set(orders['order_id'])
    print(f"[*] payments.order_id -> orders.order_id        : {len(missing_payments_orders)} unmatched")

    # Reviews -> Orders
    missing_reviews_orders = set(reviews['order_id']) - set(orders['order_id'])
    print(f"[*] reviews.order_id -> orders.order_id         : {len(missing_reviews_orders)} unmatched")

    # Category translations
    missing_trans = set(products['product_category_name'].dropna()) - set(translation['product_category_name'].dropna())
    print(f"[*] products.category -> translation.category    : {len(missing_trans)} untranslated categories ({missing_trans})")
    print("=" * 80)


if __name__ == "__main__":
    default_dir = os.path.join("data", "Brazilian E-Commerce Public Dataset by Olist")
    if not os.path.exists(default_dir):
        print(f"[!] Path not found: {default_dir}")
    else:
        profile_datasets(default_dir)
        check_referential_integrity(default_dir)
