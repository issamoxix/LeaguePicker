import traceback

def with_try_except(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"error: {e}, stack: {traceback.format_exc()}. ")
            return e
    return wrapper