import pytest
from sqlalchemy import text
from app.db.session import get_db

def test_basic_db_connection():
    """Test basic database connectivity"""
    # Get a database session
    db = next(get_db())
    try:
        # Test that we can execute a simple query
        result = db.execute(text("SELECT 1"))
        assert result.scalar() == 1
        print("Basic connection successful")

        # Test that we can query the books table
        result = db.execute(text("SELECT COUNT(*) FROM books"))
        count = result.scalar()
        print(f"Number of books in database: {count}")
        assert count > 0, "No books found in database"

        # Get a sample book
        result = db.execute(text("SELECT title FROM books LIMIT 1"))
        title = result.scalar()
        print(f"Sample book title: {title}")
        assert title is not None, "Could not retrieve a book title"

    finally:
        db.close()
