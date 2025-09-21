from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.models import User, Review, UserFavorite, Book
from app.schemas.profile import ProfileUpdate

class ProfileService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_profile(self, user_id: int) -> Optional[User]:
        """Get a user's profile by ID"""
        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    def update_profile(self, user_id: int, profile_data: ProfileUpdate) -> User:
        """Update a user's profile"""
        user = self.get_user_profile(user_id)
        if not user:
            raise ValueError("User not found")
        
        for field, value in profile_data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_reviews(self, user_id: int, limit: int = 10, offset: int = 0) -> List[Review]:
        """Get a user's reviews"""
        return (
            self.db.query(Review)
            .filter(Review.user_id == user_id, Review.is_deleted == False)
            .order_by(desc(Review.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_user_favorites(self, user_id: int, limit: int = 10, offset: int = 0) -> List[UserFavorite]:
        """Get a user's favorite books"""
        return (
            self.db.query(UserFavorite)
            .filter(UserFavorite.user_id == user_id)
            .order_by(desc(UserFavorite.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def add_favorite(self, user_id: int, book_id: int) -> UserFavorite:
        """Add a book to user's favorites"""
        # Check if book exists
        book = self.db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise ValueError("Book not found")
            
        # Check if already favorited
        existing = (
            self.db.query(UserFavorite)
            .filter(
                UserFavorite.user_id == user_id,
                UserFavorite.book_id == book_id
            )
            .first()
        )
        if existing:
            return existing

        favorite = UserFavorite(
            user_id=user_id,
            book_id=book_id,
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(favorite)
        self.db.commit()
        self.db.refresh(favorite)
        return favorite

    def remove_favorite(self, user_id: int, book_id: int) -> bool:
        """Remove a book from user's favorites"""
        result = (
            self.db.query(UserFavorite)
            .filter(
                UserFavorite.user_id == user_id,
                UserFavorite.book_id == book_id
            )
            .delete()
        )
        self.db.commit()
        return bool(result)

    def update_last_login(self, user_id: int) -> None:
        """Update user's last login time"""
        user = self.get_user_profile(user_id)
        if user:
            user.last_login = datetime.now(timezone.utc)
            self.db.commit()
