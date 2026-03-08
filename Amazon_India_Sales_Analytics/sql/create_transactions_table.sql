-- ============================================================================
-- Amazon India Sales Analytics - Transactions Table (SQLite)
-- Purpose: Main transaction data with decade of sales (2015-2025)
-- Total Records: 1,127,609+ transactions
-- Database: SQLite 3
-- ============================================================================

CREATE TABLE transactions (
    -- Primary Key & Identifiers
    transaction_id TEXT PRIMARY KEY NOT NULL,
    order_date DATE NOT NULL,
    order_year INTEGER NOT NULL,
    order_month INTEGER NOT NULL,
    order_quarter INTEGER NOT NULL,
    
    -- Customer Information
    customer_id TEXT NOT NULL,
    customer_city TEXT,
    customer_state TEXT,
    customer_tier TEXT,
    customer_spending_tier TEXT,
    customer_age_group TEXT,
    customer_rating REAL,
    
    -- Product Information
    product_id TEXT NOT NULL,
    product_name TEXT,
    category TEXT,
    subcategory TEXT,
    brand TEXT,
    product_weight_kg REAL,
    product_rating REAL,
    
    -- Pricing Information
    original_price_inr REAL NOT NULL,
    discount_percent REAL,
    discounted_price_inr REAL,
    quantity INTEGER NOT NULL,
    subtotal_inr REAL,
    delivery_charges REAL,
    final_amount_inr REAL NOT NULL,
    
    -- Delivery & Fulfillment
    delivery_days INTEGER,
    delivery_type TEXT,
    return_status TEXT,
    
    -- Membership & Promotions
    is_prime_member INTEGER,
    is_prime_eligible INTEGER,
    is_festival_sale INTEGER,
    festival_name TEXT,
    
    -- Payment Method
    payment_method TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TRIGGER - Auto-update the updated_at timestamp on row changes
-- ============================================================================
CREATE TRIGGER transactions_update_timestamp 
AFTER UPDATE ON transactions
BEGIN
  UPDATE transactions 
  SET updated_at = CURRENT_TIMESTAMP 
  WHERE transaction_id = NEW.transaction_id;
END;

-- ============================================================================
-- INDEXES - Optimized for Common Query Patterns
-- ============================================================================

-- 1. TIME-BASED INDEXES (Essential for trend analysis)
CREATE INDEX IF NOT EXISTS idx_order_date ON transactions(order_date);
CREATE INDEX IF NOT EXISTS idx_order_year ON transactions(order_year);
CREATE INDEX IF NOT EXISTS idx_order_year_month ON transactions(order_year, order_month);
CREATE INDEX IF NOT EXISTS idx_order_quarter ON transactions(order_quarter);

-- 2. CUSTOMER ANALYSIS INDEXES
CREATE INDEX IF NOT EXISTS idx_customer_id ON transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_customer_tier ON transactions(customer_tier);
CREATE INDEX IF NOT EXISTS idx_customer_spending_tier ON transactions(customer_spending_tier);
CREATE INDEX IF NOT EXISTS idx_customer_age_group ON transactions(customer_age_group);
CREATE INDEX IF NOT EXISTS idx_customer_state ON transactions(customer_state);
CREATE INDEX IF NOT EXISTS idx_customer_city ON transactions(customer_city);

-- 3. PRODUCT ANALYSIS INDEXES
CREATE INDEX IF NOT EXISTS idx_product_id ON transactions(product_id);
CREATE INDEX IF NOT EXISTS idx_category ON transactions(category);
CREATE INDEX IF NOT EXISTS idx_subcategory ON transactions(subcategory);
CREATE INDEX IF NOT EXISTS idx_brand ON transactions(brand);
CREATE INDEX IF NOT EXISTS idx_category_subcategory ON transactions(category, subcategory);

-- 4. FINANCIAL/REVENUE INDEXES
CREATE INDEX IF NOT EXISTS idx_final_amount_inr ON transactions(final_amount_inr);
CREATE INDEX IF NOT EXISTS idx_original_price_inr ON transactions(original_price_inr);
CREATE INDEX IF NOT EXISTS idx_discount_percent ON transactions(discount_percent);

-- 5. MEMBERSHIP & PROMOTIONS INDEXES
CREATE INDEX IF NOT EXISTS idx_is_prime_member ON transactions(is_prime_member);
CREATE INDEX IF NOT EXISTS idx_is_festival_sale ON transactions(is_festival_sale);
CREATE INDEX IF NOT EXISTS idx_festival_name ON transactions(festival_name);

-- 6. PAYMENT METHOD INDEXES
CREATE INDEX IF NOT EXISTS idx_payment_method ON transactions(payment_method);

-- 7. DELIVERY & FULFILLMENT INDEXES
CREATE INDEX IF NOT EXISTS idx_delivery_type ON transactions(delivery_type);
CREATE INDEX IF NOT EXISTS idx_return_status ON transactions(return_status);

-- 8. COMPOSITE INDEXES - For common JOIN patterns and aggregations
CREATE INDEX IF NOT EXISTS idx_year_category ON transactions(order_year, category);
CREATE INDEX IF NOT EXISTS idx_year_customer ON transactions(order_year, customer_id);
CREATE INDEX IF NOT EXISTS idx_customer_category ON transactions(customer_id, category);
CREATE INDEX IF NOT EXISTS idx_date_amount ON transactions(order_date, final_amount_inr);
CREATE INDEX IF NOT EXISTS idx_category_amount ON transactions(category, final_amount_inr);
CREATE INDEX IF NOT EXISTS idx_customer_tier_spending ON transactions(customer_tier, final_amount_inr);
CREATE INDEX IF NOT EXISTS idx_prime_member_amount ON transactions(is_prime_member, final_amount_inr);
CREATE INDEX IF NOT EXISTS idx_festival_category ON transactions(is_festival_sale, category);

-- 9. PERFORMANCE ANALYSIS INDEXES
CREATE INDEX IF NOT EXISTS idx_quantity ON transactions(quantity);
CREATE INDEX IF NOT EXISTS idx_delivery_days ON transactions(delivery_days);

-- ============================================================================
-- TABLE STATISTICS
-- ============================================================================
/*
Expected Data Characteristics:
- Total Records: 1,127,609+ transactions
- Date Range: 2015 to 2025 (10+ years)
- Categories: Multiple product categories
- States: Across India
- Prime Members: Yes/No
- Payment Methods: Multiple (Card, UPI, EMI, COD, etc.)

Sample Query Performance with Indexes:
1. Revenue by Year: Uses idx_order_year
2. Customer Segmentation: Uses idx_customer_id, idx_customer_tier
3. Category Performance: Uses idx_category
4. Festival Analysis: Uses idx_is_festival_sale, idx_festival_name
5. Geographic Analysis: Uses idx_customer_state, idx_customer_city
6. Prime Member Impact: Uses idx_is_prime_member
7. Price Elasticity: Uses idx_original_price_inr, idx_final_amount_inr
*/

-- ============================================================================
-- OPTIONAL: ADD FOREIGN KEY CONSTRAINTS (if you have dimension tables)
-- ============================================================================
/*
-- NOTE: Enable foreign keys in SQLite (required!)
PRAGMA foreign_keys = ON;

-- Add foreign key constraints:

ALTER TABLE transactions 
  ADD CONSTRAINT fk_customer FOREIGN KEY (customer_id) 
  REFERENCES customer_dim(customer_id) 
  ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE transactions 
  ADD CONSTRAINT fk_product FOREIGN KEY (product_id) 
  REFERENCES product_dim(product_id) 
  ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE transactions 
  ADD CONSTRAINT fk_category FOREIGN KEY (category) 
  REFERENCES category_dim(category_name) 
  ON DELETE RESTRICT ON UPDATE CASCADE;
*/

-- ============================================================================
-- SAMPLE VERIFICATION QUERIES
-- ============================================================================
/*
-- Check table structure
PRAGMA table_info(transactions);

-- Check indexes
PRAGMA index_list(transactions);

-- Sample data retrieval
SELECT * FROM transactions LIMIT 10;

-- Row count
SELECT COUNT(*) as total_transactions FROM transactions;

-- Date range
SELECT MIN(order_date) as earliest_date, MAX(order_date) as latest_date FROM transactions;

-- Revenue summary
SELECT 
    COUNT(*) as transactions,
    SUM(final_amount_inr) as total_revenue,
    AVG(final_amount_inr) as avg_transaction_value
FROM transactions;
*/
