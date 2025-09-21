from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.auth import get_current_user
from app.db.session import get_db
from app.schemas.review import (
    ReviewResponse,
    ReviewCreate,
    ReviewUpdate,
    ReviewVoteCreate,
    ReviewSearchParams
)
from app.services.review import ReviewService

router = APIRouter(prefix="/v1/reviews", tags=["reviews"])

@router.post("", response_model=ReviewResponse)
def create_review(
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        print(f"Creating review for user {current_user.id} on book {review.book_id}")
        review_service = ReviewService(db)
        result = review_service.create_review(current_user.id, review)
        print(f"Review created successfully: {result.id}")
        
        # Calculate can_edit field (within 24 hours)
        can_edit = (datetime.now(timezone.utc) - result.created_at).total_seconds() < 24 * 3600
        
        # Create the response with all required fields
        response_dict = {
            "id": result.id,
            "text": result.text,
            "rating": result.rating,
            "user_id": result.user_id,
            "book_id": result.book_id,
            "created_at": result.created_at,
            "updated_at": result.updated_at,
            "is_deleted": result.is_deleted,
            "helpful_votes": result.helpful_votes,
            "unhelpful_votes": result.unhelpful_votes,
            "user": {"id": result.user.id, "email": result.user.email},
            "can_edit": can_edit
        }
        
        return ReviewResponse.model_validate(response_dict)
    except ValueError as e:
        print(f"ValueError in create_review: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error in create_review: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=dict)
def list_reviews(
    book_id: Optional[int] = None,
    user_id: Optional[int] = None,
    rating: Optional[int] = Query(None, ge=1, le=5),
    sort_by: Optional[str] = Query(None, pattern="^(date|rating|votes)$"),
    sort_order: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    page: int = Query(1, gt=0),
    items_per_page: int = Query(50, gt=0, le=100),
    db: Session = Depends(get_db)
):
    review_service = ReviewService(db)
    search_params = ReviewSearchParams(
        book_id=book_id,
        user_id=user_id,
        rating=rating,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        items_per_page=items_per_page
    )
    reviews, total_count = review_service.get_reviews(search_params)
    
    # Convert each SQLAlchemy Review model to Pydantic ReviewResponse
    review_items = []
    for review in reviews:
        # Calculate if the review can be edited (within 24 hours)
        can_edit = (datetime.now(timezone.utc) - review.created_at).total_seconds() < 24 * 3600
        review_dict = {
            "id": review.id,
            "text": review.text,
            "rating": review.rating,
            "user_id": review.user_id,
            "book_id": review.book_id,
            "created_at": review.created_at,
            "updated_at": review.updated_at,
            "is_deleted": review.is_deleted,
            "helpful_votes": review.helpful_votes,
            "unhelpful_votes": review.unhelpful_votes,
            "user": {"id": review.user.id, "email": review.user.email},
            "can_edit": can_edit
        }
        review_items.append(ReviewResponse.model_validate(review_dict))
    
    return {
        "items": review_items,
        "total": total_count,
        "page": page,
        "items_per_page": items_per_page,
        "total_pages": (total_count + items_per_page - 1) // items_per_page
    }

@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(review_id: int, db: Session = Depends(get_db)):
    review_service = ReviewService(db)
    review = review_service.get_review(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    review: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        review_service = ReviewService(db)
        updated_review = review_service.update_review(current_user.id, review_id, review)
        if not updated_review:
            raise HTTPException(status_code=404, detail="Review not found or unauthorized")
        return updated_review
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    review_service = ReviewService(db)
    if not review_service.delete_review(current_user.id, review_id):
        raise HTTPException(status_code=404, detail="Review not found or unauthorized")
    return {"message": "Review deleted successfully"}

@router.post("/{review_id}/vote")
def vote_review(
    review_id: int,
    vote: ReviewVoteCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        review_service = ReviewService(db)
        if not review_service.vote_review(current_user.id, review_id, vote):
            raise HTTPException(status_code=404, detail="Review not found")
        return {"message": "Vote recorded successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
