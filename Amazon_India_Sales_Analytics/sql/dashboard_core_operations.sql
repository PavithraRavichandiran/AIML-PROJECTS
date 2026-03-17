-- ============================================================================
-- Amazon India Sales Analytics - Dashboard Core SQL Operations
-- Purpose: Validation, KPI Aggregations, Complex Joins, Performance, BI Views
-- Target DB: SQLite (AmazonIndia.db)
-- ============================================================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

-- ============================================================================
-- 1) DATA LOADING & VALIDATION PROCEDURES
-- ============================================================================

CREATE TABLE IF NOT EXISTS data_quality_audit (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_ts TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    check_name TEXT NOT NULL,
    check_category TEXT NOT NULL,
    failed_count INTEGER NOT NULL,
    total_count INTEGER,
    status TEXT NOT NULL,
    notes TEXT
);

DELETE FROM data_quality_audit WHERE DATE(audit_ts) = DATE('now');

INSERT INTO data_quality_audit (check_name, check_category, failed_count, total_count, status, notes)
SELECT
    'transactions_missing_customer_fk',
    'referential_integrity',
    COUNT(*),
    (SELECT COUNT(*) FROM transactions),
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    'transactions.customer_id not found in customers.customer_id'
FROM transactions t
LEFT JOIN customers c ON c.customer_id = t.customer_id
WHERE c.customer_id IS NULL;

INSERT INTO data_quality_audit (check_name, check_category, failed_count, total_count, status, notes)
SELECT
    'transactions_missing_product_fk',
    'referential_integrity',
    COUNT(*),
    (SELECT COUNT(*) FROM transactions),
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    'transactions.product_id not found in products.product_id'
FROM transactions t
LEFT JOIN products p ON p.product_id = t.product_id
WHERE p.product_id IS NULL;

INSERT INTO data_quality_audit (check_name, check_category, failed_count, total_count, status, notes)
SELECT
    'transactions_missing_time_fk',
    'referential_integrity',
    COUNT(*),
    (SELECT COUNT(*) FROM transactions),
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    'DATE(transactions.order_date) not found in time_dimension.date_value'
FROM transactions t
LEFT JOIN time_dimension d ON d.date_value = DATE(t.order_date)
WHERE d.date_value IS NULL;

INSERT INTO data_quality_audit (check_name, check_category, failed_count, total_count, status, notes)
SELECT
    'invalid_financial_rows',
    'domain_validation',
    COUNT(*),
    (SELECT COUNT(*) FROM transactions),
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    'negative amounts, non-positive quantity, or discount out of range'
FROM transactions
WHERE final_amount_inr < 0
   OR original_price_inr < 0
   OR quantity <= 0
   OR (discount_percent IS NOT NULL AND (discount_percent < 0 OR discount_percent > 100));

INSERT INTO data_quality_audit (check_name, check_category, failed_count, total_count, status, notes)
SELECT
    'invalid_rating_rows',
    'domain_validation',
    COUNT(*),
    (SELECT COUNT(*) FROM transactions),
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    'customer_rating or product_rating outside [0,5]'
FROM transactions
WHERE (customer_rating IS NOT NULL AND (customer_rating < 0 OR customer_rating > 5))
   OR (product_rating IS NOT NULL AND (product_rating < 0 OR product_rating > 5));

INSERT INTO data_quality_audit (check_name, check_category, failed_count, total_count, status, notes)
SELECT
    'duplicate_transaction_ids',
    'uniqueness',
    COALESCE(SUM(cnt) - COUNT(*), 0),
    (SELECT COUNT(*) FROM transactions),
    CASE WHEN COALESCE(SUM(cnt) - COUNT(*), 0) = 0 THEN 'PASS' ELSE 'FAIL' END,
    'duplicate transaction_id values in transactions'
FROM (
    SELECT transaction_id, COUNT(*) AS cnt
    FROM transactions
    GROUP BY transaction_id
    HAVING COUNT(*) > 1
);

-- ============================================================================
-- 2) AGGREGATION QUERIES FOR DASHBOARD KPIs (Materialized KPI Tables)
-- ============================================================================

DROP TABLE IF EXISTS kpi_daily;
CREATE TABLE kpi_daily AS
SELECT
    DATE(t.order_date) AS order_date,
    d.year,
    d.month,
    d.month_name,
    d.quarter,
    d.season_name,
    d.is_festival_season,
    COUNT(*) AS orders,
    COUNT(DISTINCT t.customer_id) AS unique_customers,
    SUM(t.quantity) AS units_sold,
    ROUND(SUM(t.final_amount_inr), 2) AS revenue_inr,
    ROUND(AVG(t.final_amount_inr), 2) AS avg_order_value_inr,
    ROUND(SUM(t.final_amount_inr) / NULLIF(COUNT(DISTINCT t.customer_id), 0), 2) AS arpu_inr,
    ROUND(SUM(CASE WHEN t.is_prime_member = 1 THEN t.final_amount_inr ELSE 0 END), 2) AS prime_revenue_inr,
    ROUND(SUM(CASE WHEN t.is_festival_sale = 1 THEN t.final_amount_inr ELSE 0 END), 2) AS festival_revenue_inr,
    ROUND(SUM(CASE WHEN t.return_status IS NOT NULL AND LOWER(t.return_status) != 'not returned' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS return_rate_pct
FROM transactions t
JOIN time_dimension d ON d.date_value = DATE(t.order_date)
GROUP BY DATE(t.order_date), d.year, d.month, d.month_name, d.quarter, d.season_name, d.is_festival_season;

DROP TABLE IF EXISTS kpi_monthly;
CREATE TABLE kpi_monthly AS
SELECT
    d.year,
    d.month,
    d.month_name,
    d.quarter,
    COUNT(*) AS orders,
    COUNT(DISTINCT t.customer_id) AS unique_customers,
    COUNT(DISTINCT t.product_id) AS unique_products,
    SUM(t.quantity) AS units_sold,
    ROUND(SUM(t.final_amount_inr), 2) AS revenue_inr,
    ROUND(AVG(t.final_amount_inr), 2) AS avg_order_value_inr,
    ROUND(SUM(t.final_amount_inr) / NULLIF(COUNT(*), 0), 2) AS revenue_per_order_inr,
    ROUND(SUM(t.final_amount_inr) / NULLIF(COUNT(DISTINCT t.customer_id), 0), 2) AS arpu_inr,
    ROUND(SUM(CASE WHEN t.payment_method = 'UPI' THEN t.final_amount_inr ELSE 0 END), 2) AS upi_revenue_inr,
    ROUND(SUM(CASE WHEN t.payment_method = 'Cash on Delivery' THEN t.final_amount_inr ELSE 0 END), 2) AS cod_revenue_inr
FROM transactions t
JOIN time_dimension d ON d.date_value = DATE(t.order_date)
GROUP BY d.year, d.month, d.month_name, d.quarter;

DROP TABLE IF EXISTS kpi_category_monthly;
CREATE TABLE kpi_category_monthly AS
SELECT
    d.year,
    d.month,
    t.category,
    t.subcategory,
    COUNT(*) AS orders,
    SUM(t.quantity) AS units_sold,
    ROUND(SUM(t.final_amount_inr), 2) AS revenue_inr,
    ROUND(AVG(t.discount_percent), 2) AS avg_discount_pct,
    ROUND(AVG(t.final_amount_inr), 2) AS avg_order_value_inr,
    ROUND(AVG(t.delivery_days), 2) AS avg_delivery_days
FROM transactions t
JOIN time_dimension d ON d.date_value = DATE(t.order_date)
GROUP BY d.year, d.month, t.category, t.subcategory;

-- ============================================================================
-- 3) COMPLEX JOINS FOR MULTI-TABLE ANALYSIS (BI Views)
-- ============================================================================

CREATE VIEW IF NOT EXISTS vw_fact_sales_enriched AS
SELECT
    t.transaction_id,
    DATE(t.order_date) AS order_date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,
    d.day_of_week,
    d.day_name,
    d.season_name,
    d.is_festival_season,
    d.festival_season,
    c.customer_id,
    c.city AS customer_city_dim,
    c.state AS customer_state_dim,
    c.customer_tier,
    c.customer_spending_tier,
    c.age_group,
    c.customer_segment,
    c.is_prime_member AS customer_prime_flag,
    p.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    p.brand,
    p.original_price_inr AS product_list_price_inr,
    p.cost_price_inr,
    p.is_bestseller,
    t.quantity,
    t.discount_percent,
    t.discounted_price_inr,
    t.final_amount_inr,
    (t.final_amount_inr - (COALESCE(p.cost_price_inr, 0) * t.quantity)) AS est_gross_margin_inr,
    t.payment_method,
    t.delivery_days,
    t.return_status,
    t.is_festival_sale
FROM transactions t
LEFT JOIN customers c ON c.customer_id = t.customer_id
LEFT JOIN products p ON p.product_id = t.product_id
LEFT JOIN time_dimension d ON d.date_value = DATE(t.order_date);

CREATE VIEW IF NOT EXISTS vw_customer_360 AS
SELECT
    c.customer_id,
    c.customer_tier,
    c.customer_spending_tier,
    c.customer_segment,
    c.city,
    c.state,
    c.is_prime_member,
    c.total_transactions AS profile_transactions,
    c.total_spend_inr AS profile_total_spend,
    COUNT(t.transaction_id) AS txn_count,
    ROUND(SUM(t.final_amount_inr), 2) AS txn_revenue_inr,
    ROUND(AVG(t.final_amount_inr), 2) AS txn_aov_inr,
    COUNT(DISTINCT t.category) AS categories_bought,
    MIN(DATE(t.order_date)) AS first_order_date,
    MAX(DATE(t.order_date)) AS last_order_date
FROM customers c
LEFT JOIN transactions t ON t.customer_id = c.customer_id
GROUP BY
    c.customer_id, c.customer_tier, c.customer_spending_tier, c.customer_segment,
    c.city, c.state, c.is_prime_member, c.total_transactions, c.total_spend_inr;

CREATE VIEW IF NOT EXISTS vw_product_360 AS
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    p.brand,
    p.is_bestseller,
    p.is_prime_eligible,
    p.product_rating,
    p.stock_quantity,
    COUNT(t.transaction_id) AS txn_count,
    ROUND(SUM(t.final_amount_inr), 2) AS revenue_inr,
    ROUND(SUM(t.quantity), 2) AS units_sold,
    ROUND(AVG(t.discount_percent), 2) AS avg_discount_pct,
    ROUND(AVG(t.delivery_days), 2) AS avg_delivery_days,
    ROUND(SUM(CASE WHEN t.return_status IS NOT NULL AND LOWER(t.return_status) != 'not returned' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(t.transaction_id), 0), 2) AS return_rate_pct
FROM products p
LEFT JOIN transactions t ON t.product_id = p.product_id
GROUP BY
    p.product_id, p.product_name, p.category, p.subcategory, p.brand,
    p.is_bestseller, p.is_prime_eligible, p.product_rating, p.stock_quantity;

-- ============================================================================
-- 4) PERFORMANCE OPTIMIZATION FOR LARGE DATASETS
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_transactions_order_date_only ON transactions(DATE(order_date));
CREATE INDEX IF NOT EXISTS idx_transactions_join_customer_date ON transactions(customer_id, order_date);
CREATE INDEX IF NOT EXISTS idx_transactions_join_product_date ON transactions(product_id, order_date);
CREATE INDEX IF NOT EXISTS idx_transactions_kpi_grouping ON transactions(order_year, order_month, category, subcategory);
CREATE INDEX IF NOT EXISTS idx_transactions_payment_year ON transactions(payment_method, order_year);
CREATE INDEX IF NOT EXISTS idx_transactions_prime_year ON transactions(is_prime_member, order_year);

CREATE INDEX IF NOT EXISTS idx_customers_city_state_tier ON customers(city, state, customer_tier);
CREATE INDEX IF NOT EXISTS idx_products_cat_brand_bestseller ON products(category, brand, is_bestseller);
CREATE INDEX IF NOT EXISTS idx_time_dimension_year_month ON time_dimension(year, month);

ANALYZE;

-- ============================================================================
-- 5) CONNECTION SETUP FOR VISUALIZATION TOOLS (BI-Friendly Views)
-- ============================================================================

CREATE VIEW IF NOT EXISTS vw_bi_daily_kpi AS
SELECT
    order_date,
    year,
    month,
    month_name,
    quarter,
    season_name,
    is_festival_season,
    orders,
    unique_customers,
    units_sold,
    revenue_inr,
    avg_order_value_inr,
    arpu_inr,
    prime_revenue_inr,
    festival_revenue_inr,
    return_rate_pct
FROM kpi_daily;

CREATE VIEW IF NOT EXISTS vw_bi_monthly_kpi AS
SELECT
    year,
    month,
    month_name,
    quarter,
    orders,
    unique_customers,
    unique_products,
    units_sold,
    revenue_inr,
    avg_order_value_inr,
    revenue_per_order_inr,
    arpu_inr,
    upi_revenue_inr,
    cod_revenue_inr
FROM kpi_monthly;

CREATE VIEW IF NOT EXISTS vw_bi_category_kpi AS
SELECT
    year,
    month,
    category,
    subcategory,
    orders,
    units_sold,
    revenue_inr,
    avg_discount_pct,
    avg_order_value_inr,
    avg_delivery_days
FROM kpi_category_monthly;

-- ============================================================================
-- QUICK HEALTH CHECK OUTPUTS
-- ============================================================================

-- Select from these after running script:
-- SELECT * FROM data_quality_audit ORDER BY audit_id;
-- SELECT * FROM vw_bi_monthly_kpi ORDER BY year DESC, month DESC LIMIT 24;
-- SELECT * FROM vw_bi_category_kpi ORDER BY year DESC, month DESC, revenue_inr DESC LIMIT 50;
-- SELECT * FROM vw_fact_sales_enriched LIMIT 20;
