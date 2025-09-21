import pytest
from sqlalchemy.orm import Session
from app.db.models import User, Book, Review, UserFavorite
from app.services.recommendation import RecommendationService

@pytest.fixture
def sample_data(db: Session):
    # Create test user
    user = User(name="Recommendation User", email="test@example.com", hashed_password="dummy_hash")
    db.add(user)
    db.commit()
    
    # Create test books
    books = [
        Book(
            title=f"Book {i}",
            author=f"Author {i}",
            genres=[f"Genre{i}", f"Genre{i+1}"],
            average_rating=4.0 + (i/10),
            isbn=f"123-456-{i:04d}"
        )
        for i in range(1, 6)
    ]
    db.add_all(books)
    db.commit()
    
    # Add some reviews and favorites
    review = Review(
        user_id=user.id,
        book_id=books[0].id,
        text="Great book!",
        rating=5
    )
    favorite = UserFavorite(
        user_id=user.id,
        book_id=books[1].id
    )
    db.add_all([review, favorite])
    db.commit()
    
    return {
        "user": user,
        "books": books,
        "review": review,
        "favorite": favorite
    }

def test_get_user_preferences(db: Session, sample_data):
    service = RecommendationService(db)
    preferences = service._get_user_preferences(sample_data["user"].id)
    
    assert preferences
    assert isinstance(preferences, dict)
    assert sum(preferences.values()) == pytest.approx(1.0)
    assert all(genre.startswith("Genre") for genre in preferences.keys())

def test_calculate_book_score(db: Session, sample_data):
    service = RecommendationService(db)
    book = sample_data["books"][0]
    preferences = {"Genre1": 0.5, "Genre2": 0.5}
    
    score = service._calculate_book_score(book, preferences)
    assert score > book.average_rating  # Score should be boosted by matching genres

def test_get_popular_books(db: Session, sample_data):
    service = RecommendationService(db)
    exclude_ids = {sample_data["books"][0].id}
    popular_books = service._get_popular_books(limit=3, exclude_ids=exclude_ids)
    
    assert len(popular_books) == 3
    assert all(book["book_id"] not in exclude_ids for book in popular_books)
    # Check if sorted by rating
    ratings = [book["average_rating"] for book in popular_books]
    assert ratings == sorted(ratings, reverse=True)

def test_get_recommendations_new_user(db: Session, sample_data):
    service = RecommendationService(db)
    # Create new user with no history
    new_user = User(name="New User", email="new@example.com", hashed_password="dummy_hash")
    db.add(new_user)
    db.commit()
    
    result = service.get_recommendations(new_user.id, limit=3)
    assert result["is_fallback"] is True
    assert len(result["recommendations"]) == 3

def test_get_recommendations_with_history(db: Session, sample_data):
    service = RecommendationService(db)
    result = service.get_recommendations(sample_data["user"].id, limit=3)
    
    assert result["is_fallback"] is False
    assert len(result["recommendations"]) == 3
    # Check that reviewed/favorited books are excluded
    excluded_ids = {sample_data["review"].book_id, sample_data["favorite"].book_id}
    assert all(
        book["book_id"] not in excluded_ids 
        for book in result["recommendations"]
    )

def test_get_recommendations_limit_respected(db: Session, sample_data):
    service = RecommendationService(db)
    limit = 2
    result = service.get_recommendations(sample_data["user"].id, limit=limit)
    
    assert len(result["recommendations"]) == limit
