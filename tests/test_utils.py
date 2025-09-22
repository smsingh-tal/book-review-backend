"""Test database utilities"""
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.models import Book

def populate_test_books(db: Session):
    """Add sample books to the test database"""
    from datetime import datetime
    
    # Create multiple test books with varying genres and ratings
    genres_sets = [
        ["Fiction", "Adventure"],
        ["Mystery", "Thriller"],
        ["Romance", "Drama"],
        ["Science Fiction", "Fantasy"],
        ["Literary Fiction", "Contemporary"],
        ["Horror", "Supernatural"],
        ["Historical Fiction", "War"],
        ["Young Adult", "Coming of Age"]
    ]
    
    books = []
    for i in range(48):  # Create 48 test books
        rating = 3.5 + (i % 15) / 10.0  # Ratings from 3.5 to 5.0
        book = Book(
            title=f"Test Book {i + 1}",
            author=f"Author {i + 1}",
            isbn=f"{i + 1:013d}",
            genres=genres_sets[i % len(genres_sets)],
            average_rating=rating,
            total_reviews=10 + i,
            publication_date=datetime(2020 + (i % 5), 1, 1).date()
        )
        books.append(book)
    
    db.add_all(books)
    db.commit()
