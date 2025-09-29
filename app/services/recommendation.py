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
from collections import Counter
import numpy as np
from openai import AsyncOpenAI
import logging
from dotenv import load_dotenv
from app.core.config import get_settings

# Load environment variables
load_dotenv()

class RecommendationService:
    def __init__(self, db: Session):
        self.db = db
        settings = get_settings()
        try:
            self.cache = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            self.cache.ping()
        except:
            self.cache = None
            logging.warning("Redis not available, caching disabled")
            
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.cache_ttl = 24 * 60 * 60  # 24 hours

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

    def _get_user_genre_preferences(self, user_id: int) -> Dict[str, float]:
        """Get user's genre preferences based on their favorite books."""
        favorites = self.db.query(UserFavorite).filter(UserFavorite.user_id == user_id).all()
        if not favorites:
            return {}

        # Get all favorite books
        favorite_book_ids = [fav.book_id for fav in favorites]
        favorite_books = self.db.query(Book).filter(Book.id.in_(favorite_book_ids)).all()

        # First collect all unique genres to give equal weight initially
        unique_genres = set()
        for book in favorite_books:
            if book.genres:
                unique_genres.update(book.genres)

        # Then count how many books have each genre
        genre_counter = Counter()
        for book in favorite_books:
            if book.genres:
                # Count each genre once per book
                genres_in_book = set(book.genres)
                for genre in genres_in_book:
                    genre_counter[genre] += 1

        # Calculate genre weights using book-level counts
        total_books = len(favorite_books)
        if total_books == 0:
            return {}

        # Calculate base weights
        weights = {genre: count/total_books for genre, count in genre_counter.items()}
        logging.info(f"Raw genre weights: {weights}")
        return weights

    async def get_recommendations(
        self,
        user_id: int,
        limit: int = 10,
        recommendation_type: RecommendationType = RecommendationType.TOP_RATED,
        genre: Optional[str] = None
    ) -> Dict[str, any]:
        """Get personalized recommendations for a user."""
        return await self._get_recommendations_async(
            user_id=user_id,
            limit=limit,
            recommendation_type=recommendation_type,
            genre=genre
        )

    def _get_similar_recommendations(
        self, 
        books: List[Book], 
        user_preferences: Dict[str, float],
        limit: int
    ) -> List[Tuple[Book, float, str]]:
        """Get recommendations based on genre preferences."""
        # First collect exact genre sets from user's preferences to prioritize exact matches
        logging.info(f"User preferences: {user_preferences}")
        
        user_genre_sets = set()
        for genre_set in books:
            if not genre_set.genres or not set(genre_set.genres).intersection(set(user_preferences.keys())):
                continue
            user_genre_sets.add(frozenset(genre_set.genres))
            
        logging.info(f"User genre sets: {[list(gs) for gs in user_genre_sets]}")

        scored_books = []
        for book in books:
            if not book.genres:
                continue

            # Find matching genres
            book_genres = set(book.genres)
            logging.info(f"Book {book.title} genres: {book_genres}")
            matching_genres = [g for g in book.genres if g in user_preferences]
            if not matching_genres:
                logging.info(f"Book {book.title} has no matching genres")
                continue
            logging.info(f"Book {book.title} matching genres: {matching_genres}")
            
            # Calculate match percentages and bonuses
            n_matches = len(matching_genres)
            n_book_genres = len(book_genres)
            
            # Score based on total preference weight of matching genres
            preference_score = 0
            for genre in matching_genres:
                # Perfect match gets full weight
                if genre in book.genres:
                    preference_score += user_preferences[genre]
                # Partial match gets reduced weight
                else:
                    preference_score += user_preferences[genre] * 0.5
            base_score = preference_score * 100.0  # Scale up to make preference matches dominant
            logging.info(f"Book {book.title}: Base score {base_score} from preference score {preference_score}")
            
            # Add bonus for matching more genres as a percentage
            match_percentage = n_matches / n_book_genres
            percentage_bonus = match_percentage * 10.0  # Up to 10 points for 100% match
            logging.info(f"Book {book.title}: Percentage bonus {percentage_bonus} from {n_matches}/{n_book_genres} matches")
            
            # Calculate exact genre set match bonus for exact user genre sets
            exact_match_bonus = 50.0 if frozenset(book.genres) in user_genre_sets else 0.0
            logging.info(f"Book {book.title}: Exact match bonus {exact_match_bonus}")
            
            # Combine scores with proper weighting - weighted preference score dominates
            final_score = base_score + percentage_bonus + exact_match_bonus
            
            # Add a tiny boost for higher ratings only to break ties
            rating_boost = (float(book.average_rating or 3.0) - 3.0) / 1000.0
            final_score += rating_boost
            logging.info(f"Book {book.title}: Final score {final_score} (base={base_score}, pct_bonus={percentage_bonus}, exact_bonus={exact_match_bonus}, rating_boost={rating_boost})")
            
            reason = f"Matches your interest in {', '.join(matching_genres)}"
            scored_books.append((book, final_score, reason))

        # Sort by score (which already factors in genre matches)
        return sorted(
            scored_books,
            key=lambda x: x[1],  # Sort by score only
            reverse=True
        )[:limit]

    def _get_top_rated_recommendations(self, books: List[Book], limit: int, genre: Optional[str] = None) -> List[Tuple[Book, float, str]]:
        """Get recommendations based on highest ratings and review counts."""
        scored_books = []
        for book in books:
            try:
                # Use average rating as the base score
                base_score = float(book.average_rating or 0)
                
                # Only apply a small boost based on number of reviews to break ties
                # between books with same rating
                review_boost = min((book.total_reviews or 0) / 1000.0, 0.1)
                
                final_score = base_score + review_boost
                
                reason = f"Top rated book with {book.average_rating:.1f} rating"
                if book.total_reviews:
                    reason += f" from {book.total_reviews} reviews"
                if genre and genre in (book.genres or []):
                    reason = f"Top rated {genre} book"
                
                if final_score > 0:
                    scored_books.append((book, final_score, reason))
                    
            except (TypeError, ValueError):
                continue
                
        return sorted(scored_books, key=lambda x: x[1], reverse=True)[:limit]

    async def _get_book_embeddings(self, book: Book) -> Optional[List[float]]:
        """Get embeddings for book content using OpenAI API"""
        cache_key = f"book_embedding:{book.id}"
        
        # Try to get from cache first
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                return json.loads(cached)
        
        # Create a rich text representation of the book
        text = (
            f"Title: {book.title}\n"
            f"Author: {book.author}\n"
            f"Genres: {', '.join(book.genres or [])}\n"
            f"Description: {book.description or ''}"
        )
        
        try:
            response = await self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            embedding = response.data[0].embedding
            
            # Cache the embedding
            if self.cache:
                self.cache.setex(
                    cache_key,
                    self.cache_ttl,
                    json.dumps(embedding)
                )
            
            return embedding
        except Exception as e:
            logging.error(f"Error getting embeddings for book {book.id}: {str(e)}")
            return None

    async def _get_user_interest_embedding(self, user_id: int) -> Optional[List[float]]:
        """Get an embedding representing user's reading interests"""
        cache_key = f"user_embedding:{user_id}"
        
        # Try cache first
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                return json.loads(cached)
        
        # Get user's favorite and reviewed books
        favorites = self.db.query(Book).join(UserFavorite).filter(UserFavorite.user_id == user_id).all()
        reviews = self.db.query(Book, Review).join(Review).filter(Review.user_id == user_id).all()
        
        if not favorites and not reviews:
            return None
            
        # Create a text representation of user's interests
        interests = []
        
        # Add favorite books
        for book in favorites:
            interests.append(f"Likes: {book.title} by {book.author}")
            if book.genres:
                interests.extend(f"Interested in {genre}" for genre in book.genres)
        
        # Add reviewed books with sentiment
        for book, review in reviews:
            sentiment = "likes" if review.rating >= 4 else "neutral about" if review.rating >= 3 else "dislikes"
            interests.append(f"{sentiment}: {book.title} by {book.author}")
            if book.genres:
                interests.extend(f"Has read {genre}" for genre in book.genres)
        
        try:
            # Get embedding for user's interests
            response = await self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input="\n".join(interests)
            )
            embedding = response.data[0].embedding
            
            # Cache the embedding
            if self.cache:
                self.cache.setex(
                    cache_key,
                    self.cache_ttl,
                    json.dumps(embedding)
                )
            
            return embedding
        except Exception as e:
            logging.error(f"Error getting user interest embedding: {str(e)}")
            return None

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2:
            return 0.0
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

    async def _get_ai_recommendations(
        self,
        books: List[Book],
        user_id: int,
        limit: int,
        genre: Optional[str] = None
    ) -> List[Tuple[Book, float, str]]:
        """Get AI-powered recommendations using OpenAI embeddings"""
        try:
            # Get user's interest embedding
            user_embedding = await self._get_user_interest_embedding(user_id)
            if not user_embedding:
                return []
            
            scored_books = []
            for book in books:
                # Get book embedding
                book_embedding = await self._get_book_embeddings(book)
                if not book_embedding:
                    continue
                
                # Calculate similarity score
                similarity = self._cosine_similarity(user_embedding, book_embedding)
                
                # Apply genre boost if matching requested genre
                if genre and genre in (book.genres or []):
                    similarity *= 1.2
                
                # Create explanation
                reason = "AI recommendation based on your reading history"
                if genre and genre in (book.genres or []):
                    reason = f"AI recommendation matching your interest in {genre}"
                
                scored_books.append((book, similarity, reason))
            
            # Sort by similarity and return top matches
            return sorted(scored_books, key=lambda x: x[1], reverse=True)[:limit]
            
        except Exception as e:
            logging.error(f"Error in AI recommendations: {str(e)}")
            return []

    async def _get_recommendations_async(
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
                    Book.average_rating.isnot(None)
                )
            )
            
            if genre:
                query = query.filter(
                    Book.genres.isnot(None),
                    func.array_to_string(Book.genres, ',', '').ilike(f'%{genre}%')
                )
            books = query.all()
            
            if not books:
                # Fallback to popular books if no matches found
                recommendations = self._get_popular_books(limit)
                return {
                    "recommendations": recommendations,
                    "is_fallback": True,
                    "fallback_reason": f"No {'genre-specific ' if genre else ''}books found",
                    "recommendation_type": recommendation_type,
                    "is_ai_powered": False
                }

            # Get recommendations based on type
            if recommendation_type == RecommendationType.TOP_RATED:
                scored_books = self._get_top_rated_recommendations(books, limit, genre)
                is_ai_powered = False
            else:  # SIMILAR
                # Try AI recommendations first since they can capture more nuanced patterns
                try:
                    logging.info("Attempting AI recommendations")
                    scored_books = await self._get_ai_recommendations(books, user_id, limit, genre)
                    logging.info("AI recommendations succeeded")
                    is_ai_powered = True  # Only set to True if AI call succeeds
                except Exception as e:
                    logging.error(f"AI recommendations failed: {str(e)}")
                    scored_books = []
                    is_ai_powered = False  # Set to False on AI failure
                    logging.info("Falling back to genre-based recommendations")

                if not scored_books:
                    # Fall back to genre-based
                    user_preferences = self._get_user_genre_preferences(user_id)
                    if user_preferences:
                        scored_books = self._get_similar_recommendations(books, user_preferences, limit)
                    else:
                        scored_books = self._get_top_rated_recommendations(books, limit, genre)
                    if not scored_books:
                        scored_books = self._get_top_rated_recommendations(books, limit, genre)

            # Create recommendation objects
            recommendations = [
                self._create_book_recommendation(book=book, score=score, reason=reason)
                for book, score, reason in scored_books
            ]

            return {
                "recommendations": recommendations,
                "is_fallback": False,
                "recommendation_type": recommendation_type,
                "is_ai_powered": is_ai_powered
            }
            
        except Exception as e:
            logging.error(f"Error in get_recommendations: {str(e)}")
            recommendations = self._get_popular_books(limit)
            return {
                "recommendations": recommendations,
                "is_fallback": True,
                "fallback_reason": "Error processing recommendations",
                "recommendation_type": recommendation_type,
                "is_ai_powered": False
            }
