import asyncio
import time
from contextlib import suppress
from functools import wraps

from typing_extensions import Awaitable, Callable, ParamSpec, TypeAlias, TypeVar

_T = TypeVar("_T")
_P = ParamSpec("_P")
_AsyncFunc: TypeAlias = Callable[_P, Awaitable[_T]]
_Func: TypeAlias = Callable[_P, _T]


def retries(
        num_retries: int,
        timeout: float,
        exception: type[Exception] = Exception
) -> Callable[[_Func[_P, _T]], _Func[_P, _T | None]]:

    def decorator(function: _Func[_P, _T]) -> _Func[_P, _T | None]:

        @wraps(function)
        def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T | None:
            for _ in range(num_retries):
                with suppress(exception):
                    return function(*args, **kwargs)
                time.sleep(timeout)
            return None

        return wrapper

    return decorator


def async_retries(
        num_retries: int,
        timeout: float,
        exception: type[Exception] = Exception,
) -> Callable[[_AsyncFunc[_P, _T]], _AsyncFunc[_P, _T | None]]:

    def decorator(function: _AsyncFunc[_P, _T]) -> _AsyncFunc[_P, _T | None]:

        @wraps(function)
        async def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T | None:
            for _ in range(num_retries):
                with suppress(exception):
                    return await function(*args, **kwargs)
                await asyncio.sleep(timeout)
            return None

        return wrapper

    return decorator
