"""
Automated End-to-End ETL Pipeline for Olist E-Commerce Platform.
Author: Aaryaraj Patil
Description:
    Extracts raw CSV files, applies transformations, executes SQL DDL schema,
    loads cleaned data into MySQL in dependency order, and verifies data integrity.
"""

import os
import time
from pathlib import Path
import pandas as pd
from sqlalchemy import text
from src.config import DATA_DIR, BATCH_SIZE, PROJECT_ROOT, DB_NAME
from src.logger import setup_logger
from src.db_connector import get_db_engine
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

logger = setup_logger("etl_pipeline")


class OlistETLPipeline:
    """
    Orchestrates the Extraction, Transformation, and Ingestion of the Olist dataset.
    """

    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or DATA_DIR
        self.engine = get_db_engine()
        self.cleaned_dfs = {}

    def extract(self):
        """
        Step 1: Extract raw CSV files into pandas DataFrames.
        """
        logger.info("=== STEP 1: EXTRACTING RAW CSV FILES ===")
        start_time = time.time()

        files = {
            "customers": "olist_customers_dataset.csv",
            "geolocation": "olist_geolocation_dataset.csv",
            "orders": "olist_orders_dataset.csv",
            "order_items": "olist_order_items_dataset.csv",
            "payments": "olist_order_payments_dataset.csv",
            "reviews": "olist_order_reviews_dataset.csv",
            "products": "olist_products_dataset.csv",
            "sellers": "olist_sellers_dataset.csv",
            "translation": "product_category_name_translation.csv"
        }

        self.raw_dfs = {}
        for key, fname in files.items():
            fpath = os.path.join(self.data_dir, fname)
            if not os.path.exists(fpath):
                raise FileNotFoundError(f"Required raw dataset missing: {fpath}")
            logger.info(f"Loading {fname}...")
            self.raw_dfs[key] = pd.read_csv(fpath)

        logger.info(f"Extraction completed in {time.time() - start_time:.2f} seconds.")

    def transform(self):
        """
        Step 2: Clean, standardize, and transform the extracted data.
        """
        logger.info("=== STEP 2: TRANSFORMING & CLEANING DATASETS ===")
        start_time = time.time()

        self.cleaned_dfs["dim_geolocation"] = clean_geolocation_data(self.raw_dfs["geolocation"])
        self.cleaned_dfs["dim_customers"] = clean_customers_data(self.raw_dfs["customers"])
        self.cleaned_dfs["dim_sellers"] = clean_sellers_data(self.raw_dfs["sellers"])
        self.cleaned_dfs["dim_products"] = clean_products_data(self.raw_dfs["products"], self.raw_dfs["translation"])
        self.cleaned_dfs["fact_orders"] = clean_orders_data(self.raw_dfs["orders"])
        self.cleaned_dfs["fact_order_items"] = clean_order_items_data(self.raw_dfs["order_items"])
        self.cleaned_dfs["fact_order_payments"] = clean_order_payments_data(self.raw_dfs["payments"])
        self.cleaned_dfs["fact_order_reviews"] = clean_order_reviews_data(self.raw_dfs["reviews"])

        logger.info(f"Transformation completed in {time.time() - start_time:.2f} seconds.")

    def setup_database_schema(self):
        """
        Executes the DDL schema file to create tables, keys, and indexes.
        """
        logger.info("=== SETTING UP DATABASE SCHEMA ===")
        server_engine = get_db_engine("")
        with server_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))
            conn.commit()

        schema_file = PROJECT_ROOT / "database" / "01_schema_setup.sql"
        with open(schema_file, "r", encoding="utf-8") as f:
            sql_statements = f.read().split(";")

        with self.engine.connect() as conn:
            for statement in sql_statements:
                cleaned = statement.strip()
                if cleaned:
                    conn.execute(text(cleaned))
            conn.commit()
        logger.info("Database schema setup executed successfully.")

    def load(self):
        """
        Step 3: Load cleaned DataFrames into MySQL tables in relational dependency order.
        """
        logger.info("=== STEP 3: LOADING DATA INTO MYSQL ===")
        start_time = time.time()

        # Ingestion hierarchy: Dimensions first, then Orders, then Items/Payments/Reviews
        load_order = [
            ("dim_geolocation", self.cleaned_dfs["dim_geolocation"]),
            ("dim_customers", self.cleaned_dfs["dim_customers"]),
            ("dim_sellers", self.cleaned_dfs["dim_sellers"]),
            ("dim_products", self.cleaned_dfs["dim_products"]),
            ("fact_orders", self.cleaned_dfs["fact_orders"]),
            ("fact_order_items", self.cleaned_dfs["fact_order_items"]),
            ("fact_order_payments", self.cleaned_dfs["fact_order_payments"]),
            ("fact_order_reviews", self.cleaned_dfs["fact_order_reviews"])
        ]

        for table_name, df in load_order:
            logger.info(f"Loading {len(df):,} records into `{table_name}`...")
            # For fact_order_reviews, omit surrogate_review_id so AUTO_INCREMENT generates it
            load_df = df.copy()
            if table_name == "fact_order_reviews" and "surrogate_review_id" in load_df.columns:
                load_df = load_df.drop(columns=["surrogate_review_id"])

            load_df.to_sql(
                name=table_name,
                con=self.engine,
                if_exists="append",
                index=False,
                chunksize=BATCH_SIZE,
                method="multi"
            )
            logger.info(f"Successfully loaded `{table_name}`.")

        logger.info(f"Data loading completed in {time.time() - start_time:.2f} seconds.")

    def setup_views(self):
        """
        Executes analytical SQL views setup.
        """
        logger.info("=== CREATING ANALYTICAL VIEWS ===")
        views_file = PROJECT_ROOT / "database" / "02_views_and_marts.sql"
        with open(views_file, "r", encoding="utf-8") as f:
            sql_statements = f.read().split(";")

        with self.engine.connect() as conn:
            for statement in sql_statements:
                cleaned = statement.strip()
                if cleaned:
                    conn.execute(text(cleaned))
            conn.commit()
        logger.info("Analytical views created successfully.")

    def verify(self):
        """
        Validates record counts in MySQL against transformed DataFrames.
        """
        logger.info("=== STEP 4: VERIFYING INGESTION COUNTS ===")
        with self.engine.connect() as conn:
            for table_name, df in self.cleaned_dfs.items():
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name};")).scalar()
                df_count = len(df)
                status = "MATCH" if result == df_count else "MISMATCH"
                logger.info(f"Table `{table_name}`: Database={result:,} | DataFrame={df_count:,} [{status}]")

    def run_pipeline(self):
        """
        Executes complete pipeline from extraction to verification.
        """
        logger.info("Starting Olist ETL Pipeline execution...")
        self.extract()
        self.transform()
        self.setup_database_schema()
        self.load()
        self.setup_views()
        self.verify()
        logger.info("Olist ETL Pipeline finished successfully.")


if __name__ == "__main__":
    pipeline = OlistETLPipeline()
    pipeline.run_pipeline()
