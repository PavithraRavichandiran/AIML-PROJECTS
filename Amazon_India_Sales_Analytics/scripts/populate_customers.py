"""
Amazon India Sales Analytics - Populate Customers Table (Optimized V2)
Purpose: Extract and populate customers table from transactions data with chunked processing
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

LOG_FILE = LOG_DIR / f'populate_customers_v2_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
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
# CUSTOMERS POPULATION - CHUNKED VERSION
# ============================================================================

def populate_customers_chunked():
    """
    Extract and populate customers table from transactions using chunked processing.
    This version processes customers in batches to avoid memory issues and supports resume.
    """
    logger.info(f"\n{'='*80}")
    logger.info("POPULATING CUSTOMERS TABLE (CHUNKED VERSION)")
    logger.info(f"{'='*80}\n")
    
    try:
        # Connect to database
        conn = sqlite3.connect(str(DB_PATH), timeout=300)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=20000")
        conn.execute("PRAGMA temp_store=MEMORY")
        logger.info(f"✓ Connected to database: {DB_PATH}")
        logger.info("✓ Database optimizations applied\n")
        
        cursor = conn.cursor()
        
        # Get counts
        logger.info("Step 1: Analyzing customer data...")
        cursor.execute("SELECT COUNT(*) FROM customers")
        existing_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM transactions WHERE customer_id IS NOT NULL")
        total_unique = cursor.fetchone()[0]
        
        logger.info(f"  Current customers in DB: {existing_count:,}")
        logger.info(f"  Unique customers in transactions: {total_unique:,}")
        logger.info(f"  Remaining to insert: {total_unique - existing_count:,}\n")
        
        if existing_count >= total_unique:
            logger.info("[OK] All customers already populated!\n")
            conn.close()
            return True
        
        # Get existing customer IDs (load as set for fast lookup)
        logger.info("Step 2: Loading existing customer IDs...")
        cursor.execute("SELECT customer_id FROM customers")
        existing_ids = {row[0] for row in cursor.fetchall()}
        logger.info(f"✓ Loaded {len(existing_ids):,} existing customer IDs\n")
        
        # Get list of new customer IDs to process
        logger.info("Step 3: Identifying new customers to insert...")
        cursor.execute("""
            SELECT DISTINCT customer_id 
            FROM transactions 
            WHERE customer_id IS NOT NULL 
            ORDER BY customer_id
        """)
        all_customer_ids = [row[0] for row in cursor.fetchall()]
        new_customer_ids = [cid for cid in all_customer_ids if cid not in existing_ids]
        
        logger.info(f"✓ Found {len(new_customer_ids):,} new customers to process\n")
        
        if len(new_customer_ids) == 0:
            logger.info("[OK] No new customers to insert!\n")
            conn.close()
            return True
        
        # Process in manageable chunks
        logger.info("Step 4: Processing and inserting customers in chunks...")
        chunk_size = 25000  # Process 25K at a time to avoid memory issues
        insert_batch = 500  # Insert 500 rows per batch
        total_inserted = 0
        total_to_insert = len(new_customer_ids)
        
        logger.info(f"  Chunk size: {chunk_size:,} customers")
        logger.info(f"  Insert batch: {insert_batch} rows")
        logger.info(f"  Total chunks: {(total_to_insert + chunk_size - 1) // chunk_size}\n")
        
        for chunk_num, chunk_start in enumerate(range(0, total_to_insert, chunk_size), 1):
            chunk_end = min(chunk_start + chunk_size, total_to_insert)
            chunk_ids = new_customer_ids[chunk_start:chunk_end]
            chunk_count = len(chunk_ids)
            
            logger.info(f"Chunk {chunk_num}: Processing {chunk_count:,} customers (IDs {chunk_start:,} to {chunk_end-1:,})")
            
            # Build parameterized query
            placeholders = ','.join(['?' for _ in chunk_ids])
            query = f"""
            SELECT 
                customer_id,
                customer_city as city,
                customer_state as state,
                customer_tier,
                customer_spending_tier,
                customer_age_group as age_group,
                customer_rating,
                is_prime_member,
                COUNT(*) as total_transactions,
                SUM(final_amount_inr) as total_spend_inr,
                AVG(final_amount_inr) as avg_order_value_inr,
                MAX(order_date) as last_purchase_date,
                MIN(order_date) as account_created_date
            FROM transactions
            WHERE customer_id IN ({placeholders})
            GROUP BY customer_id
            """
            
            # Extract data for this chunk
            df_chunk = pd.read_sql_query(query, conn, params=chunk_ids)
            logger.info(f"  ✓ Extracted {len(df_chunk):,} customer records")
            
            # Add derived columns
            df_chunk['customer_name'] = 'Customer_' + df_chunk['customer_id']
            df_chunk['is_active'] = 1
            df_chunk['total_reviews_posted'] = (df_chunk['total_transactions'] / 10).astype(int)
            df_chunk['loyalty_points'] = (df_chunk['total_spend_inr'] / 100).astype(int)
            df_chunk['rfm_segment'] = 'Standard'
            df_chunk['customer_segment'] = 'Regular'
            df_chunk['lifetime_value_predicted_inr'] = df_chunk['total_spend_inr'] * 1.5
            df_chunk['churn_risk_score'] = 0.3
            df_chunk['engagement_score'] = 0.6
            df_chunk['loyalty_tier'] = 'Bronze'
            df_chunk['email_opt_in'] = 1
            df_chunk['sms_opt_in'] = 1
            
            # Insert in smaller batches
            chunk_inserted = 0
            for i in range(0, len(df_chunk), insert_batch):
                batch = df_chunk.iloc[i:i+insert_batch]
                batch.to_sql('customers', conn, if_exists='append', index=False, method='multi')
                chunk_inserted += len(batch)
                total_inserted += len(batch)
            
            # Commit after each chunk
            conn.commit()
            
            percentage = (total_inserted / total_to_insert) * 100
            total_in_db = existing_count + total_inserted
            logger.info(f"  ✓ Inserted {chunk_inserted:,} customers | Progress: {total_inserted:,}/{total_to_insert:,} ({percentage:.1f}%) | DB Total: {total_in_db:,}")
            logger.info("")
        
        logger.info(f"[SUCCESS] Inserted {total_inserted:,} new customers\n")
        
        # Final verification
        logger.info("Step 5: Final verification...")
        cursor.execute("SELECT COUNT(*) FROM customers")
        final_count = cursor.fetchone()[0]
        logger.info(f"  Customers in database: {final_count:,}")
        logger.info(f"  Expected total: {total_unique:,}")
        
        if final_count == total_unique:
            logger.info("  ✓ Perfect match! All customers populated successfully")
        else:
            difference = total_unique - final_count
            logger.warning(f"  ⚠ Difference: {difference:,} customers")
        
        # Show statistics
        logger.info("\n" + "="*80)
        logger.info("CUSTOMER STATISTICS")
        logger.info("="*80 + "\n")
        
        stats_query = """
        SELECT 
            COUNT(*) as total_customers,
            SUM(CASE WHEN is_prime_member = 1 THEN 1 ELSE 0 END) as prime_members,
            ROUND(AVG(total_spend_inr), 2) as avg_lifetime_spend,
            ROUND(SUM(total_spend_inr), 2) as total_revenue,
            ROUND(AVG(total_transactions), 2) as avg_transactions
        FROM customers
        """
        stats_df = pd.read_sql_query(stats_query, conn)
        logger.info("Overall Metrics:")
        logger.info(stats_df.to_string(index=False))
        
        logger.info("\nBy Customer Tier:")
        tier_query = """
        SELECT 
            customer_tier,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customers), 1) as pct,
            ROUND(AVG(total_spend_inr), 2) as avg_spend
        FROM customers
        GROUP BY customer_tier
        ORDER BY customer_tier
        """
        tier_df = pd.read_sql_query(tier_query, conn)
        logger.info(tier_df.to_string(index=False))
        
        logger.info("\nBy Spending Tier:")
        spending_query = """
        SELECT 
            customer_spending_tier,
            COUNT(*) as count,
            ROUND(AVG(total_spend_inr), 2) as avg_spend,
            ROUND(SUM(total_spend_inr), 2) as total_revenue
        FROM customers
        GROUP BY customer_spending_tier
        ORDER BY 
            CASE customer_spending_tier
                WHEN 'High Spender' THEN 1
                WHEN 'Medium Spender' THEN 2
                WHEN 'Low Spender' THEN 3
                ELSE 4
            END
        """
        spending_df = pd.read_sql_query(spending_query, conn)
        logger.info(spending_df.to_string(index=False))
        logger.info("")
        
        conn.close()
        
        logger.info("="*80)
        logger.info("[SUCCESS] CUSTOMERS TABLE POPULATION COMPLETED")
        logger.info("="*80 + "\n")
        
        return True
        
    except Exception as e:
        logger.error(f"\n[ERROR] Failed to populate customers: {str(e)}")
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
    logger.info("POPULATE CUSTOMERS TABLE - VERSION 2 (OPTIMIZED)")
    logger.info(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Database: {DB_PATH}")
    logger.info(f"Log File: {LOG_FILE}")
    logger.info(f"{'*'*80}\n")
    
    success = populate_customers_chunked()
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info(f"{'*'*80}")
    if success:
        logger.info("✓ POPULATION COMPLETED SUCCESSFULLY")
    else:
        logger.info("✗ POPULATION FAILED - Check log for details")
    logger.info(f"Duration: {duration}")
    logger.info(f"Ended: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"{'*'*80}\n")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
