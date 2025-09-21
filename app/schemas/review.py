from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.book import Book

# User response schema (simplified version)
class UserResponse(BaseModel):
    id: int
    email: str
    model_config = ConfigDict(from_attributes=True)

class ReviewBase(BaseModel):
    text: str = Field(..., min_length=5)  # changed from content to text to match DB model
    rating: int = Field(..., ge=1, le=5)

class ReviewCreate(ReviewBase):
    book_id: int

class ReviewUpdate(BaseModel):
    text: Optional[str] = Field(None, min_length=5)
    rating: Optional[int] = Field(None, ge=1, le=5)

class ReviewVoteCreate(BaseModel):
    is_helpful: bool

class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    book_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_deleted: bool = False
    helpful_votes: int = 0
    unhelpful_votes: int = 0
    user: UserResponse
    can_edit: bool  # Will be calculated based on 24-hour window
    
    model_config = ConfigDict(from_attributes=True)

class ReviewSearchParams(BaseModel):
    book_id: Optional[int] = None
    user_id: Optional[int] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    page: int = Field(default=1, gt=0)
    items_per_page: int = Field(default=50, gt=0, le=100)
    sort_by: Optional[str] = Field(None, pattern='^(date|rating|votes)$')
    sort_order: Optional[str] = Field(None, pattern='^(asc|desc)$')
