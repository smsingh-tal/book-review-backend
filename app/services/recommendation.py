import os
from typing import List, Dict, Set, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from app.db.models import Book, Review, User, UserFavorite
from app.schemas.recommendation import RecommendationType
import random
from datetime import datetime, timedelta
import aiohttp
import asyncio
from functools import lru_cache
from redis import Redis
import json

class RecommendationService:
    def __init__(self, db: Session):
        self.db = db
        try:
            self.cache = Redis(host='localhost', port=6379, db=0, decode_responses=True)
            self.cache.ping()  # Test connection
        except:
            self.cache = None  # Disable caching if Redis is not available
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.cache_ttl = 24 * 60 * 60  # 24 hours in seconds

    def _create_book_recommendation(self, book: Book, score: float, reason: str) -> Dict:
        """Helper method to create a standardized book recommendation dictionary."""
        return {
            "book_id": book.id,
            "title": book.title,
            "author": book.author,
            "genres": book.genres or [],
            "average_rating": float(book.average_rating or 0),
            "rating_count": book.total_reviews or 0,
            "relevance_score": float(score),
            "recommendation_reason": reason,
            "publication_year": book.publication_date.year if book.publication_date else None
        }

    def _get_popular_books(self, limit: int, exclude_ids: Set[int] = None) -> List[Dict]:
        """Fallback method to get popular books."""
        if exclude_ids is None:
            exclude_ids = set()
            
        popular_books = (
            self.db.query(Book)
            .filter(
                and_(
                    Book.id.notin_(exclude_ids),
                    Book.average_rating >= 3.5,
                    Book.total_reviews > 0
                )
            )
            .order_by(desc(Book.total_reviews), desc(Book.average_rating))
            .limit(limit)
            .all()
        )
        
        return [
            self._create_book_recommendation(
                book=book,
                score=float(book.average_rating or 0) * (1 + min((book.total_reviews or 0) / 100, 0.5)),
                reason=f"Popular book with {book.total_reviews or 0} reviews"
            )
            for book in popular_books
        ]

    async def get_recommendations(
        self,
        user_id: int,
        limit: int = 10,
        recommendation_type: RecommendationType = RecommendationType.TOP_RATED,
        genre: Optional[str] = None
    ) -> Dict[str, any]:
        """Get personalized book recommendations for a user."""
        try:
            # Get user's read books to exclude
            exclude_ids = set()
            user_reviews = self.db.query(Review).filter(Review.user_id == user_id).all()
            user_favorites = self.db.query(UserFavorite).filter(UserFavorite.user_id == user_id).all()
            
            for review in user_reviews:
                exclude_ids.add(review.book_id)
            for favorite in user_favorites:
                exclude_ids.add(favorite.book_id)

            # Query books excluding read ones and applying filters
            query = self.db.query(Book).filter(
                and_(
                    Book.id.notin_(exclude_ids),
                    Book.average_rating.isnot(None),
                    Book.total_reviews > 0
                )
            )
            
            if genre:
                query = query.filter(Book.genres.contains([genre]))
                
            books = query.all()
            if not books:
                # Fallback to popular books if no matches found
                recommendations = self._get_popular_books(limit)
                return {
                    "recommendations": recommendations,
                    "is_fallback": True,
                    "fallback_reason": f"No {'genre-specific ' if genre else ''}books found",
                    "recommendation_type": recommendation_type
                }

            scored_books = []
            for book in books:
                try:
                    # Calculate base score from rating
                    base_score = float(book.average_rating or 0)
                    
                    # Apply review count boost
                    review_boost = min((book.total_reviews or 0) / 100.0, 0.5)
                    
                    # Calculate genre preference boost
                    genre_boost = 0.5 if genre and genre in (book.genres or []) else 0
                    
                    # Calculate final score
                    final_score = max(base_score * (1 + review_boost + genre_boost), 0)
                    
                    if final_score > 0:  # Only include books with positive scores
                        scored_books.append((
                            book,
                            final_score,
                            f"Highly rated book{' in your preferred genre' if genre_boost > 0 else ''}"
                        ))
                except (TypeError, ValueError):
                    continue  # Skip books with invalid data

            # Sort by score and take top N
            scored_books.sort(key=lambda x: x[1], reverse=True)
            recommendations = [
                self._create_book_recommendation(book=book, score=score, reason=reason)
                for book, score, reason in scored_books[:limit]
            ]

            return {
                "recommendations": recommendations,
                "is_fallback": False,
                "fallback_reason": None,
                "recommendation_type": recommendation_type
            }
            
        except Exception as e:
            # Log the error and fall back to popular books
            print(f"Error in get_recommendations: {str(e)}")
            recommendations = self._get_popular_books(limit)
            return {
                "recommendations": recommendations,
                "is_fallback": True,
                "fallback_reason": "Error processing recommendations",
                "recommendation_type": recommendation_type
            }
