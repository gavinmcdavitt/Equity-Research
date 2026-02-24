from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests

def retry_decorator():
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.exceptions.HTTPError, requests.exceptions.ConnectionError, requests.exceptions.Timeout))
    )