"""
Configuration module for Olist Data Platform.
Reads database credentials and pipeline parameters from environment variables or .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Database Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "olist_ecommerce_db")

# Construct SQLAlchemy database URL
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

# Base project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = os.getenv("DATA_DIR", str(PROJECT_ROOT / "data" / "Brazilian E-Commerce Public Dataset by Olist"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 5000))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
