from typing import Union


class TrendsBase:
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


class TrendsCache(TrendsBase):
    def cache_key(self) -> str:
        return f"cache:trends:{self.source}:{self.keyword}"


class TrendsQueue(TrendsBase):
    def cache_key(self) -> str:
        return f"queue:trends:{self.source}:{self.keyword}"
