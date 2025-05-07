from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from app.models.error import ErrorResponse
import logging


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logging.exception("Unhandled exception")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                message="Internal Server Error", error=str(exc)
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                message="Request validation error", error=str(exc)
            ).model_dump(),
        )

    @app.exception_handler(ResponseValidationError)
    async def response_validation_handler(
        request: Request, exc: ResponseValidationError
    ):
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                message="Response validation error", error=str(exc)
            ).model_dump(),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        detail = exc.detail
        if isinstance(detail, dict):
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "success": False,
                    "message": detail.get("message", "HTTP error"),
                    "error": detail.get("error"),
                },
            )
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "message": str(detail), "error": None},
        )
