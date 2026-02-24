import time
from functools import wraps
from src.config import config

def rate_limited():
    last_call = [0]
    delay = config['sec']['rate_limit_seconds']

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            if now - last_call[0] < delay:
                time.sleep(delay - (now - last_call[0]))
            last_call[0] = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator