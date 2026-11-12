"""
Delivery Delay Risk & Predictive Analytics Module.
Author: Aaryaraj Patil
Description:
    Analyzes logistics bottlenecks and trains machine learning models to identify
    key drivers of late customer deliveries across Brazil.
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

try:
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import classification_report, roc_auc_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = setup_logger("delivery_delay_model")


def build_delay_prediction_dataset(data_dir: str = None) -> pd.DataFrame:
    """
    Constructs feature set for predicting order delivery delays.
    """
    dir_path = data_dir or DATA_DIR
    logger.info("Extracting tables for delivery delay risk modeling...")

    orders = pd.read_csv(os.path.join(dir_path, "olist_orders_dataset.csv"))
    items = pd.read_csv(os.path.join(dir_path, "olist_order_items_dataset.csv"))
    products = pd.read_csv(os.path.join(dir_path, "olist_products_dataset.csv"))
    cust = pd.read_csv(os.path.join(dir_path, "olist_customers_dataset.csv"))
    sellers = pd.read_csv(os.path.join(dir_path, "olist_sellers_dataset.csv"))

    # Delivered orders with valid dates
    orders = orders[orders["order_status"] == "delivered"].dropna(subset=["order_delivered_customer_date"]).copy()
    orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])
    orders["order_delivered_customer_date"] = pd.to_datetime(orders["order_delivered_customer_date"])
    orders["order_estimated_delivery_date"] = pd.to_datetime(orders["order_estimated_delivery_date"])

    # Target: is_delayed (1 if actual > estimated, else 0)
    orders["is_delayed"] = (orders["order_delivered_customer_date"] > orders["order_estimated_delivery_date"]).astype(int)

    # Item & Product aggregates per order
    item_prod = pd.merge(items, products, on="product_id", how="left")
    order_features = item_prod.groupby("order_id").agg({
        "order_item_id": "count",
        "price": "sum",
        "freight_value": "sum",
        "product_weight_g": "mean",
        "seller_id": "first"
    }).reset_index().rename(columns={"order_item_id": "item_count"})

    # Merge with sellers and customers
    merged = pd.merge(orders[["order_id", "customer_id", "order_purchase_timestamp", "is_delayed"]], order_features, on="order_id")
    merged = pd.merge(merged, cust[["customer_id", "customer_state"]], on="customer_id")
    merged = pd.merge(merged, sellers[["seller_id", "seller_state"]], on="seller_id")

    # Feature Engineering
    merged["is_interstate"] = (merged["customer_state"] != merged["seller_state"]).astype(int)
    merged["freight_ratio"] = merged["freight_value"] / (merged["price"] + 0.01)
    merged["product_weight_kg"] = merged["product_weight_g"].fillna(merged["product_weight_g"].median()) / 1000.0
    merged["purchase_month"] = merged["order_purchase_timestamp"].dt.month
    merged["purchase_dayofweek"] = getattr(merged["order_purchase_timestamp"].dt, "day_of_week", merged["order_purchase_timestamp"].dt.dayofweek)

    logger.info(f"Feature dataset prepared: {len(merged):,} orders. Delay rate: {merged['is_delayed'].mean()*100:.2f}%")
    return merged


def train_delay_classifier(df: pd.DataFrame):
    """
    Evaluates delay risk factors using Statistical Correlation and Random Forest (if sklearn installed).
    """
    feature_cols = [
        "item_count", "price", "freight_value", "freight_ratio",
        "product_weight_kg", "is_interstate", "purchase_month", "purchase_dayofweek"
    ]

    print("\n" + "=" * 80)
    print("DELIVERY DELAY RISK FACTORS - STATISTICAL CORRELATION")
    print("=" * 80)
    correlations = df[feature_cols + ["is_delayed"]].corr()["is_delayed"].drop("is_delayed").sort_values(ascending=False)
    for feat, corr in correlations.items():
        print(f"  - {feat:20s}: Correlation with delay = {corr:+.4f}")
    print("=" * 80 + "\n")

    if not SKLEARN_AVAILABLE:
        print("[!] Note: scikit-learn is not installed in the environment; statistical correlation analysis shown above.")
        return

    X = df[feature_cols].copy()
    y = df["is_delayed"]

    # Stratified Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

    logger.info("Training Random Forest Classifier on logistics features...")
    clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1, class_weight="balanced")
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)[:, 1]

    roc_auc = roc_auc_score(y_test, y_prob)

    print("=" * 80)
    print("RANDOM FOREST LOGISTICS CLASSIFIER EVALUATION")
    print("=" * 80)
    print(f"ROC-AUC Score: {roc_auc:.4f}\n")
    print(classification_report(y_test, y_pred, target_names=["On-Time (0)", "Delayed (1)"]))

    importance_df = pd.DataFrame({
        "Feature": feature_cols,
        "Importance": clf.feature_importances_
    }).sort_values(by="Importance", ascending=False)

    print("TOP LOGISTICS DELAY RISK DRIVERS (FEATURE IMPORTANCE):")
    for _, row in importance_df.iterrows():
        print(f"  - {row['Feature']:20s}: {row['Importance']*100:5.2f}%")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    df_data = build_delay_prediction_dataset()
    train_delay_classifier(df_data)
