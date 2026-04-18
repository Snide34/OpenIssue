"""
Duplicate Detection API
Enhanced duplicate analysis with reasoning
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.services.duplicate_detector import duplicate_detector

router = APIRouter(prefix="/duplicates", tags=["Duplicates"])


class DuplicateCheckRequest(BaseModel):
    """Request model for duplicate check"""
    title: str = Field(..., min_length=1, description="Issue title")
    description: str = Field(default="", description="Issue description")
    top_k: int = Field(default=10, ge=1, le=50, description="Number of similar issues to find")


@router.post("/check")
async def check_duplicates(request: DuplicateCheckRequest):
    """
    Check for duplicate issues with detailed analysis
    
    Returns:
    - similar_issues: List of similar issues with scores
    - duplicate_level: definite/likely/possible/none
    - reasoning: Explanation of why these are duplicates
    - confidence: Confidence score (0-1)
    - clusters: Issues grouped by similarity level
    - statistics: Summary statistics
    """
    
    try:
        result = duplicate_detector.analyze_duplicates(
            title=request.title,
            description=request.description,
            top_k=request.top_k
        )
        
        return {
            "success": True,
            **result
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Duplicate detection failed: {str(e)}"
        )


@router.get("/stats")
async def get_duplicate_stats():
    """
    Get overall duplicate detection statistics
    """
    # TODO: Implement statistics from database
    return {
        "total_checks": 0,
        "duplicates_found": 0,
        "average_similarity": 0,
        "most_duplicated_issues": []
    }
