from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.auth import get_current_user
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from app.services.recommendation import RecommendationService

router = APIRouter()

@router.post("/recommendations", response_model=RecommendationResponse)
def get_recommendations(
    request: RecommendationRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized book recommendations for the current user.
    Uses a combination of user preferences, reading history, and ratings
    to provide relevant recommendations.
    """
    try:
        recommendation_service = RecommendationService(db)
        result = recommendation_service.get_recommendations(
            user_id=current_user.id,
            limit=request.limit
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting recommendations: {str(e)}"
        )
