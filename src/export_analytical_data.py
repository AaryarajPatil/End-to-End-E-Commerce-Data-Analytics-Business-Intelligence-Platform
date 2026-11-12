"""
Curated Data Export Utility for Power BI & Offline Analytics.
Author: Aaryaraj Patil
Description:
    Exports cleaned dimension and fact tables to curated CSV/Parquet formats
    for immediate drag-and-drop loading into Power BI Desktop or Tableau.
"""

import os
from pathlib import Path
from src.config import DATA_DIR, PROJECT_ROOT
from src.logger import setup_logger
from src.data_cleaner import (
    clean_geolocation_data,
    clean_products_data,
    clean_orders_data,
    clean_customers_data,
    clean_sellers_data,
    clean_order_items_data,
    clean_order_payments_data,
    clean_order_reviews_data,
)
import pandas as pd

logger = setup_logger("export_analytical_data")


def export_curated_datasets(output_dir: str = None):
    """
    Transforms raw datasets and exports cleaned tables into the designated output directory.
    """
    out_path = Path(output_dir) if output_dir else PROJECT_ROOT / "data" / "curated"
    out_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Exporting curated analytical tables to: {out_path}...")

    # Load raw
    raw_customers = pd.read_csv(os.path.join(DATA_DIR, "olist_customers_dataset.csv"))
    raw_geo = pd.read_csv(os.path.join(DATA_DIR, "olist_geolocation_dataset.csv"))
    raw_orders = pd.read_csv(os.path.join(DATA_DIR, "olist_orders_dataset.csv"))
    raw_items = pd.read_csv(os.path.join(DATA_DIR, "olist_order_items_dataset.csv"))
    raw_payments = pd.read_csv(os.path.join(DATA_DIR, "olist_order_payments_dataset.csv"))
    raw_reviews = pd.read_csv(os.path.join(DATA_DIR, "olist_order_reviews_dataset.csv"))
    raw_products = pd.read_csv(os.path.join(DATA_DIR, "olist_products_dataset.csv"))
    raw_sellers = pd.read_csv(os.path.join(DATA_DIR, "olist_sellers_dataset.csv"))
    raw_trans = pd.read_csv(os.path.join(DATA_DIR, "product_category_name_translation.csv"))

    # Clean
    tables = {
        "dim_geolocation": clean_geolocation_data(raw_geo),
        "dim_customers": clean_customers_data(raw_customers),
        "dim_sellers": clean_sellers_data(raw_sellers),
        "dim_products": clean_products_data(raw_products, raw_trans),
        "fact_orders": clean_orders_data(raw_orders),
        "fact_order_items": clean_order_items_data(raw_items),
        "fact_order_payments": clean_order_payments_data(raw_payments),
        "fact_order_reviews": clean_order_reviews_data(raw_reviews)
    }

    # Save to curated directory
    for name, df in tables.items():
        csv_file = out_path / f"{name}.csv"
        df.to_csv(csv_file, index=False)
        logger.info(f"Saved `{name}` -> {csv_file} ({len(df):,} rows)")

    logger.info("All curated datasets exported successfully.")


if __name__ == "__main__":
    export_curated_datasets()
