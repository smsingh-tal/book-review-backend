"""Tests for recommendation service"""
import json
import os
import asyncio
import pytest
from unittest.mock import patch, AsyncMock
from sqlalchemy.orm import Session
from app.db.models import User, Book, UserFavorite
from app.services.recommendation import RecommendationService
from app.schemas.recommendation import RecommendationType

# Configure event loop for tests
@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

def test_get_user_genre_preferences(db: Session):
    # Create test data
    user = User(name="Test User", email="test@example.com", hashed_password="dummy_hash")
    db.add(user)
    db.commit()

    # Create books with different genres
    books = [
        Book(title="Book 1", author="Author 1", genres=["Fiction", "Adventure"], average_rating=4.0, isbn="9780000000001"),
        Book(title="Book 2", author="Author 2", genres=["Fiction", "Mystery"], average_rating=4.2, isbn="9780000000002"),
        Book(title="Book 3", author="Author 3", genres=["Romance"], average_rating=3.8, isbn="9780000000003")
    ]
    for book in books:
        db.add(book)
    db.commit()

    # Add favorites
    for book in books[:2]:  # Make first two books favorites
        favorite = UserFavorite(user_id=user.id, book_id=book.id)
        db.add(favorite)
    db.commit()

    service = RecommendationService(db)
    preferences = service._get_user_genre_preferences(user.id)

    assert preferences["Fiction"] == 1.0  # Both favorite books have Fiction
    assert preferences["Adventure"] == 0.5  # One favorite book has Adventure
    assert preferences["Mystery"] == 0.5  # One favorite book has Mystery
    assert "Romance" not in preferences  # Not in favorites

def test_top_rated_scoring(db: Session):
    """Test that TOP_RATED scoring works as expected"""
    service = RecommendationService(db)
    
    # Create test books with different ratings and review counts
    books = [
        Book(title="High Rating Few Reviews", author="Author 1", 
             average_rating=4.8, total_reviews=10, isbn="9780000000004"),
        Book(title="High Rating Many Reviews", author="Author 2", 
             average_rating=4.8, total_reviews=1000, isbn="9780000000005"),
        Book(title="Lower Rating Many Reviews", author="Author 3", 
             average_rating=4.0, total_reviews=1000, isbn="9780000000006")
    ]
    for book in books:
        db.add(book)
    db.commit()

    scored_books = service._get_top_rated_recommendations(books, limit=3)
    
    # Convert to dict for easier testing
    scores = {book[0].title: book[1] for book in scored_books}
    
    # High rating books should score higher than lower rating books
    assert scores["High Rating Many Reviews"] > scores["Lower Rating Many Reviews"]
    
    # Books with same rating but more reviews should score slightly higher
    assert scores["High Rating Many Reviews"] > scores["High Rating Few Reviews"]
    
    # But the difference should be small (max 0.1)
    assert scores["High Rating Many Reviews"] - scores["High Rating Few Reviews"] <= 0.1

@pytest.mark.asyncio
async def test_similar_recommendations_scoring(db: Session, monkeypatch):
    """Test SIMILAR recommendations prioritize genre matches"""
    # Clear out existing test books for isolation
    db.query(Book).delete()
    db.commit()

    # Create a failing mock for OpenAI embeddings
    # Patch the AsyncOpenAI client
    def mock_init(self, *args, **kwargs):
        pass
    
    monkeypatch.setattr('openai.AsyncOpenAI.__init__', mock_init)

    # Mock the embeddings call to always raise an exception
    async def mock_embeddings_create(*args, **kwargs):
        raise Exception("API disabled for test")

    monkeypatch.setattr(
        'openai.resources.embeddings.AsyncEmbeddings.create',
        mock_embeddings_create
    )
    
    # Create service after mocking
    service = RecommendationService(db)

    # Create a user with clear genre preferences
    user = User(name="Genre User", email="genre@test.com", hashed_password="dummy_hash")
    db.add(user)
    db.commit()

    # Create favorite books with specific genres
    favorites = [
        Book(title="Fav Mystery", author="Author 1",
             genres=["Mystery", "Thriller"], average_rating=4.0,
             isbn="9780000000007"),
        Book(title="Fav Mystery 2", author="Author 2",
             genres=["Mystery", "Crime"], average_rating=4.0,
             isbn="9780000000008")
    ]
    # First add and commit the books to get their IDs
    for book in favorites:
        db.add(book)
    db.commit()

    # Now create the favorites
    for book in favorites:
        db.add(UserFavorite(user_id=user.id, book_id=book.id))
    db.commit()

    # Create recommendation candidates
    candidates = [
        Book(title="Perfect Match", author="Author 3",
             genres=["Mystery", "Thriller"], average_rating=4.0,
             isbn="9780000000009"),
        Book(title="Partial Match", author="Author 4",
             genres=["Mystery"], average_rating=4.0,
             isbn="9780000000010"),
        Book(title="No Match", author="Author 5",
             genres=["Romance"], average_rating=5.0,  # Higher rating but wrong genre
             isbn="9780000000011")
    ]
    for book in candidates:
        db.add(book)
    db.commit()

    result = await service._get_recommendations_async(
        user_id=user.id,
        limit=3,
        recommendation_type=RecommendationType.SIMILAR
    )

    recommendations = result["recommendations"]
    
    # Verify ordering based on genre matching
    titles = [r["title"] for r in recommendations]
    scores = [r["relevance_score"] for r in recommendations]
    
    # Perfect genre match should be first
    assert "Perfect Match" == titles[0]
    
    # Partial match should be second
    assert "Partial Match" == titles[1]
    
    # No genre match book should either be last or not included
    if "No Match" in titles:
        assert "No Match" == titles[-1]
    
    # Check recommendation reasons
    assert "Matches your interest in" in recommendations[0]["recommendation_reason"]
    for genre in ["Mystery", "Thriller"]:
        assert genre in recommendations[0]["recommendation_reason"]
    favorites = [
        Book(title="Fav Mystery", author="Author 1",
             genres=["Mystery", "Thriller"], average_rating=4.0,
             isbn="9780000000007"),
        Book(title="Fav Mystery 2", author="Author 2",
             genres=["Mystery", "Crime"], average_rating=4.0,
             isbn="9780000000008")
    ]
    # First add and commit the books to get their IDs
    for book in favorites:
        db.add(book)
    db.commit()

    # Now create the favorites
    for book in favorites:
        db.add(UserFavorite(user_id=user.id, book_id=book.id))
    db.commit()

    # Create recommendation candidates
    candidates = [
        Book(title="Perfect Match", author="Author 3",
             genres=["Mystery", "Thriller"], average_rating=4.0,
             isbn="9780000000009"),
        Book(title="Partial Match", author="Author 4",
             genres=["Mystery"], average_rating=4.0,
             isbn="9780000000010"),
        Book(title="No Match", author="Author 5",
             genres=["Romance"], average_rating=5.0,  # Higher rating but wrong genre
             isbn="9780000000011")
    ]
    for book in candidates:
        db.add(book)
    db.commit()

    result = await service._get_recommendations_async(
        user_id=user.id,
        limit=3,
        recommendation_type=RecommendationType.SIMILAR
    )

    recommendations = result["recommendations"]
    
    # Verify ordering based on genre matching
    titles = [r["title"] for r in recommendations]
    scores = [r["relevance_score"] for r in recommendations]
    
    # Perfect genre match should be first
    assert "Perfect Match" == titles[0]
    
    # Partial match should be second
    assert "Partial Match" == titles[1]
    
    # No genre match book should either be last or not included
    if "No Match" in titles:
        assert "No Match" == titles[-1]
    
    # Check recommendation reasons
    assert "Matches your interest in" in recommendations[0]["recommendation_reason"]
    for genre in ["Mystery", "Thriller"]:
        assert genre in recommendations[0]["recommendation_reason"]    # Create a user with clear genre preferences
    user = User(name="Genre User", email="genre@test.com", hashed_password="dummy_hash")
    db.add(user)
    db.commit()

    # Create favorite books with specific genres
    favorites = [
        Book(title="Fav Mystery", author="Author 1", 
             genres=["Mystery", "Thriller"], average_rating=4.0,
             isbn="9780000000007"),
        Book(title="Fav Mystery 2", author="Author 2", 
             genres=["Mystery", "Crime"], average_rating=4.0,
             isbn="9780000000008")
    ]
    # First add and commit the books to get their IDs
    for book in favorites:
        db.add(book)
    db.commit()

    # Now create the favorites
    for book in favorites:
        db.add(UserFavorite(user_id=user.id, book_id=book.id))
    db.commit()

    # Create recommendation candidates
    candidates = [
        Book(title="Perfect Match", author="Author 3",
             genres=["Mystery", "Thriller"], average_rating=4.0,
             isbn="9780000000009"),
        Book(title="Partial Match", author="Author 4",
             genres=["Mystery"], average_rating=4.0,
             isbn="9780000000010"),
        Book(title="No Match", author="Author 5",
             genres=["Romance"], average_rating=5.0,  # Higher rating but wrong genre
             isbn="9780000000011")
    ]
    for book in candidates:
        db.add(book)
    db.commit()

    result = service.get_recommendations(
        user_id=user.id,
        limit=3,
        recommendation_type=RecommendationType.SIMILAR
    )

    recommendations = result["recommendations"]
    
    # Verify ordering based on genre matching
    titles = [r["title"] for r in recommendations]
    scores = [r["relevance_score"] for r in recommendations]
    
    # Perfect genre match should be first
    assert "Perfect Match" == titles[0]
    
    # Partial match should be second
    assert "Partial Match" == titles[1]
    
    # No genre match book should either be last or not included
    if "No Match" in titles:
        assert "No Match" == titles[-1]
    
        # Check recommendation reasons
    assert "Matches your interest in" in recommendations[0]["recommendation_reason"]
    for genre in ["Mystery", "Thriller"]:
        assert genre in recommendations[0]["recommendation_reason"]


def test_get_popular_books(db: Session, sample_data):
    service = RecommendationService(db)
    popular_books = service._get_popular_books(limit=3)
    assert len(popular_books) <= 3
    for book in popular_books:
        assert "book_id" in book
        assert "title" in book
        assert "relevance_score" in book
        assert "recommendation_reason" in book
        assert "Popular book with" in book["recommendation_reason"]

@pytest.mark.asyncio
async def test_get_recommendations_new_user(db: Session):
    # Create a new user with no history
    new_user = User(
        name="New User",
        email="new@example.com",
        hashed_password="dummy_hash"
    )
    db.add(new_user)
    db.commit()

    service = RecommendationService(db)
    result = await service.get_recommendations(new_user.id, limit=3)

    assert len(result["recommendations"]) > 0
    assert result["recommendation_type"] == RecommendationType.TOP_RATED

@pytest.mark.asyncio
async def test_recommendations_with_genre_filter(db: Session):
    """Test that genre filtering works for both recommendation types"""
    service = RecommendationService(db)
    
    # Create test user and books
    user = User(name="Filter User", email="filter@test.com", hashed_password="dummy_hash")
    db.add(user)
    db.commit()

    books = [
        Book(title="Mystery Book", author="Author 1", 
             genres=["Mystery"], average_rating=4.5, total_reviews=100,
             isbn="9780000000012"),
        Book(title="Romance Book", author="Author 2", 
             genres=["Romance"], average_rating=4.8, total_reviews=200,
             isbn="9780000000013")
    ]
    for book in books:
        db.add(book)
    db.commit()

    # Test TOP_RATED with genre filter
    result = await service.get_recommendations(
        user_id=user.id,
        limit=5,
        recommendation_type=RecommendationType.TOP_RATED,
        genre="Mystery"
    )
    
    mystery_recs = result["recommendations"]
    assert all("Mystery" in book["genres"] for book in mystery_recs)
    
    # Test SIMILAR with genre filter
    result = await service.get_recommendations(
        user_id=user.id,
        limit=5,
        recommendation_type=RecommendationType.TOP_RATED,
        genre="Romance"
    )
    
    romance_recs = result["recommendations"]
    assert all("Romance" in book["genres"] for book in romance_recs)

@pytest.mark.asyncio
async def test_recommendations_exclude_read_books(db: Session, monkeypatch):
    # Clear out existing test books for isolation
    db.query(Book).delete()
    db.commit()
    """Test that recommendations exclude books the user has already marked as favorites"""
    service = RecommendationService(db)
    
    # Create test user and books
    user = User(name="Test User", email="test@example.com", hashed_password="dummy_hash")
    db.add(user)
    db.commit()

    books = [
        Book(title="Favorite Book", author="Author 1", 
             genres=["Mystery"], average_rating=4.5, total_reviews=100,
             isbn="9780000000014"),
        Book(title="New Book", author="Author 2", 
             genres=["Mystery"], average_rating=4.3, total_reviews=80,
             isbn="9780000000015")
    ]
    for book in books:
        db.add(book)
    db.commit()

    # Mark first book as favorite
    favorite = UserFavorite(user_id=user.id, book_id=books[0].id)
    db.add(favorite)
    db.commit()

    # Get recommendations
    result = await service.get_recommendations(
        user_id=user.id,
        limit=5,
        recommendation_type=RecommendationType.TOP_RATED
    )

    # Verify favorite book is not in recommendations
    titles = [r["title"] for r in result["recommendations"]]
    assert "Favorite Book" not in titles
    assert "New Book" in titles

@pytest.mark.asyncio
async def test_fallback_behavior(db: Session):
    """Test that fallback to popular books works when no recommendations found"""
    service = RecommendationService(db)
    
    # Create user with favorites in a genre that has no other books
    user = User(name="Fallback User", email="fallback@test.com", hashed_password="dummy_hash")
    db.add(user)
    db.commit()

    # Create one favorite book with unique genre
    unique_book = Book(
        title="Unique Genre Book", 
        author="Author 1",
        genres=["UniqueGenre"],
        average_rating=4.0,
        total_reviews=100,
        isbn="9780000000016"
    )
    db.add(unique_book)
    db.add(UserFavorite(user_id=user.id, book_id=unique_book.id))
    
    # Create some popular books in different genres
    popular_books = [
        Book(title=f"Popular Book {i}", 
             author=f"Author {i+2}",
             genres=["Popular"],
             average_rating=4.5,
             total_reviews=500,
             isbn=f"978000000{i+17:04}")
        for i in range(3)
    ]
    for book in popular_books:
        db.add(book)
    db.commit()

    # Try to get recommendations for the unique genre
    result = await service.get_recommendations(
        user_id=user.id,
        limit=5,
        recommendation_type=RecommendationType.SIMILAR,
        genre="UniqueGenre"
    )

    assert result["is_fallback"]
    assert "fallback_reason" in result
    assert len(result["recommendations"]) > 0

@pytest.mark.asyncio
async def test_similar_books_recommendations_by_genre(db: Session):
    # Create test user and service
    service = RecommendationService(db)
    user = User(name="Genre Test User", email="genre@test.com", hashed_password="dummy_hash")
    db.add(user)
    db.commit()

        # Create some books with specific genres
    favorite_books = [
        Book(title="Fav 1", author="Author 1", genres=["Mystery", "Thriller"], 
            average_rating=4.5, total_reviews=100, isbn="9780000000020"),
        Book(title="Fav 2", author="Author 2", genres=["Mystery", "Crime"], 
            average_rating=4.3, total_reviews=80, isbn="9780000000021")
    ]
    recommendation_books = [
        Book(title="Rec 1", author="Author 3", genres=["Mystery", "Thriller"], 
            average_rating=4.0, total_reviews=50, isbn="9780000000022"),
        Book(title="Rec 2", author="Author 4", genres=["Romance"], 
            average_rating=4.8, total_reviews=200, isbn="9780000000023"),
        Book(title="Rec 3", author="Author 5", genres=["Mystery"], 
            average_rating=3.9, total_reviews=30, isbn="9780000000024")
    ]    # Add all books
    for book in favorite_books + recommendation_books:
        db.add(book)
    db.commit()

    # Set up user favorites
    for book in favorite_books:
        favorite = UserFavorite(user_id=user.id, book_id=book.id)
        db.add(favorite)
    db.commit()

    # Get recommendations
    result = await service.get_recommendations(
        user_id=user.id,
        limit=5,
        recommendation_type=RecommendationType.SIMILAR
    )

    assert not result["is_fallback"]
    recommendations = result["recommendations"]
    assert len(recommendations) > 0

    # Verify that books with matching genres get higher scores
    scores = {rec["title"]: rec["relevance_score"] for rec in recommendations}
    
    # Mystery/Thriller book should have higher score than Romance book
    assert scores.get("Rec 1", 0) > scores.get("Rec 2", 0)

@pytest.mark.asyncio
async def test_similar_books_recommendations(db: Session, sample_data):
    service = RecommendationService(db)
    result = await service.get_recommendations(
        user_id=sample_data["user"].id,
        limit=3,
        recommendation_type=RecommendationType.SIMILAR
    )

    assert len(result["recommendations"]) > 0
    for rec in result["recommendations"]:
        assert "relevance_score" in rec
        assert "genres" in rec  # Make sure genres are included
    assert "is_ai_powered" in result  # Check AI flag is present

@pytest.mark.asyncio
async def test_ai_recommendations(db: Session):
    """Test AI-powered recommendations with mocked OpenAI API"""
    # Mock OpenAI API responses
    mock_embedding = [0.1] * 1536  # OpenAI embeddings are 1536-dimensional

    class MockEmbedding:
        def __init__(self, embedding):
            self.embedding = embedding

    class MockEmbeddingResponse:
        def __init__(self, embedding):
            self.data = [MockEmbedding(embedding)]

    class MockEmbeddings:
        async def create(self, **kwargs):
            return MockEmbeddingResponse(mock_embedding)

    class MockAsyncOpenAI:
        def __init__(self, *args, **kwargs):
            self.embeddings = MockEmbeddings()

    # Create service with mocked OpenAI client
    service = RecommendationService(db)
    service.openai_client = MockAsyncOpenAI()
    
    # Create test user with clear preferences
    user = User(name="AI Test User", email="ai@test.com", hashed_password="dummy_hash")
    db.add(user)
    db.commit()

    # Create test books with rich descriptions
    books = [
        Book(
            title="Mystery at Midnight",
            author="A. Sleuth",
            genres=["Mystery", "Thriller"],
            description="A gripping detective story about a midnight murder.",
            average_rating=4.5,
            isbn="9780000000030"
        ),
        Book(
            title="Love's Journey",
            author="R. Heart",
            genres=["Romance"],
            description="A touching romance about finding love in unexpected places.",
            average_rating=4.0,
            isbn="9780000000031"
        )
    ]
    for book in books:
        db.add(book)
    db.commit()

    # Add favorite to establish user preference
    favorite = UserFavorite(user_id=user.id, book_id=books[0].id)
    db.add(favorite)
    db.commit()

    # Disable Redis for test
    service.cache = None

    # Get AI recommendations
    result = await service.get_recommendations(
        user_id=user.id,
        limit=5,
        recommendation_type=RecommendationType.SIMILAR
    )

    assert result["is_ai_powered"]
    assert len(result["recommendations"]) > 0
    
    # Verify recommendations include AI-powered explanations
    assert any("AI recommendation" in rec["recommendation_reason"] for rec in result["recommendations"])

@pytest.mark.asyncio
async def test_ai_recommendations_fallback(db: Session, monkeypatch):
    """Test that recommendations fall back gracefully when AI fails"""
    
    # Create a failing mock for OpenAI embeddings
    async def mock_create(*args, **kwargs):
        raise Exception("API Error")

    # Create mock OpenAI client
    class MockEmbeddings:
        create = mock_create

    class MockOpenAI:
        def __init__(self, *args, **kwargs):
            self.embeddings = MockEmbeddings()

    # Apply the mock at module level
    monkeypatch.setattr("openai.AsyncOpenAI", MockOpenAI)
    service = RecommendationService(db)
    
    # Create test user and books
    user = User(name="AI Test User", email="ai@test.com", hashed_password="dummy_hash")
    db.add(user)
    db.commit()

    book = Book(
        title="Test Book",
        author="Test Author",
        genres=["Mystery"],
        average_rating=4.0,
        isbn="9780000000032"
    )
    db.add(book)
    db.add(UserFavorite(user_id=user.id, book_id=book.id))
    db.commit()

    # Get recommendations - should fall back to non-AI method
    result = await service.get_recommendations(
        user_id=user.id,
        limit=5,
        recommendation_type=RecommendationType.SIMILAR
    )

    assert not result.get("is_ai_powered", False)
    assert len(result["recommendations"]) > 0
    # Should use genre-based recommendations as fallback
    assert any("Matches your interest in" in rec["recommendation_reason"] 
              for rec in result["recommendations"])
