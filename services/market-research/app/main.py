from fastapi import FastAPI
from app.routes import research
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(title="Market Research Service")
app.include_router(research.router)
register_exception_handlers(app)
