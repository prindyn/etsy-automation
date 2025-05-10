from pydantic import BaseModel
from typing import Union


class KeywordEntry(BaseModel):
    keyword: str
    count: int


class KeywordResponse(BaseModel):
    keyword: str
    score: Union[int, float]
