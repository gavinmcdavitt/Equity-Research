# S&P 500 Fundamental Equity Research Pipeline – Phase 1

**Fully automated local ingestion of S&P 500 company data**

Phase 1 focuses **exclusively** on:

- Fetching the current list of S&P 500 companies
- Mapping tickers → CIKs (SEC identifiers)
- Downloading raw 10-K and 10-Q filings (2010–present) from EDGAR
- Storing raw HTML filings locally in an organized structure
- Fetching and storing historical daily stock price data
- Recording structured metadata in a PostgreSQL database

**No parsing, no NLP, no financial statement extraction** — that is reserved for Phase 2.

## Features

- 100% local execution (no cloud dependencies)
- Uses only free, public sources: Wikipedia (S&P list), SEC EDGAR JSON endpoints, yfinance for prices
- Rate-limit respectful downloads (10 requests/sec max to SEC)
- Idempotent design — safe to re-run at any time
- Handles amended filings (10-K/A, 10-Q/A) as separate entries
- Logs everything (progress, warnings, errors)
- PostgreSQL metadata storage + filesystem raw data
- Multi-threaded price fetching (fast)

## Current Scope (Phase 1 only)

- ~501 S&P 500 companies
- ~10,000–25,000+ filings metadata rows
- Raw HTML filings saved to disk (~10–25 GB total on first run)
- Daily OHLCV price data (CSV) from ~2010 to present


## Prerequisites

- **Python** 3.10+
- **PostgreSQL** 15+ (local install)
- Internet connection (for Wikipedia, SEC EDGAR, Yahoo Finance)

## Setup Instructions (Replicate the Project)

### 1. Clone / create the project folder

```bash
git clone <your-repo-url> equity_research_pipeline
# or just create the folder structure manually
cd equity_research_pipeline


python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt

Install and start a postresSQL (windows)

# Create DB
psql -U postgres -c "CREATE DATABASE equity_research_db;"

# Apply schema
psql -U postgres -d equity_research_db -f setup_db.sql

#configure the tables
database:
  uri: postgresql://postgres:YOUR_PASSWORD_HERE@localhost:5432/equity_research_db

paths:
  data_dir: ./data
  raw_filings_dir: raw_filings
  price_data_dir: price_data
  logs_dir: ./logs

sec:
  user_agent: 'EquityResearchPipeline YOUR_NAME your.email@gmail.com'   # ← REQUIRED by SEC

pipeline:
  start_year: 2010
  batch_size: 50


#Run Code
python -m src.main


#Check Database after it runs to ensure everything is downloaded properly
-- In psql or pgAdmin
\c equity_research_db

SELECT count(*) FROM companies;          -- ~500–503
SELECT count(*) FROM filings;            -- 10k–25k+
SELECT count(*) FROM filings WHERE download_status = true;  -- should be close to total
