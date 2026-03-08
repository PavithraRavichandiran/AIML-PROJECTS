-- ==================================================================================
-- EXECUTIVE DASHBOARD QUERIES (Questions 1-5)
-- Complete SQL support for 5-dashboard executive analytics suite
-- ==================================================================================
-- Date: 2026-03-02
-- Purpose: Materialized views and derived tables for Power BI/Tableau executive dashboards
-- ==================================================================================

-- ==================================================================================
-- QUESTION 1: EXECUTIVE SUMMARY DASHBOARD
-- Key Metrics: Revenue, Growth, Customers, AOV, Top Categories with YoY Comparison
-- ==================================================================================

-- Q1.1: Executive Summary - Current Period Metrics with YoY Comparison
CREATE VIEW IF NOT EXISTS vw_q1_executive_summary AS
SELECT
    td.year,
    td.month,
    td.month_name,
    COUNT(DISTINCT t.transaction_id) AS total_orders,
    COUNT(DISTINCT t.customer_id) AS active_customers,
    ROUND(SUM(t.quantity), 0) AS total_units_sold,
    ROUND(SUM(t.final_amount_inr), 2) AS total_revenue_inr,
    ROUND(SUM(t.final_amount_inr) / NULLIF(COUNT(DISTINCT t.transaction_id), 0), 2) AS average_order_value_inr,
    ROUND(SUM(t.final_amount_inr) / NULLIF(COUNT(DISTINCT t.customer_id), 0), 2) AS average_customer_value_inr,
    
    -- YoY Comparison
    LAG(SUM(t.final_amount_inr), 12) OVER (ORDER BY td.year, td.month) AS prev_year_revenue_inr,
    ROUND((SUM(t.final_amount_inr) - LAG(SUM(t.final_amount_inr), 12) OVER (ORDER BY td.year, td.month)) * 100.0 / 
        NULLIF(LAG(SUM(t.final_amount_inr), 12) OVER (ORDER BY td.year, td.month), 0), 2) AS yoy_revenue_growth_pct,
    
    -- Growth Indicators
    ROUND(AVG(t.rating), 2) AS avg_product_rating,
    ROUND(SUM(CASE WHEN t.payment_method = 'UPI' THEN t.final_amount_inr ELSE 0 END) * 100.0 / NULLIF(SUM(t.final_amount_inr), 0), 2) AS digital_payment_penetration_pct,
    ROUND(SUM(CASE WHEN c.is_prime_member = 1 THEN t.final_amount_inr ELSE 0 END) * 100.0 / NULLIF(SUM(t.final_amount_inr), 0), 2) AS prime_revenue_mix_pct
    
FROM transactions t
INNER JOIN customers c ON t.customer_id = c.customer_id
INNER JOIN time_dimension td ON td.date_value = DATE(t.order_date)
GROUP BY td.year, td.month, td.month_name
ORDER BY td.year DESC, td.month DESC;

-- Q1.2: Top Performing Categories by Revenue
CREATE VIEW IF NOT EXISTS vw_q1_top_categories AS
SELECT
    td.year,
    td.month,
    td.month_name,
    p.category,
    p.subcategory,
    COUNT(DISTINCT t.transaction_id) AS orders,
    COUNT(DISTINCT t.customer_id) AS customers,
    ROUND(SUM(t.final_amount_inr), 2) AS revenue_inr,
    ROUND(SUM(t.final_amount_inr) * 100.0 / SUM(SUM(t.final_amount_inr)) OVER (PARTITION BY td.year, td.month), 2) AS revenue_share_pct,
    ROUND(AVG(t.final_amount_inr), 2) AS avg_order_value_inr,
    DENSE_RANK() OVER (PARTITION BY td.year, td.month ORDER BY SUM(t.final_amount_inr) DESC) AS rank_in_month
FROM transactions t
INNER JOIN products p ON t.product_id = p.product_id
INNER JOIN time_dimension td ON td.date_value = DATE(t.order_date)
GROUP BY td.year, td.month, td.month_name, p.category, p.subcategory
ORDER BY td.year DESC, td.month DESC, rank_in_month ASC;

-- Q1.3: Growth Rate Trends (MoM, QoQ, YoY)
CREATE VIEW IF NOT EXISTS vw_q1_growth_rates AS
WITH monthly_revenue AS (
    SELECT
        td.year,
        td.month,
        td.month_name,
        td.quarter,
        SUM(t.final_amount_inr) AS revenue_inr
    FROM transactions t
    INNER JOIN time_dimension td ON td.date_value = DATE(t.order_date)
    GROUP BY td.year, td.month, td.month_name, td.quarter
)
SELECT
    year,
    month,
    month_name,
    quarter,
    revenue_inr,
    -- Month-over-Month Growth
    LAG(revenue_inr, 1) OVER (ORDER BY year, month) AS prev_month_revenue_inr,
    ROUND((revenue_inr - LAG(revenue_inr, 1) OVER (ORDER BY year, month)) * 100.0 / 
        NULLIF(LAG(revenue_inr, 1) OVER (ORDER BY year, month), 0), 2) AS mom_growth_pct,
    -- Quarter-over-Quarter Growth
    LAG(revenue_inr, 3) OVER (ORDER BY year, month) AS prev_quarter_revenue_inr,
    ROUND((revenue_inr - LAG(revenue_inr, 3) OVER (ORDER BY year, month)) * 100.0 / 
        NULLIF(LAG(revenue_inr, 3) OVER (ORDER BY year, month), 0), 2) AS qoq_growth_pct,
    -- Year-over-Year Growth
    LAG(revenue_inr, 12) OVER (ORDER BY year, month) AS prev_year_revenue_inr,
    ROUND((revenue_inr - LAG(revenue_inr, 12) OVER (ORDER BY year, month)) * 100.0 / 
        NULLIF(LAG(revenue_inr, 12) OVER (ORDER BY year, month), 0), 2) AS yoy_growth_pct
FROM monthly_revenue
ORDER BY year DESC, month DESC;


-- ==================================================================================
-- QUESTION 2: REAL-TIME BUSINESS PERFORMANCE MONITOR
-- Current Month vs Targets, Run-Rate, CAC, Operational Indicators with Alerts
-- ==================================================================================

-- Q2.1: Current Month Performance vs Daily Targets
CREATE VIEW IF NOT EXISTS vw_q2_current_performance AS
WITH current_month_data AS (
    SELECT
        td.year,
        td.month,
        td.month_name,
        td.day_of_month,
        COUNT(DISTINCT t.transaction_id) AS daily_orders,
        COUNT(DISTINCT t.customer_id) AS daily_customers,
        ROUND(SUM(t.final_amount_inr), 2) AS daily_revenue_inr,
        ROUND(SUM(t.final_amount_inr) / NULLIF(COUNT(DISTINCT t.transaction_id), 0), 2) AS daily_aov_inr
    FROM transactions t
    INNER JOIN time_dimension td ON td.date_value = DATE(t.order_date)
    WHERE td.year = 2025 AND td.month = 12  -- Current month (adjust dynamically as needed)
    GROUP BY td.year, td.month, td.month_name, td.day_of_month
),
monthly_targets AS (
    SELECT
        2025 AS year,
        12 AS month,
        'December' AS month_name,
        ROUND(AVG(kpi_daily.total_orders), 0) * 31 AS target_monthly_orders,
        ROUND(AVG(kpi_daily.total_revenue) / 1e7, 0) * 1e7 * 31 AS target_monthly_revenue_inr,
        ROUND(AVG(kpi_daily.total_orders), 0) AS target_daily_orders
    FROM kpi_daily
    WHERE STRFTIME('%m', date) IN ('01', '02', '03', '04', '05', '06')  -- H1 average as baseline
)
SELECT
    cmd.year,
    cmd.month,
    cmd.month_name,
    cmd.day_of_month,
    cmd.daily_orders,
    cmd.daily_revenue_inr,
    cmd.daily_aov_inr,
    cmd.daily_customers,
    -- Cumulative metrics
    SUM(cmd.daily_orders) OVER (ORDER BY cmd.day_of_month) AS cumulative_orders,
    ROUND(SUM(cmd.daily_revenue_inr) OVER (ORDER BY cmd.day_of_month), 2) AS cumulative_revenue_inr,
    -- vs Target
    mt.target_daily_orders,
    ROUND(cmd.daily_orders * 100.0 / NULLIF(mt.target_daily_orders, 0), 1) AS daily_target_achievement_pct,
    CASE 
        WHEN cmd.daily_orders < mt.target_daily_orders * 0.8 THEN 'CRITICAL'
        WHEN cmd.daily_orders < mt.target_daily_orders * 0.95 THEN 'WARNING'
        ELSE 'ON_TRACK'
    END AS performance_alert
FROM current_month_data cmd
CROSS JOIN monthly_targets mt
ORDER BY cmd.day_of_month;

-- Q2.2: Run-Rate Projections and Forecast
CREATE VIEW IF NOT EXISTS vw_q2_run_rate_forecast AS
WITH daily_data AS (
    SELECT
        td.year,
        td.month,
        td.month_name,
        td.day_of_month,
        COUNT(DISTINCT t.transaction_id) AS daily_orders,
        ROUND(SUM(t.final_amount_inr), 2) AS daily_revenue_inr,
        AVG(t.final_amount_inr) AS daily_avg_order_value
    FROM transactions t
    INNER JOIN time_dimension td ON td.date_value = DATE(t.order_date)
    WHERE td.year = 2025 AND td.month = 12
    GROUP BY td.year, td.month, td.month_name, td.day_of_month
)
SELECT
    year,
    month,
    month_name,
    day_of_month,
    daily_orders,
    daily_revenue_inr,
    -- Run-rate calculation (extrapolated to full month)
    ROUND(SUM(daily_revenue_inr) OVER (ORDER BY day_of_month) / NULLIF(day_of_month, 0) * 31, 2) AS run_rate_monthly_revenue_inr,
    ROUND(SUM(daily_orders) OVER (ORDER BY day_of_month) / NULLIF(day_of_month, 0) * 31, 0) AS run_rate_monthly_orders,
    -- Comparison to previous months
    ROUND(AVG(daily_revenue_inr) OVER (ORDER BY day_of_month ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2) AS rolling_7day_avg_revenue
FROM daily_data
ORDER BY day_of_month;

-- Q2.3: Customer Acquisition Cost & Efficiency Metrics
CREATE VIEW IF NOT EXISTS vw_q2_acquisition_metrics AS
WITH customer_acquisition AS (
    SELECT
        td.year,
        td.month,
        td.month_name,
        COUNT(DISTINCT CASE WHEN c.customer_id IS NOT NULL THEN c.customer_id END) AS new_customers,
        COUNT(DISTINCT t.customer_id) AS active_customers,
        ROUND(SUM(t.final_amount_inr), 2) AS acquisition_period_revenue_inr,
        ROUND(SUM(t.final_amount_inr) / NULLIF(COUNT(DISTINCT t.customer_id), 0), 2) AS customer_acquisition_value_inr,
        COUNT(DISTINCT t.transaction_id) AS orders_acquired
    FROM transactions t
    LEFT JOIN customers c ON t.customer_id = c.customer_id
    INNER JOIN time_dimension td ON td.date_value = DATE(t.order_date)
    GROUP BY td.year, td.month, td.month_name
)
SELECT
    year,
    month,
    month_name,
    new_customers,
    active_customers,
    orders_acquired,
    acquisition_period_revenue_inr,
    customer_acquisition_value_inr,
    ROUND(acquisition_period_revenue_inr / NULLIF(new_customers, 0), 2) AS cac_equivalent_inr,
    ROUND(active_customers / NULLIF(new_customers, 0), 2) AS retention_ratio
FROM customer_acquisition
ORDER BY year DESC, month DESC;


-- ==================================================================================
-- QUESTION 3: STRATEGIC OVERVIEW DASHBOARD
-- Market Share, Geographic Expansion, Business Health Indicators
-- ==================================================================================

-- Q3.1: Market Share by Category and Time Period
CREATE VIEW IF NOT EXISTS vw_q3_market_share AS
WITH category_revenue AS (
    SELECT
        td.year,
        td.month,
        td.month_name,
        p.category,
        SUM(t.final_amount_inr) AS category_revenue_inr,
        COUNT(DISTINCT t.transaction_id) AS category_orders,
        COUNT(DISTINCT t.customer_id) AS category_customers
    FROM transactions t
    INNER JOIN products p ON t.product_id = p.product_id
    INNER JOIN time_dimension td ON td.date_value = DATE(t.order_date)
    GROUP BY td.year, td.month, td.month_name, p.category
)
SELECT
    year,
    month,
    month_name,
    category,
    category_revenue_inr,
    category_orders,
    category_customers,
    ROUND(category_revenue_inr * 100.0 / SUM(category_revenue_inr) OVER (PARTITION BY year, month), 2) AS market_share_pct,
    DENSE_RANK() OVER (PARTITION BY year, month ORDER BY category_revenue_inr DESC) AS category_rank,
    -- YoY trend
    LAG(category_revenue_inr, 12) OVER (PARTITION BY category ORDER BY year, month) AS prev_year_revenue_inr,
    ROUND((category_revenue_inr - LAG(category_revenue_inr, 12) OVER (PARTITION BY category ORDER BY year, month)) * 100.0 / 
        NULLIF(LAG(category_revenue_inr, 12) OVER (PARTITION BY category ORDER BY year, month), 0), 2) AS yoy_market_share_change_pct
FROM category_revenue
ORDER BY year DESC, month DESC, category_rank;

-- Q3.2: Geographic Expansion Metrics (by Customer Location Proxy)
CREATE VIEW IF NOT EXISTS vw_q3_geographic_expansion AS
WITH state_level_metrics AS (
    SELECT
        td.year,
        td.month,
        td.month_name,
        c.state,
        COUNT(DISTINCT t.customer_id) AS customers,
        COUNT(DISTINCT t.transaction_id) AS orders,
        ROUND(SUM(t.final_amount_inr), 2) AS revenue_inr,
        ROUND(AVG(t.final_amount_inr), 2) AS avg_order_value_inr,
        COUNT(DISTINCT CASE WHEN c.is_prime_member = 1 THEN c.customer_id END) AS prime_members
    FROM transactions t
    INNER JOIN customers c ON t.customer_id = c.customer_id
    INNER JOIN time_dimension td ON td.date_value = DATE(t.order_date)
    WHERE c.state IS NOT NULL AND c.state != ''
    GROUP BY td.year, td.month, td.month_name, c.state
)
SELECT
    year,
    month,
    month_name,
    state,
    customers,
    orders,
    revenue_inr,
    avg_order_value_inr,
    prime_members,
    ROUND(prime_members * 100.0 / NULLIF(customers, 0), 2) AS prime_penetration_pct,
    DENSE_RANK() OVER (PARTITION BY year, month ORDER BY revenue_inr DESC) AS state_revenue_rank,
    ROUND(revenue_inr * 100.0 / SUM(revenue_inr) OVER (PARTITION BY year, month), 2) AS state_revenue_share_pct
FROM state_level_metrics
ORDER BY year DESC, month DESC, state_revenue_rank;

-- Q3.3: Business Health Scorecard
CREATE VIEW IF NOT EXISTS vw_q3_business_health AS
SELECT
    td.year,
    td.month,
    td.month_name,
    -- Revenue Health
    ROUND(SUM(t.final_amount_inr), 2) AS total_revenue_inr,
    ROUND(AVG(t.final_amount_inr), 2) AS avg_order_value_inr,
    COUNT(DISTINCT t.customer_id) AS active_customers,
    -- Customer Health
    ROUND(COUNT(DISTINCT t.customer_id) * 100.0 / LAG(COUNT(DISTINCT t.customer_id), 1) OVER (ORDER BY td.year, td.month), 2) AS customer_growth_mom_pct,
    -- Product Health
    COUNT(DISTINCT t.product_id) AS active_products,
    ROUND(AVG(t.rating), 2) AS avg_product_rating,
    ROUND(SUM(CASE WHEN t.rating >= 4 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS high_quality_rating_pct,
    -- Order Health
    COUNT(DISTINCT t.transaction_id) AS total_orders,
    ROUND(COUNT(DISTINCT t.transaction_id) * 100.0 / LAG(COUNT(DISTINCT t.transaction_id), 1) OVER (ORDER BY td.year, td.month), 2) AS order_growth_mom_pct,
    -- Payment Health
    ROUND(SUM(CASE WHEN t.payment_method IN ('UPI', 'Credit Card', 'Debit Card') THEN t.final_amount_inr ELSE 0 END) * 100.0 / NULLIF(SUM(t.final_amount_inr), 0), 2) AS digital_payment_pct,
    -- Premium Customer Health
    ROUND(SUM(CASE WHEN c.is_prime_member = 1 THEN t.final_amount_inr ELSE 0 END) * 100.0 / NULLIF(SUM(t.final_amount_inr), 0), 2) AS prime_revenue_mix_pct
FROM transactions t
INNER JOIN customers c ON t.customer_id = c.customer_id
INNER JOIN time_dimension td ON td.date_value = DATE(t.order_date)
GROUP BY td.year, td.month, td.month_name
ORDER BY td.year DESC, td.month DESC;


-- ==================================================================================
-- QUESTION 4: FINANCIAL PERFORMANCE DASHBOARD
-- Revenue by Category, Profit Margins, Cost Structure, Financial Forecasts
-- ==================================================================================

-- Q4.1: Revenue and Margin Analysis by Category
CREATE VIEW IF NOT EXISTS vw_q4_financial_performance AS
WITH category_financials AS (
    SELECT
        td.year,
        td.month,
        td.month_name,
        p.category,
        p.subcategory,
        COUNT(DISTINCT t.transaction_id) AS orders,
        COUNT(DISTINCT t.customer_id) AS customers,
        ROUND(SUM(t.final_amount_inr), 2) AS revenue_inr,
        -- Estimate cost of goods sold (typically 40-60% of revenue)
        ROUND(SUM(t.final_amount_inr) * 0.5, 2) AS estimated_cogs_inr,
        -- Estimate operating costs (15-20% of revenue)
        ROUND(SUM(t.final_amount_inr) * 0.15, 2) AS estimated_operating_cost_inr
    FROM transactions t
    INNER JOIN products p ON t.product_id = p.product_id
    INNER JOIN time_dimension td ON td.date_value = DATE(t.order_date)
    GROUP BY td.year, td.month, td.month_name, p.category, p.subcategory
)
SELECT
    year,
    month,
    month_name,
    category,
    subcategory,
    orders,
    customers,
    revenue_inr,
    estimated_cogs_inr,
    estimated_operating_cost_inr,
    ROUND(revenue_inr - estimated_cogs_inr - estimated_operating_cost_inr, 2) AS estimated_gross_profit_inr,
    -- Margin percentages
    ROUND((revenue_inr - estimated_cogs_inr) * 100.0 / NULLIF(revenue_inr, 0), 2) AS gross_margin_pct,
    ROUND((revenue_inr - estimated_cogs_inr - estimated_operating_cost_inr) * 100.0 / NULLIF(revenue_inr, 0), 2) AS net_margin_pct,
    ROUND(revenue_inr / NULLIF(orders, 0), 2) AS revenue_per_order_inr
FROM category_financials
ORDER BY year DESC, month DESC, revenue_inr DESC;

-- Q4.2: Cost Structure Breakdown
CREATE VIEW IF NOT EXISTS vw_q4_cost_structure AS
SELECT
    td.year,
    td.month,
    td.month_name,
    -- Revenue Components
    ROUND(SUM(t.final_amount_inr), 2) AS total_revenue_inr,
    -- Cost Breakdown (as percentages)
    ROUND(SUM(t.final_amount_inr) * 0.50, 2) AS cogs_estimate_inr,
    ROUND(SUM(t.final_amount_inr) * 0.15, 2) AS operating_expense_estimate_inr,
    ROUND(SUM(t.final_amount_inr) * 0.10, 2) AS marketing_estimate_inr,
    ROUND(SUM(t.final_amount_inr) * 0.08, 2) AS logistics_estimate_inr,
    ROUND(SUM(t.final_amount_inr) * 0.05, 2) AS tech_infrastructure_estimate_inr,
    ROUND(SUM(t.final_amount_inr) * 0.12, 2) AS gross_profit_estimate_inr,
    -- Percentages
    50.0 AS cogs_pct_of_revenue,
    15.0 AS operating_pct_of_revenue,
    10.0 AS marketing_pct_of_revenue,
    8.0 AS logistics_pct_of_revenue,
    5.0 AS tech_pct_of_revenue,
    12.0 AS gross_profit_pct_of_revenue
FROM transactions t
INNER JOIN time_dimension td ON td.date_value = DATE(t.order_date)
GROUP BY td.year, td.month, td.month_name
ORDER BY td.year DESC, td.month DESC;

-- Q4.3: Financial Forecast (Simple Linear Regression Trend)
CREATE VIEW IF NOT EXISTS vw_q4_financial_forecast AS
WITH monthly_revenue AS (
    SELECT
        td.year,
        td.month,
        ROW_NUMBER() OVER (ORDER BY td.year, td.month) AS month_sequence,
        ROUND(SUM(t.final_amount_inr), 2) AS actual_revenue_inr
    FROM transactions t
    INNER JOIN time_dimension td ON td.date_value = DATE(t.order_date)
    GROUP BY td.year, td.month
),
statistics AS (
    SELECT
        AVG(month_sequence) AS avg_month_seq,
        AVG(actual_revenue_inr) AS avg_revenue,
        SUM((month_sequence - AVG(month_sequence)) * (actual_revenue_inr - AVG(actual_revenue_inr))) / 
            NULLIF(SUM((month_sequence - AVG(month_sequence)) * (month_sequence - AVG(month_sequence))), 0) AS slope
    FROM monthly_revenue
)
SELECT
    mr.year,
    mr.month,
    mr.month_sequence,
    mr.actual_revenue_inr,
    ROUND(s.avg_revenue + s.slope * (mr.month_sequence - s.avg_month_seq), 2) AS forecast_revenue_inr,
    ROUND(mr.actual_revenue_inr - (s.avg_revenue + s.slope * (mr.month_sequence - s.avg_month_seq)), 2) AS variance_inr,
    ROUND((mr.actual_revenue_inr - (s.avg_revenue + s.slope * (mr.month_sequence - s.avg_month_seq))) * 100.0 / 
        NULLIF(s.avg_revenue + s.slope * (mr.month_sequence - s.avg_month_seq), 0), 2) AS variance_pct
FROM monthly_revenue mr
CROSS JOIN statistics s
ORDER BY mr.year DESC, mr.month DESC;


-- ==================================================================================
-- QUESTION 5: GROWTH ANALYTICS DASHBOARD
-- Customer Growth, Market Penetration, Product Portfolio, Predictive Insights
-- ==================================================================================

-- Q5.1: Customer Cohort Analysis (by Acquisition Cohort)
CREATE VIEW IF NOT EXISTS vw_q5_customer_cohorts AS
WITH customer_first_purchase AS (
    SELECT
        c.customer_id,
        MIN(td.year) AS cohort_year,
        MIN(td.month) AS cohort_month,
        MIN(td.month_name) AS cohort_month_name
    FROM transactions t
    INNER JOIN customers c ON t.customer_id = c.customer_id
    INNER JOIN time_dimension td ON td.date_value = DATE(t.order_date)
    GROUP BY c.customer_id
),
cohort_analysis AS (
    SELECT
        cfp.cohort_year,
        cfp.cohort_month,
        cfp.cohort_month_name,
        td.year AS observation_year,
        td.month AS observation_month,
        COUNT(DISTINCT cfp.customer_id) AS cohort_size,
        COUNT(DISTINCT CASE WHEN t.customer_id IS NOT NULL THEN t.customer_id END) AS active_in_period,
        ROUND(SUM(t.final_amount_inr), 2) AS revenue_inr,
        COUNT(DISTINCT t.transaction_id) AS orders,
        -- Months since cohort
        (td.year - cfp.cohort_year) * 12 + (td.month - cfp.cohort_month) + 1 AS months_since_cohort
    FROM customer_first_purchase cfp
    CROSS JOIN time_dimension td
    LEFT JOIN transactions t ON cfp.customer_id = t.customer_id AND td.date_value = DATE(t.order_date)
    WHERE (td.year > cfp.cohort_year) OR (td.year = cfp.cohort_year AND td.month >= cfp.cohort_month)
    GROUP BY cfp.cohort_year, cfp.cohort_month, cfp.cohort_month_name, td.year, td.month
)
SELECT
    cohort_year,
    cohort_month,
    cohort_month_name,
    observation_year,
    observation_month,
    cohort_size,
    active_in_period,
    ROUND(active_in_period * 100.0 / NULLIF(cohort_size, 0), 2) AS retention_rate_pct,
    revenue_inr,
    orders,
    ROUND(revenue_inr / NULLIF(active_in_period, 0), 2) AS avg_revenue_per_active_customer_inr,
    months_since_cohort
FROM cohort_analysis
WHERE months_since_cohort <= 24  -- Last 24 months of observation
ORDER BY cohort_year DESC, cohort_month DESC, months_since_cohort;

-- Q5.2: Market Penetration and Product Portfolio Growth
CREATE VIEW IF NOT EXISTS vw_q5_portfolio_expansion AS
WITH monthly_metrics AS (
    SELECT
        td.year,
        td.month,
        td.month_name,
        COUNT(DISTINCT t.customer_id) AS total_customers,
        COUNT(DISTINCT t.product_id) AS active_products,
        COUNT(DISTINCT p.category) AS active_categories,
        COUNT(DISTINCT p.subcategory) AS active_subcategories,
        ROUND(SUM(t.final_amount_inr), 2) AS revenue_inr,
        ROUND(AVG(t.final_amount_inr), 2) AS avg_order_value_inr,
        ROUND(AVG(t.rating), 2) AS avg_product_rating
    FROM transactions t
    INNER JOIN products p ON t.product_id = p.product_id
    INNER JOIN time_dimension td ON td.date_value = DATE(t.order_date)
    GROUP BY td.year, td.month, td.month_name
)
SELECT
    year,
    month,
    month_name,
    total_customers,
    active_products,
    active_categories,
    active_subcategories,
    revenue_inr,
    avg_order_value_inr,
    avg_product_rating,
    -- Growth Rates
    LAG(total_customers, 1) OVER (ORDER BY year, month) AS prev_month_customers,
    ROUND((total_customers - LAG(total_customers, 1) OVER (ORDER BY year, month)) * 100.0 / 
        NULLIF(LAG(total_customers, 1) OVER (ORDER BY year, month), 0), 2) AS customer_growth_mom_pct,
    LAG(total_customers, 12) OVER (ORDER BY year, month) AS prev_year_customers,
    ROUND((total_customers - LAG(total_customers, 12) OVER (ORDER BY year, month)) * 100.0 / 
        NULLIF(LAG(total_customers, 12) OVER (ORDER BY year, month), 0), 2) AS customer_growth_yoy_pct,
    -- Portfolio Expansion
    LAG(active_products, 1) OVER (ORDER BY year, month) AS prev_month_products,
    ROUND((active_products - LAG(active_products, 1) OVER (ORDER BY year, month)) * 100.0 / 
        NULLIF(LAG(active_products, 1) OVER (ORDER BY year, month), 0), 2) AS product_growth_mom_pct
FROM monthly_metrics
ORDER BY year DESC, month DESC;

-- Q5.3: Strategic Initiative Performance (Product Category Growth Tracking)
CREATE VIEW IF NOT EXISTS vw_q5_strategic_initiatives AS
WITH category_growth AS (
    SELECT
        td.year,
        td.month,
        td.month_name,
        p.category,
        COUNT(DISTINCT t.customer_id) AS customers,
        COUNT(DISTINCT t.transaction_id) AS orders,
        ROUND(SUM(t.final_amount_inr), 2) AS revenue_inr,
        ROUND(AVG(t.final_amount_inr), 2) AS avg_order_value_inr,
        ROUND(SUM(CASE WHEN c.is_prime_member = 1 THEN t.final_amount_inr ELSE 0 END), 2) AS prime_revenue_inr,
        ROUND(AVG(t.rating), 2) AS avg_rating
    FROM transactions t
    INNER JOIN products p ON t.product_id = p.product_id
    INNER JOIN customers c ON t.customer_id = c.customer_id
    INNER JOIN time_dimension td ON td.date_value = DATE(t.order_date)
    GROUP BY td.year, td.month, td.month_name, p.category
)
SELECT
    year,
    month,
    month_name,
    category,
    customers,
    orders,
    revenue_inr,
    avg_order_value_inr,
    prime_revenue_inr,
    avg_rating,
    -- Performance Metrics
    ROUND(revenue_inr * 100.0 / SUM(revenue_inr) OVER (PARTITION BY year, month), 2) AS revenue_share_pct,
    DENSE_RANK() OVER (PARTITION BY year, month ORDER BY revenue_inr DESC) AS category_rank,
    -- Growth Tracking
    LAG(revenue_inr, 1) OVER (PARTITION BY category ORDER BY year, month) AS prev_month_revenue_inr,
    ROUND((revenue_inr - LAG(revenue_inr, 1) OVER (PARTITION BY category ORDER BY year, month)) * 100.0 / 
        NULLIF(LAG(revenue_inr, 1) OVER (PARTITION BY category ORDER BY year, month), 0), 2) AS category_mom_growth_pct,
    LAG(revenue_inr, 12) OVER (PARTITION BY category ORDER BY year, month) AS prev_year_revenue_inr,
    ROUND((revenue_inr - LAG(revenue_inr, 12) OVER (PARTITION BY category ORDER BY year, month)) * 100.0 / 
        NULLIF(LAG(revenue_inr, 12) OVER (PARTITION BY category ORDER BY year, month), 0), 2) AS category_yoy_growth_pct,
    -- Prime Penetration in Category
    ROUND(prime_revenue_inr * 100.0 / NULLIF(revenue_inr, 0), 2) AS prime_penetration_pct
FROM category_growth
ORDER BY year DESC, month DESC, category_rank;

-- Q5.4: Churn and Retention Analysis (Predictive Health Indicator)
CREATE VIEW IF NOT EXISTS vw_q5_retention_analysis AS
WITH monthly_customer_status AS (
    SELECT
        td.year,
        td.month,
        td.month_name,
        c.customer_id,
        COUNT(DISTINCT t.transaction_id) AS orders_in_month,
        ROUND(SUM(t.final_amount_inr), 2) AS revenue_in_month
    FROM transactions t
    INNER JOIN customers c ON t.customer_id = c.customer_id
    INNER JOIN time_dimension td ON td.date_value = DATE(t.order_date)
    GROUP BY td.year, td.month, td.month_name, c.customer_id
)
SELECT
    mcs.year,
    mcs.month,
    mcs.month_name,
    COUNT(DISTINCT mcs.customer_id) AS active_customers,
    COUNT(DISTINCT CASE WHEN lag_mcs.customer_id IS NOT NULL THEN mcs.customer_id END) AS retained_customers,
    COUNT(DISTINCT CASE WHEN lag_mcs.customer_id IS NULL THEN mcs.customer_id END) AS new_customers,
    COUNT(DISTINCT CASE WHEN mcs2.customer_id IS NULL THEN lag_mcs.customer_id END) AS churned_customers,
    ROUND(COUNT(DISTINCT CASE WHEN lag_mcs.customer_id IS NOT NULL THEN mcs.customer_id END) * 100.0 / 
        NULLIF(COUNT(DISTINCT lag_mcs.customer_id), 0), 2) AS retention_rate_pct,
    ROUND(COUNT(DISTINCT CASE WHEN mcs2.customer_id IS NULL THEN lag_mcs.customer_id END) * 100.0 / 
        NULLIF(COUNT(DISTINCT lag_mcs.customer_id), 0), 2) AS churn_rate_pct
FROM monthly_customer_status mcs
LEFT JOIN monthly_customer_status lag_mcs ON mcs.customer_id = lag_mcs.customer_id 
    AND lag_mcs.year = CASE WHEN mcs.month = 1 THEN mcs.year - 1 ELSE mcs.year END
    AND lag_mcs.month = CASE WHEN mcs.month = 1 THEN 12 ELSE mcs.month - 1 END
LEFT JOIN monthly_customer_status mcs2 ON mcs.customer_id = mcs2.customer_id 
    AND mcs2.year = CASE WHEN mcs.month = 12 THEN mcs.year + 1 ELSE mcs.year END
    AND mcs2.month = CASE WHEN mcs.month = 12 THEN 1 ELSE mcs.month + 1 END
GROUP BY mcs.year, mcs.month, mcs.month_name
ORDER BY mcs.year DESC, mcs.month DESC;

-- ==================================================================================
-- MATERIALIZATION: Create corresponding tables for performance optimization
-- ==================================================================================

-- Create materialized table for Q1 Executive Summary (refresh nightly)
CREATE TABLE IF NOT EXISTS q1_executive_summary_materialized AS SELECT * FROM vw_q1_executive_summary WHERE 0;
CREATE TABLE IF NOT EXISTS q1_top_categories_materialized AS SELECT * FROM vw_q1_top_categories WHERE 0;
CREATE TABLE IF NOT EXISTS q1_growth_rates_materialized AS SELECT * FROM vw_q1_growth_rates WHERE 0;

-- Create materialized table for Q2 Real-time Monitor
CREATE TABLE IF NOT EXISTS q2_current_performance_materialized AS SELECT * FROM vw_q2_current_performance WHERE 0;
CREATE TABLE IF NOT EXISTS q2_run_rate_materialized AS SELECT * FROM vw_q2_run_rate_forecast WHERE 0;
CREATE TABLE IF NOT EXISTS q2_acquisition_metrics_materialized AS SELECT * FROM vw_q2_acquisition_metrics WHERE 0;

-- Create materialized table for Q3 Strategic Overview
CREATE TABLE IF NOT EXISTS q3_market_share_materialized AS SELECT * FROM vw_q3_market_share WHERE 0;
CREATE TABLE IF NOT EXISTS q3_geographic_expansion_materialized AS SELECT * FROM vw_q3_geographic_expansion WHERE 0;
CREATE TABLE IF NOT EXISTS q3_business_health_materialized AS SELECT * FROM vw_q3_business_health WHERE 0;

-- Create materialized table for Q4 Financial Performance
CREATE TABLE IF NOT EXISTS q4_financial_performance_materialized AS SELECT * FROM vw_q4_financial_performance WHERE 0;
CREATE TABLE IF NOT EXISTS q4_cost_structure_materialized AS SELECT * FROM vw_q4_cost_structure WHERE 0;
CREATE TABLE IF NOT EXISTS q4_financial_forecast_materialized AS SELECT * FROM vw_q4_financial_forecast WHERE 0;

-- Create materialized table for Q5 Growth Analytics
CREATE TABLE IF NOT EXISTS q5_customer_cohorts_materialized AS SELECT * FROM vw_q5_customer_cohorts WHERE 0;
CREATE TABLE IF NOT EXISTS q5_portfolio_expansion_materialized AS SELECT * FROM vw_q5_portfolio_expansion WHERE 0;
CREATE TABLE IF NOT EXISTS q5_strategic_initiatives_materialized AS SELECT * FROM vw_q5_strategic_initiatives WHERE 0;
CREATE TABLE IF NOT EXISTS q5_retention_analysis_materialized AS SELECT * FROM vw_q5_retention_analysis WHERE 0;

-- ==================================================================================
-- PERFORMANCE INDEXES
-- ==================================================================================
CREATE INDEX IF NOT EXISTS idx_q1_summary_year_month ON vw_q1_executive_summary(year, month);
CREATE INDEX IF NOT EXISTS idx_q2_performance_year_month ON vw_q2_current_performance(year, month);
CREATE INDEX IF NOT EXISTS idx_q3_market_share_year_month ON vw_q3_market_share(year, month);
CREATE INDEX IF NOT EXISTS idx_q4_financial_year_month ON vw_q4_financial_performance(year, month);
CREATE INDEX IF NOT EXISTS idx_q5_cohort_time ON vw_q5_customer_cohorts(cohort_year, cohort_month);

-- ==================================================================================
-- QUESTIONS 11-15: CUSTOMER ANALYTICS EXTENSIONS
-- ==================================================================================

-- Q11.1: RFM segment distribution with LTV
CREATE VIEW IF NOT EXISTS vw_q11_rfm_distribution AS
SELECT rfm_segment,
       COUNT(*) AS customer_count,
       ROUND(AVG(lifetime_value_predicted_inr),2) AS avg_ltv,
       ROUND(AVG(monetary_value_inr),2) AS avg_monetary
FROM customers
GROUP BY rfm_segment;

-- Q11.2: Behavioral segmentation summary
CREATE VIEW IF NOT EXISTS vw_q11_behavioral_segmentation AS
SELECT customer_segment,
       COUNT(*) AS customer_count,
       ROUND(AVG(total_spend_inr),2) AS avg_spend,
       ROUND(AVG(total_transactions),2) AS avg_transactions,
       ROUND(AVG(return_rate),2) AS avg_return_rate
FROM customers
GROUP BY customer_segment;

-- Q11.3: Simple LTV buckets
CREATE VIEW IF NOT EXISTS vw_q11_ltv_buckets AS
SELECT
   CASE
       WHEN lifetime_value_predicted_inr < 1000 THEN 'Low'
       WHEN lifetime_value_predicted_inr < 5000 THEN 'Medium'
       ELSE 'High'
   END AS ltv_bucket,
   COUNT(*) AS customers,
   ROUND(AVG(lifetime_value_predicted_inr),2) AS avg_ltv
FROM customers
GROUP BY ltv_bucket;

-- Q11.4: Sample marketing recommendations (high churn risk or at-risk RFM)
CREATE VIEW IF NOT EXISTS vw_q11_marketing_recs AS
SELECT customer_id, rfm_segment, customer_segment, lifetime_value_predicted_inr, churn_risk_score, email_opt_in, sms_opt_in
FROM customers
WHERE (churn_risk_score > 0.7 OR rfm_segment LIKE 'At Risk%')
LIMIT 100;

-- Q12.1: Acquisition channels (using payment_method as proxy)
CREATE VIEW IF NOT EXISTS vw_q12_acquisition_channels AS
SELECT t.payment_method AS channel,
       COUNT(DISTINCT t.customer_id) AS new_customers,
       SUM(t.final_amount_inr) AS revenue_inr
FROM transactions t
INNER JOIN (
    SELECT customer_id, MIN(order_date) AS first_order
    FROM transactions
    GROUP BY customer_id
) first_tx ON t.customer_id = first_tx.customer_id AND t.order_date = first_tx.first_order
GROUP BY t.payment_method;

-- Q12.2: Purchase patterns since first order
CREATE VIEW IF NOT EXISTS vw_q12_purchase_patterns AS
WITH first_tx AS (
   SELECT customer_id, MIN(order_date) AS first_order
   FROM transactions
   GROUP BY customer_id
),
customer_orders AS (
   SELECT t.customer_id,
          (strftime('%Y', t.order_date) - strftime('%Y', ft.first_order))*12 +
          (strftime('%m', t.order_date) - strftime('%m', ft.first_order)) + 1 AS months_since_first,
          COUNT(t.transaction_id) AS orders
   FROM transactions t
   JOIN first_tx ft ON t.customer_id = ft.customer_id
   GROUP BY t.customer_id, months_since_first
)
SELECT months_since_first, AVG(orders) AS avg_orders
FROM customer_orders
GROUP BY months_since_first
ORDER BY months_since_first;

-- Q12.3: Category transition flows
CREATE VIEW IF NOT EXISTS vw_q12_category_transitions AS
WITH ranked AS (
    SELECT customer_id, category,
           ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) AS seq
    FROM transactions
)
SELECT r1.category AS from_category, r2.category AS to_category, COUNT(DISTINCT r1.customer_id) AS customer_count
FROM ranked r1
JOIN ranked r2 ON r1.customer_id = r2.customer_id AND r2.seq = r1.seq + 1
WHERE r1.category != r2.category
GROUP BY r1.category, r2.category;

-- Q12.4: Customer evolution stage counts
CREATE VIEW IF NOT EXISTS vw_q12_customer_evolution AS
SELECT 
   CASE 
      WHEN total_transactions = 1 THEN 'First-Time'
      WHEN total_transactions BETWEEN 2 AND 5 THEN 'Repeat'
      ELSE 'Loyal'
   END AS lifecycle_stage,
   COUNT(*) AS customer_count
FROM (
   SELECT customer_id, COUNT(*) AS total_transactions
   FROM transactions
   GROUP BY customer_id
) sub
GROUP BY lifecycle_stage;

-- Q13.1: Prime vs non-prime revenue mix
CREATE VIEW IF NOT EXISTS vw_q13_prime_mix AS
SELECT c.is_prime_member,
       COUNT(DISTINCT t.transaction_id) AS orders,
       COUNT(DISTINCT t.customer_id) AS customers,
       SUM(t.final_amount_inr) AS revenue_inr,
       AVG(t.final_amount_inr) AS avg_order_value
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
GROUP BY c.is_prime_member;

-- Q13.2: Prime retention by month
CREATE VIEW IF NOT EXISTS vw_q13_prime_retention AS
WITH monthly_status AS (
   SELECT td.year, td.month, c.is_prime_member,
          c.customer_id,
          COUNT(DISTINCT t.transaction_id) AS orders
   FROM transactions t
   JOIN customers c ON t.customer_id = c.customer_id
   JOIN time_dimension td ON td.date_value = DATE(t.order_date)
   GROUP BY td.year, td.month, c.is_prime_member, c.customer_id
),
lagged AS (
   SELECT ms.*,
          LAG(ms.customer_id) OVER (PARTITION BY ms.is_prime_member, ms.customer_id ORDER BY ms.year, ms.month) AS prev_cust
   FROM monthly_status ms
)
SELECT year, month, is_prime_member,
       COUNT(DISTINCT customer_id) AS active_customers,
       COUNT(DISTINCT prev_cust) AS retained_customers,
       ROUND(COUNT(DISTINCT prev_cust)*100.0/NULLIF(COUNT(DISTINCT customer_id),0),2) AS retention_rate_pct
FROM lagged
GROUP BY year, month, is_prime_member;

-- Q13.3: Prime membership LTV comparison
CREATE VIEW IF NOT EXISTS vw_q13_member_value AS
SELECT is_prime_member,
       COUNT(*) AS customers,
       ROUND(AVG(lifetime_value_predicted_inr),2) AS avg_ltv
FROM customers
GROUP BY is_prime_member;

-- Q14.1: Churn prediction listing
CREATE VIEW IF NOT EXISTS vw_q14_churn_prediction AS
SELECT
   customer_id,
   churn_risk_score,
   last_purchase_date
FROM customers
WHERE churn_risk_score IS NOT NULL
ORDER BY churn_risk_score DESC
LIMIT 1000;

-- Q14.2: Retention strategy effectiveness by loyalty tier
CREATE VIEW IF NOT EXISTS vw_q14_strategy_effectiveness AS
SELECT loyalty_tier,
       COUNT(*) AS customers,
       AVG(churn_risk_score) AS avg_churn_risk,
       AVG(lifetime_value_predicted_inr) AS avg_ltv
FROM customers
GROUP BY loyalty_tier;

-- Q14.3: Customer lifecycle by account age
CREATE VIEW IF NOT EXISTS vw_q14_customer_lifecycle AS
SELECT
   CASE WHEN julianday('now') - julianday(account_created_date) < 365 THEN 'New'
        WHEN julianday('now') - julianday(account_created_date) BETWEEN 365 AND 1095 THEN 'Established'
        ELSE 'Veteran' END AS account_age_stage,
   COUNT(*) AS customers
FROM customers
GROUP BY account_age_stage;

-- Q15.1: Age-group × category preferences
CREATE VIEW IF NOT EXISTS vw_q15_age_category_preferences AS
SELECT c.age_group, t.category, COUNT(*) AS orders, SUM(t.final_amount_inr) AS revenue
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
GROUP BY c.age_group, t.category;

-- Q15.2: Spend patterns by age group
CREATE VIEW IF NOT EXISTS vw_q15_age_spending AS
SELECT age_group, AVG(total_spend_inr) AS avg_spend, AVG(total_transactions) AS avg_transactions
FROM customers
GROUP BY age_group;

-- Q15.3: Geographic behavior by age
CREATE VIEW IF NOT EXISTS vw_q15_geographic_age AS
SELECT c.state, c.age_group, COUNT(*) AS orders, SUM(t.final_amount_inr) AS revenue
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
GROUP BY c.state, c.age_group;

-- Q15.4: High-value demographic marketing opportunities
CREATE VIEW IF NOT EXISTS vw_q15_marketing_opportunities AS
SELECT c.age_group,
       c.state,
       SUM(t.final_amount_inr) AS revenue_inr,
       COUNT(DISTINCT t.customer_id) AS customers
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
GROUP BY c.age_group, c.state
ORDER BY revenue_inr DESC;


-- ==================================================================================
-- QUESTIONS 16-20: PRODUCT & INVENTORY ANALYTICS
-- ==================================================================================

-- Q16: Product Performance Dashboard
CREATE VIEW IF NOT EXISTS vw_q16_product_performance AS
SELECT
    product_id,
    product_name,
    category,
    brand,
    SUM(quantity) AS units_sold,
    SUM(final_amount_inr) AS revenue_inr,
    ROUND(AVG(product_rating),2) AS avg_rating,
    ROUND(SUM(CASE WHEN return_status = 'Returned' THEN 1 ELSE 0 END) * 100.0 /
          NULLIF(COUNT(*),0),2) AS return_rate_pct
FROM transactions
GROUP BY product_id, product_name, category, brand
ORDER BY revenue_inr DESC;

-- Q17: Brand Analytics Dashboard
CREATE VIEW IF NOT EXISTS vw_q17_brand_performance AS
SELECT
    brand,
    category,
    SUM(final_amount_inr) AS revenue_inr,
    SUM(quantity) AS units_sold,
    COUNT(DISTINCT product_id) AS num_products,
    ROUND(SUM(final_amount_inr) * 100.0 /
          NULLIF(SUM(SUM(final_amount_inr)) OVER (PARTITION BY category),0),2) AS market_share_pct
FROM transactions
GROUP BY brand, category;

-- Q18: Inventory Optimization Dashboard
CREATE VIEW IF NOT EXISTS vw_q18_inventory_demand AS
SELECT
    product_id,
    strftime('%Y', order_date) AS year,
    strftime('%m', order_date) AS month,
    SUM(quantity) AS units_sold,
    ROUND(AVG(final_amount_inr),2) AS avg_price
FROM transactions
GROUP BY product_id, year, month;

-- Q19: Product Rating & Review Dashboard
CREATE VIEW IF NOT EXISTS vw_q19_ratings AS
SELECT
    product_id,
    product_name,
    ROUND(AVG(product_rating),2) AS avg_product_rating,
    COUNT(*) AS review_count,
    ROUND(SUM(CASE WHEN customer_rating >= 4 THEN 1 ELSE 0 END) * 100.0 /
          NULLIF(COUNT(*),0),2) AS positive_pct
FROM transactions
WHERE customer_rating IS NOT NULL
GROUP BY product_id, product_name;

-- Q20: New Product Launch Dashboard
CREATE VIEW IF NOT EXISTS vw_q20_new_product_launch AS
WITH first_order AS (
    SELECT product_id, MIN(order_date) AS launch_date
    FROM transactions
    GROUP BY product_id
)
SELECT
    t.product_id,
    t.product_name,
    f.launch_date,
    SUM(t.final_amount_inr) AS revenue_since_launch,
    COUNT(*) AS orders_since_launch,
    ROUND(JULIANDAY('now') - JULIANDAY(f.launch_date),1) AS days_since_launch
FROM transactions t
JOIN first_order f ON t.product_id = f.product_id
GROUP BY t.product_id, t.product_name, f.launch_date;

-- OPTIONAL: Create materialized tables for high-volume new views if needed
