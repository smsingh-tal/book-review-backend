from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import get_settings
import logging
from app.db.models import Base, Book  # Import Base and models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_engine():
    try:
        settings = get_settings()
        logger.info(f"Connecting to database: {settings.DB_NAME} on {settings.DB_HOST}:{settings.DB_PORT}")
        engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_size=20,  # Increased pool size for better concurrency
            max_overflow=20,  # Increased max overflow
            pool_timeout=30,  # Added timeout
            pool_recycle=1800,  # Recycle connections after 30 minutes
            echo=False  # Disable SQL echoing for performance
        )
        # Test the connection and set the search path
        with engine.connect() as conn:
            logger.info("Testing database connection...")
            result = conn.execute(text("SELECT current_database(), current_user, current_schema()"))
            db_name, user, schema = result.fetchone()
            logger.info(f"Connected to database: {db_name} as user: {user} using schema: {schema}")
            
            # Set and verify search path
            conn.execute(text('SET search_path TO public'))
            result = conn.execute(text('SHOW search_path'))
            logger.info(f"Search path set to: {result.scalar()}")
            
            
            conn.commit()
        logger.info("Database connection established successfully")
        return engine
    except Exception as e:
        logger.error(f"Failed to create database engine: {str(e)}")
        raise

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        db.close()
