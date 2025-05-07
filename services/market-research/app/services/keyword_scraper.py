import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
from loguru import logger
from app.core.config import settings
from app.storage.cache import get_cached_keywords, set_cached_keywords

ETSY_API_KEY = settings.ET_SY_API_KEY
ETSY_API_URL = "https://openapi.etsy.com/v3/application/listings/active"

HEADERS = {"x-api-key": ETSY_API_KEY}


async def get_top_keywords(limit: int = 100) -> List[Dict[str, str]]:
    # Check cache first
    cached = await get_cached_keywords(limit)
    if cached:
        return cached

    # If not cached, run API or fallback
    try:
        keywords = fetch_from_api(limit)
    except Exception as e:
        logger.warning(f"API failed: {e}, falling back to scraping...")
        keywords = fetch_from_scraping(limit)

    # Cache and return
    await set_cached_keywords(limit, keywords)
    return keywords


def fetch_from_api(limit: int) -> List[Dict[str, str]]:
    """Fetch trending keywords from Etsy API listings."""
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

    ranked = rank_keywords(keywords)
    return ranked[:limit]


def fetch_from_scraping(limit: int) -> List[Dict[str, str]]:
    """Scrape Etsy search result tags for popular products."""
    search_url = "https://www.etsy.com/search?q=digital+planner"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
    }

    # TEMPORARY: return static top keywords
    return [
        {"keyword": "digital planner", "count": 50},
        {"keyword": "goodnotes", "count": 40},
        {"keyword": "printable", "count": 35},
        {"keyword": "budget planner", "count": 25},
        {"keyword": "notability", "count": 20},
    ][:limit]

    response = httpx.get(search_url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    tags = []

    for tag_elem in soup.select("ul.wt-list-unstyled li span"):
        tag_text = tag_elem.text.strip().lower()
        if tag_text:
            tags.append(tag_text)

    ranked = rank_keywords(tags)
    return ranked[:limit]


def rank_keywords(tags: List[str]) -> List[Dict[str, str]]:
    """Count tag frequency and return ranked list."""
    from collections import Counter

    tag_counts = Counter(tags)
    ranked = [{"keyword": k, "count": v} for k, v in tag_counts.most_common()]
    return ranked
