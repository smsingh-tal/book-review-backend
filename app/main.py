from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, storage, profile, recommendation, book, review
from app.db.session import get_db
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
from fastapi.staticfiles import StaticFiles
import os


app = FastAPI(title="Book Review Platform")

# Log database configuration on startup
from app.core.config import get_settings
settings = get_settings()
logger.info("Database Configuration:")
logger.info("  Host: {}".format(settings.DB_HOST))
logger.info("  Port: {}".format(settings.DB_PORT))
logger.info("  Database: {}".format(settings.DB_NAME))
logger.info("  User: {}".format(settings.DB_USER))
logger.info("  URL: {}".format(settings.DATABASE_URL))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with database connection check"""
    # Test database connection and log details
    db = next(get_db())
    try:
        # Verify connection details
        result = db.execute(text("SELECT current_database(), current_user, current_schema()"))
        db_name, user, schema = result.fetchone()
        logger.info("Successfully connected to database:")
        logger.info("  Database: {}".format(db_name))
        logger.info("  User: {}".format(user))
        logger.info("  Schema: {}".format(schema))
        
        # Check if we can access the books table
        result = db.execute(text("SELECT COUNT(*) FROM books"))
        count = result.scalar()
        logger.info("Found {} books in database".format(count))
        if count == 0:
            logger.warning("No books found in database - this might indicate a connection to the wrong database")
            
        return {
            "message": "Welcome to Book Review Platform API",
            "database": db_name,
            "user": user,
            "schema": schema,
            "book_count": count
        }
    except Exception as e:
        logger.error("Database connection error: {}".format(str(e)))
        return {
            "message": "Welcome to Book Review Platform API",
            "error": str(e)
        }
    finally:
        db.close()

@app.get("/health")
async def health_check():
    """Health check endpoint for the API"""
    return {"status": "healthy", "timestamp": str(datetime.now())}# Add a way to override get_db dependency
test_session = None

def override_get_db():
    global test_session
    if test_session:
        return test_session
    return next(get_db())

# Only override get_db when test_session is set
app.dependency_overrides[get_db] = override_get_db

app.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
app.include_router(storage.router, prefix="/v1/storage", tags=["storage"])
app.include_router(profile.router, prefix="/v1/profile", tags=["profile"])
app.include_router(recommendation.router, prefix="/v1/recommendations", tags=["recommendations"])
app.include_router(book.router, prefix="/v1/books", tags=["books"])
app.include_router(review.router, prefix="/v1/reviews", tags=["reviews"])

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

# Mount uploads directory
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
