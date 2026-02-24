import yfinance as yf
from datetime import datetime, timedelta
from src.utils.logger import logger
from src.utils.retry_handler import retry_decorator

@retry_decorator()
def fetch_prices(ticker: str, start_date: str, end_date: str = None, path: str = None) -> tuple:
    try:
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        data = yf.download(ticker, start=start_date, end=end_date)
        if path:
            data.to_csv(path)
            logger.info(f"Saved price data for {ticker} to {path}")
        start = data.index.min().date() if not data.empty else datetime.strptime(start_date, '%Y-%m-%d').date()
        end = data.index.max().date() if not data.empty else datetime.now().date()
        return start, end
    except Exception as e:
        logger.error(f"Error fetching prices for {ticker}: {e}")
        raise