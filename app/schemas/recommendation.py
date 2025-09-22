from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional

class RecommendationType(str, Enum):
    TOP_RATED = "top_rated"
    SIMILAR = "similar"
    AI = "ai"

class RecommendationRequest(BaseModel):
    limit: int = Field(default=10, ge=1, le=50)
    recommendation_type: RecommendationType = RecommendationType.TOP_RATED
    genre: Optional[str] = None
    
class BookRecommendation(BaseModel):
    book_id: int
    title: str
    author: str
    genres: List[str]
    average_rating: float
    relevance_score: float
    recommendation_reason: str
    rating_count: int
    publication_year: Optional[int] = None

class RecommendationResponse(BaseModel):
    recommendations: List[BookRecommendation]
    is_fallback: bool = False
    fallback_reason: Optional[str] = None
    recommendation_type: RecommendationType
