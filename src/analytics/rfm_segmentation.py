"""
RFM (Recency, Frequency, Monetary) Customer Segmentation Module.
Author: Aaryaraj Patil
Description:
    Quantifies customer lifetime engagement, segments buyers using RFM scores,
    and produces strategic marketing recommendations.
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
import numpy as np
from src.config import DATA_DIR, PROJECT_ROOT
from src.logger import setup_logger

logger = setup_logger("rfm_segmentation")


def compute_rfm_segments(data_dir: str = None) -> pd.DataFrame:
    """
    Computes RFM metrics and assigns segments to all unique customers.
    """
    dir_path = data_dir or DATA_DIR
    logger.info("Loading orders, customers, and payments for RFM calculation...")

    orders = pd.read_csv(os.path.join(dir_path, "olist_orders_dataset.csv"))
    cust = pd.read_csv(os.path.join(dir_path, "olist_customers_dataset.csv"))
    payments = pd.read_csv(os.path.join(dir_path, "olist_order_payments_dataset.csv"))

    # Filter to delivered orders
    delivered_orders = orders[orders["order_status"] == "delivered"].copy()
    delivered_orders["order_purchase_timestamp"] = pd.to_datetime(delivered_orders["order_purchase_timestamp"])

    # Merge orders with customers
    order_cust = pd.merge(delivered_orders, cust[["customer_id", "customer_unique_id", "customer_state"]], on="customer_id")

    # Order level spend
    order_spend = payments.groupby("order_id")["payment_value"].sum().reset_index()
    order_master = pd.merge(order_cust, order_spend, on="order_id", how="left")
    order_master["payment_value"] = order_master["payment_value"].fillna(0.0)

    # Reference snapshot date: 1 day after the latest purchase in the dataset
    snapshot_date = order_master["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
    logger.info(f"Snapshot analysis date set to: {snapshot_date.date()}")

    # Aggregate RFM by customer_unique_id
    rfm = order_master.groupby("customer_unique_id").agg({
        "order_purchase_timestamp": lambda x: (snapshot_date - x.max()).days,
        "order_id": "nunique",
        "payment_value": "sum",
        "customer_state": "first"
    }).reset_index()

    rfm.columns = ["customer_unique_id", "recency", "frequency", "monetary", "customer_state"]

    # Compute R, F, M quintiles (1-5)
    # Recency: lower days is better -> invert labels
    rfm["r_score"] = pd.qcut(rfm["recency"], q=5, labels=[5, 4, 3, 2, 1]).astype(int)
    
    # Frequency: heavily skewed (97% are 1 order). Custom bins:
    rfm["f_score"] = rfm["frequency"].apply(lambda f: 5 if f >= 4 else (4 if f == 3 else (3 if f == 2 else 1)))
    
    # Monetary: higher spend is better
    rfm["m_score"] = pd.qcut(rfm["monetary"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)

    # Segment mapping logic
    def assign_segment(row):
        r, f, m = row["r_score"], row["f_score"], row["m_score"]
        if r >= 4 and f >= 4:
            return "Champions"
        elif r >= 3 and f >= 3:
            return "Loyal Customers"
        elif r >= 4 and f == 1:
            return "New Promising Customers"
        elif r == 3 and f == 1:
            return "Potential Loyalists"
        elif r == 2 and f >= 3:
            return "At Risk"
        elif r == 1 and f >= 3:
            return "Can't Lose Them"
        elif r <= 2 and f == 1 and m >= 4:
            return "Hibernating High Spenders"
        elif r <= 2 and f == 1 and m < 4:
            return "Lost / Inactive"
        else:
            return "Needs Attention"

    rfm["rfm_segment"] = rfm.apply(assign_segment, axis=1)

    # Print Segment Summary
    summary = rfm.groupby("rfm_segment").agg(
        customer_count=("customer_unique_id", "count"),
        avg_recency_days=("recency", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
        total_revenue=("monetary", "sum")
    ).reset_index()

    total_cust = len(rfm)
    total_rev = rfm["monetary"].sum()
    summary["pct_customers"] = (summary["customer_count"] / total_cust) * 100
    summary["pct_revenue"] = (summary["total_revenue"] / total_rev) * 100
    summary = summary.sort_values(by="total_revenue", ascending=False)

    print("\n" + "=" * 90)
    print("CUSTOMER RFM SEGMENTATION SUMMARY")
    print("=" * 90)
    for _, row in summary.iterrows():
        print(f"[{row['rfm_segment'].upper():26s}] Customers: {row['customer_count']:6,d} ({row['pct_customers']:5.1f}%) | "
              f"Revenue: R${row['total_revenue']:10,.2f} ({row['pct_revenue']:5.1f}%) | "
              f"Avg Spend: R${row['avg_monetary']:6.2f} | Avg Recency: {row['avg_recency_days']:4.0f}d")
    print("=" * 90 + "\n")

    return rfm


if __name__ == "__main__":
    df_rfm = compute_rfm_segments()
