from typing import Protocol

from attrs import frozen

from lsap.exception import PaginationError
from lsap.schema._abc import PaginatedRequest

from .cache import PaginationCache


class ItemsFetcher[T](Protocol):
    async def __call__(self) -> list[T] | None: ...


@frozen
class Page[T]:
    items: list[T]
    total: int
    pagination_id: str
    has_more: bool


async def paginate[T](
    req: PaginatedRequest,
    cache: PaginationCache[T],
    fetcher: ItemsFetcher[T],
) -> Page[T] | None:
    """
    paginated requests with caching.
    """

    pagination_id = req.pagination_id
    if pagination_id:
        if (cached := cache.get(pagination_id)) is not None:
            items = cached
        else:
            raise PaginationError(
                f"Pagination ID '{pagination_id}' not found or expired"
            )
    else:
        if req.start_index != 0:
            raise PaginationError("pagination_id is required for non-zero start_index")

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
        pagination_id=pagination_id,
        has_more=has_more,
    )
