from pytrends.request import TrendReq
from typing import List, Dict
from loguru import logger

from app.storage.trends import TrendsCache
from app.services.redis_service import get_cache, set_cache

# === Global pytrends instance with headers ===
pytrends = TrendReq(
    hl="en-US",
    tz=360,
    requests_args={
        "headers": {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
        }
    },
)


async def get_trending_keywords(
    keyword: str,
    limit: int = 100,
) -> List[Dict[str, str]]:
    """
    Get trending related keywords from Google Trends.
    Falls back to pytrends.suggestions if related queries fail.
    """
    cache_obj = TrendsCache(source="google", keyword=keyword)

    cached = await get_cache(cache_obj)
    if cached:
        return cached

    try:
        pytrends.build_payload([keyword], cat=0, timeframe="now 7-d", geo="US")
        related = pytrends.related_queries()
        top_df = related.get(keyword, {}).get("top")

        if top_df is None or top_df.empty:
            raise ValueError("No related queries found, triggering fallback.")

        ranked = [
            {"keyword": row["query"].lower(), "count": int(row["value"])}
            for _, row in top_df.head(limit).iterrows()
        ]

        await set_cache(TrendsCache("google", keyword, ranked), ttl_sec=3600)
        return ranked

    except Exception as e:
        logger.warning(f"[Fallback] Google Trends failed: {e}")
        return await fallback_to_suggestions(keyword, limit)


async def fallback_to_suggestions(
    keyword: str,
    limit: int,
) -> List[Dict[str, str]]:
    """
    Use pytrends.suggestions() as a fallback method.
    """
    try:
        suggestions = pytrends.suggestions(keyword)
        if not suggestions:
            logger.warning("Google suggestions returned no results.")
            return []

        fallback_results = [
            {"keyword": s["title"].lower(), "count": i + 1}
            for i, s in enumerate(suggestions[:limit])
        ]

        await set_cache(
            TrendsCache("google", keyword, fallback_results),
            ttl_sec=3600,
        )
        return fallback_results

    except Exception as e:
        logger.error(f"Google Suggestions fallback failed: {e}")
        return []
