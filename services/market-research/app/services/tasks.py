from celery import Celery
from app.services.keyword_scraper import get_top_keywords

celery_app = Celery("tasks", broker="redis://redis:6379/0")


@celery_app.task
def run_market_research(limit: int = 100):
    return get_top_keywords(limit)
