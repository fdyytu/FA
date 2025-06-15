from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.infrastructure.config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Create database engine with proper configuration for PostgreSQL and SQLite
def create_database_engine():
    """Create database engine with appropriate settings"""
    if settings.is_postgresql:
        # PostgreSQL configuration
        logger.info("Configuring PostgreSQL engine")
        return create_engine(
            settings.DATABASE_URL,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_recycle=settings.DB_POOL_RECYCLE,
            echo=settings.DEBUG,  # Log SQL queries in debug mode
        )
    else:
        # SQLite configuration
        logger.info("Configuring SQLite engine")
        return create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False},
            echo=settings.DEBUG,
        )

engine = create_database_engine()

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
