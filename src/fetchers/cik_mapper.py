import requests
from src.config import config
from src.utils.logger import logger
from src.utils.retry_handler import retry_decorator
from src.utils.rate_limiter import rate_limited

headers = {'User-Agent': config['sec']['user_agent']}

@rate_limited()
@retry_decorator()
def fetch_cik_mapping() -> dict:
    url = 'https://www.sec.gov/files/company_tickers.json'
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        mapping = {}
        for v in data.values():
            ticker = v['ticker']
            cik = str(v['cik_str']).zfill(10)
            name = v['title']
            mapping[ticker] = {'cik': cik, 'name': name}
        logger.info(f"Fetched CIK mapping for {len(mapping)} companies")
        return mapping
    except Exception as e:
        logger.error(f"Error fetching CIK mapping: {e}")
        raise