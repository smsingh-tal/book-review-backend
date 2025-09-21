from typing import List, Dict, Set, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.db.models import Book, Review, User, UserFavorite
import random

class RecommendationService:
    def __init__(self, db: Session):
        self.db = db
        
    def _get_user_preferences(self, user_id: int) -> Dict[str, float]:
        """Get user's genre preferences based on their reviews and favorites."""
        # Get all books reviewed or favorited by user
        user_reviews = self.db.query(Review).filter(Review.user_id == user_id).all()
        user_favorites = self.db.query(UserFavorite).filter(UserFavorite.user_id == user_id).all()
        
        # Collect book IDs
        book_ids = set()
        book_ids.update(review.book_id for review in user_reviews)
        book_ids.update(favorite.book_id for favorite in user_favorites)
        
        # Get all books
        books = self.db.query(Book).filter(Book.id.in_(book_ids)).all()
        
        # Calculate genre preferences
        genre_counts: Dict[str, int] = {}
        for book in books:
            for genre in book.genres:
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
                
        # Normalize preferences
        total = sum(genre_counts.values()) if genre_counts else 1
        return {genre: count/total for genre, count in genre_counts.items()}
    
    def _calculate_book_score(self, book: Book, user_preferences: Dict[str, float]) -> float:
        """Calculate a relevance score for a book based on user preferences."""
        # Base score is the book's average rating
        score = float(book.average_rating)
        
        # Add genre preference boost
        genre_boost = sum(user_preferences.get(genre, 0) for genre in book.genres)
        score += genre_boost
        
        return score
        
    def _get_popular_books(self, limit: int, exclude_ids: Set[int]) -> List[Dict]:
        """Fallback method to get popular books."""
        popular_books = (
            self.db.query(Book)
            .filter(Book.id.notin_(exclude_ids))
            .order_by(desc(Book.average_rating))
            .limit(limit)
            .all()
        )
        
        return [
            {
                "book_id": book.id,
                "title": book.title,
                "author": book.author,
                "genres": book.genres,
                "average_rating": book.average_rating,
                "relevance_score": book.average_rating,
                "recommendation_reason": "Popular book with high ratings"
            }
            for book in popular_books
        ]
    
    def get_recommendations(self, user_id: int, limit: int = 10) -> Dict[str, any]:
        """Get personalized book recommendations for a user."""
        try:
            # Get user's genre preferences
            user_preferences = self._get_user_preferences(user_id)
            
            # Get books already reviewed or favorited by user
            user_reviews = self.db.query(Review).filter(Review.user_id == user_id).all()
            user_favorites = self.db.query(UserFavorite).filter(UserFavorite.user_id == user_id).all()
            
            # Collect book IDs to exclude
            exclude_ids = set()
            exclude_ids.update(review.book_id for review in user_reviews)
            exclude_ids.update(favorite.book_id for favorite in user_favorites)
            
            # If user has no preferences, return popular books
            if not user_preferences:
                return {
                    "recommendations": self._get_popular_books(limit, exclude_ids),
                    "is_fallback": True
                }
                
            # Get all books not reviewed/favorited by user
            candidate_books = (
                self.db.query(Book)
                .filter(Book.id.notin_(exclude_ids))
                .all()
            )
            
            # Score and sort books
            scored_books = []
            for book in candidate_books:
                score = self._calculate_book_score(book, user_preferences)
                
                # Calculate primary genre match
                matching_genres = set(book.genres) & set(user_preferences.keys())
                reason = (
                    f"Matches your interest in {', '.join(matching_genres)}" 
                    if matching_genres 
                    else "Popular book you might enjoy"
                )
                
                scored_books.append({
                    "book_id": book.id,
                    "title": book.title,
                    "author": book.author,
                    "genres": book.genres,
                    "average_rating": book.average_rating,
                    "relevance_score": score,
                    "recommendation_reason": reason
                })
                
            # Sort by score and return top N
            recommendations = sorted(
                scored_books, 
                key=lambda x: x["relevance_score"], 
                reverse=True
            )[:limit]
            
            return {
                "recommendations": recommendations,
                "is_fallback": False
            }
            
        except Exception as e:
            # If anything fails, return popular books as fallback
            return {
                "recommendations": self._get_popular_books(limit, set()),
                "is_fallback": True
            }
