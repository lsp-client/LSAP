import uuid
from collections import OrderedDict

from attrs import Factory, define


@define
class PaginationCache[T]:
    """
    A simple LRU-based cache for storing paginated results.
    """

    capacity: int = 128
    _cache: OrderedDict[str, T] = Factory(OrderedDict)

    def get(self, pagination_id: str) -> T | None:
        """
        Retrieve data from the cache and move it to the end (MRU).
        """
        if pagination_id not in self._cache:
            return None
        self._cache.move_to_end(pagination_id)
        return self._cache[pagination_id]

    def put(self, data: T) -> str:
        """
        Store data in the cache and return a new pagination ID.
        """
        pagination_id = str(uuid.uuid4())
        self._cache[pagination_id] = data
        if len(self._cache) > self.capacity:
            self._cache.popitem(last=False)
        return pagination_id
