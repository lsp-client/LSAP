from collections import OrderedDict

from attrs import Factory, define

from .id import generate_short_id


@define
class LRUCache[K, V]:
    """
    A simple LRU-based cache.
    """

    capacity: int = 128
    _cache: OrderedDict[K, V] = Factory(OrderedDict)

    def get(self, key: K) -> V | None:
        """
        Retrieve data from the cache and move it to the end (MRU).
        """
        if key not in self._cache:
            return None
        self._cache.move_to_end(key)
        return self._cache[key]

    def put(self, key: K, value: V) -> None:
        """
        Store data in the cache.
        """
        self._cache[key] = value
        if len(self._cache) > self.capacity:
            self._cache.popitem(last=False)

    def pop(self, key: K) -> V | None:
        """
        Remove and return an item from the cache.
        """
        return self._cache.pop(key, None)


@define
class PaginationCache[T]:
    """
    A simple LRU-based cache for storing paginated results.
    """

    capacity: int = 128
    _inner: LRUCache[str, list[T]] = Factory(
        lambda self: LRUCache(capacity=self.capacity), takes_self=True
    )

    def get(self, pagination_id: str) -> list[T] | None:
        """
        Retrieve data from the cache and move it to the end (MRU).
        """
        return self._inner.get(pagination_id)

    def put(self, data: list[T]) -> str:
        """
        Store data in the cache and return a new pagination ID.
        """
        pagination_id = generate_short_id()
        self._inner.put(pagination_id, data)
        return pagination_id
