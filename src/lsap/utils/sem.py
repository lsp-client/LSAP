from collections.abc import Awaitable, Callable

import anyio


def with_sem[**P, R](
    sem: anyio.Semaphore,
    func: Callable[P, Awaitable[R]],
    *args: P.args,
    **kwargs: P.kwargs,
) -> Callable[[], Awaitable[R]]:
    async def wrapper() -> R:
        async with sem:
            return await func(*args, **kwargs)

    return wrapper
