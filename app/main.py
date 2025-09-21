from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, storage, profile, recommendation, book, review
from app.db.session import get_db
from sqlalchemy import text
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
from fastapi.staticfiles import StaticFiles
import os


from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    from app.core.config import get_settings
    settings = get_settings()
    # Log database configuration
    logger.info("Database Configuration:")
    logger.info(f"  Host: {settings.DB_HOST}")
    logger.info(f"  Port: {settings.DB_PORT}")
    logger.info(f"  Database: {settings.DB_NAME}")
    logger.info(f"  User: {settings.DB_USER}")
    logger.info(f"  URL: {settings.DATABASE_URL}")
    # Test database connection
    db = next(get_db())
    try:
        # Verify connection details
        result = db.execute(text("SELECT current_database(), current_user, current_schema()"))
        db_name, user, schema = result.fetchone()
        logger.info(f"Successfully connected to database:")
        logger.info(f"  Database: {db_name}")
        logger.info(f"  User: {user}")
        logger.info(f"  Schema: {schema}")
        # Check if we can access the books table
        result = db.execute(text("SELECT COUNT(*) FROM books"))
        count = result.scalar()
        logger.info(f"Found {count} books in database")
        if count == 0:
            logger.warning("No books found in database - this might indicate a connection to the wrong database")
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise
    finally:
        db.close()
    yield

app = FastAPI(title="Book Review Platform", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    # Test database connection
    db = next(get_db())
    try:
        result = db.execute(text("SELECT COUNT(*) FROM books"))
        count = result.scalar()
        return {
            "message": "Welcome to Book Review Platform API",
            "book_count": count
        }
    except Exception as e:
        return {
            "message": "Welcome to Book Review Platform API",
            "error": str(e)
        }

# Add a way to override get_db dependency
test_session = None

def override_get_db():
    global test_session
    if test_session:
        return test_session
    return next(get_db())

# Only override get_db when test_session is set
app.dependency_overrides[get_db] = override_get_db

app.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
app.include_router(storage.router)
app.include_router(profile.router, prefix="/v1/profile", tags=["profile"])
app.include_router(recommendation.router, prefix="/v1/recommendations", tags=["recommendations"])
app.include_router(book.router)
app.include_router(review.router)

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

# Mount uploads directory
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
