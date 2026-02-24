import os
from src.config import config
from src.utils.logger import logger

class FileRepo:
    def __init__(self):
        self.data_dir = config['paths']['data_dir']
        self.raw_filings_dir = os.path.join(self.data_dir, config['paths']['raw_filings_dir'])
        self.price_data_dir = os.path.join(self.data_dir, config['paths']['price_data_dir'])
        os.makedirs(self.raw_filings_dir, exist_ok=True)
        os.makedirs(self.price_data_dir, exist_ok=True)

    def get_filing_path(self, ticker: str, filename: str) -> str:
        ticker_dir = os.path.join(self.raw_filings_dir, ticker.upper())  # Normalize ticker case if needed
        os.makedirs(ticker_dir, exist_ok=True)
        return os.path.join(ticker_dir, filename)

    def filing_exists(self, path: str) -> bool:
        return os.path.exists(path) and os.path.getsize(path) > 0

    def save_filing(self, path: str, content: str):
        try:
            # Normalize and create all parent directories
            os.makedirs(os.path.dirname(path), exist_ok=True)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Saved filing to {path}")
        except Exception as e:
            logger.error(f"Error saving filing to {path}: {e}")

    def get_price_path(self, ticker: str) -> str:
        return os.path.join(self.price_data_dir, f"{ticker}.csv")

    def price_exists(self, path: str) -> bool:
        return os.path.exists(path) and os.path.getsize(path) > 0