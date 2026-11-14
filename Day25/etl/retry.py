import functools
import time

from etl.logger import get_logger

log = get_logger(__name__)


def retry(times=3, delay=2, backoff=2, exceptions=(Exception,)):
    """Re-run a function if it raises, waiting longer each time (2s, 4s, 8s...).

    The last failure is re-raised so the caller (and Airflow) still sees it.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            wait = delay
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    log.warning("%s failed (attempt %d/%d): %s", func.__name__, attempt, times, exc)
                    if attempt == times:
                        raise
                    time.sleep(wait)
                    wait *= backoff

        return wrapper

    return decorator
