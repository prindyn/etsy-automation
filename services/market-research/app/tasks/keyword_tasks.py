from loguru import logger
from celery import shared_task
from app.services.trends_scraper_google import get_trending_keywords
from app.services.keyword_scraper_etsy import get_top_keywords
from app.core.utils import run_safe_async


def process_keyword_task(keyword: str, source: str):
    if source == "google":
        return process_keyword_google_task.delay(keyword)
    elif source == "etsy":
        return process_keyword_etsy_task.delay(keyword)
    else:
        raise ValueError(f"Unknown source: {source}")


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    rate_limit="2/m",
)
def process_keyword_google_task(self, keyword: str):
    logger.info(f"[Celery] [Google] Processing '{keyword}'")

    try:
        return run_safe_async(get_trending_keywords(keyword))
    except Exception as e:
        logger.error(f"[Celery] Error for Google keyword '{keyword}': {e}")
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def process_keyword_etsy_task(self, keyword: str):
    logger.info(f"[Celery] [Etsy] Processing '{keyword}'")

    try:
        return run_safe_async(get_top_keywords(keyword))
    except Exception as e:
        logger.error(f"[Celery] Error for Etsy keyword '{keyword}': {e}")
        raise self.retry(exc=e)
