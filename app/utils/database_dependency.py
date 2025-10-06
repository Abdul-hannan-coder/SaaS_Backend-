"""
Database dependency for FastAPI
"""
from typing import Generator
from sqlmodel import Session
from fastapi import Request
from .my_logger import get_logger

logger = get_logger("DATABASE")

def get_database_session(request: Request) -> Generator[Session, None, None]:
    """Database session dependency using cached engine from app state"""
    try:
        # Get the cached engine from app state
        engine = request.app.state.database_engine
        if not engine:
            logger.error("Database engine not available in app state")
            raise Exception("Database connection failed")
        
        with Session(engine) as session:
            yield session
    except Exception as e:
        logger.error(f"Database session error: {e}")
        raise
