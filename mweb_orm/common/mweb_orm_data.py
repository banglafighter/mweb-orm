from dataclasses import dataclass
from mw_common import SDLize


@dataclass(kw_only=True)
class Pagination(SDLize):
    page: int = 1
    itemPerPage: int = 20
    total: int = 0
    totalPage: int = 0
    items: list | None = None

    def __repr__(self) -> str:
        return f"page: {self.page}, itemPerPage: {self.itemPerPage}, total: {self.total}"
