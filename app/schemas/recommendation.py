from pydantic import BaseModel
from typing import List

class RecommendationRequest(BaseModel):
    user_id: int
    limit: int = 10
    
class BookRecommendation(BaseModel):
    book_id: int
    title: str
    author: str
    genres: List[str]
    average_rating: float
    relevance_score: float
    recommendation_reason: str

class RecommendationResponse(BaseModel):
    recommendations: List[BookRecommendation]
    is_fallback: bool = False
