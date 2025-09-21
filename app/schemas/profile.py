from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, ConfigDict

class ProfileBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: EmailStr
    name: str
    profile_image_url: Optional[str] = None

class ProfileUpdate(ProfileBase):
    pass

class FavoriteBase(BaseModel):
    book_id: int

class FavoriteCreate(FavoriteBase):
    pass

class FavoriteResponse(FavoriteBase):
    id: int
    created_at: datetime

class ReviewBase(BaseModel):
    book_id: int
    content: str
    rating: int
    
class ReviewBrief(ReviewBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

class ProfileResponse(ProfileBase):
    id: int
    created_at: datetime
    last_login: Optional[datetime]
    reviews: List[ReviewBrief]
    favorites: List[FavoriteResponse]
