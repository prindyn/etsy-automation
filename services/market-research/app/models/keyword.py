from pydantic import BaseModel


class KeywordEntry(BaseModel):
    keyword: str
    count: int
