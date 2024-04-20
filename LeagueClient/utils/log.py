import traceback
import logging
import sys

def with_try_except(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"error: {e}, stack: {traceback.format_exc()}. ")
            return e
    return wrapper

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))
