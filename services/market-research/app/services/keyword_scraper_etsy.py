import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
from loguru import logger
from collections import Counter

from app.core.config import settings
from app.storage.keywords import KeywordCache
from app.services.redis_service import get_cache, set_cache

ETSY_API_URL = f"{settings.ETSY_API_BASE}/listings/active"
ETSY_WEB_SEARCH_URL = f"{settings.ETSY_WEB_BASE}/search"
HEADERS = {"x-api-key": settings.ETSY_API_KEY}


async def get_top_keywords(
    keyword: str,
    limit: int = 100,
) -> List[Dict[str, str]]:
    keyword = keyword.strip().lower().replace(" ", "-") + f":{limit}"
    cache_obj = KeywordCache("etsy", keyword)

    # Try cache
    cached = await get_cache(cache_obj)
    if cached:
        return cached

    try:
        keywords = fetch_from_api(limit)
    except Exception as e:
        logger.warning(f"Etsy API failed: {e}, falling back to scraping...")
        keywords = await fetch_from_scraping(keyword, limit)

    cache_obj.value = keywords
    await set_cache(cache_obj, ttl_sec=3600)
    return keywords


def fetch_from_api(limit: int) -> List[Dict[str, str]]:
    params = {
        "limit": min(limit, 100),
        "offset": 0,
        "sort_on": "score",
        "sort_order": "desc",
        "includes": "images,tags",
    }

    response = httpx.get(ETSY_API_URL, headers=HEADERS, params=params)
    response.raise_for_status()

    listings = response.json().get("results", [])

    keywords = []
    for item in listings:
        for tag in item.get("tags", []):
            keywords.append(tag.lower())

    return _rank_keywords(keywords)


async def fetch_from_scraping(
    keyword: str,
    limit: int,
) -> List[Dict[str, str]]:
    """
    Use Etsy search page scraping as fallback if API fails.
    """
    try:
        search_url = f"{ETSY_WEB_SEARCH_URL}?q={keyword.replace(' ', '+')}"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
        }

        response = httpx.get(search_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        tags = [
            tag.text.strip().lower()
            for tag in soup.select("ul.wt-list-unstyled li span")
            if tag.text.strip()
        ]
        return _rank_keywords(tags, limit)

    except Exception as e:
        logger.error(f"Etsy scraping failed: {e}")
        return []


def _rank_keywords(tags: List[str]) -> List[Dict[str, str]]:
    tag_counts = Counter(tags)
    return [{"keyword": k, "score": v} for k, v in tag_counts.most_common()]
