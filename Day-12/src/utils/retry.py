import functools
import time

from src.utils.logger import get_logger

log = get_logger("retry")


def retry(max_attempts: int = 3, delay: float = 2, backoff: float = 2):
    """Retry a function with exponential backoff, re-raising after the last attempt."""

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            wait = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except Exception as exc:
                    if attempt == max_attempts:
                        log.error("%s failed after %d attempts: %s", fn.__name__, attempt, exc)
                        raise
                    log.warning(
                        "%s failed (attempt %d/%d): %s. Retrying in %ss",
                        fn.__name__, attempt, max_attempts, exc, wait,
                    )
                    time.sleep(wait)
                    wait *= backoff

        return wrapper

    return decorator
