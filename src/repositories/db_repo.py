from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from src.models.db_models import Base, Company, Filing, PriceMetadata
from src.config import config
from src.utils.logger import logger
from sqlalchemy.orm import joinedload  # or selectinload for larger

class DBRepo:
    def __init__(self):
        self.engine = create_engine(config['database']['uri'])
        Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)

    def get_all_companies(self):
        with self.Session() as session:
            return (
                session.query(Company)
                .options(joinedload(Company.filings))  # ← eager load filings
                .all()
            )

    def upsert_company(self, ticker: str, cik: str, name: str):
        with self.Session() as session:
            try:
                company = session.query(Company).filter_by(ticker=ticker).first()
                if company:
                    company.cik = cik
                    company.company_name = name
                else:
                    company = Company(ticker=ticker, cik=cik, company_name=name)
                    session.add(company)
                session.commit()
                return company
            except Exception as e:
                session.rollback()
                logger.error(f"Error upserting company {ticker}: {e}")
                raise

    def upsert_filing(self, company_id: int, filing_type: str, fiscal_year: int, fiscal_quarter: int or None,
                      filing_date: str, accession_number: str, primary_doc: str, file_path: str):
        with self.Session() as session:
            try:
                filing = session.query(Filing).filter_by(company_id=company_id, accession_number=accession_number).first()
                if not filing:
                    filing = Filing(
                        company_id=company_id,
                        filing_type=filing_type,
                        fiscal_year=fiscal_year,
                        fiscal_quarter=fiscal_quarter,
                        filing_date=filing_date,
                        accession_number=accession_number,
                        primary_doc=primary_doc,
                        file_path=file_path
                    )
                    session.add(filing)
                session.commit()
                return filing
            except Exception as e:
                session.rollback()
                logger.error(f"Error upserting filing {accession_number}: {e}")
                raise

    def get_pending_filings(self):
        with self.Session() as session:
            return (
                session.query(Filing)
                .filter_by(download_status=False)
                .options(joinedload(Filing.company))  # ← Eager load the Company for each Filing
                .all()
            )

    def update_filing_download_status(self, filing_id: int, status: bool):
        with self.Session() as session:
            try:
                filing = session.query(Filing).get(filing_id)
                if filing:
                    filing.download_status = status
                    session.commit()
            except Exception as e:
                session.rollback()
                logger.error(f"Error updating download status for filing {filing_id}: {e}")

    def update_filing_validation_status(self, filing_id: int, status: bool):
        with self.Session() as session:
            try:
                filing = session.query(Filing).get(filing_id)
                if filing:
                    filing.validation_status = status
                    session.commit()
            except Exception as e:
                session.rollback()
                logger.error(f"Error updating validation status for filing {filing_id}: {e}")

    def upsert_price_metadata(self, company_id: int, file_path: str, start_date: str, end_date: str):
        with self.Session() as session:
            try:
                meta = session.query(PriceMetadata).filter_by(company_id=company_id).first()
                if meta:
                    meta.file_path = file_path
                    meta.start_date = start_date
                    meta.end_date = end_date
                else:
                    meta = PriceMetadata(
                        company_id=company_id,
                        file_path=file_path,
                        start_date=start_date,
                        end_date=end_date
                    )
                    session.add(meta)
                session.commit()
            except Exception as e:
                session.rollback()
                logger.error(f"Error upserting price metadata for company {company_id}: {e}")

    def get_price_metadata(self, company_id: int):
        with self.Session() as session:
            return session.query(PriceMetadata).filter_by(company_id=company_id).first()

    def update_company_metadata_fetched(self, company_id: int):
        with self.Session() as session:
            try:
                company = session.query(Company).get(company_id)
                if company:
                    # Use one of these lines (pick the one matching your import):

                    # If you used: from datetime import datetime
                    company.last_metadata_fetched = datetime.utcnow()

                    # OR if you used: import datetime
                    # company.last_metadata_fetched = datetime.datetime.utcnow()

                    session.commit()
            except Exception as e:
                session.rollback()
                logger.error(f"Error updating metadata fetch time for company {company_id}: {e}")