from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.auth import get_current_user
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from app.services.recommendation import RecommendationService

router = APIRouter()

@router.post("/", response_model=RecommendationResponse)
async def get_recommendations(
    request: RecommendationRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized book recommendations for the current user.
    
    Available recommendation types:
    - top_rated: Returns highest rated books matching user's preferences
    - similar: Returns books similar to user's favorites and highly rated books
    - ai: Returns AI-powered recommendations using OpenAI (falls back to similar if AI fails)
    
    Optional parameters:
    - limit: Number of recommendations to return (default: 10, max: 50)
    - genre: Filter recommendations by specific genre
    """
    try:
        recommendation_service = RecommendationService(db)
        result = await recommendation_service.get_recommendations(
            user_id=current_user.id,
            limit=request.limit,
            recommendation_type=request.recommendation_type,
            genre=request.genre
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting recommendations: {str(e)}"
        )
