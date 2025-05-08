from typing import Union


class KeywordBase:
    def __init__(
        self,
        source: str,
        keyword: str,
        value: Union[dict, list, str] = None,
    ):
        self.source = source
        self.keyword = keyword
        self.value = value

    def get_value(self) -> Union[dict, list, str]:
        return self.value


class KeywordCache(KeywordBase):
    def cache_key(self) -> str:
        return f"cache:research:{self.source}:{self.keyword}"


class KeywordQueue(KeywordBase):
    def cache_key(self) -> str:
        return f"queue:research:{self.source}:{self.keyword}"
