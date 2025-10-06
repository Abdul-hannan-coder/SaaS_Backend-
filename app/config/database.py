import sys
import os
from pathlib import Path
from urllib.parse import urlparse, unquote
from sqlmodel import SQLModel, create_engine, Session, text
from clickhouse_driver import Client
from .my_settings import settings
from ..utils.my_logger import get_logger


def initialize_database_engine():
    """
    Initialize MySQL SQLModel engine
    """
    try:
        get_logger(name="UZAIR").info("🔧 Initializing Database engine...")
        # Create SQLModel engine for MySQL ORM operations only
        if settings.DATABASE_URL:
            mysql_url = settings.DATABASE_URL
        else:
            mysql_url = settings.DATABASE_URL
        mysql_engine = create_engine(
            mysql_url,
            echo=True,  # Set to False in production
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=10,
            max_overflow=20
        )
        # test connection by executing a simple query
        with mysql_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        get_logger(name="UZAIR").info("✅ Database engine initialized successfully")
        return mysql_engine
    except Exception as e:
        get_logger(name="UZAIR").error(f"❌ Could not initialize Database engine: {e}")
        return None
