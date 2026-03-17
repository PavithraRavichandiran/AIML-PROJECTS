"""
Amazon India Sales Analytics - Populate Products Table
Purpose: Extract and populate products table from transactions data
"""

import pandas as pd
import sqlite3
from datetime import datetime
import logging
from pathlib import Path
import sys

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / 'AmazonIndia.db'
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / f'populate_products_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# PRODUCTS POPULATION
# ============================================================================

def populate_products():
    """Extract and populate products table from transactions"""
    logger.info(f"\n{'='*80}")
    logger.info("POPULATING PRODUCTS TABLE")
    logger.info(f"{'='*80}\n")
    
    try:
        # Connect to database
        conn = sqlite3.connect(str(DB_PATH), timeout=300)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=20000")
        conn.execute("PRAGMA temp_store=MEMORY")
        logger.info(f"[OK] Connected to database: {DB_PATH}")
        logger.info("[OK] Database optimizations applied\n")
        
        cursor = conn.cursor()
        
        # Check existing products
        logger.info("Step 1: Analyzing product data...")
        cursor.execute("SELECT COUNT(*) FROM products")
        existing_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT product_id) FROM transactions WHERE product_id IS NOT NULL")
        total_unique = cursor.fetchone()[0]
        
        logger.info(f"  Current products in DB: {existing_count:,}")
        logger.info(f"  Unique products in transactions: {total_unique:,}")
        logger.info(f"  Remaining to insert: {total_unique - existing_count:,}\n")
        
        if existing_count >= total_unique:
            logger.info("[OK] All products already populated!\n")
            conn.close()
            return True
        
        # Get existing product IDs
        existing_ids = set()
        if existing_count > 0:
            logger.info("Step 2: Loading existing product IDs...")
            cursor.execute("SELECT product_id FROM products")
            existing_ids = {row[0] for row in cursor.fetchall()}
            logger.info(f"[OK] Loaded {len(existing_ids):,} existing product IDs\n")
        
        # Extract product data with aggregations
        logger.info("Step 3: Extracting and aggregating product data from transactions...")
        query = """
        SELECT 
            product_id,
            product_name,
            category,
            subcategory,
            brand,
            AVG(product_weight_kg) as product_weight_kg,
            AVG(original_price_inr) as original_price_inr,
            MIN(discounted_price_inr) as min_selling_price_inr,
            MAX(discounted_price_inr) as max_selling_price_inr,
            AVG(product_rating) as product_rating,
            COUNT(*) as total_reviews,
            COUNT(DISTINCT transaction_id) as total_rating_count,
            MAX(CASE WHEN is_prime_eligible = 1 THEN 1 ELSE 0 END) as is_prime_eligible,
            MIN(order_date) as first_sale_date,
            MAX(order_date) as last_sale_date
        FROM transactions
        WHERE product_id IS NOT NULL
        GROUP BY product_id
        """
        
        df_products = pd.read_sql_query(query, conn)
        total_products = len(df_products)
        logger.info(f"[OK] Extracted {total_products:,} unique products from transactions\n")
        
        # Filter out existing products
        if len(existing_ids) > 0:
            df_products = df_products[~df_products['product_id'].isin(existing_ids)]
            logger.info(f"[OK] Filtered to {len(df_products):,} new products (skipping {len(existing_ids):,} existing)\n")
        
        if len(df_products) == 0:
            logger.info("[OK] No new products to insert!\n")
            conn.close()
            return True
        
        # Display sample data
        logger.info("Sample of extracted product data (first 5 records):")
        logger.info(df_products.head(5).to_string())
        logger.info("\n")
        
        # Add additional columns with defaults
        logger.info("Step 4: Adding default values for missing columns...")
        
        # Generate SKU from product_id
        df_products['sku'] = 'SKU-' + df_products['product_id']
        
        # Pricing - set cost price as 70% of original price
        df_products['cost_price_inr'] = df_products['original_price_inr'] * 0.7
        
        # Stock and inventory - random reasonable values
        import numpy as np
        np.random.seed(42)
        df_products['stock_quantity'] = np.random.randint(50, 500, size=len(df_products))
        df_products['reorder_level'] = (df_products['stock_quantity'] * 0.2).astype(int)
        df_products['warehouse_location'] = np.random.choice(
            ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata'], 
            size=len(df_products)
        )
        
        # Product status
        df_products['is_active'] = 1
        df_products['is_bestseller'] = (df_products['total_reviews'] > df_products['total_reviews'].quantile(0.75)).astype(int)
        df_products['is_hazardous'] = 0
        
        # Additional attributes
        df_products['manufacturer'] = df_products['brand']  # Default manufacturer to brand
        df_products['model_number'] = 'MODEL-' + df_products['product_id']
        df_products['warranty_months'] = 12
        df_products['return_days'] = 30
        
        # Timestamps
        df_products['created_at'] = df_products['first_sale_date']
        df_products['updated_at'] = df_products['last_sale_date']
        df_products['last_restocked_at'] = df_products['last_sale_date']
        
        # Drop temporary columns
        df_products = df_products.drop(['first_sale_date', 'last_sale_date'], axis=1)
        
        logger.info(f"[OK] Added missing columns. Total columns: {len(df_products.columns)}\n")
        
        # Insert into products table
        logger.info("Step 5: Inserting products into database...")
        batch_size = 100
        inserted = 0
        total = len(df_products)
        
        logger.info(f"Using batch size: {batch_size}")
        logger.info(f"Starting insertion of {total:,} products...\n")
        
        for i in range(0, total, batch_size):
            batch = df_products.iloc[i:i+batch_size]
            try:
                batch.to_sql('products', conn, if_exists='append', index=False, method='multi')
                inserted += len(batch)
                
                # Progress indicator every 200 products
                if inserted % 200 == 0 or inserted == total:
                    percentage = (inserted / total) * 100
                    total_in_db = existing_count + inserted
                    logger.info(f"  Progress: {inserted:,}/{total:,} ({percentage:.1f}%) | Total in DB: {total_in_db:,}")
                    
            except sqlite3.IntegrityError as e:
                logger.warning(f"  Skipping duplicate batch at row {i}: {str(e)}")
                continue
            except Exception as e:
                logger.error(f"  Error inserting batch at row {i}: {str(e)}")
                conn.rollback()
                raise
        
        conn.commit()
        logger.info(f"\n[OK] All {inserted:,} products inserted successfully\n")
        
        # Final verification
        logger.info("Step 6: Final verification...")
        cursor.execute("SELECT COUNT(*) FROM products")
        final_count = cursor.fetchone()[0]
        logger.info(f"  Products in database: {final_count:,}")
        logger.info(f"  Expected total: {total_unique:,}")
        
        if final_count == total_unique:
            logger.info("  [OK] Perfect match! All products populated successfully\n")
        else:
            difference = total_unique - final_count
            logger.warning(f"  [WARNING] Difference: {difference:,} products\n")
        
        # Show sample of inserted data
        logger.info("Sample of inserted products (first 3 records):")
        verify_df = pd.read_sql_query("SELECT product_id, product_name, category, brand, original_price_inr, stock_quantity FROM products LIMIT 3", conn)
        logger.info(verify_df.to_string(index=False))
        logger.info("\n")
        
        # Show product statistics
        logger.info("="*80)
        logger.info("PRODUCT STATISTICS SUMMARY")
        logger.info("="*80 + "\n")
        
        # Overall stats
        overall_query = """
        SELECT 
            COUNT(*) as total_products,
            COUNT(DISTINCT category) as total_categories,
            COUNT(DISTINCT subcategory) as total_subcategories,
            COUNT(DISTINCT brand) as total_brands,
            ROUND(AVG(original_price_inr), 2) as avg_price,
            ROUND(MIN(original_price_inr), 2) as min_price,
            ROUND(MAX(original_price_inr), 2) as max_price,
            SUM(is_bestseller) as bestseller_count
        FROM products
        """
        overall_df = pd.read_sql_query(overall_query, conn)
        logger.info("Overall Product Metrics:")
        logger.info(overall_df.to_string(index=False))
        logger.info("\n")
        
        # Category breakdown
        logger.info("Products by Category:")
        category_query = """
        SELECT 
            category,
            COUNT(*) as product_count,
            ROUND(AVG(original_price_inr), 2) as avg_price,
            SUM(is_bestseller) as bestsellers
        FROM products
        GROUP BY category
        ORDER BY product_count DESC
        LIMIT 10
        """
        category_df = pd.read_sql_query(category_query, conn)
        logger.info(category_df.to_string(index=False))
        logger.info("\n")
        
        # Top brands
        logger.info("Top 10 Brands by Product Count:")
        brand_query = """
        SELECT 
            brand,
            COUNT(*) as product_count,
            ROUND(AVG(original_price_inr), 2) as avg_price,
            ROUND(AVG(product_rating), 2) as avg_rating
        FROM products
        WHERE brand IS NOT NULL
        GROUP BY brand
        ORDER BY product_count DESC
        LIMIT 10
        """
        brand_df = pd.read_sql_query(brand_query, conn)
        logger.info(brand_df.to_string(index=False))
        logger.info("\n")
        
        # Price range distribution
        logger.info("Price Range Distribution:")
        price_query = """
        SELECT 
            CASE 
                WHEN original_price_inr < 1000 THEN 'Under 1K'
                WHEN original_price_inr < 5000 THEN '1K-5K'
                WHEN original_price_inr < 10000 THEN '5K-10K'
                WHEN original_price_inr < 25000 THEN '10K-25K'
                WHEN original_price_inr < 50000 THEN '25K-50K'
                ELSE 'Above 50K'
            END as price_range,
            COUNT(*) as product_count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM products), 2) as percentage
        FROM products
        GROUP BY price_range
        ORDER BY 
            CASE price_range
                WHEN 'Under 1K' THEN 1
                WHEN '1K-5K' THEN 2
                WHEN '5K-10K' THEN 3
                WHEN '10K-25K' THEN 4
                WHEN '25K-50K' THEN 5
                ELSE 6
            END
        """
        price_df = pd.read_sql_query(price_query, conn)
        logger.info(price_df.to_string(index=False))
        logger.info("\n")
        
        conn.close()
        
        logger.info("="*80)
        logger.info("[SUCCESS] PRODUCTS TABLE POPULATION COMPLETED")
        logger.info("="*80 + "\n")
        
        return True
        
    except Exception as e:
        logger.error(f"\n[ERROR] Failed to populate products: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution flow"""
    start_time = datetime.now()
    
    logger.info(f"\n{'*'*80}")
    logger.info("POPULATE PRODUCTS TABLE")
    logger.info(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Database: {DB_PATH}")
    logger.info(f"Log File: {LOG_FILE}")
    logger.info(f"{'*'*80}\n")
    
    success = populate_products()
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info(f"{'*'*80}")
    if success:
        logger.info("[SUCCESS] POPULATION COMPLETED")
    else:
        logger.info("[FAILED] Check log for details")
    logger.info(f"Duration: {duration}")
    logger.info(f"Ended: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"{'*'*80}\n")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
