import time
from typing import Callable, Dict, Tuple, Type, TypeVar

T = TypeVar("T")


def assert_stops_raising(
    fn: Callable[..., T],
    args: Tuple = (),
    kwargs: Dict = None,
    exception_type: Type[Exception] = Exception,
    timeout: float = 10,
    interval: float = 1,
    delay: float = 0,
) -> T:
    """Assert that ``fn`` returns successfully within ``timeout``
    seconds, trying every ``interval`` seconds.
    If ``exception_type`` is provided, fail unless the exception thrown is
    an instance of ``exception_type``.
    """
    if delay > 0:
        time.sleep(delay)

    if kwargs is None:
        kwargs = {}

    give_up = time.time() + timeout
    while True:
        try:
            return fn(*args, **kwargs)
        except exception_type:
            if time.time() >= give_up:
                raise
        time.sleep(interval)
        interval += 1


def assert_keeps_raising(
    fn: Callable,
    args: Tuple = (),
    kwargs: Dict = None,
    exception_type: Type[Exception] = Exception,
    timeout: float = 10,
    interval: float = 1,
    delay: float = 0,
) -> None:
    """Assert that ``fn`` continues to raise for at least ``timeout``
    seconds, trying every ``interval`` seconds.
    If ``exception_type`` is provided, fail unless the exception thrown is
    an instance of ``exception_type``.
    """
    if delay > 0:
        time.sleep(delay)

    if kwargs is None:
        kwargs = {}

    give_up = time.time() + timeout
    while time.time() < give_up:
        try:
            fn(*args, **kwargs)
            # If we didn't raise the desired exception, raise one now.
            raise ValueError(f"Expected exception {exception_type} not raised")
        except exception_type:
            pass
        time.sleep(interval)
        interval += 1
