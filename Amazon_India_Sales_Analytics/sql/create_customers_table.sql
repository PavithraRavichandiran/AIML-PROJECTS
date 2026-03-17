-- ============================================================================
-- Amazon India Sales Analytics - Customers Table (SQLite)
-- Purpose: Customer master data with RFM, behavioral, and demographic segmentation
-- Database: SQLite 3
-- ============================================================================

CREATE TABLE customers (
    -- Primary Key & Identifiers
    customer_id TEXT PRIMARY KEY NOT NULL,
    
    -- Personal Information
    customer_name TEXT NOT NULL,
    email TEXT UNIQUE,
    phone_number TEXT,
    date_of_birth DATE,
    gender TEXT,
    
    -- Demographic Segmentation
    age_group TEXT,
    customer_age INTEGER,
    
    -- Geographic Information
    primary_address TEXT,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    postal_code TEXT,
    country TEXT DEFAULT 'India',
    latitude REAL,
    longitude REAL,
    
    -- Secondary Address (for deliveries)
    secondary_address TEXT,
    secondary_city TEXT,
    secondary_state TEXT,
    
    -- Customer Classification
    customer_tier TEXT,
    customer_spending_tier TEXT,
    customer_segment TEXT,
    
    -- Membership & Loyalty
    is_prime_member INTEGER DEFAULT 0,
    prime_member_since DATE,
    prime_renewal_date DATE,
    loyalty_points INTEGER DEFAULT 0,
    loyalty_tier TEXT,
    
    -- RFM Segmentation
    recency_days INTEGER,
    frequency_transactions INTEGER,
    monetary_value_inr REAL,
    rfm_segment TEXT,
    
    -- Behavioral Metrics
    avg_order_value_inr REAL,
    total_spend_inr REAL,
    total_transactions INTEGER DEFAULT 0,
    total_reviews_posted INTEGER DEFAULT 0,
    avg_rating_given REAL,
    
    -- Purchase Behavior
    preferred_payment_method TEXT,
    preferred_delivery_type TEXT,
    avg_delivery_days INTEGER,
    return_rate REAL,
    
    -- Communication Preferences
    email_opt_in INTEGER DEFAULT 1,
    sms_opt_in INTEGER DEFAULT 1,
    push_notification_opt_in INTEGER DEFAULT 1,
    promotional_offers_opt_in INTEGER DEFAULT 1,
    preferred_communication_channel TEXT,
    
    -- Account Status
    account_status TEXT DEFAULT 'Active',
    account_created_date DATE NOT NULL,
    last_login_date DATE,
    last_purchase_date DATE,
    is_active INTEGER DEFAULT 1,
    
    -- Metadata & Tracking
    customer_rating REAL,
    total_rating_count INTEGER DEFAULT 0,
    lifetime_value_predicted_inr REAL,
    churn_risk_score REAL,
    engagement_score REAL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(email),
    CHECK(customer_rating >= 0 AND customer_rating <= 5),
    CHECK(total_spend_inr >= 0),
    CHECK(loyalty_points >= 0)
);

-- ============================================================================
-- TRIGGER - Auto-update the updated_at timestamp on row changes
-- ============================================================================
CREATE TRIGGER customers_update_timestamp 
AFTER UPDATE ON customers
BEGIN
  UPDATE customers 
  SET updated_at = CURRENT_TIMESTAMP 
  WHERE customer_id = NEW.customer_id;
END;

-- ============================================================================
-- INDEXES - Optimized for Customer Analysis & Segmentation
-- ============================================================================

-- 1. PRIMARY KEY & UNIQUE INDEXES
-- customer_id PRIMARY KEY is already created above
CREATE INDEX IF NOT EXISTS idx_email ON customers(email);

-- 2. GEOGRAPHIC INDEXES (For regional analysis)
CREATE INDEX IF NOT EXISTS idx_city ON customers(city);
CREATE INDEX IF NOT EXISTS idx_state ON customers(state);
CREATE INDEX IF NOT EXISTS idx_postal_code ON customers(postal_code);
CREATE INDEX IF NOT EXISTS idx_city_state ON customers(city, state);

-- 3. DEMOGRAPHIC SEGMENTATION INDEXES
CREATE INDEX IF NOT EXISTS idx_age_group ON customers(age_group);
CREATE INDEX IF NOT EXISTS idx_customer_age ON customers(customer_age);
CREATE INDEX IF NOT EXISTS idx_gender ON customers(gender);

-- 4. CUSTOMER CLASSIFICATION INDEXES
CREATE INDEX IF NOT EXISTS idx_customer_tier ON customers(customer_tier);
CREATE INDEX IF NOT EXISTS idx_customer_spending_tier ON customers(customer_spending_tier);
CREATE INDEX IF NOT EXISTS idx_customer_segment ON customers(customer_segment);
CREATE INDEX IF NOT EXISTS idx_tier_spending ON customers(customer_tier, customer_spending_tier);

-- 5. MEMBERSHIP & LOYALTY INDEXES
CREATE INDEX IF NOT EXISTS idx_is_prime_member ON customers(is_prime_member);
CREATE INDEX IF NOT EXISTS idx_prime_member_since ON customers(prime_member_since);
CREATE INDEX IF NOT EXISTS idx_loyalty_tier ON customers(loyalty_tier);
CREATE INDEX IF NOT EXISTS idx_loyalty_points ON customers(loyalty_points);

-- 6. RFM SEGMENTATION INDEXES
CREATE INDEX IF NOT EXISTS idx_rfm_segment ON customers(rfm_segment);
CREATE INDEX IF NOT EXISTS idx_recency_days ON customers(recency_days);
CREATE INDEX IF NOT EXISTS idx_frequency_transactions ON customers(frequency_transactions);
CREATE INDEX IF NOT EXISTS idx_monetary_value ON customers(monetary_value_inr);

-- 7. BEHAVIORAL METRICS INDEXES
CREATE INDEX IF NOT EXISTS idx_avg_order_value ON customers(avg_order_value_inr);
CREATE INDEX IF NOT EXISTS idx_total_spend ON customers(total_spend_inr);
CREATE INDEX IF NOT EXISTS idx_total_transactions ON customers(total_transactions);
CREATE INDEX IF NOT EXISTS idx_return_rate ON customers(return_rate);
CREATE INDEX IF NOT EXISTS idx_avg_rating_given ON customers(avg_rating_given);

-- 8. PREFERENCE INDEXES
CREATE INDEX IF NOT EXISTS idx_preferred_payment ON customers(preferred_payment_method);
CREATE INDEX IF NOT EXISTS idx_preferred_delivery ON customers(preferred_delivery_type);
CREATE INDEX IF NOT EXISTS idx_communication_channel ON customers(preferred_communication_channel);

-- 9. ACCOUNT STATUS INDEXES
CREATE INDEX IF NOT EXISTS idx_account_status ON customers(account_status);
CREATE INDEX IF NOT EXISTS idx_is_active ON customers(is_active);
CREATE INDEX IF NOT EXISTS idx_account_created_date ON customers(account_created_date);
CREATE INDEX IF NOT EXISTS idx_last_login_date ON customers(last_login_date);
CREATE INDEX IF NOT EXISTS idx_last_purchase_date ON customers(last_purchase_date);

-- 10. CAMPAIGN & ENGAGEMENT INDEXES
CREATE INDEX IF NOT EXISTS idx_email_opt_in ON customers(email_opt_in);
CREATE INDEX IF NOT EXISTS idx_sms_opt_in ON customers(sms_opt_in);
CREATE INDEX IF NOT EXISTS idx_promotional_opt_in ON customers(promotional_offers_opt_in);
CREATE INDEX IF NOT EXISTS idx_engagement_score ON customers(engagement_score);
CREATE INDEX IF NOT EXISTS idx_churn_risk_score ON customers(churn_risk_score);

-- 11. LIFETIME VALUE INDEXES
CREATE INDEX IF NOT EXISTS idx_lifetime_value ON customers(lifetime_value_predicted_inr);
CREATE INDEX IF NOT EXISTS idx_customer_rating ON customers(customer_rating);

-- 12. COMPOSITE INDEXES - For common segmentation queries
CREATE INDEX IF NOT EXISTS idx_tier_engagement ON customers(customer_tier, engagement_score);
CREATE INDEX IF NOT EXISTS idx_segment_churn ON customers(customer_segment, churn_risk_score);
CREATE INDEX IF NOT EXISTS idx_prime_ltv ON customers(is_prime_member, lifetime_value_predicted_inr);
CREATE INDEX IF NOT EXISTS idx_active_ltv ON customers(is_active, lifetime_value_predicted_inr);
CREATE INDEX IF NOT EXISTS idx_state_segment ON customers(state, customer_segment);
CREATE INDEX IF NOT EXISTS idx_rfm_ltv ON customers(rfm_segment, lifetime_value_predicted_inr);
CREATE INDEX IF NOT EXISTS idx_age_spending ON customers(age_group, total_spend_inr);

-- 13. TEMPORAL INDEXES
CREATE INDEX IF NOT EXISTS idx_created_at ON customers(created_at);
CREATE INDEX IF NOT EXISTS idx_updated_at ON customers(updated_at);

-- ============================================================================
-- TABLE STATISTICS & DOCUMENTATION
-- ============================================================================
/*
Customer Table Design for Amazon India:

Columns Overview:
- Identifiers: 1 column
- Personal Info: 5 columns
- Demographics: 2 columns
- Geographic: 8 columns
- Classification: 3 columns
- Membership: 4 columns
- RFM Segmentation: 4 columns
- Behavioral Metrics: 5 columns
- Purchase Behavior: 4 columns
- Communication: 5 columns
- Account Status: 5 columns
- Metadata: 7 columns
Total: 63 columns

Segmentation Dimensions:
1. RFM: Recency, Frequency, Monetary
2. Demographic: Age, Gender
3. Geographic: City, State
4. Behavioral: Spending tier, Purchase frequency
5. Membership: Prime, Loyalty
6. Engagement: Email opt-in, CMC preferences
7. Risk: Churn score, LTV prediction

Index Strategy:
- Demographic: Age, gender analysis
- Geographic: Regional performance
- Segmentation: RFM, tier, segment filters
- Membership: Prime impact analysis
- Behavior: Spending patterns, engagement
- Temporal: Customer lifecycle tracking
- Composite: Multi-dimensional analysis

Expected Usage Patterns:
1. Customer segmentation by RFM: idx_rfm_segment
2. Regional analysis: idx_city_state
3. Prime member analysis: idx_is_prime_member + lifetime_value
4. Churn risk identification: idx_churn_risk_score
5. Campaign targeting: Email/SMS opt-in filters
6. LTV prediction: idx_lifetime_value
7. Engagement scoring: idx_engagement_score
8. Demographic trends: idx_age_group + idx_customer_spending_tier
*/

-- ============================================================================
-- SAMPLE VERIFICATION QUERIES
-- ============================================================================
/*
-- Check table structure
PRAGMA table_info(customers);

-- Check indexes
PRAGMA index_list(customers);

-- Sample data retrieval
SELECT * FROM customers LIMIT 10;

-- Customer segmentation summary
SELECT 
    rfm_segment,
    customer_segment,
    COUNT(*) as customer_count,
    AVG(total_spend_inr) as avg_spend,
    AVG(lifetime_value_predicted_inr) as avg_ltv,
    AVG(engagement_score) as avg_engagement
FROM customers
WHERE is_active = 1
GROUP BY rfm_segment, customer_segment;

-- Geographic distribution
SELECT 
    state,
    city,
    COUNT(*) as customer_count,
    AVG(total_spend_inr) as avg_spend,
    SUM(total_spend_inr) as total_spend,
    AVG(churn_risk_score) as avg_churn_risk
FROM customers
WHERE is_active = 1
GROUP BY state, city
ORDER BY total_spend DESC;

-- Prime membership analysis
SELECT 
    CASE WHEN is_prime_member = 1 THEN 'Prime' ELSE 'Non-Prime' END as membership,
    COUNT(*) as customer_count,
    AVG(total_spend_inr) as avg_spend,
    AVG(total_transactions) as avg_transactions,
    AVG(lifetime_value_predicted_inr) as avg_ltv,
    AVG(engagement_score) as avg_engagement
FROM customers
WHERE is_active = 1
GROUP BY is_prime_member;

-- Customer tier analysis
SELECT 
    customer_tier,
    customer_spending_tier,
    COUNT(*) as customer_count,
    MIN(total_spend_inr) as min_spend,
    AVG(total_spend_inr) as avg_spend,
    MAX(total_spend_inr) as max_spend,
    AVG(lifetime_value_predicted_inr) as avg_ltv
FROM customers
WHERE is_active = 1
GROUP BY customer_tier, customer_spending_tier;

-- Churn risk identification
SELECT 
    customer_id,
    customer_name,
    customer_tier,
    total_spend_inr,
    last_purchase_date,
    churn_risk_score,
    engagement_score
FROM customers
WHERE is_active = 1 
  AND churn_risk_score > 0.7
ORDER BY churn_risk_score DESC
LIMIT 20;

-- High-value customers (LTV)
SELECT 
    customer_id,
    customer_name,
    city,
    state,
    total_spend_inr,
    lifetime_value_predicted_inr,
    is_prime_member,
    rfm_segment,
    engagement_score
FROM customers
WHERE is_active = 1
  AND lifetime_value_predicted_inr > 50000
ORDER BY lifetime_value_predicted_inr DESC
LIMIT 20;

-- Campaign targeting (actively engaged, email opt-in)
SELECT 
    COUNT(*) as targeted_customers,
    AVG(total_spend_inr) as avg_spend,
    SUM(total_spend_inr) as total_spend,
    AVG(engagement_score) as avg_engagement,
    CASE WHEN is_prime_member = 1 THEN 'Prime' ELSE 'Non-Prime' END as membership
FROM customers
WHERE is_active = 1 
  AND email_opt_in = 1 
  AND engagement_score > 0.5
GROUP BY is_prime_member;

-- Customer lifecycle metrics
SELECT 
    CAST((julianday('now') - julianday(account_created_date)) / 365.25 AS INTEGER) as years_as_customer,
    COUNT(*) as customer_count,
    AVG(total_spend_inr) as avg_spend,
    AVG(total_transactions) as avg_transactions,
    AVG(lifetime_value_predicted_inr) as avg_ltv
FROM customers
WHERE is_active = 1
GROUP BY years_as_customer
ORDER BY years_as_customer;
*/

-- ============================================================================
-- OPTIONAL: CREATE RELATED DIMENSION TABLES
-- ============================================================================
/*
-- Customer Segments Dimension
CREATE TABLE customer_segments (
    segment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    segment_name TEXT UNIQUE NOT NULL,
    description TEXT,
    target_marketing_spend REAL,
    priority_level INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customer Tiers Dimension
CREATE TABLE customer_tiers (
    tier_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tier_name TEXT UNIQUE NOT NULL,
    min_spend REAL,
    max_spend REAL,
    benefits_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Modify customers table to use foreign keys:
ALTER TABLE customers ADD COLUMN segment_id INTEGER;
ALTER TABLE customers ADD FOREIGN KEY (segment_id) REFERENCES customer_segments(segment_id);

-- Customer Activity Log (for tracking interactions)
CREATE TABLE customer_activity_log (
    activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT NOT NULL,
    activity_type TEXT NOT NULL,
    activity_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activity_details TEXT,
    channel TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE INDEX IF NOT EXISTS idx_activity_customer ON customer_activity_log(customer_id);
CREATE INDEX IF NOT EXISTS idx_activity_date ON customer_activity_log(activity_date);
CREATE INDEX IF NOT EXISTS idx_activity_type ON customer_activity_log(activity_type);
*/
