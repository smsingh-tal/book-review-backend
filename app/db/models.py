from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, DECIMAL, Date, Text, ARRAY, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone
from sqlalchemy import event

Base = declarative_base()

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    last_login = Column(DateTime(timezone=True))
    status = Column(String(20), default="active")
    profile_image_url = Column(String(255))

    # Relationships
    reviews = relationship("Review", back_populates="user")
    favorites = relationship("UserFavorite", back_populates="user")

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)
    isbn = Column(String(13), nullable=False)
    publication_date = Column(Date)
    average_rating = Column(DECIMAL(3, 2), default=0.0)
    total_reviews = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    genres = Column(ARRAY(String(50)), nullable=True)

    # Relationships
    reviews = relationship("Review", back_populates="book", cascade="all, delete-orphan")
    favorites = relationship("UserFavorite", back_populates="book")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    text = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), onupdate=utc_now)
    is_deleted = Column(Boolean, default=False)
    helpful_votes = Column(Integer, nullable=False, default=0)
    unhelpful_votes = Column(Integer, nullable=False, default=0)

    # Relationships
    user = relationship("User", back_populates="reviews")
    book = relationship("Book", back_populates="reviews")
    votes = relationship("ReviewVote", back_populates="review")

    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'book_id', name='uix_user_book_review'),
    )

    @property
    def content(self):
        """Alias for text field to maintain API compatibility"""
        return self.text

    @content.setter
    def content(self, value):
        """Setter for content that maps to text field"""
        self.text = value

class ReviewVote(Base):
    __tablename__ = "review_votes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False)
    is_helpful = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    # Relationships
    review = relationship("Review", back_populates="votes")

    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'review_id', name='uix_user_review_vote'),
    )

class UserFavorite(Base):
    __tablename__ = "user_favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    # Relationships
    user = relationship("User", back_populates="favorites")
    book = relationship("Book", back_populates="favorites")

    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'book_id', name='uix_user_book_favorite'),
    )

class InvalidatedToken(Base):
    __tablename__ = "invalidated_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(500), nullable=False, unique=True, index=True)
    invalidated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
