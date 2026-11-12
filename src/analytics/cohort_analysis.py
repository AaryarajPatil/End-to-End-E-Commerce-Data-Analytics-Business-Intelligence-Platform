"""
Cohort & Retention Analysis Module for Olist E-Commerce Platform.
Author: Aaryaraj Patil
Description:
    Builds monthly customer acquisition cohorts and tracks retention rates
    across 12+ months to analyze churn dynamics.
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
import numpy as np
from src.config import DATA_DIR
from src.logger import setup_logger

logger = setup_logger("cohort_analysis")


def get_month_period(date_series: pd.Series) -> pd.Series:
    """Helper to convert datetime series to period Year-Month"""
    return date_series.dt.to_period("M")


def compute_cohort_matrix(data_dir: str = None) -> pd.DataFrame:
    """
    Computes monthly acquisition cohorts and retention rates.
    """
    dir_path = data_dir or DATA_DIR
    logger.info("Loading orders and customers for Cohort analysis...")

    orders = pd.read_csv(os.path.join(dir_path, "olist_orders_dataset.csv"))
    cust = pd.read_csv(os.path.join(dir_path, "olist_customers_dataset.csv"))

    # Delivered orders only
    orders = orders[orders["order_status"] == "delivered"].copy()
    orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])

    # Merge customer_unique_id
    df = pd.merge(orders[["order_id", "customer_id", "order_purchase_timestamp"]],
                  cust[["customer_id", "customer_unique_id"]],
                  on="customer_id")

    # Order month
    df["order_month"] = df["order_purchase_timestamp"].dt.to_period("M")

    # Determine Cohort Month (first purchase month per unique customer)
    df["cohort_month"] = df.groupby("customer_unique_id")["order_month"].transform("min")

    # Calculate Cohort Index (months since first purchase)
    # cohort_index = (order_year - cohort_year) * 12 + (order_month - cohort_month)
    df["cohort_index"] = (
        (df["order_month"].dt.year - df["cohort_month"].dt.year) * 12 +
        (df["order_month"].dt.month - df["cohort_month"].dt.month)
    )

    # Group by cohort_month and cohort_index
    cohort_data = df.groupby(["cohort_month", "cohort_index"])["customer_unique_id"].nunique().reset_index()

    # Pivot table into matrix
    cohort_counts = cohort_data.pivot(index="cohort_month", columns="cohort_index", values="customer_unique_id")
    cohort_counts = cohort_counts.fillna(0).astype(int)

    # Calculate Retention Rate % (relative to month 0)
    cohort_sizes = cohort_counts.iloc[:, 0]
    retention_matrix = cohort_counts.divide(cohort_sizes, axis=0) * 100

    print("\n" + "=" * 90)
    print("CUSTOMER ACQUISITION COHORT RETENTION RATES (%)")
    print("=" * 90)
    # Display first 8 columns of retention matrix
    formatted_retention = retention_matrix.iloc[:, :9].round(2)
    print(formatted_retention.to_string())
    print("=" * 90 + "\n")

    return retention_matrix


if __name__ == "__main__":
    matrix = compute_cohort_matrix()
