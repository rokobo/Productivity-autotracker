"""
A module implementing a retry mechanism for functions.

Example usage:
    @retry(attempts=3, wait=2.0)
    def example_function(param):
        ...
"""
# pylint: disable=broad-exception-caught
import time
import logging
from typing import Callable, TypeVar, Any, Optional
from helper_io import load_config


logging.basicConfig(
    filename='../app.log',
    filemode='w',
    format='%(asctime)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('app')
T = TypeVar('T')
logger.error("Logger started")


def retry(
    attempts: int = 0, wait: float = 0.5
) -> Callable[[Callable[..., T]], Callable[..., Optional[T]]]:
    """
    Retry decorator for any function.

    Args:
        attempts (int, optional): Attempts to execute function.
            Defaults to retry attemps defined in configuration file.
        wait (float, optional): Wait time in between attempts. Defaults to 0.5.
        return_params (int, optional): How many None values to return if fail.

    Returns:
        Callable[[Callable[..., T]], Callable[..., Optional[T]]]:
            Returns decorator that wraps the function with the retry mechanism.
    """
    attempts = load_config()["RETRY_ATTEMPS"] if attempts == 0 else attempts

    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        """
        Decorator function that applies the retry mechanism.

        Args:
            func (Callable[..., T]): Function to be wrapped.

        Returns:
            Callable[..., Optional[T]]: Wrapped function with retry logic.
        """
        def wrapper(*args: Any, **kwargs: Any) -> Optional[T]:
            """
            Wrapper function that executes the retries.

            Args:
                *args (Any): Variable length arg list for wrapped function.
                **kwargs (Any): Arbitrary keyword args for wrapped function.

            Returns:
                Optional[T]: Wrapped function return or None if all tries fail.
            """
            for attempt in range(attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(
                        "Error at function %s() on attempt %i: %s(\"%s\")",
                        func.__name__,
                        attempt + 1,
                        type(e).__name__,
                        e
                    )
                time.sleep(wait)
            return None
        return wrapper
    return decorator
