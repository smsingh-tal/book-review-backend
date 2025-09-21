"""Test database configuration and setup"""
import pytest
from datetime import datetime, date, timezone
from sqlalchemy.exc import IntegrityError
from app.db.models import Base, User, Book, Review, ReviewVote, UserFavorite

def test_create_user(db):
    """Test user creation and retrieval"""
    user = User(
        name="Test User",
        email="test@example.com",
        hashed_password="testpass",
        created_at=datetime.now(timezone.utc)
    )
    db.add(user)
    db.commit()
    
    saved_user = db.query(User).filter_by(email="test@example.com").first()
    assert saved_user is not None
    assert saved_user.email == "test@example.com"
    assert saved_user.status == "active"  # Default value test

def test_create_book(db):
    """Test book creation and retrieval"""
    book = Book(
        title="Test Book",
        author="Test Author",
        isbn="1234567890",
        genres=["Fiction"],
        created_at=datetime.now(timezone.utc)
    )
    db.add(book)
    db.commit()
    
    saved_book = db.query(Book).filter_by(title="Test Book").first()
    assert saved_book is not None
    assert saved_book.author == "Test Author"
    assert "Fiction" in saved_book.genres
    assert saved_book.average_rating == 0.0  # Default value test

def test_create_review(db):
    """Test review creation with user and book relationship"""
    # Create user and book first
    user = User(
        name="Reviewer",
        email="reviewer@example.com",
        hashed_password="hashed_password",
        created_at=datetime.now(timezone.utc)
    )
    book = Book(
        title="Book for Review", 
        author="Author", 
        isbn="1234567891",
        created_at=datetime.now(timezone.utc)
    )
    db.add_all([user, book])
    db.commit()
    
    review = Review(
        book_id=book.id,
        user_id=user.id,
        rating=5,
        text="Great book!",
        created_at=datetime.now(timezone.utc)
    )
    db.add(review)
    db.commit()
    
    # Query for the review we just created, not the first in the DB
    saved_review = db.query(Review).filter_by(user_id=user.id, book_id=book.id).first()
    assert saved_review is not None
    assert saved_review.text == "Great book!"
    assert saved_review.user.email == "reviewer@example.com"
    assert saved_review.book.title == "Book for Review"

def test_review_unique_constraint(db):
    """Test that a user cannot review the same book twice"""
    user = User(
        name="Unique User",
        email="user@example.com",
        hashed_password="hashed_password",
        created_at=datetime.now(timezone.utc)
    )
    book = Book(
        title="Unique Test Book", 
        author="Author", 
        isbn="1234567893",
        created_at=datetime.now(timezone.utc)
    )
    db.add_all([user, book])
    db.commit()
    
    # First review
    review1 = Review(
        user_id=user.id,
        book_id=book.id,
        text="First review",
        rating=4,
        created_at=datetime.now(timezone.utc)
    )
    db.add(review1)
    db.commit()
    
    # Try to add second review for same book by same user
    review2 = Review(
        user_id=user.id,
        book_id=book.id,
        text="Second review",
        rating=5,
        created_at=datetime.now(timezone.utc)
    )
    db.add(review2)
    
    with pytest.raises(IntegrityError):  # Should raise unique constraint violation
        db.commit()

def test_review_votes(db):
    """Test review voting system"""
    # Setup user, book, and review
    user = User(
        name="Reviewer",
        email="reviewer@example.com",
        hashed_password="hashed_password",
        created_at=datetime.now(timezone.utc)
    )
    voter = User(
        name="Voter",
        email="voter@example.com",
        hashed_password="hashed_password",
        created_at=datetime.now(timezone.utc)
    )
    book = Book(
        title="Voted Book", 
        author="Author", 
        isbn="1234567894",
        created_at=datetime.now(timezone.utc)
    )
    db.add_all([user, voter, book])
    db.commit()
    
    review = Review(
        user_id=user.id, 
        book_id=book.id, 
        text="Review", 
        rating=4,
        created_at=datetime.now(timezone.utc)
    )
    db.add(review)
    db.commit()
    
    # Add vote
    vote = ReviewVote(
        user_id=voter.id,
        review_id=review.id,
        is_helpful=True,
        created_at=datetime.now(timezone.utc)
    )
    db.add(vote)
    db.commit()
    
    saved_vote = db.query(ReviewVote).first()
    assert saved_vote is not None
    assert saved_vote.is_helpful is True
    assert saved_vote.review.text == "Review"

def test_user_favorites(db):
    """Test user favorites functionality"""
    user = User(
        name="Bookworm",
        email="bookworm@example.com", 
        hashed_password="hashed_password",
        created_at=datetime.now(timezone.utc)
    )
    book = Book(
        title="Favorite Book", 
        author="Author", 
        isbn="1234567895",
        created_at=datetime.now(timezone.utc)
    )
    db.add_all([user, book])
    db.commit()
    
    favorite = UserFavorite(
        user_id=user.id,
        book_id=book.id,
        created_at=datetime.now(timezone.utc)
    )
    db.add(favorite)
    db.commit()
    
    saved_favorite = db.query(UserFavorite).first()
    assert saved_favorite is not None
    assert saved_favorite.user.email == "bookworm@example.com"
    assert saved_favorite.book.title == "Favorite Book"

def test_cascade_delete(db):
    """Test that deleting a book cascades to related reviews"""
    user = User(
        name="Cascade",
        email="cascade@example.com",
        hashed_password="hashed_password",
        created_at=datetime.now(timezone.utc)
    )
    book = Book(
        title="Delete Me", 
        author="Author", 
        isbn="1234567892",
        created_at=datetime.now(timezone.utc)
    )
    db.add_all([user, book])
    db.commit()
    
    review = Review(
        user_id=user.id, 
        book_id=book.id, 
        text="To be deleted", 
        rating=3,
        created_at=datetime.now(timezone.utc)
    )
    db.add(review)
    db.commit()
    
    # Delete the book
    db.delete(book)
    db.commit()
    
    # Check that review is also deleted
    remaining_review = db.query(Review).filter_by(id=review.id).first()
    assert remaining_review is None

