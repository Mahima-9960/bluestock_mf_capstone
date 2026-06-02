-- sql/schema.sql

-- Table for Mutual Fund Metadata
CREATE TABLE IF NOT EXISTS fund_master (
    scheme_code INTEGER PRIMARY KEY,
    scheme_name TEXT,
    category TEXT,
    sub_category TEXT,
    risk_grade TEXT,
    aum_crore REAL
);

-- Table for Historical NAV Data
CREATE TABLE IF NOT EXISTS nav_history (
    scheme_code INTEGER,
    nav_date DATE,
    nav REAL,
    FOREIGN KEY (scheme_code) REFERENCES fund_master (scheme_code)
);

-- Indexes to make your EDA queries run much faster
CREATE INDEX IF NOT EXISTS idx_nav_date ON nav_history(nav_date);
CREATE INDEX IF NOT EXISTS idx_scheme_code ON nav_history(scheme_code);