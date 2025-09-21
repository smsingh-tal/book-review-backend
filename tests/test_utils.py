"""Test database utilities"""
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.models import Book

def populate_test_books(db: Session):
    """Add sample books to the test database"""
    # Create multiple test books
    books = [
        {
            "title": f"Test Book {i}",
            "author": f"Author {i}",
            "isbn": f"{i:013d}",
            "genres": ["Fiction", "Adventure"],
            "average_rating": 4.5,
            "total_reviews": 10
        }
        for i in range(48)  # Create 48 test books to match init_books.sql
    ]
    
    for book_data in books:
        db.execute(
            text("""
                INSERT INTO books (title, author, isbn, genres, average_rating, total_reviews, created_at)
                VALUES (:title, :author, :isbn, :genres, :average_rating, :total_reviews, CURRENT_TIMESTAMP)
            """),
            book_data
        )
    
    db.commit()
