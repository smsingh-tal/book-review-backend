from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session
from app.db.models import Review, ReviewVote, Book
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewVoteCreate, ReviewSearchParams

class ReviewService:
    def __init__(self, db: Session):
        self.db = db

    def get_review(self, review_id: int) -> Optional[Review]:
        return self.db.query(Review).filter(Review.id == review_id, Review.is_deleted == False).first()

    def get_reviews(self, params: ReviewSearchParams) -> Tuple[List[Review], int]:
        query = self.db.query(Review).filter(Review.is_deleted == False)
        
        # Apply filters
        if params.book_id:
            query = query.filter(Review.book_id == params.book_id)
        if params.user_id:
            query = query.filter(Review.user_id == params.user_id)
        if params.rating:
            query = query.filter(Review.rating == params.rating)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply sorting
        if params.sort_by:
            if params.sort_by == 'date':
                sort_column = Review.created_at
            elif params.sort_by == 'rating':
                sort_column = Review.rating
            elif params.sort_by == 'votes':
                sort_column = Review.helpful_votes
            
            if params.sort_order == 'desc':
                sort_column = sort_column.desc()
            query = query.order_by(sort_column)
        else:
            # Default sort by latest
            query = query.order_by(Review.created_at.desc())
        
        # Apply pagination
        query = query.offset((params.page - 1) * params.items_per_page).limit(params.items_per_page)
        
        return query.all(), total_count

    def create_review(self, user_id: int, review_data: ReviewCreate) -> Review:
        print(f"ReviewService: Creating review for user {user_id} on book {review_data.book_id}")
        
        # Verify book exists
        book = self.db.query(Book).filter(Book.id == review_data.book_id).first()
        if not book:
            print(f"ReviewService: Book {review_data.book_id} not found")
            raise ValueError(f"Book with ID {review_data.book_id} not found")

        try:
            # Check if user has already reviewed this book
            existing_review = self.db.query(Review).filter(
                Review.user_id == user_id,
                Review.book_id == review_data.book_id,
                Review.is_deleted == False
            ).first()
            
            if existing_review:
                print(f"ReviewService: Updating existing review {existing_review.id}")
                # Update the existing review instead of raising error
                existing_review.text = review_data.text
                existing_review.rating = review_data.rating
                existing_review.updated_at = datetime.now(timezone.utc)
                self.db.commit()
                self.db.refresh(existing_review)
                # Now update book stats after review update
                self._update_book_rating(review_data.book_id)
                return existing_review

            print(f"ReviewService: Creating new review")
            # Create new review
            db_review = Review(
                user_id=user_id,
                book_id=review_data.book_id,
                text=review_data.text,
                rating=review_data.rating,
                created_at=datetime.now(timezone.utc)
            )
            self.db.add(db_review)
            self.db.commit()
            print(f"ReviewService: New review committed to database")
            self.db.refresh(db_review)
            # Now update book stats after review commit/refresh
            self._update_book_rating(review_data.book_id)
            print(f"ReviewService: Book rating updated")
            return db_review
        except Exception as e:
            print(f"ReviewService Error: {str(e)}")
            import traceback
            print(f"ReviewService Traceback: {traceback.format_exc()}")
            raise

    def update_review(self, user_id: int, review_id: int, review_data: ReviewUpdate) -> Optional[Review]:
        db_review = self.get_review(review_id)
        if not db_review or db_review.user_id != user_id:
            return None

        # Check 24-hour edit window
        if datetime.now(timezone.utc) - db_review.created_at > timedelta(hours=24):
            raise ValueError("Review can only be edited within 24 hours of creation")

        # Update fields
        update_data = review_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_review, field, value)
        
        db_review.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(db_review)

        # If rating was updated, update book's average rating
        if 'rating' in update_data:
            self._update_book_rating(db_review.book_id)

        return db_review

    def delete_review(self, user_id: int, review_id: int) -> bool:
        db_review = self.get_review(review_id)
        if not db_review or db_review.user_id != user_id:
            return False

        # Soft delete
        db_review.is_deleted = True
        db_review.updated_at = datetime.now(timezone.utc)
        self.db.commit()

        # Update book's average rating and review count
        self._update_book_rating(db_review.book_id)
        
        return True

    def vote_review(self, user_id: int, review_id: int, vote_data: ReviewVoteCreate) -> bool:
        db_review = self.get_review(review_id)
        if not db_review:
            return False

        # Check if user is trying to vote on their own review
        if db_review.user_id == user_id:
            raise ValueError("Cannot vote on your own review")

        # Check for existing vote
        existing_vote = self.db.query(ReviewVote).filter(
            ReviewVote.user_id == user_id,
            ReviewVote.review_id == review_id
        ).first()

        if existing_vote:
            # Update existing vote if different
            if existing_vote.is_helpful != vote_data.is_helpful:
                existing_vote.is_helpful = vote_data.is_helpful
                self.db.commit()
        else:
            # Create new vote
            db_vote = ReviewVote(
                user_id=user_id,
                review_id=review_id,
                is_helpful=vote_data.is_helpful
            )
            self.db.add(db_vote)
            self.db.commit()

        # Update helpful/unhelpful counts
        self._update_vote_counts(review_id)
        return True

    def _update_book_rating(self, book_id: int, commit: bool = True) -> None:
        """Update book's average rating and total reviews count"""
        # Get all active reviews for the book
        reviews = self.db.query(Review).filter(
            Review.book_id == book_id,
            Review.is_deleted == False
        ).all()
        total_reviews = len(reviews)
        if total_reviews > 0:
            average_rating = round(sum(r.rating for r in reviews) / total_reviews, 1)
        else:
            average_rating = 0.0

        # Update book
        book = self.db.query(Book).filter(Book.id == book_id).first()
        if book:
            book.average_rating = average_rating
            book.total_reviews = total_reviews
            if commit:
                self.db.commit()

    def _update_vote_counts(self, review_id: int) -> None:
        """Update helpful and unhelpful vote counts for a review"""
        helpful_count = self.db.query(func.count(ReviewVote.id)).filter(
            ReviewVote.review_id == review_id,
            ReviewVote.is_helpful == True
        ).scalar()

        unhelpful_count = self.db.query(func.count(ReviewVote.id)).filter(
            ReviewVote.review_id == review_id,
            ReviewVote.is_helpful == False
        ).scalar()

        review = self.get_review(review_id)
        if review:
            review.helpful_votes = helpful_count
            review.unhelpful_votes = unhelpful_count
            self.db.commit()
