import functools
from collections.abc import Callable
from logging import Logger
from typing import Concatenate, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def with_logger(logger: Logger):
    def wrapper(func: Callable[Concatenate[Logger, P], R]) -> Callable[P, R]:
        @functools.wraps(func)
        def inner(*args: P.args, **kwargs: P.kwargs) -> R:
            return func(logger, *args, **kwargs)

        return inner

    return wrapper
