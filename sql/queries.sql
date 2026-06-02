-- sql/queries.sql

-- 1. Funds with Expense Ratio < 1% (Cost-efficient funds)
SELECT scheme_name, category, expense_ratio_pct 
FROM dim_fund 
WHERE expense_ratio_pct < 1.0 
ORDER BY expense_ratio_pct ASC;

-- 2. Average NAV per Month for a specific fund (e.g., HDFC Top 100)
SELECT strftime('%Y-%m', nav_date) AS month, AVG(nav) AS avg_nav 
FROM fact_nav 
WHERE amfi_code = '125497' 
GROUP BY month 
ORDER BY month DESC;

-- 3. Total Transaction Inflow by State
SELECT state, SUM(amount_inr) AS total_inflow 
FROM fact_transactions 
WHERE transaction_type IN ('SIP', 'LUMPSUM') 
GROUP BY state 
ORDER BY total_inflow DESC;

-- 4. Top 5 Funds by 3-Year Return
SELECT f.scheme_name, p.return_3yr_pct 
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.return_3yr_pct DESC 
LIMIT 5;

-- 5. Transaction Count by Type (SIP vs Lumpsum vs Redemption)
SELECT transaction_type, COUNT(*) AS total_transactions 
FROM fact_transactions 
GROUP BY transaction_type;

-- 6. Top 5 Funds by Best Risk-Adjusted Return (Sharpe Ratio)
SELECT f.scheme_name, f.category, p.sharpe_ratio 
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.sharpe_ratio IS NOT NULL
ORDER BY p.sharpe_ratio DESC 
LIMIT 5;

-- 7. Average Transaction Amount by City (Top 10 Cities)
SELECT city, AVG(amount_inr) AS avg_transaction_size 
FROM fact_transactions 
GROUP BY city 
ORDER BY avg_transaction_size DESC 
LIMIT 10;

-- 8. KYC Status Distribution of Investors
SELECT kyc_status, COUNT(DISTINCT investor_id) AS total_investors 
FROM fact_transactions 
GROUP BY kyc_status;

-- 9. Funds with the Highest Maximum Drawdown (Highest Risk)
SELECT f.scheme_name, p.max_drawdown_pct 
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.max_drawdown_pct ASC -- Drawdown is negative, so ASC gets the worst drops
LIMIT 5;

-- 10. Total SIP Amount Processed in 2025
SELECT SUM(amount_inr) AS total_sip_2025 
FROM fact_transactions 
WHERE transaction_type = 'SIP' AND strftime('%Y', transaction_date) = '2025';