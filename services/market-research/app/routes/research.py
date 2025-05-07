from fastapi import APIRouter, Query
from app.services.keyword_scraper import get_top_keywords
from typing import List
from app.models.keyword import KeywordEntry

router = APIRouter(prefix="/keywords", tags=["Market Research"])


@router.get("/top", response_model=List[KeywordEntry])
async def top_keywords(limit: int = Query(50, ge=1, le=100)):
    """
    Get top Etsy keywords either via API or scraping fallback.

    Query Params:
    - limit: number of keywords to return (default: 50)
    """
    return await get_top_keywords(limit)
