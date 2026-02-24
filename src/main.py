import os
from datetime import datetime, timedelta
from multiprocessing import Pool
from tqdm import tqdm
from src.config import config
from src.utils.logger import logger
from src.repositories.db_repo import DBRepo
from src.repositories.file_repo import FileRepo
from src.fetchers.sp500_fetcher import fetch_sp500_tickers
from src.fetchers.cik_mapper import fetch_cik_mapping
from src.fetchers.edgar_metadata_fetcher import fetch_filings_metadata, detect_missing_filings
from src.fetchers.filing_downloader import download_filing
from src.fetchers.price_fetcher import fetch_prices
from src.utils.validator import validate_filing
from src.models.db_models import Company, Filing, PriceMetadata
from datetime import datetime, timedelta  # Ensure this import is at top if not there
db_repo = DBRepo()
file_repo = FileRepo()
start_year = config['pipeline']['start_year']
batch_size = config['pipeline']['batch_size']


def process_company(company):
    # Skip metadata fetch if we fetched recently and have some filings
    skip_threshold = timedelta(days=1)  # Re-fetch daily; adjust as needed (e.g., hours=6 for more frequent)
    now = datetime.utcnow()

    has_filings = bool(company.filings)  # If eager-loaded, this is fast
    recently_fetched = (
            company.last_metadata_fetched is not None and
            now - company.last_metadata_fetched < skip_threshold
    )

    if has_filings and recently_fetched:
        logger.info(f"Skipping metadata fetch for {company.ticker} (recently processed)")
        return  # Skip to next company

    # Otherwise fetch
    metadata = fetch_filings_metadata(company.cik, start_year)
    for m in metadata:
        filename = f"{m['fiscal_year']}_{m['filing_type'].replace('/', '_')}"
        if m['fiscal_quarter']:
            filename += f"_Q{m['fiscal_quarter']}"
        filename += ".html"
        rel_path = f"{company.ticker}/{filename}"
        db_repo.upsert_filing(
            company.id, m['filing_type'], m['fiscal_year'], m['fiscal_quarter'],
            m['filing_date'], m['accession_number'], m['primary_doc'], rel_path
        )

    # Mark as fetched
    db_repo.update_company_metadata_fetched(company.id)

    detect_missing_filings(company, start_year)


def process_prices(company):
    price_path = file_repo.get_price_path(company.ticker)
    meta = db_repo.get_price_metadata(company.id)
    needs_update = True
    if meta and meta.last_fetched > datetime.now() - timedelta(days=1):
        needs_update = False
    if needs_update or not file_repo.price_exists(price_path):
        start_date = f"{start_year}-01-01"
        start, end = fetch_prices(company.ticker, start_date, path=price_path)
        db_repo.upsert_price_metadata(company.id, price_path, start, end)


def main():
    logger.info("Starting Phase 1 pipeline")

    # Step 1: Fetch S&P 500 tickers
    tickers = fetch_sp500_tickers()

    # Step 2: Fetch CIK mapping
    mapping = fetch_cik_mapping()

    # Step 3: Upsert companies
    for ticker in tqdm(tickers, desc="Upserting companies"):
        if ticker in mapping:
            db_repo.upsert_company(ticker, mapping[ticker]['cik'], mapping[ticker]['name'])

    companies = db_repo.get_all_companies()

    # Step 4: Process metadata in batches (sequential for rate limit)
    for i in tqdm(range(0, len(companies), batch_size), desc="Processing metadata batches"):
        batch = companies[i:i + batch_size]
        for company in batch:
            process_company(company)

    # Step 5: Download pending filings (sequential)
    pending_filings = db_repo.get_pending_filings()
    for filing in tqdm(pending_filings, desc="Downloading filings"):
        # Clean way: always build from raw_filings_dir + stored rel_path (ticker/filename.html)
        full_path = os.path.join(file_repo.raw_filings_dir, filing.file_path)
        if not file_repo.filing_exists(full_path):
            success = download_filing(filing.company.cik, filing.accession_number, filing.primary_doc, full_path, file_repo)
            db_repo.update_filing_download_status(filing.id, success)

    # Step 6: Fetch prices in parallel
    with Pool(processes=os.cpu_count()) as pool:
        list(tqdm(pool.imap(process_prices, companies), total=len(companies), desc="Fetching prices"))

    # Step 7: Validate filings
    all_filings = []  # Query all downloaded
    with db_repo.Session() as session:
        all_filings = session.query(Filing).filter_by(download_status=True).all()
    for filing in tqdm(all_filings, desc="Validating filings"):
        full_path = os.path.join(file_repo.data_dir, file_repo.raw_filings_dir, filing.file_path)
        valid = validate_filing(full_path)
        db_repo.update_filing_validation_status(filing.id, valid)

    logger.info("Phase 1 pipeline completed")


if __name__ == "__main__":
    main()