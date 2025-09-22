"""Tests for recommendation service"""
import json
from unittest.mock import patch, AsyncMock
import pytest
import asyncio
from sqlalchemy.orm import Session
from app.db.models import User
from app.services.recommendation import RecommendationService
from app.schemas.recommendation import RecommendationType

def test_get_user_preferences(db: Session, sample_data):
    service = RecommendationService(db)
    user_id = sample_data["user"].id
    preferences = service._get_user_preferences(user_id)
    assert isinstance(preferences, dict)
    assert len(preferences) > 0  # Since we have sample data

def test_calculate_book_score(db: Session, sample_data):
    service = RecommendationService(db)
    book = sample_data["books"][0]
    user_preferences = {"Fiction": 0.7, "Adventure": 0.3}
    score = service._calculate_book_score(book, user_preferences)
    assert isinstance(score, float)
    assert score >= 0

def test_get_popular_books(db: Session, sample_data):
    service = RecommendationService(db)
    popular_books = service._get_popular_books(limit=3)
    assert len(popular_books) <= 3
    for book in popular_books:
        assert "book_id" in book
        assert "title" in book
        assert "relevance_score" in book

@pytest.mark.asyncio
async def test_get_recommendations_new_user(db: Session, sample_data):
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

    assert result["is_fallback"] is True  # Should fall back to popular books
    assert result["recommendation_type"] == RecommendationType.TOP_RATED

@pytest.mark.asyncio
async def test_get_recommendations_with_history(db: Session, sample_data):
    service = RecommendationService(db)
    result = await service.get_recommendations(sample_data["user"].id, limit=3)

    assert len(result["recommendations"]) <= 3
    for rec in result["recommendations"]:
        assert "book_id" in rec
        assert "title" in rec
        assert "relevance_score" in rec

@pytest.mark.asyncio
async def test_get_recommendations_limit_respected(db: Session, sample_data):
    service = RecommendationService(db)
    
    # Test with different limits
    for limit in [1, 3, 5]:
        result = await service.get_recommendations(sample_data["user"].id, limit=limit)
        assert len(result["recommendations"]) <= limit

@pytest.mark.asyncio
async def test_top_rated_recommendations(db: Session, sample_data):
    service = RecommendationService(db)
    result = await service.get_recommendations(
        user_id=sample_data["user"].id,
        limit=3,
        recommendation_type=RecommendationType.TOP_RATED
    )

    assert not result["is_fallback"]  # Should not fall back for TOP_RATED type
    assert len(result["recommendations"]) > 0
    for rec in result["recommendations"]:
        assert "relevance_score" in rec

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

@pytest.mark.asyncio
async def test_ai_recommendations_with_fallback(db: Session, sample_data):
    service = RecommendationService(db)
    # Don't set the API key to trigger fallback
    service.openai_api_key = None

    result = await service.get_recommendations(
        user_id=sample_data["user"].id,
        limit=3,
        recommendation_type=RecommendationType.AI
    )
    assert result["is_fallback"] is True
    assert result["recommendation_type"] == RecommendationType.SIMILAR  # Falls back to similar books
    assert "AI recommendations unavailable" in result["fallback_reason"]

@patch('app.services.recommendation.RecommendationService._get_ai_recommendations')
@pytest.mark.asyncio
async def test_ai_recommendations_success(mock_ai, db: Session, sample_data):
    ai_response = [{
        "book_id": 1,
        "title": "AI Recommended Book",
        "author": "AI Author",
        "genres": ["Fiction"],
        "average_rating": 4.5,
        "rating_count": 100,
        "publication_year": 2024,
        "relevance_score": 0.95,
        "recommendation_reason": "AI generated reason"
    }]
    # Configure the async mock
    mock_ai.return_value = ai_response

    service = RecommendationService(db)
    service.openai_api_key = "dummy_key"  # Ensure API key is set
    result = await service.get_recommendations(
        user_id=sample_data["user"].id,
        limit=1,
        recommendation_type=RecommendationType.AI
    )

    assert result["is_fallback"] is False
    assert result["recommendation_type"] == RecommendationType.AI
    assert len(result["recommendations"]) == 1
    assert result["recommendations"][0]["book_id"] == 1
    assert result["recommendations"][0]["title"] == "AI Recommended Book"

@pytest.mark.asyncio
async def test_genre_filtered_recommendations(db: Session, sample_data):
    service = RecommendationService(db)
    # Use Fiction since we know our test data has Fiction books
    result = await service.get_recommendations(
        user_id=sample_data["user"].id,
        limit=3,
        recommendation_type=RecommendationType.SIMILAR,
        genre="Fiction"
    )

    assert result["is_fallback"] is False
    assert all("Fiction" in rec["genres"] for rec in result["recommendations"])

@pytest.mark.asyncio
@patch('app.services.recommendation.RecommendationService._get_ai_recommendations')
async def test_cache_hits_for_ai_recommendations(mock_ai, db: Session, sample_data):
    service = RecommendationService(db)
    service.openai_api_key = "dummy_key"  # Ensure API key is set

    # Set up mock for _get_ai_recommendations
    ai_response = [{
        "book_id": 1,
        "title": "AI Generated Book",
        "author": "AI Author",
        "genres": ["Fiction"],
        "average_rating": 4.5,
        "relevance_score": 0.95,
        "recommendation_reason": "AI reason"
    }]
    
    # Create a proper async side effect
    async def mock_coro(*args, **kwargs):
        return ai_response
    mock_ai.side_effect = mock_coro

    # Patch Redis functionality
    with patch.object(service, 'cache') as mock_cache:
        # First call - cache miss
        mock_cache.get.return_value = None
        result1 = await service.get_recommendations(
            user_id=sample_data["user"].id,
            limit=3,
            recommendation_type=RecommendationType.AI
        )

        # Make sure get was called
        assert mock_cache.get.called
        assert mock_cache.get.call_count == 1

        # Reset the mock for second call
        mock_cache.reset_mock()
        
        # Second call - cache hit with correct format
        cached_response = {
            "recommendations": [{
                "book_id": 1,
                "title": "Cached Book",
                "author": "Cached Author",
                "genres": ["Fiction"],
                "average_rating": 4.5,
                "relevance_score": 0.95,
                "recommendation_reason": "Cached reason"
            }],
            "is_fallback": False,
            "fallback_reason": None,
            "recommendation_type": RecommendationType.AI
        }
        mock_cache.get.return_value = json.dumps(cached_response)

        result2 = await service.get_recommendations(
            user_id=sample_data["user"].id,
            limit=3,
            recommendation_type=RecommendationType.AI
        )

        # Verify cache was hit and no setex call was made
        assert mock_cache.get.called
        assert mock_cache.get.call_count == 1
        assert not mock_cache.setex.called
        assert not result2["is_fallback"]
        assert len(result2["recommendations"]) == 1
