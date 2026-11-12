"""
Data Cleaning & Transformation Utilities for Olist Dataset.
Author: Aaryaraj Patil
Description:
    Contains modular transformation functions for standardizing strings,
    aggregating geolocation coordinates, translating categories, and handling null values.
"""

import pandas as pd
import numpy as np
from src.logger import setup_logger

logger = setup_logger("data_cleaner")

# Custom category translations not present in raw translation file
CUSTOM_CATEGORY_TRANSLATIONS = {
    "portateis_cozinha_e_preparadores_de_alimentos": "small_appliances_kitchen",
    "pc_gamer": "pc_gamer"
}


def clean_geolocation_data(df_geo: pd.DataFrame) -> pd.DataFrame:
    """
    Deduplicates 1M+ geolocation rows to unique zip_code_prefix records.
    Calculates median latitude/longitude and selects the dominant city/state.
    """
    logger.info(f"Cleaning geolocation records: input shape {df_geo.shape}...")

    # Drop exact duplicates first
    df_clean = df_geo.drop_duplicates()

    # Aggregate coordinates by median
    coords = df_clean.groupby("geolocation_zip_code_prefix").agg({
        "geolocation_lat": "median",
        "geolocation_lng": "median"
    }).reset_index()

    # Determine dominant city and state per zip code
    dominant_location = (
        df_clean.groupby(["geolocation_zip_code_prefix", "geolocation_city", "geolocation_state"])
        .size()
        .reset_index(name="counts")
        .sort_values(["geolocation_zip_code_prefix", "counts"], ascending=[True, False])
        .drop_duplicates(subset=["geolocation_zip_code_prefix"])
        [["geolocation_zip_code_prefix", "geolocation_city", "geolocation_state"]]
    )

    merged = pd.merge(coords, dominant_location, on="geolocation_zip_code_prefix")
    merged.rename(columns={"geolocation_zip_code_prefix": "zip_code_prefix"}, inplace=True)

    # Standardize string fields
    merged["geolocation_city"] = merged["geolocation_city"].str.strip().str.title()
    merged["geolocation_state"] = merged["geolocation_state"].str.strip().str.upper()

    logger.info(f"Geolocation aggregated successfully into {len(merged):,} unique zip codes.")
    return merged


def clean_products_data(df_prod: pd.DataFrame, df_trans: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans products dataset:
    - Merges category translations including missing manual entries
    - Fills missing category values with 'unknown'
    - Standardizes column names
    """
    logger.info(f"Cleaning products dataset: {len(df_prod):,} products...")
    df_prod = df_prod.copy()

    # Build comprehensive translation dictionary
    trans_dict = dict(zip(df_trans["product_category_name"], df_trans["product_category_name_english"]))
    trans_dict.update(CUSTOM_CATEGORY_TRANSLATIONS)

    # Fill null Portuguese category
    df_prod["product_category_name"] = df_prod["product_category_name"].fillna("unknown")

    # Map English category
    df_prod["product_category_name_english"] = df_prod["product_category_name"].map(trans_dict).fillna("unknown")

    # Standardize column naming
    rename_cols = {
        "product_name_lenght": "product_name_length",
        "product_description_lenght": "product_description_length"
    }
    df_prod.rename(columns=rename_cols, inplace=True)

    return df_prod


def clean_orders_data(df_orders: pd.DataFrame) -> pd.DataFrame:
    """
    Converts timestamps to proper datetime format and handles lifecycle statuses.
    """
    logger.info(f"Cleaning orders dataset: {len(df_orders):,} orders...")
    df_orders = df_orders.copy()

    timestamp_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]

    for col in timestamp_cols:
        df_orders[col] = pd.to_datetime(df_orders[col], errors="coerce")

    # Clean status strings
    df_orders["order_status"] = df_orders["order_status"].str.strip().str.lower()
    return df_orders


def clean_customers_data(df_cust: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans customer table: standardizes city names and trims state codes.
    """
    logger.info(f"Cleaning customers: {len(df_cust):,} records...")
    df_cust = df_cust.copy()
    df_cust["customer_city"] = df_cust["customer_city"].str.strip().str.title()
    df_cust["customer_state"] = df_cust["customer_state"].str.strip().str.upper()
    return df_cust


def clean_sellers_data(df_sellers: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans seller table: standardizes city names and trims state codes.
    """
    logger.info(f"Cleaning sellers: {len(df_sellers):,} records...")
    df_sellers = df_sellers.copy()
    df_sellers["seller_city"] = df_sellers["seller_city"].str.strip().str.title()
    df_sellers["seller_state"] = df_sellers["seller_state"].str.strip().str.upper()
    return df_sellers


def clean_order_items_data(df_items: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans order items and converts shipping limit date.
    """
    logger.info(f"Cleaning order items: {len(df_items):,} records...")
    df_items = df_items.copy()
    df_items["shipping_limit_date"] = pd.to_datetime(df_items["shipping_limit_date"], errors="coerce")
    df_items["price"] = pd.to_numeric(df_items["price"], errors="coerce").fillna(0.0)
    df_items["freight_value"] = pd.to_numeric(df_items["freight_value"], errors="coerce").fillna(0.0)
    return df_items


def clean_order_payments_data(df_payments: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans order payments and fills undefined payment types.
    """
    logger.info(f"Cleaning order payments: {len(df_payments):,} records...")
    df_payments = df_payments.copy()
    df_payments["payment_type"] = df_payments["payment_type"].str.strip().str.lower()
    df_payments.loc[df_payments["payment_type"] == "not_defined", "payment_type"] = "other"
    df_payments["payment_value"] = pd.to_numeric(df_payments["payment_value"], errors="coerce").fillna(0.0)
    return df_payments


def clean_order_reviews_data(df_reviews: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans order reviews: converts timestamps and handles text comments.
    """
    logger.info(f"Cleaning order reviews: {len(df_reviews):,} records...")
    df_reviews = df_reviews.copy()
    df_reviews["review_creation_date"] = pd.to_datetime(df_reviews["review_creation_date"], errors="coerce")
    df_reviews["review_answer_timestamp"] = pd.to_datetime(df_reviews["review_answer_timestamp"], errors="coerce")
    df_reviews["review_score"] = pd.to_numeric(df_reviews["review_score"], errors="coerce").fillna(5).astype(int)
    # Truncate overly long comment titles if necessary
    df_reviews["review_comment_title"] = df_reviews["review_comment_title"].astype(str).str.slice(0, 255)
    df_reviews.loc[df_reviews["review_comment_title"] == "nan", "review_comment_title"] = None
    df_reviews.loc[df_reviews["review_comment_message"] == "nan", "review_comment_message"] = None
    return df_reviews
