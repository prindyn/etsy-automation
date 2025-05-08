from fastapi import APIRouter, Query, Body, HTTPException
from typing import List, Dict
from loguru import logger

from app.models.keyword import KeywordEntry
from app.tasks.keyword_tasks import process_keyword_task
from app.storage.keywords import KeywordCache, KeywordQueue
from app.services.redis_service import get_cache, set_cache
from app.services.keyword_scraper_etsy import get_top_keywords
from app.services.trends_scraper_google import get_trending_keywords

router = APIRouter(prefix="/keywords", tags=["Market Keyword Research"])


@router.get("/etsy", response_model=List[KeywordEntry])
async def top_etsy_keywords(
    q: str = Query("digital planner"), limit: int = Query(50, ge=1, le=100)
):
    """
    Get top Etsy keywords using scraping or API.
    """
    return await get_top_keywords(keyword=q, limit=limit)


@router.get("/google", response_model=List[KeywordEntry])
async def top_google_keywords(
    q: str = Query("digital planner"), limit: int = Query(10, ge=1, le=20)
):
    """
    Get trending keywords from Google Trends for the given query.
    """
    return await get_trending_keywords(keyword=q, limit=limit)


@router.post("/queue")
async def queue_keyword_task(
    payload: Dict[str, str] = Body(
        ..., example={"keyword": "digital planner", "source": "google"}
    )
):
    """
    Enqueue a keyword for background market research via Celery.
    """
    keyword = payload.get("keyword")
    source = payload.get("source")

    if not keyword or not source:
        raise HTTPException(
            status_code=400, detail="Both 'keyword' and 'source' are required."
        )

    queue_entry = KeywordQueue(source, keyword, {"status": "queued"})
    await set_cache(queue_entry)

    logger.info(f"Queued keyword: {keyword} from source: {source}")
    task = process_keyword_task(keyword, source)
    return {"status": "queued", "task_id": task.id}


@router.get("/", response_model=Dict)
async def get_cached_result(
    payload: Dict[str, str] = Body(
        ..., example={"q": "digital planner", "source": "google"}
    )
):
    """
    Retrieve cached research result from Redis.
    """
    storage = KeywordCache(payload.get("source"), payload.get("q"))
    result = await get_cache(storage)
    if not result:
        raise HTTPException(
            status_code=404,
            detail="No data found for this keyword",
        )
    return {"results": result}
