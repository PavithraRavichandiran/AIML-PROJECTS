"""
Amazon India Sales Analytics - Bulk Data Insertion with Validation
Purpose: Load cleaned data from CSV files into SQLite database with comprehensive validation
Database: amazon_india_analytics.db
"""

import pandas as pd
import sqlite3
import os
import logging
from datetime import datetime
from pathlib import Path
import sys

# ============================================================================
# CONFIGURATION
# ============================================================================

# File paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'cleaned'
DB_PATH = BASE_DIR / 'AmazonIndia.db'
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# Logging setup
LOG_FILE = LOG_DIR / f'bulk_insert_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
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
# DATA VALIDATION FUNCTIONS
# ============================================================================

class DataValidator:
    """Comprehensive data validation for all tables"""
    
    @staticmethod
    def validate_transactions(df):
        """Validate transaction data"""
        issues = []
        
        # Check required columns
        required_cols = ['transaction_id', 'order_date', 'customer_id', 'product_id', 
                        'final_amount_inr']
        for col in required_cols:
            if col not in df.columns:
                issues.append(f"Missing required column: {col}")
        
        # Check data types and values
        if 'order_date' in df.columns:
            try:
                df['order_date'] = pd.to_datetime(df['order_date'])
            except Exception as e:
                issues.append(f"Invalid date format in order_date: {str(e)}")
        
        # Check for nulls in critical columns
        for col in required_cols:
            if col in df.columns and df[col].isnull().sum() > 0:
                null_count = df[col].isnull().sum()
                issues.append(f"Column {col} has {null_count} null values")
        
        # Check numeric values are positive
        numeric_cols = ['final_amount_inr', 'original_price_inr', 'quantity', 'discount_percent']
        for col in numeric_cols:
            if col in df.columns:
                if (df[col] < 0).any():
                    neg_count = (df[col] < 0).sum()
                    issues.append(f"Column {col} has {neg_count} negative values")
        
        # Check discount_percent is between 0-100
        if 'discount_percent' in df.columns:
            invalid = ((df['discount_percent'] < 0) | (df['discount_percent'] > 100)).sum()
            if invalid > 0:
                issues.append(f"discount_percent has {invalid} values outside 0-100 range")
        
        # Check quantity is >= 1
        if 'quantity' in df.columns:
            invalid = (df['quantity'] < 1).sum()
            if invalid > 0:
                issues.append(f"quantity has {invalid} values less than 1")
        
        return issues
    
    @staticmethod
    def validate_products(df):
        """Validate product data"""
        issues = []
        
        required_cols = ['product_id', 'product_name', 'category', 'subcategory', 
                        'original_price_inr']
        for col in required_cols:
            if col not in df.columns:
                issues.append(f"Missing required column: {col}")
        
        # Check for nulls
        for col in required_cols:
            if col in df.columns and df[col].isnull().sum() > 0:
                null_count = df[col].isnull().sum()
                issues.append(f"Column {col} has {null_count} null values")
        
        # Check price is positive
        if 'original_price_inr' in df.columns:
            invalid = (df['original_price_inr'] <= 0).sum()
            if invalid > 0:
                issues.append(f"original_price_inr has {invalid} non-positive values")
        
        # Check rating is 0-5
        if 'product_rating' in df.columns and df['product_rating'].notna().any():
            invalid = ((df['product_rating'] < 0) | (df['product_rating'] > 5)).sum()
            if invalid > 0:
                issues.append(f"product_rating has {invalid} values outside 0-5 range")
        
        # Check stock is non-negative
        if 'stock_quantity' in df.columns:
            invalid = (df['stock_quantity'] < 0).sum()
            if invalid > 0:
                issues.append(f"stock_quantity has {invalid} negative values")
        
        return issues
    
    @staticmethod
    def validate_customers(df):
        """Validate customer data"""
        issues = []
        
        required_cols = ['customer_id', 'city', 'state', 'account_created_date']
        for col in required_cols:
            if col not in df.columns:
                issues.append(f"Missing required column: {col}")
        
        # Check for nulls in critical columns
        for col in required_cols:
            if col in df.columns and df[col].isnull().sum() > 0:
                null_count = df[col].isnull().sum()
                issues.append(f"Column {col} has {null_count} null values")
        
        # Validate dates
        date_cols = ['date_of_birth', 'account_created_date', 'prime_member_since']
        for col in date_cols:
            if col in df.columns and df[col].notna().any():
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception as e:
                    issues.append(f"Invalid date format in {col}: {str(e)}")
        
        # Check rating is 0-5
        if 'customer_rating' in df.columns and df['customer_rating'].notna().any():
            invalid = ((df['customer_rating'] < 0) | (df['customer_rating'] > 5)).sum()
            if invalid > 0:
                issues.append(f"customer_rating has {invalid} values outside 0-5 range")
        
        # Check spending is non-negative
        if 'total_spend_inr' in df.columns:
            invalid = (df['total_spend_inr'] < 0).sum()
            if invalid > 0:
                issues.append(f"total_spend_inr has {invalid} negative values")
        
        # Validate email uniqueness
        if 'email' in df.columns:
            duplicates = df[df['email'].notna()]['email'].duplicated().sum()
            if duplicates > 0:
                issues.append(f"email has {duplicates} duplicate values")
        
        return issues

# ============================================================================
# BULK INSERT FUNCTIONS
# ============================================================================

class BulkDataInserter:
    """Handle bulk data insertion with error handling and rollback capability"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.stats = {
            'total_rows': 0,
            'inserted_rows': 0,
            'failed_rows': 0,
            'validation_errors': 0
        }
    
    def connect(self):
        """Create database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def insert_transactions(self, csv_file):
        """Load and insert transaction data"""
        logger.info(f"\n{'='*80}")
        logger.info(f"LOADING TRANSACTIONS: {csv_file}")
        logger.info(f"{'='*80}")
        
        try:
            # Read CSV
            df = pd.read_csv(csv_file, low_memory=False)
            logger.info(f"Loaded {len(df)} transaction records from CSV")
            self.stats['total_rows'] = len(df)
            
            # Validate data
            validator = DataValidator()
            issues = validator.validate_transactions(df)
            
            if issues:
                logger.warning(f"Found {len(issues)} validation issues:")
                for issue in issues:
                    logger.warning(f"  - {issue}")
                self.stats['validation_errors'] += len(issues)
            
            # Data cleaning
            df['order_date'] = pd.to_datetime(df['order_date'])
            
            # Replace NaN with None for NULL insertion
            df = df.where(pd.notna(df), None)
            
            # SQLite has max 999 variables limit
            # With 34 columns, safe batch size is 999/34 = 29, use 25 to be safe
            batch_size = 25
            total_batches = (len(df) + batch_size - 1) // batch_size
            
            logger.info(f"Inserting in batches of {batch_size} rows ({total_batches} batches)")
            
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]
                batch_num = i//batch_size + 1
                try:
                    batch.to_sql('transactions', self.conn, if_exists='append', 
                               index=False, method='multi')
                    self.stats['inserted_rows'] += len(batch)
                    
                    # Log every 1000 batches (25000 rows)
                    if batch_num % 1000 == 0 or batch_num == total_batches:
                        logger.info(f"Progress: {batch_num}/{total_batches} batches ({self.stats['inserted_rows']:,} rows)")
                except Exception as e:
                    logger.error(f"Error inserting batch {batch_num}: {str(e)}")
                    self.stats['failed_rows'] += len(batch)
            
            self.conn.commit()
            logger.info(f"✓ Successfully inserted {self.stats['inserted_rows']:,} transactions")
            
        except Exception as e:
            logger.error(f"Failed to process transactions: {str(e)}")
            self.conn.rollback()
    
    def insert_products(self, csv_file):
        """Load and insert product data"""
        logger.info(f"\n{'='*80}")
        logger.info(f"LOADING PRODUCTS: {csv_file}")
        logger.info(f"{'='*80}")
        
        try:
            df = pd.read_csv(csv_file, low_memory=False)
            logger.info(f"Loaded {len(df)} product records from CSV")
            self.stats['total_rows'] = len(df)
            
            # Validate data
            validator = DataValidator()
            issues = validator.validate_products(df)
            
            if issues:
                logger.warning(f"Found {len(issues)} validation issues:")
                for issue in issues:
                    logger.warning(f"  - {issue}")
                self.stats['validation_errors'] += len(issues)
            
            # Data cleaning
            df = df.where(pd.notna(df), None)
            
            # SQLite has max 999 variables limit
            # With 36 columns, safe batch size is 999/36 = 27, use 25 to be safe
            batch_size = 25
            total_batches = (len(df) + batch_size - 1) // batch_size
            
            logger.info(f"Inserting in batches of {batch_size} rows ({total_batches} batches)")
            
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]
                batch_num = i//batch_size + 1
                try:
                    batch.to_sql('products', self.conn, if_exists='append', 
                               index=False, method='multi')
                    self.stats['inserted_rows'] += len(batch)
                    
                    # Log every 200 batches (5000 rows)
                    if batch_num % 200 == 0 or batch_num == total_batches:
                        logger.info(f"Progress: {batch_num}/{total_batches} batches ({self.stats['inserted_rows']:,} rows)")
                except Exception as e:
                    logger.error(f"Error inserting batch {batch_num}: {str(e)}")
                    self.stats['failed_rows'] += len(batch)
            
            self.conn.commit()
            logger.info(f"✓ Successfully inserted {self.stats['inserted_rows']} products")
            
        except Exception as e:
            logger.error(f"Failed to process products: {str(e)}")
            self.conn.rollback()
    
    def insert_customers(self, csv_file):
        """Load and insert customer data"""
        logger.info(f"\n{'='*80}")
        logger.info(f"LOADING CUSTOMERS: {csv_file}")
        logger.info(f"{'='*80}")
        
        try:
            df = pd.read_csv(csv_file, low_memory=False)
            logger.info(f"Loaded {len(df)} customer records from CSV")
            self.stats['total_rows'] = len(df)
            
            # Validate data
            validator = DataValidator()
            issues = validator.validate_customers(df)
            
            if issues:
                logger.warning(f"Found {len(issues)} validation issues:")
                for issue in issues:
                    logger.warning(f"  - {issue}")
                self.stats['validation_errors'] += len(issues)
            
            # Data cleaning
            date_cols = ['date_of_birth', 'account_created_date', 'prime_member_since', 
                        'last_login_date', 'last_purchase_date']
            for col in date_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            df = df.where(pd.notna(df), None)
            
            # SQLite has max 999 variables limit
            # With 63 columns, safe batch size is 999/63 = 15, use 15 to be safe
            batch_size = 15
            total_batches = (len(df) + batch_size - 1) // batch_size
            
            logger.info(f"Inserting in batches of {batch_size} rows ({total_batches} batches)")
            
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]
                batch_num = i//batch_size + 1
                try:
                    batch.to_sql('customers', self.conn, if_exists='append', 
                               index=False, method='multi')
                    self.stats['inserted_rows'] += len(batch)
                    
                    # Log every 200 batches (3000 rows)
                    if batch_num % 200 == 0 or batch_num == total_batches:
                        logger.info(f"Progress: {batch_num}/{total_batches} batches ({self.stats['inserted_rows']:,} rows)")
                except Exception as e:
                    logger.error(f"Error inserting batch {batch_num}: {str(e)}")
                    self.stats['failed_rows'] += len(batch)
            
            self.conn.commit()
            logger.info(f"✓ Successfully inserted {self.stats['inserted_rows']} customers")
            
        except Exception as e:
            logger.error(f"Failed to process customers: {str(e)}")
            self.conn.rollback()
    
    def verify_inserts(self):
        """Verify number of records in each table"""
        logger.info(f"\n{'='*80}")
        logger.info("DATA VERIFICATION")
        logger.info(f"{'='*80}")
        
        cursor = self.conn.cursor()
        
        tables = ['transactions', 'products', 'customers', 'time_dimension']
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cursor.fetchone()[0]
                logger.info(f"{table}: {count:,} records")
            except Exception as e:
                logger.error(f"Error verifying {table}: {str(e)}")
    
    def report_stats(self):
        """Log insertion statistics"""
        logger.info(f"\n{'='*80}")
        logger.info("INSERTION STATISTICS")
        logger.info(f"{'='*80}")
        logger.info(f"Total rows processed: {self.stats['total_rows']:,}")
        logger.info(f"Successfully inserted: {self.stats['inserted_rows']:,}")
        logger.info(f"Failed rows: {self.stats['failed_rows']:,}")
        logger.info(f"Validation errors: {self.stats['validation_errors']}")
        logger.info(f"Success rate: {(self.stats['inserted_rows']/max(self.stats['total_rows'],1)*100):.2f}%")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution flow"""
    logger.info(f"\n{'*'*80}")
    logger.info("AMAZON INDIA SALES ANALYTICS - BULK DATA INSERTION")
    logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"{'*'*80}\n")
    
    # Initialize inserter
    inserter = BulkDataInserter(DB_PATH)
    
    # Connect to database
    if not inserter.connect():
        logger.error("Failed to connect to database. Exiting.")
        return
    
    try:
        # Load data files - adjust filenames based on actual CSV names
        logger.info("Scanning for cleaned data files...")
        
        # List CSV files to identify transaction/product/customer data
        csv_files = list(DATA_DIR.glob('*.csv'))
        logger.info(f"Found {len(csv_files)} CSV files in {DATA_DIR}")
        
        # Load main merged dataset (contains all transaction data)
        main_file = DATA_DIR / 'amazon_india_all_years_cleaned.csv'
        if main_file.exists():
            inserter.insert_transactions(main_file)
        
        # Load individual analysis files if they don't duplicate transaction data
        # Uncomment based on your specific CSV structure
        # for csv_file in csv_files:
        #     if 'transactions' in csv_file.name.lower():
        #         inserter.insert_transactions(csv_file)
        #     elif 'products' in csv_file.name.lower():
        #         inserter.insert_products(csv_file)
        #     elif 'customers' in csv_file.name.lower():
        #         inserter.insert_customers(csv_file)
        
        # Verify inserts
        inserter.verify_inserts()
        
        # Report statistics
        inserter.report_stats()
        
        logger.info(f"\n{'*'*80}")
        logger.info(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Log file: {LOG_FILE}")
        logger.info(f"{'*'*80}\n")
        
    except Exception as e:
        logger.error(f"Unexpected error during insertion: {str(e)}")
    finally:
        inserter.close()

if __name__ == "__main__":
    main()
