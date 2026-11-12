"""
Database connection and session management module using SQLAlchemy and PyMySQL.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from src.config import SQLALCHEMY_DATABASE_URI, DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
from src.logger import setup_logger

logger = setup_logger("db_connector")


def get_db_engine(custom_db: str = None) -> Engine:
    """
    Creates and returns a SQLAlchemy Engine.
    If custom_db is provided, overrides the target database name (e.g. for initial DB creation).
    """
    if custom_db is not None:
        db_uri = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{custom_db}?charset=utf8mb4"
    else:
        db_uri = SQLALCHEMY_DATABASE_URI
    return create_engine(db_uri, pool_pre_ping=True, pool_recycle=3600)


def test_connection() -> bool:
    """
    Tests connectivity to the MySQL database server.
    """
    logger.info(f"Testing MySQL connection to {DB_HOST}:{DB_PORT} as user '{DB_USER}'...")
    try:
        engine = get_db_engine("")  # connect to server without database
        with engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION();")).scalar()
            logger.info(f"Successfully connected to MySQL Server version: {result}")
        return True
    except OperationalError as e:
        logger.error(f"Failed to connect to MySQL server: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected connection error: {e}")
        return False
