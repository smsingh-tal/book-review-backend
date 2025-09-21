from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.auth import get_current_user
from app.db.session import get_db
from app.schemas.profile import ProfileResponse, ProfileUpdate, FavoriteResponse, ReviewBrief
from app.services.profile import ProfileService

router = APIRouter(tags=["profile"])

@router.get("/me", response_model=ProfileResponse)
def get_my_profile(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile"""
    profile_service = ProfileService(db)
    user = profile_service.get_user_profile(current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="Profile not found")
    return user

@router.put("/me", response_model=ProfileResponse)
def update_my_profile(
    profile_data: ProfileUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    profile_service = ProfileService(db)
    try:
        user = profile_service.update_profile(current_user.id, profile_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me/reviews", response_model=List[ReviewBrief])
def get_my_reviews(
    limit: int = 10,
    offset: int = 0,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's reviews"""
    profile_service = ProfileService(db)
    return profile_service.get_user_reviews(current_user.id, limit, offset)

@router.get("/me/favorites", response_model=List[FavoriteResponse])
def get_my_favorites(
    limit: int = 10,
    offset: int = 0,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's favorite books"""
    profile_service = ProfileService(db)
    return profile_service.get_user_favorites(current_user.id, limit, offset)

@router.post("/me/favorites/{book_id}", response_model=FavoriteResponse)
def add_to_favorites(
    book_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a book to current user's favorites"""
    profile_service = ProfileService(db)
    try:
        return profile_service.add_favorite(current_user.id, book_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/me/favorites/{book_id}", status_code=204)
def remove_from_favorites(
    book_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a book from current user's favorites"""
    profile_service = ProfileService(db)
    if not profile_service.remove_favorite(current_user.id, book_id):
        raise HTTPException(status_code=404, detail="Book not found in favorites")
