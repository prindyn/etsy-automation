import logging
import sys
from loguru import logger
from app.core.config import settings


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Forward standard logging to Loguru
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        logger.opt(
            depth=6,
            exception=record.exc_info,
        ).log(
            level,
            record.getMessage(),
        )


def setup_logging():
    # Clear existing loggers
    logging.root.handlers = []
    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    # Redirect logs from these modules to Loguru
    for name in (
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "httpx",
        "celery",
    ):
        logging.getLogger(name).handlers = [InterceptHandler()]
        logging.getLogger(name).propagate = False

    logger.remove()
    logger.add(
        sys.stdout,
        colorize=True,
        backtrace=True,
        diagnose=True,
        level=settings.LOG_LEVEL.upper(),
        format="<green>[{time:YYYY-MM-DD HH:mm:ss.SSS}]</green> "
        "<level>{level: <8}</level> "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>",
    )
