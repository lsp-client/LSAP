from typing import Protocol

from attrs import frozen

from lsap.schema.abc import PaginatedRequest

from .cache import PaginationCache


class ItemsFetcher[T](Protocol):
    async def __call__(self) -> list[T] | None: ...


@frozen
class Page[T]:
    items: list[T]
    total: int
    pagination_id: str | None

    @property
    def has_more(self) -> bool:
        return self.pagination_id is not None


async def paginate[T](
    req: PaginatedRequest,
    cache: PaginationCache[T],
    fetcher: ItemsFetcher[T],
) -> Page[T] | None:
    """
    paginated requests with caching.
    """

    pagination_id = req.pagination_id
    if pagination_id and (cached := cache.get(pagination_id)) is not None:
        items = cached
    else:
        items = await fetcher()
        if items is None:
            return None
        pagination_id = cache.put(items)

    total = len(items)
    start = req.start_index
    limit = req.max_items
    paginated = items[start : start + limit] if limit is not None else items[start:]

    has_more = (start + len(paginated)) < total
    return Page(
        items=paginated,
        total=total,
        pagination_id=pagination_id if has_more else None,
    )
