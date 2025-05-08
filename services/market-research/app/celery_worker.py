from celery import Celery

celery_app = Celery("market_research")
celery_app.config_from_object("app.celery_config")

# Autodiscover tasks
celery_app.autodiscover_tasks(["app.tasks.keyword_tasks"])

if not celery_app.conf.broker_url.startswith("redis"):
    raise RuntimeError(
        f"Invalid broker configured: {celery_app.conf.broker_url}",
    )
