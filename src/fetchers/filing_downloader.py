# src/fetchers/filing_downloader.py
import requests
from src.config import config
from src.utils.logger import logger
from src.utils.retry_handler import retry_decorator
from src.utils.rate_limiter import rate_limited

headers = {'User-Agent': config['sec']['user_agent']}


@rate_limited()
@retry_decorator()
def download_filing(cik: str, accession_number: str, primary_doc: str, full_path: str, file_repo) -> bool:
    cik_no_zero = cik.lstrip('0')
    acc_no_dash = accession_number.replace('-', '')
    url = f'https://www.sec.gov/Archives/edgar/data/{cik_no_zero}/{acc_no_dash}/{primary_doc}'

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # Now we can use the passed file_repo instance
        file_repo.save_filing(full_path, response.text)
        logger.info(f"Downloaded filing {accession_number} to {full_path}")
        return True

    except requests.exceptions.HTTPError as e:
        if e.response and e.response.status_code == 404:
            logger.warning(f"Filing not found (404): {url} - skipping")
            return False
        logger.error(f"HTTP error downloading {accession_number}: {e}")
        return False

    except Exception as e:
        logger.error(f"Error downloading filing {accession_number}: {e}")
        return False