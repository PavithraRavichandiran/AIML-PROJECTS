-- ============================================================================
-- Amazon India Sales Analytics - Executive Dashboard Views
-- Purpose: Ready-to-use SQL views for dashboard visuals
-- ============================================================================

-- 1) Monthly executive KPI overview with MoM and YoY growth
CREATE VIEW IF NOT EXISTS vw_exec_monthly_overview AS
WITH base AS (
    SELECT
        year,
        month,
        month_name,
        quarter,
        orders,
        unique_customers,
        units_sold,
        revenue_inr,
        avg_order_value_inr,
        arpu_inr
    FROM vw_bi_monthly_kpi
)
SELECT
    year,
    month,
    month_name,
    quarter,
    orders,
    unique_customers,
    units_sold,
    revenue_inr,
    avg_order_value_inr,
    arpu_inr,
    LAG(revenue_inr) OVER (ORDER BY year, month) AS prev_month_revenue_inr,
    CASE
        WHEN LAG(revenue_inr) OVER (ORDER BY year, month) IS NULL
             OR LAG(revenue_inr) OVER (ORDER BY year, month) = 0 THEN NULL
        ELSE ROUND(
            (revenue_inr - LAG(revenue_inr) OVER (ORDER BY year, month))
            * 100.0 / LAG(revenue_inr) OVER (ORDER BY year, month), 2
        )
    END AS mom_revenue_growth_pct,
    LAG(revenue_inr, 12) OVER (ORDER BY year, month) AS last_year_same_month_revenue_inr,
    CASE
        WHEN LAG(revenue_inr, 12) OVER (ORDER BY year, month) IS NULL
             OR LAG(revenue_inr, 12) OVER (ORDER BY year, month) = 0 THEN NULL
        ELSE ROUND(
            (revenue_inr - LAG(revenue_inr, 12) OVER (ORDER BY year, month))
            * 100.0 / LAG(revenue_inr, 12) OVER (ORDER BY year, month), 2
        )
    END AS yoy_revenue_growth_pct
FROM base;

-- 2) Prime vs Non-Prime monthly revenue and order split
CREATE VIEW IF NOT EXISTS vw_exec_prime_split AS
SELECT
    d.year,
    d.month,
    d.month_name,
    CASE WHEN COALESCE(f.customer_prime_flag, 0) = 1 THEN 'Prime' ELSE 'Non-Prime' END AS member_type,
    COUNT(*) AS orders,
    ROUND(SUM(f.final_amount_inr), 2) AS revenue_inr,
    ROUND(AVG(f.final_amount_inr), 2) AS avg_order_value_inr,
    ROUND(
        SUM(f.final_amount_inr) * 100.0 /
        NULLIF(SUM(SUM(f.final_amount_inr)) OVER (PARTITION BY d.year, d.month), 0),
        2
    ) AS revenue_share_pct
FROM vw_fact_sales_enriched f
JOIN time_dimension d ON d.date_value = f.order_date
GROUP BY d.year, d.month, d.month_name, member_type;

-- 3) Payment method mix by month
CREATE VIEW IF NOT EXISTS vw_exec_payment_mix AS
SELECT
    d.year,
    d.month,
    d.month_name,
    f.payment_method,
    COUNT(*) AS orders,
    ROUND(SUM(f.final_amount_inr), 2) AS revenue_inr,
    ROUND(
        SUM(f.final_amount_inr) * 100.0 /
        NULLIF(SUM(SUM(f.final_amount_inr)) OVER (PARTITION BY d.year, d.month), 0),
        2
    ) AS payment_revenue_share_pct
FROM vw_fact_sales_enriched f
JOIN time_dimension d ON d.date_value = f.order_date
GROUP BY d.year, d.month, d.month_name, f.payment_method;

-- 4) Category share by month with ranking
CREATE VIEW IF NOT EXISTS vw_exec_category_share AS
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
    ROUND(
        revenue_inr * 100.0 /
        NULLIF(SUM(revenue_inr) OVER (PARTITION BY year, month), 0),
        2
    ) AS category_revenue_share_pct,
    DENSE_RANK() OVER (PARTITION BY year, month ORDER BY revenue_inr DESC) AS category_rank_in_month
FROM vw_bi_category_kpi;

-- 5) Festival vs Non-Festival monthly impact
CREATE VIEW IF NOT EXISTS vw_exec_festival_impact AS
SELECT
    d.year,
    d.month,
    d.month_name,
    CASE WHEN COALESCE(f.is_festival_sale, 0) = 1 THEN 'Festival Sale' ELSE 'Non-Festival' END AS sale_type,
    COUNT(*) AS orders,
    ROUND(SUM(f.final_amount_inr), 2) AS revenue_inr,
    ROUND(AVG(f.final_amount_inr), 2) AS avg_order_value_inr,
    ROUND(
        SUM(f.final_amount_inr) * 100.0 /
        NULLIF(SUM(SUM(f.final_amount_inr)) OVER (PARTITION BY d.year, d.month), 0),
        2
    ) AS revenue_share_pct
FROM vw_fact_sales_enriched f
JOIN time_dimension d ON d.date_value = f.order_date
GROUP BY d.year, d.month, d.month_name, sale_type;


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

-- ==================================================================================
-- OPERATIONS & LOGISTICS ANALYTICS (QUESTIONS 21-25)
-- ==================================================================================

-- Q21: Delivery Performance Dashboard
CREATE VIEW IF NOT EXISTS vw_q21_delivery_performance AS
SELECT
    strftime('%Y', order_date) AS year,
    strftime('%m', order_date) AS month,
    customer_state,
    delivery_type,
    COUNT(*) AS total_orders,
    ROUND(AVG(delivery_days), 1) AS avg_delivery_days,
    ROUND(SUM(CASE WHEN delivery_days <= 3 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS on_time_delivery_pct,
    ROUND(SUM(final_amount_inr), 2) AS total_revenue_inr,
    ROUND(AVG(final_amount_inr), 2) AS avg_order_value_inr
FROM transactions
WHERE delivery_days IS NOT NULL
GROUP BY year, month, customer_state, delivery_type;

-- Q22: Payment Analytics Dashboard
CREATE VIEW IF NOT EXISTS vw_q22_payment_analytics AS
WITH payment_summary AS (
    SELECT
        strftime('%Y', order_date) AS year,
        strftime('%m', order_date) AS month,
        payment_method,
        COUNT(*) AS transactions,
        SUM(final_amount_inr) AS revenue_inr,
        AVG(final_amount_inr) AS avg_transaction_value_inr,
        SUM(CASE WHEN return_status = 'Returned' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS return_rate_pct
    FROM transactions
    GROUP BY strftime('%Y', order_date), strftime('%m', order_date), payment_method
),
monthly_total AS (
    SELECT
        strftime('%Y', order_date) AS year,
        strftime('%m', order_date) AS month,
        SUM(final_amount_inr) AS total_revenue_inr
    FROM transactions
    GROUP BY strftime('%Y', order_date), strftime('%m', order_date)
)
SELECT
    ps.year,
    ps.month,
    ps.payment_method,
    ps.transactions,
    ROUND(ps.revenue_inr, 2) AS revenue_inr,
    ROUND(ps.revenue_inr * 100.0 / mt.total_revenue_inr, 2) AS payment_share_pct,
    ROUND(ps.avg_transaction_value_inr, 2) AS avg_transaction_value_inr,
    ROUND(ps.return_rate_pct, 2) AS return_rate_pct
FROM payment_summary ps
INNER JOIN monthly_total mt ON ps.year = mt.year AND ps.month = mt.month;

-- Q23: Return & Cancellation Dashboard
CREATE VIEW IF NOT EXISTS vw_q23_return_cancellation AS
SELECT
    category,
    subcategory,
    strftime('%Y', order_date) AS year,
    strftime('%m', order_date) AS month,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN return_status = 'Returned' THEN 1 ELSE 0 END) AS returned_orders,
    ROUND(SUM(CASE WHEN return_status = 'Returned' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS return_rate_pct,
    ROUND(SUM(CASE WHEN return_status = 'Returned' THEN final_amount_inr ELSE 0 END), 2) AS return_value_lost_inr,
    ROUND(AVG(CASE WHEN return_status = 'Returned' THEN customer_rating ELSE NULL END), 2) AS avg_return_customer_rating
FROM transactions
GROUP BY category, subcategory, year, month;

-- Q24: Customer Service Dashboard
CREATE VIEW IF NOT EXISTS vw_q24_customer_service AS
SELECT
    strftime('%Y', order_date) AS year,
    strftime('%m', order_date) AS month,
    customer_state,
    ROUND(AVG(customer_rating), 2) AS avg_customer_satisfaction,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN customer_rating < 3 THEN 1 ELSE 0 END) AS low_satisfaction_orders,
    ROUND(SUM(CASE WHEN customer_rating < 3 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS low_satisfaction_pct,
    ROUND(AVG(delivery_days), 1) AS avg_delivery_days,
    ROUND(SUM(CASE WHEN delivery_days > 7 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS delayed_delivery_pct
FROM transactions
WHERE customer_rating IS NOT NULL
GROUP BY year, month, customer_state;

-- Q25: Supply Chain Dashboard
CREATE VIEW IF NOT EXISTS vw_q25_supply_chain AS
SELECT
    brand,
    category,
    strftime('%Y', order_date) AS year,
    strftime('%m', order_date) AS month,
    COUNT(DISTINCT product_id) AS products_supplied,
    SUM(quantity) AS total_units,
    ROUND(AVG(delivery_days), 1) AS avg_delivery_days,
    ROUND(SUM(final_amount_inr), 2) AS total_revenue_inr,
    ROUND(AVG(product_weight_kg), 2) AS avg_product_weight_kg,
    ROUND(SUM(CASE WHEN delivery_days <= 3 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS on_time_delivery_pct
FROM transactions
WHERE brand IS NOT NULL
GROUP BY brand, category, year, month;
