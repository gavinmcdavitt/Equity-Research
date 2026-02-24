from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Company(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), unique=True, nullable=False)
    cik = Column(String(10), nullable=False)
    company_name = Column(String(255))
    last_updated = Column(DateTime, server_default=func.now())
    filings = relationship('Filing', backref='company')
    price_meta = relationship('PriceMetadata', backref='company', uselist=False)
    last_metadata_fetched = Column(DateTime, nullable=True)
class Filing(Base):
    __tablename__ = 'filings'
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    filing_type = Column(String(10), nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    fiscal_quarter = Column(Integer)
    filing_date = Column(Date)
    accession_number = Column(String(20), nullable=False)
    primary_doc = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    download_status = Column(Boolean, default=False)
    validation_status = Column(Boolean, default=False)
    last_updated = Column(DateTime, server_default=func.now())

class PriceMetadata(Base):
    __tablename__ = 'price_metadata'
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    file_path = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    last_fetched = Column(DateTime, server_default=func.now())