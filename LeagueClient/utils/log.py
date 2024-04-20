import traceback
import logging
import sys

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.info("Logger initialized")

def with_try_except(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"error: {e}, stack: {traceback.format_exc()}. ")
            return e
    return wrapper
