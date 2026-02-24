CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) UNIQUE NOT NULL,
    cik VARCHAR(10) NOT NULL,
    company_name VARCHAR(255),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE filings (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    filing_type VARCHAR(10) NOT NULL,
    fiscal_year INTEGER NOT NULL,
    fiscal_quarter INTEGER,
    filing_date DATE NOT NULL,
    accession_number VARCHAR(20) NOT NULL,
    primary_doc VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    download_status BOOLEAN DEFAULT FALSE,
    validation_status BOOLEAN DEFAULT FALSE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, accession_number)
);

CREATE INDEX idx_filings_company_id ON filings(company_id);
CREATE INDEX idx_filings_filing_type ON filings(filing_type);
CREATE INDEX idx_filings_fiscal_year ON filings(fiscal_year);

CREATE TABLE price_metadata (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    file_path VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    last_fetched TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id)
);