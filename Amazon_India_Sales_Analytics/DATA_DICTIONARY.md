# Data Dictionary

Project: Amazon India Sales Analytics
Database: SQLite (`AmazonIndia.db`)
Data window: 2015-01-01 to 2025-12-31

## 1. Data Model Overview

Primary tables:
- `transactions`: fact table for orders and revenue
- `customers`: customer master, segmentation, and behavior
- `products`: product catalog and pricing attributes
- `time_dimension`: calendar, fiscal, seasonality, and festival flags

Primary analytical layer:
- Executive and thematic SQL views in `sql/dashboard_executive_questions_1_5.sql`, `sql/dashboard_executive_views.sql`, and `sql/dashboard_core_operations.sql`

Cleaned data outputs:
- Base cleaned datasets in `data/cleaned/amazon_india_all_years_cleaned.csv` and `data/cleaned/amazon_india_all_years_cleaned.parquet`
- Question-wise exports in `data/cleaned/Q01_*` through `data/cleaned/Q10_*`

## 2. Table: transactions

Source: `sql/create_transactions_table.sql`
Grain: one row per transaction/order line record
Primary key: `transaction_id`

Core columns:
- `transaction_id` (TEXT): Unique transaction identifier.
- `order_date` (DATE): Transaction date.
- `order_year` (INTEGER): Calendar year extracted from order date.
- `order_month` (INTEGER): Calendar month (1-12).
- `order_quarter` (INTEGER): Quarter (1-4).
- `customer_id` (TEXT): Foreign key reference to customer.
- `product_id` (TEXT): Foreign key reference to product.
- `category` (TEXT): Product category.
- `subcategory` (TEXT): Product subcategory.
- `brand` (TEXT): Product brand.
- `original_price_inr` (REAL): List price in INR.
- `discount_percent` (REAL): Discount percentage applied.
- `discounted_price_inr` (REAL): Post-discount unit price.
- `quantity` (INTEGER): Quantity purchased.
- `subtotal_inr` (REAL): Line subtotal before delivery charges.
- `delivery_charges` (REAL): Delivery charge amount.
- `final_amount_inr` (REAL): Final amount paid in INR.
- `payment_method` (TEXT): Payment mode (for example UPI, COD, card, EMI).
- `is_prime_member` (INTEGER): Prime flag (0/1).
- `is_prime_eligible` (INTEGER): Prime-eligible order/item flag (0/1).
- `is_festival_sale` (INTEGER): Festival flag (0/1).
- `festival_name` (TEXT): Festival/event name if applicable.
- `delivery_days` (INTEGER): Delivery duration in days.
- `delivery_type` (TEXT): Delivery mode/classification.
- `return_status` (TEXT): Return/cancellation state.
- `customer_city` (TEXT): Customer city at transaction time.
- `customer_state` (TEXT): Customer state at transaction time.
- `customer_tier` (TEXT): City tier classification.
- `customer_age_group` (TEXT): Customer age segment.
- `created_at` (TIMESTAMP): Record creation timestamp.
- `updated_at` (TIMESTAMP): Record update timestamp.

## 3. Table: customers

Source: `sql/create_customers_table.sql`
Grain: one row per unique customer
Primary key: `customer_id`

Core columns:
- `customer_id` (TEXT): Unique customer identifier.
- `customer_name` (TEXT): Customer full name.
- `email` (TEXT): Customer email (unique when available).
- `phone_number` (TEXT): Contact number.
- `date_of_birth` (DATE): Birth date.
- `gender` (TEXT): Gender label.
- `age_group` (TEXT): Age-band segment.
- `customer_age` (INTEGER): Numeric age.
- `city` (TEXT): Primary city.
- `state` (TEXT): Primary state.
- `postal_code` (TEXT): Postal code.
- `country` (TEXT): Country, default India.
- `latitude` (REAL): Latitude coordinate.
- `longitude` (REAL): Longitude coordinate.
- `customer_tier` (TEXT): Tier classification.
- `customer_spending_tier` (TEXT): Spending tier segment.
- `customer_segment` (TEXT): Business/customer segment label.
- `is_prime_member` (INTEGER): Prime status (0/1).
- `prime_member_since` (DATE): Prime membership start date.
- `loyalty_points` (INTEGER): Loyalty points balance.
- `loyalty_tier` (TEXT): Loyalty tier.
- `recency_days` (INTEGER): Days since last purchase.
- `frequency_transactions` (INTEGER): Number of transactions.
- `monetary_value_inr` (REAL): Total spend for RFM monetary dimension.
- `rfm_segment` (TEXT): RFM segment name.
- `avg_order_value_inr` (REAL): Average order value.
- `total_spend_inr` (REAL): Cumulative spend.
- `total_transactions` (INTEGER): Total transaction count.
- `preferred_payment_method` (TEXT): Preferred payment method.
- `return_rate` (REAL): Return ratio.
- `account_status` (TEXT): Account lifecycle status.
- `is_active` (INTEGER): Active status flag (0/1).
- `last_purchase_date` (DATE): Latest purchase date.
- `lifetime_value_predicted_inr` (REAL): Predicted LTV.
- `churn_risk_score` (REAL): Churn risk score.
- `engagement_score` (REAL): Engagement score.
- `created_at` (TIMESTAMP): Record creation timestamp.
- `updated_at` (TIMESTAMP): Record update timestamp.

## 4. Table: products

Source: `sql/create_products_table.sql`
Grain: one row per product SKU/entity
Primary key: `product_id`

Core columns:
- `product_id` (TEXT): Unique product identifier.
- `product_name` (TEXT): Product name.
- `category` (TEXT): Product category.
- `subcategory` (TEXT): Product subcategory.
- `brand` (TEXT): Brand name.
- `manufacturer` (TEXT): Manufacturer name.
- `sku` (TEXT): Stock keeping unit (unique).
- `model_number` (TEXT): Model number.
- `product_weight_kg` (REAL): Weight in kilograms.
- `product_dimensions` (TEXT): Dimension string.
- `original_price_inr` (REAL): Base list price in INR.
- `cost_price_inr` (REAL): Cost price estimate in INR.
- `min_selling_price_inr` (REAL): Lower allowed selling price.
- `max_selling_price_inr` (REAL): Upper allowed selling price.
- `product_rating` (REAL): Product rating.
- `total_reviews` (INTEGER): Review volume.
- `stock_quantity` (INTEGER): Current stock quantity.
- `reorder_level` (INTEGER): Reorder threshold.
- `warehouse_location` (TEXT): Warehouse location.
- `is_active` (INTEGER): Active catalog flag (0/1).
- `is_bestseller` (INTEGER): Bestseller flag (0/1).
- `is_prime_eligible` (INTEGER): Prime-eligible item flag (0/1).
- `warranty_months` (INTEGER): Warranty duration in months.
- `return_days` (INTEGER): Return window in days.
- `created_at` (TIMESTAMP): Record creation timestamp.
- `updated_at` (TIMESTAMP): Record update timestamp.

## 5. Table: time_dimension

Source: `sql/create_time_dimension_table.sql`
Grain: one row per date
Primary key: `date_id`
Natural key: `date_value`

Core columns:
- `date_id` (INTEGER): Surrogate key for date joins.
- `date_value` (DATE): Calendar date.
- `year` (INTEGER): Calendar year.
- `quarter` (INTEGER): Quarter (1-4).
- `month` (INTEGER): Month (1-12).
- `month_name` (TEXT): Full month label.
- `year_month` (TEXT): Year-month composite key.
- `ISO_week` (INTEGER): ISO week number.
- `day` (INTEGER): Day of month.
- `day_of_week` (INTEGER): Day index (0-6 based on implementation).
- `day_name` (TEXT): Day label.
- `is_weekday` (INTEGER): Weekday flag (0/1).
- `is_weekend` (INTEGER): Weekend flag (0/1).
- `is_business_day` (INTEGER): Business day flag (0/1).
- `is_holiday_india` (INTEGER): India holiday flag (0/1).
- `is_festival_season` (INTEGER): Festival season flag (0/1).
- `festival_season` (TEXT): Festival season name.
- `season_name` (TEXT): Seasonal bucket (for example summer/monsoon/winter).
- `is_diwali` (INTEGER): Diwali flag (0/1).
- `is_holi` (INTEGER): Holi flag (0/1).
- `is_christmas` (INTEGER): Christmas flag (0/1).
- `is_new_year` (INTEGER): New Year flag (0/1).
- `is_independence_day` (INTEGER): Independence Day flag (0/1).
- `is_republic_day` (INTEGER): Republic Day flag (0/1).
- `is_dussehra` (INTEGER): Dussehra flag (0/1).
- `is_navratri` (INTEGER): Navratri flag (0/1).
- `holiday_name` (TEXT): Holiday/festival label.
- `days_since_first_date` (INTEGER): Relative day index from start date.
- `days_until_year_end` (INTEGER): Remaining days in year.

## 6. Relationships (Logical)

- `transactions.customer_id` joins to `customers.customer_id`
- `transactions.product_id` joins to `products.product_id`
- `transactions.order_date` joins to `time_dimension.date_value`

Note:
- The analytical views are pre-aggregated for BI and many dashboards can run without explicit relationship modeling in Power BI/Tableau.

## 7. Derived Analytical Views

Main view sets:
- Q1 views: `vw_q1_executive_summary`, `vw_q1_top_categories`, `vw_q1_growth_rates`
- Q2 views: `vw_q2_current_performance`, `vw_q2_run_rate_forecast`, `vw_q2_acquisition_metrics`
- Q3 views: `vw_q3_market_share`, `vw_q3_geographic_expansion`, `vw_q3_business_health`
- Q4 views: `vw_q4_financial_performance`, `vw_q4_cost_structure`, `vw_q4_financial_forecast`
- Q5 views: `vw_q5_customer_cohorts`, `vw_q5_portfolio_expansion`, `vw_q5_strategic_initiatives`, `vw_q5_retention_analysis`

For detailed field-level BI mapping, refer to:
- `DASHBOARD_POWERBI_TABLEAU_MAPPING.md`

## 8. Cleaned Dataset File Dictionary

Primary cleaned files:
- `data/cleaned/amazon_india_all_years_cleaned.csv`: Full cleaned transaction dataset.
- `data/cleaned/amazon_india_all_years_cleaned.parquet`: Columnar optimized version of cleaned data.

Question summary files (examples):
- `data/cleaned/Q01_Revenue_Analysis_Summary.csv`
- `data/cleaned/Q02_Seasonal_Analysis_Summary.csv`
- `data/cleaned/Q03_RFM_Analysis_Summary.csv`
- `data/cleaned/Q04_Executive_Summary.csv`
- `data/cleaned/Q05_Executive_Summary.csv`
- `data/cleaned/Q06_Executive_Summary.csv`
- `data/cleaned/Q08_Executive_Summary.csv`
- `data/cleaned/Q09_Executive_Summary.csv`

## 9. Data Conventions

- Currency fields ending with `_inr` are stored in Indian Rupees.
- Percentage metrics generally end with `_pct` and are represented as percentages.
- Binary flags are stored as integers (`0` or `1`).
- Date fields use ISO-like `YYYY-MM-DD` format.
- Timestamp fields are maintained for lineage and update auditing.
