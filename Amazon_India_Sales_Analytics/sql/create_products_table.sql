-- ============================================================================
-- Amazon India Sales Analytics - Products Table (SQLite)
-- Purpose: Product catalog with category hierarchies
-- Database: SQLite 3
-- ============================================================================

CREATE TABLE products (
    -- Primary Key & Product Identifiers
    product_id TEXT PRIMARY KEY NOT NULL,
    product_name TEXT NOT NULL,
    
    -- Category Hierarchy
    category TEXT NOT NULL,
    subcategory TEXT NOT NULL,
    
    -- Brand & Manufacturer
    brand TEXT,
    manufacturer TEXT,
    
    -- Product Specifications
    product_weight_kg REAL,
    product_dimensions TEXT,
    sku TEXT UNIQUE,
    model_number TEXT,
    
    -- Pricing Information
    original_price_inr REAL NOT NULL,
    cost_price_inr REAL,
    min_selling_price_inr REAL,
    max_selling_price_inr REAL,
    
    -- Product Ratings & Reviews
    product_rating REAL,
    total_reviews INTEGER,
    total_rating_count INTEGER,
    
    -- Availability & Stock
    stock_quantity INTEGER DEFAULT 0,
    reorder_level INTEGER,
    warehouse_location TEXT,
    
    -- Product Status
    is_active INTEGER DEFAULT 1,
    is_bestseller INTEGER DEFAULT 0,
    is_prime_eligible INTEGER DEFAULT 0,
    is_hazardous INTEGER DEFAULT 0,
    
    -- Additional Attributes
    color TEXT,
    size TEXT,
    material TEXT,
    warranty_months INTEGER,
    return_days INTEGER,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_restocked_at TIMESTAMP,
    
    -- Constraints
    UNIQUE(sku),
    CHECK(original_price_inr >= 0),
    CHECK(stock_quantity >= 0),
    CHECK(product_rating >= 0 AND product_rating <= 5)
);

-- ============================================================================
-- TRIGGER - Auto-update the updated_at timestamp on row changes
-- ============================================================================
CREATE TRIGGER products_update_timestamp 
AFTER UPDATE ON products
BEGIN
  UPDATE products 
  SET updated_at = CURRENT_TIMESTAMP 
  WHERE product_id = NEW.product_id;
END;

-- ============================================================================
-- INDEXES - Optimized for Common Query Patterns
-- ============================================================================

-- 1. PRIMARY KEY & UNIQUE INDEXES
-- product_id PRIMARY KEY is already created above
CREATE INDEX IF NOT EXISTS idx_sku ON products(sku);

-- 2. CATEGORY HIERARCHY INDEXES (Essential for catalog browsing)
CREATE INDEX IF NOT EXISTS idx_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_subcategory ON products(subcategory);
CREATE INDEX IF NOT EXISTS idx_category_subcategory ON products(category, subcategory);

-- 3. BRAND & MANUFACTURER INDEXES
CREATE INDEX IF NOT EXISTS idx_brand ON products(brand);
CREATE INDEX IF NOT EXISTS idx_manufacturer ON products(manufacturer);

-- 4. PRICING INDEXES (For price analysis and optimization)
CREATE INDEX IF NOT EXISTS idx_original_price_inr ON products(original_price_inr);
CREATE INDEX IF NOT EXISTS idx_cost_price_inr ON products(cost_price_inr);
CREATE INDEX IF NOT EXISTS idx_min_selling_price ON products(min_selling_price_inr);
CREATE INDEX IF NOT EXISTS idx_max_selling_price ON products(max_selling_price_inr);

-- 5. RATINGS & REVIEWS INDEXES
CREATE INDEX IF NOT EXISTS idx_product_rating ON products(product_rating);
CREATE INDEX IF NOT EXISTS idx_total_reviews ON products(total_reviews);
CREATE INDEX IF NOT EXISTS idx_rating_desc ON products(product_rating DESC, total_reviews DESC);

-- 6. AVAILABILITY & STOCK INDEXES
CREATE INDEX IF NOT EXISTS idx_stock_quantity ON products(stock_quantity);
CREATE INDEX IF NOT EXISTS idx_reorder_level ON products(reorder_level);
CREATE INDEX IF NOT EXISTS idx_warehouse_location ON products(warehouse_location);
CREATE INDEX IF NOT EXISTS idx_low_stock ON products(stock_quantity, reorder_level);

-- 7. PRODUCT STATUS INDEXES
CREATE INDEX IF NOT EXISTS idx_is_active ON products(is_active);
CREATE INDEX IF NOT EXISTS idx_is_bestseller ON products(is_bestseller);
CREATE INDEX IF NOT EXISTS idx_is_prime_eligible ON products(is_prime_eligible);
CREATE INDEX IF NOT EXISTS idx_is_hazardous ON products(is_hazardous);

-- 8. PRODUCT ATTRIBUTES INDEXES
CREATE INDEX IF NOT EXISTS idx_color ON products(color);
CREATE INDEX IF NOT EXISTS idx_size ON products(size);
CREATE INDEX IF NOT EXISTS idx_material ON products(material);
CREATE INDEX IF NOT EXISTS idx_warranty ON products(warranty_months);

-- 9. COMPOSITE INDEXES - For common JOIN and filtering patterns
CREATE INDEX IF NOT EXISTS idx_category_active ON products(category, is_active);
CREATE INDEX IF NOT EXISTS idx_brand_category ON products(brand, category);
CREATE INDEX IF NOT EXISTS idx_price_rating ON products(original_price_inr, product_rating);
CREATE INDEX IF NOT EXISTS idx_active_bestseller ON products(is_active, is_bestseller);
CREATE INDEX IF NOT EXISTS idx_stock_category ON products(stock_quantity, category);
CREATE INDEX IF NOT EXISTS idx_prime_eligible_rating ON products(is_prime_eligible, product_rating);

-- 10. METADATA & TEMPORAL INDEXES
CREATE INDEX IF NOT EXISTS idx_created_at ON products(created_at);
CREATE INDEX IF NOT EXISTS idx_updated_at ON products(updated_at);
CREATE INDEX IF NOT EXISTS idx_last_restocked ON products(last_restocked_at);

-- 11. FULL-TEXT SEARCH INDEX (for product name searches)
-- Note: This uses SQLite FTS5. Run separately if FTS5 is not available:
-- CREATE VIRTUAL TABLE products_fts USING fts5(
--     product_name, 
--     category, 
--     brand, 
--     content=products, 
--     content_rowid=rowid
-- );

-- ============================================================================
-- TABLE STATISTICS & DOCUMENTATION
-- ============================================================================
/*
Product Table Design for Amazon India:

Columns Overview:
- Product Identifiers: 3 columns
- Category Hierarchy: 2 columns
- Brand/Manufacturer: 2 columns
- Specifications: 4 columns
- Pricing: 4 columns
- Ratings/Reviews: 3 columns
- Availability: 3 columns
- Status Flags: 4 columns
- Attributes: 5 columns
- Metadata: 3 columns
Total: 36 columns

Index Strategy:
- Time-based: Performance tracking, catalog updates
- Category: Browsing, filtering by product type
- Brand: Brand performance analysis
- Pricing: Price elasticity, margin analysis
- Ratings: Quality metrics, bestseller identification
- Stock: Inventory management, supply chain optimization
- Status: Active product filters, Prime eligibility
- Composite: Common dashboard queries

Expected Usage Patterns:
1. Browse products by category/subcategory: idx_category_subcategory
2. Find bestsellers with high ratings: idx_active_bestseller + idx_rating_desc
3. Stock analysis: idx_low_stock, idx_stock_category
4. Price analysis by category: idx_category + idx_original_price_inr
5. Prime eligibility filtering: idx_prime_eligible + idx_rating
6. Brand performance: idx_brand + idx_price_rating
*/

-- ============================================================================
-- SAMPLE VERIFICATION QUERIES
-- ============================================================================
/*
-- Check table structure
PRAGMA table_info(products);

-- Check indexes
PRAGMA index_list(products);

-- Sample data retrieval
SELECT * FROM products LIMIT 10;

-- Products by category
SELECT category, subcategory, COUNT(*) as product_count 
FROM products 
WHERE is_active = 1
GROUP BY category, subcategory
ORDER BY category;

-- Top rated products
SELECT 
    product_name, 
    brand, 
    category,
    product_rating, 
    total_reviews,
    original_price_inr
FROM products
WHERE is_active = 1
ORDER BY product_rating DESC, total_reviews DESC
LIMIT 20;

-- Stock summary
SELECT 
    category,
    COUNT(*) as total_products,
    SUM(stock_quantity) as total_stock,
    AVG(stock_quantity) as avg_stock,
    SUM(CASE WHEN stock_quantity < reorder_level THEN 1 ELSE 0 END) as low_stock_count
FROM products
WHERE is_active = 1
GROUP BY category;

-- Prime eligible products summary
SELECT 
    COUNT(*) as total_products,
    SUM(CASE WHEN is_prime_eligible = 1 THEN 1 ELSE 0 END) as prime_eligible,
    SUM(CASE WHEN is_bestseller = 1 THEN 1 ELSE 0 END) as bestsellers,
    AVG(original_price_inr) as avg_price,
    AVG(product_rating) as avg_rating
FROM products
WHERE is_active = 1;

-- Price range by category
SELECT 
    category,
    MIN(original_price_inr) as min_price,
    MAX(original_price_inr) as max_price,
    AVG(original_price_inr) as avg_price
FROM products
WHERE is_active = 1
GROUP BY category;
*/

-- ============================================================================
-- OPTIONAL: CREATE CATEGORY DIMENSION TABLE (for normalization)
-- ============================================================================
/*
CREATE TABLE product_categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT UNIQUE NOT NULL,
    description TEXT,
    parent_category_id INTEGER,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (parent_category_id) REFERENCES product_categories(category_id)
);

CREATE TABLE product_subcategories (
    subcategory_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subcategory_name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    description TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (category_id) REFERENCES product_categories(category_id),
    UNIQUE(subcategory_name, category_id)
);

-- Then modify products table to use foreign keys:
ALTER TABLE products ADD COLUMN category_id INTEGER;
ALTER TABLE products ADD COLUMN subcategory_id INTEGER;
ALTER TABLE products ADD FOREIGN KEY (category_id) REFERENCES product_categories(category_id);
ALTER TABLE products ADD FOREIGN KEY (subcategory_id) REFERENCES product_subcategories(subcategory_id);
*/

-- ============================================================================
-- OPTIONAL: CREATE BRAND DIMENSION TABLE (for normalization)
-- ============================================================================
/*
CREATE TABLE brands (
    brand_id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand_name TEXT UNIQUE NOT NULL,
    brand_logo_url TEXT,
    description TEXT,
    country_of_origin TEXT,
    is_official TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Then modify products table:
ALTER TABLE products ADD COLUMN brand_id INTEGER;
ALTER TABLE products ADD FOREIGN KEY (brand_id) REFERENCES brands(brand_id);
*/
