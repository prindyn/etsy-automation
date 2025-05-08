from fastapi import FastAPI
from app.routes import research
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.celery_worker import celery_app

setup_logging()

app = FastAPI(title="Market Research Service")

# Assign Celery app to FastAPI state
app.state.celery_app = celery_app

# Register routes and exception handlers
app.include_router(research.router)
register_exception_handlers(app)
