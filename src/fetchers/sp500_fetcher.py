import requests
from bs4 import BeautifulSoup
from src.utils.logger import logger
from src.utils.retry_handler import retry_decorator
from src.config import config  # We'll use the sec user_agent as fallback


@retry_decorator()
def fetch_sp500_tickers() -> list:
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

    # Use a realistic browser User-Agent (required by Wikipedia)
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        ),
        # Optional: fallback to your config user-agent if you want consistency
        # 'User-Agent': config['sec']['user_agent'],
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()  # Raises if not 200

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', id='constituents')

        if not table:
            raise ValueError("Could not find constituents table on Wikipedia page")

        tickers = []
        for row in table.find_all('tr')[1:]:  # Skip header row
            cells = row.find_all('td')
            if cells:
                ticker = cells[0].text.strip()  # First column is Symbol/Ticker
                if ticker:  # Skip empty
                    tickers.append(ticker)

        logger.info(f"Fetched {len(tickers)} S&P 500 tickers")
        return tickers

    except requests.exceptions.HTTPError as e:
        logger.error(
            f"HTTP error fetching S&P 500: {e} (status {response.status_code if 'response' in locals() else 'N/A'})")
        raise
    except Exception as e:
        logger.error(f"Error fetching S&P 500 tickers: {e}")
        raise