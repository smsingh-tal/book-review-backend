import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.services.review import ReviewService
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewVoteCreate, ReviewSearchParams
from app.db.models import Review, Book, User, ReviewVote

@pytest.fixture
def test_user(db: Session):
    user = User(
        name="Test User",
        email="test@example.com",
        hashed_password="dummy_hash",
        created_at=datetime.now(timezone.utc)
    )
    db.add(user)
    db.commit()
    return user

@pytest.fixture
def test_book(db: Session):
    book = Book(
        title="Test Book",
        author="Test Author",
        genres=["Fiction"],
        isbn="1234567890123"  # 13 digit ISBN
    )
    db.add(book)
    db.commit()
    return book

@pytest.fixture
def test_review(db: Session, test_user: User, test_book: Book):
    review = Review(
        user_id=test_user.id,
        book_id=test_book.id,
        text="This is a test review",
        rating=4,
        created_at=datetime.now(timezone.utc)
    )
    db.add(review)
    db.commit()
    return review

def test_create_review(db: Session, test_user: User, test_book: Book):
    review_service = ReviewService(db)
    review_data = ReviewCreate(
        book_id=test_book.id,
        text="Great book!",
        rating=5
    )
    
    review = review_service.create_review(test_user.id, review_data)
    assert review.content == "Great book!"
    assert review.rating == 5
    assert review.user_id == test_user.id
    assert review.book_id == test_book.id
    assert review.is_deleted == False
    
    # Check book rating update
    db.refresh(test_book)
    assert test_book.average_rating == 5.0
    assert test_book.total_reviews == 1

def test_create_duplicate_review(db: Session, test_user: User, test_book: Book, test_review: Review):
    review_service = ReviewService(db)
    review_data = ReviewCreate(
            book_id=test_book.id,
            text="Another review",
            rating=3
    )
    # Ensure test_user has a name for not-null constraint
    test_user.name = "Duplicate User"
    db.commit()
    # The service now updates the review instead of raising, so check for update
    review_service.create_review(test_user.id, review_data)
    updated_review = db.query(Review).filter_by(user_id=test_user.id, book_id=test_book.id).first()
    assert updated_review.text == "Another review"

def test_update_review_within_window(db: Session, test_user: User, test_review: Review):
    review_service = ReviewService(db)
    update_data = ReviewUpdate(
        text="Updated content",
        rating=5
    )
    
    updated_review = review_service.update_review(test_user.id, test_review.id, update_data)
    assert updated_review is not None
    assert updated_review.text == "Updated content"
    assert updated_review.rating == 5
    assert updated_review.updated_at is not None

def test_update_review_outside_window(db: Session, test_user: User, test_review: Review):
    # Set review creation time to more than 24 hours ago
    test_review.created_at = datetime.now(timezone.utc) - timedelta(hours=25)
    db.commit()
    
    review_service = ReviewService(db)
    update_data = ReviewUpdate(text="Updated content")
    
    with pytest.raises(ValueError, match="Review can only be edited within 24 hours of creation"):
        review_service.update_review(test_user.id, test_review.id, update_data)

def test_delete_review(db: Session, test_user: User, test_review: Review, test_book: Book):
    review_service = ReviewService(db)
    
    # Delete the review
    assert review_service.delete_review(test_user.id, test_review.id) is True
    
    # Verify soft delete
    db.refresh(test_review)
    assert test_review.is_deleted is True
    
    # Check book rating update
    db.refresh(test_book)
    assert test_book.average_rating == 0.0
    assert test_book.total_reviews == 0

def test_vote_review(db: Session, test_user: User, test_review: Review):
    # Create another user to vote
    voter = User(
        name="Voter",
        email="voter@example.com",
        hashed_password="dummy_hash",
        created_at=datetime.now(timezone.utc)
    )
    db.add(voter)
    db.commit()
    
    review_service = ReviewService(db)
    vote_data = ReviewVoteCreate(is_helpful=True)
    
    # Test successful vote
    assert review_service.vote_review(voter.id, test_review.id, vote_data) is True
    
    # Verify vote counts
    db.refresh(test_review)
    assert test_review.helpful_votes == 1
    assert test_review.unhelpful_votes == 0
    
    # Test voting on own review
    with pytest.raises(ValueError, match="Cannot vote on your own review"):
        review_service.vote_review(test_user.id, test_review.id, vote_data)

def test_get_reviews_with_filters(db: Session, test_review: Review):
    review_service = ReviewService(db)
    params = ReviewSearchParams(
        book_id=test_review.book_id,
        rating=4,
        sort_by="date",
        sort_order="desc"
    )
    
    reviews, count = review_service.get_reviews(params)
    assert count == 1
    assert len(reviews) == 1
    assert reviews[0].id == test_review.id
