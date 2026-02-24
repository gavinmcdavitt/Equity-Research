import requests
from datetime import datetime
from src.config import config
from src.utils.logger import logger
from src.utils.retry_handler import retry_decorator
from src.utils.rate_limiter import rate_limited

headers = {'User-Agent': config['sec']['user_agent']}

@rate_limited()
@retry_decorator()
def fetch_filings_metadata(cik: str, start_year: int) -> list:
    url = f'https://data.sec.gov/submissions/CIK{cik}.json'
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        recent = data['filings']['recent']
        filtered = []
        current_year = datetime.now().year
        for i in range(len(recent['form'])):
            form = recent['form'][i]
            if form in ['10-K', '10-Q', '10-K/A', '10-Q/A']:
                report_date = recent['reportDate'][i]
                if report_date and int(report_date[:4]) >= start_year and int(report_date[:4]) <= current_year:
                    # only add if report_date year is reasonable
                    year = int(report_date[:4])
                    quarter = None
                    if '10-Q' in form:
                        month = int(report_date[5:7])
                        quarter = (month - 1) // 3 + 1
                    filtered.append({
                        'filing_type': form,
                        'fiscal_year': year,
                        'fiscal_quarter': quarter,
                        'filing_date': report_date,
                        'accession_number': recent['accessionNumber'][i],
                        'primary_doc': recent['primaryDocument'][i]
                    })
        logger.info(f"Fetched {len(filtered)} filings metadata for CIK {cik}")
        return filtered
    except Exception as e:
        logger.error(f"Error fetching metadata for CIK {cik}: {e}")
        return []

def detect_missing_filings(company, start_year: int):
    current_year = datetime.now().year
    expected = set()
    for y in range(start_year, current_year + 1):
        expected.add((y, '10-K', None))
        for q in [1, 2, 3]:
            expected.add((y, '10-Q', q))
    fetched = set((f.fiscal_year, f.filing_type.replace('/A', ''), f.fiscal_quarter) for f in company.filings if not '/A' in f.filing_type)
    missing = expected - fetched
    if missing:
        logger.warning(f"Missing filings for {company.ticker}: {missing}")