import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
from collections import Counter
from loguru import logger

from app.core.config import settings
from app.storage.keywords import KeywordCache
from app.services.redis_service import get_cache, set_cache
from app.common.keywords import KeywordExtractor

GUMROAD_SEARCH_URL = f"{settings.GUMROAD_WEB_BASE}/discover"


async def get_top_keywords(
    keyword: str,
    limit: int = 100,
) -> List[Dict[str, str]]:
    keyword = keyword.strip().lower().replace(" ", "+") + f":{limit}"
    cache_obj = KeywordCache("gumroad", keyword)

    # Try cache first
    # cached = await get_cache(cache_obj)
    # if cached:
    #     return cached

    try:
        extractor = KeywordExtractor(top_n=limit, use_noun_chunks_filter=True)
        keywords = await fetch_from_scraping(keyword, limit, False)
        keywords = extractor.extract(keywords, keyword)
    except Exception as e:
        logger.error(f"Gumroad scraping failed: {e}")
        keywords = []

    cache_obj.value = keywords
    await set_cache(cache_obj, ttl_sec=3600)
    return keywords


async def fetch_from_scraping(
    keyword: str, limit: int, rank: bool = True
) -> List[Dict[str, str]]:
    results = []
    offset = 0
    page_size = 36
    keyword_param = keyword.replace(" ", "+")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
    }

    async with httpx.AsyncClient() as client:
        while len(results) < limit:
            url = f"{GUMROAD_SEARCH_URL}?query={keyword_param}&from={offset}"
            response = await client.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            titles = [
                tag.text.strip().lower()
                for card in soup.select("article.product-card")
                for tag in card.select("h4")
                if tag.text.strip()
            ]

            if not titles:
                break

            results.extend(titles)
            offset += page_size + 1 if offset == 0 else page_size

    return _rank_keywords(results[:limit], limit) if rank else results


def _rank_keywords(tags: List[str], limit: int) -> List[Dict[str, str]]:
    tag_counts = Counter(tags)
    return [{"keyword": k, "count": v} for k, v in tag_counts.most_common(limit)]
