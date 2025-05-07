from pydantic import BaseModel
from typing import Optional


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error: Optional[str] = None
