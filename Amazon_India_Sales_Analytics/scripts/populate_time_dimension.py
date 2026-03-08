"""
Amazon India Sales Analytics - Populate Time Dimension Table
Purpose: Generate and populate time dimension table with comprehensive date attributes
Coverage: 2015-2025 (11 years)
"""

import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import logging
from pathlib import Path
import sys
import calendar

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / 'AmazonIndia.db'
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / f'populate_time_dimension_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
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
# INDIAN HOLIDAYS & FESTIVALS (Approximate dates - some vary by lunar calendar)
# ============================================================================

INDIAN_HOLIDAYS = {
    # Fixed National Holidays
    'Republic Day': [(1, 26)],  # January 26
    'Independence Day': [(8, 15)],  # August 15
    'Gandhi Jayanti': [(10, 2)],  # October 2
    'Christmas': [(12, 25)],  # December 25
    'New Year': [(1, 1)],  # January 1
    
    # Approximate festival dates (these vary by lunar calendar each year)
    # Using approximate dates for demonstration
    'Diwali': [(10, 24), (11, 12), (11, 1), (10, 18), (10, 27), (11, 4), (10, 19), (11, 7), (10, 27), (11, 15), (11, 4)],
    'Holi': [(3, 9), (2, 27), (3, 18), (3, 6), (2, 24), (3, 13), (3, 1), (3, 21), (3, 10), (2, 28), (3, 18)],
    'Dussehra': [(10, 13), (10, 22), (9, 30), (10, 8), (10, 15), (10, 25), (10, 5), (10, 24), (10, 12), (10, 2), (10, 20)],
    'Eid': [(7, 18), (7, 7), (6, 26), (6, 15), (6, 5), (5, 24), (5, 13), (5, 3), (4, 22), (4, 11), (4, 30)],
    'Raksha Bandhan': [(8, 10), (7, 30), (8, 18), (8, 7), (7, 26), (8, 15), (8, 3), (8, 22), (8, 11), (7, 31), (8, 19)],
    'Navratri Start': [(10, 4), (10, 13), (9, 21), (9, 29), (10, 7), (10, 17), (9, 26), (10, 15), (10, 3), (9, 23), (10, 12)],
    'Durga Puja': [(10, 11), (10, 20), (9, 28), (10, 6), (10, 13), (10, 23), (10, 3), (10, 22), (10, 10), (9, 30), (10, 18)],
    'Pongal': [(1, 14), (1, 14), (1, 14), (1, 14), (1, 14), (1, 14), (1, 14), (1, 14), (1, 14), (1, 14), (1, 14)],
    'Onam': [(9, 4), (8, 24), (9, 11), (8, 31), (8, 21), (9, 8), (8, 29), (9, 17), (9, 6), (8, 27), (9, 15)],
}

# ============================================================================
# TIME DIMENSION GENERATION
# ============================================================================

def get_indian_fiscal_year(date):
    """Get Indian fiscal year (April 1 - March 31)"""
    if date.month >= 4:
        return date.year
    else:
        return date.year - 1

def get_indian_fiscal_quarter(date):
    """Get Indian fiscal quarter (Q1: Apr-Jun, Q2: Jul-Sep, Q3: Oct-Dec, Q4: Jan-Mar)"""
    month = date.month
    if 4 <= month <= 6:
        return 1
    elif 7 <= month <= 9:
        return 2
    elif 10 <= month <= 12:
        return 3
    else:  # 1-3
        return 4

def get_season(month):
    """Get season name for India"""
    if month in [3, 4, 5, 6]:
        return 'Summer'
    elif month in [7, 8, 9]:
        return 'Monsoon'
    elif month in [10, 11]:
        return 'Autumn'
    else:  # 12, 1, 2
        return 'Winter'

def is_festival_date(date, festival_name):
    """Check if date matches a festival"""
    if festival_name not in INDIAN_HOLIDAYS:
        return 0
    
    festival_dates = INDIAN_HOLIDAYS[festival_name]
    year_idx = date.year - 2015  # Index for varying dates
    
    for fest_date in festival_dates:
        if len(fest_date) == 2:
            month, day = fest_date
            if date.month == month and date.day == day:
                return 1
        elif year_idx < len(festival_dates):
            month, day = festival_dates[year_idx]
            if date.month == month and date.day == day:
                return 1
    return 0

def get_festival_season(date):
    """Determine festival season"""
    month = date.month
    
    # Diwali/Dussehra season (Oct-Nov)
    if month in [10, 11]:
        return 'Diwali Season'
    # Christmas/New Year (Dec-Jan)
    elif month in [12, 1]:
        return 'Christmas-New Year'
    # Summer festivals (Mar-Apr)
    elif month in [3, 4]:
        return 'Spring Festival'
    # Raksha Bandhan/Independence (Aug)
    elif month == 8:
        return 'Rakhi Season'
    else:
        return None

def generate_time_dimension_data(start_date, end_date):
    """Generate complete time dimension data"""
    logger.info(f"Generating time dimension data from {start_date} to {end_date}...")
    
    # Generate date range
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    logger.info(f"Total dates to generate: {len(date_range):,}\n")
    
    records = []
    first_date = date_range[0]
    
    for idx, current_date in enumerate(date_range):
        # Progress indicator
        if (idx + 1) % 365 == 0 or (idx + 1) == len(date_range):
            logger.info(f"  Processing: {idx + 1:,}/{len(date_range):,} dates ({(idx+1)/len(date_range)*100:.1f}%)")
        
        # Date ID (YYYYMMDD format)
        date_id = int(current_date.strftime('%Y%m%d'))
        
        # Basic components
        year = current_date.year
        month = current_date.month
        day = current_date.day
        day_of_week = current_date.weekday()  # Monday=0, Sunday=6
        day_of_year = current_date.timetuple().tm_yday
        
        # Quarter
        quarter = (month - 1) // 3 + 1
        
        # Month names
        month_name = current_date.strftime('%B')
        month_short = current_date.strftime('%b')
        
        # Week calculations
        iso_week = current_date.isocalendar()[1]
        week_of_year = current_date.isocalendar()[1]
        
        # Fiscal year components
        fiscal_year_india = get_indian_fiscal_year(current_date)
        fiscal_quarter = get_indian_fiscal_quarter(current_date)
        
        # Day names
        day_name = current_date.strftime('%A')
        day_short = current_date.strftime('%a')
        
        # Business day indicators
        is_weekend = 1 if day_of_week in [5, 6] else 0  # Saturday, Sunday
        is_weekday = 1 - is_weekend
        
        # Festival checks
        is_diwali = is_festival_date(current_date, 'Diwali')
        is_holi = is_festival_date(current_date, 'Holi')
        is_christmas = is_festival_date(current_date, 'Christmas')
        is_new_year = is_festival_date(current_date, 'New Year')
        is_independence_day = is_festival_date(current_date, 'Independence Day')
        is_republic_day = is_festival_date(current_date, 'Republic Day')
        is_gandhi_jayanti = is_festival_date(current_date, 'Gandhi Jayanti')
        is_rakhi = is_festival_date(current_date, 'Raksha Bandhan')
        is_dussehra = is_festival_date(current_date, 'Dussehra')
        is_navratri = is_festival_date(current_date, 'Navratri Start')
        is_durga_puja = is_festival_date(current_date, 'Durga Puja')
        is_pongal = is_festival_date(current_date, 'Pongal')
        is_eid = is_festival_date(current_date, 'Eid')
        is_onam = is_festival_date(current_date, 'Onam')
        
        # Public holidays
        is_public_holiday = max(is_republic_day, is_independence_day, is_gandhi_jayanti)
        
        # Holiday name
        holiday_name = None
        if is_republic_day:
            holiday_name = 'Republic Day'
        elif is_independence_day:
            holiday_name = 'Independence Day'
        elif is_gandhi_jayanti:
            holiday_name = 'Gandhi Jayanti'
        elif is_diwali:
            holiday_name = 'Diwali'
        elif is_christmas:
            holiday_name = 'Christmas'
        elif is_new_year:
            holiday_name = 'New Year'
        
        # India holiday indicator (all festivals + public holidays)
        is_holiday_india = max(is_diwali, is_holi, is_christmas, is_new_year, 
                              is_independence_day, is_republic_day, is_gandhi_jayanti,
                              is_rakhi, is_dussehra, is_eid)
        
        is_business_day = 1 if (is_weekday and not is_public_holiday) else 0
        is_weekend_or_holiday = max(is_weekend, is_holiday_india)
        
        # Festival season
        festival_season = get_festival_season(current_date)
        is_festival_season = 1 if festival_season else 0
        
        # Shopping seasons
        is_festive_shopping_season = 1 if month in [10, 11, 12] else 0  # Oct-Dec
        
        # Weather seasons
        season_name = get_season(month)
        is_summer_season = 1 if season_name == 'Summer' else 0
        is_monsoon_season = 1 if season_name == 'Monsoon' else 0
        is_winter_season = 1 if season_name == 'Winter' else 0
        
        # Time series calculations
        days_since_first_date = (current_date - first_date).days
        days_until_year_end = (datetime(year, 12, 31) - current_date).days
        days_in_month = calendar.monthrange(year, month)[1]
        days_in_year = 366 if calendar.isleap(year) else 365
        
        # Fiscal year flags
        is_fiscal_year_start = 1 if (month == 4 and day == 1) else 0
        is_fiscal_year_end = 1 if (month == 3 and day == 31) else 0
        
        # Fiscal week (simplified - week from fiscal year start)
        fiscal_year_start = datetime(fiscal_year_india, 4, 1)
        fiscal_week = ((current_date - fiscal_year_start).days // 7) + 1
        
        # Create record
        record = {
            'date_id': date_id,
            'date_value': current_date.strftime('%Y-%m-%d'),
            'year': year,
            'year_name': f'FY{year}',
            'quarter': quarter,
            'quarter_name': f'Q{quarter}',
            'year_quarter': f'{year}-Q{quarter}',
            'month': month,
            'month_name': month_name,
            'month_short': month_short,
            'month_full': month_name,
            'year_month': f'{year}-{month:02d}',
            'ISO_week': iso_week,
            'iso_week_name': f'{year}-W{iso_week:02d}',
            'fiscal_week': fiscal_week,
            'week_of_year': week_of_year,
            'fiscal_year': fiscal_year_india,
            'fiscal_quarter': fiscal_quarter,
            'day': day,
            'day_of_week': day_of_week,
            'day_name': day_name,
            'day_short': day_short,
            'day_of_month': day,
            'day_of_year': day_of_year,
            'is_weekday': is_weekday,
            'is_weekend': is_weekend,
            'is_business_day': is_business_day,
            'is_holiday_india': is_holiday_india,
            'is_weekend_or_holiday': is_weekend_or_holiday,
            'is_diwali': is_diwali,
            'is_holi': is_holi,
            'is_christmas': is_christmas,
            'is_new_year': is_new_year,
            'is_independence_day': is_independence_day,
            'is_republic_day': is_republic_day,
            'is_gandhi_jayanti': is_gandhi_jayanti,
            'is_rakhi': is_rakhi,
            'is_dussehra': is_dussehra,
            'is_navratri': is_navratri,
            'is_onam': is_onam,
            'is_pongal': is_pongal,
            'is_eid': is_eid,
            'is_durga_puja': is_durga_puja,
            'festival_season': festival_season,
            'is_festival_season': is_festival_season,
            'is_festive_shopping_season': is_festive_shopping_season,
            'is_summer_season': is_summer_season,
            'is_monsoon_season': is_monsoon_season,
            'is_winter_season': is_winter_season,
            'season_name': season_name,
            'holiday_name': holiday_name,
            'is_public_holiday': is_public_holiday,
            'fiscal_year_india': fiscal_year_india,
            'is_fiscal_year_start': is_fiscal_year_start,
            'is_fiscal_year_end': is_fiscal_year_end,
            'days_since_first_date': days_since_first_date,
            'days_until_year_end': days_until_year_end,
            'days_in_month': days_in_month,
            'days_in_year': days_in_year,
        }
        
        records.append(record)
    
    logger.info(f"\n[OK] Generated {len(records):,} date records\n")
    return pd.DataFrame(records)

# ============================================================================
# MAIN POPULATION FUNCTION
# ============================================================================

def populate_time_dimension():
    """Populate time dimension table"""
    logger.info(f"\n{'='*80}")
    logger.info("POPULATING TIME DIMENSION TABLE")
    logger.info(f"{'='*80}\n")
    
    try:
        # Connect to database
        conn = sqlite3.connect(str(DB_PATH), timeout=300)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=20000")
        logger.info(f"[OK] Connected to database: {DB_PATH}")
        logger.info("[OK] Database optimizations applied\n")
        
        cursor = conn.cursor()
        
        # Check existing records
        cursor.execute("SELECT COUNT(*) FROM time_dimension")
        existing_count = cursor.fetchone()[0]
        logger.info(f"Current records in time_dimension: {existing_count:,}\n")
        
        if existing_count > 0:
            logger.info("[WARNING] Time dimension already has data!")
            logger.info("Checking date range coverage...")
            cursor.execute("SELECT MIN(date_value), MAX(date_value) FROM time_dimension")
            min_date, max_date = cursor.fetchone()
            logger.info(f"Existing coverage: {min_date} to {max_date}\n")
        
        # Get date range from transactions
        cursor.execute("SELECT MIN(order_date), MAX(order_date) FROM transactions")
        trans_min, trans_max = cursor.fetchone()
        logger.info(f"Transaction date range: {trans_min} to {trans_max}")
        
        # Define date range for time dimension (2015-2025)
        start_date = '2015-01-01'
        end_date = '2025-12-31'
        logger.info(f"Generating time dimension: {start_date} to {end_date}\n")
        
        # Generate time dimension data
        df_time = generate_time_dimension_data(start_date, end_date)
        
        # Show sample
        logger.info("Sample of generated time dimension data (first 5 rows):")
        logger.info(df_time.head(5)[['date_id', 'date_value', 'year', 'quarter', 'month_name', 
                                      'day_name', 'is_weekend', 'holiday_name']].to_string())
        logger.info("\n")
        
        # Insert data
        logger.info("Inserting time dimension data into database...")
        batch_size = 500
        inserted = 0
        total = len(df_time)
        
        for i in range(0, total, batch_size):
            batch = df_time.iloc[i:i+batch_size]
            try:
                batch.to_sql('time_dimension', conn, if_exists='append', index=False, method='multi')
                inserted += len(batch)
                
                # Progress every 1000 records
                if inserted % 1000 == 0 or inserted == total:
                    percentage = (inserted / total) * 100
                    logger.info(f"  Progress: {inserted:,}/{total:,} ({percentage:.1f}%)")
                    
            except sqlite3.IntegrityError as e:
                logger.warning(f"  Skipping duplicate batch: {str(e)}")
                continue
            except Exception as e:
                logger.error(f"  Error inserting batch: {str(e)}")
                conn.rollback()
                raise
        
        conn.commit()
        logger.info(f"\n[OK] All {inserted:,} records inserted successfully\n")
        
        # Verification
        logger.info("Verification...")
        cursor.execute("SELECT COUNT(*) FROM time_dimension")
        final_count = cursor.fetchone()[0]
        logger.info(f"  Total records in time_dimension: {final_count:,}")
        
        cursor.execute("SELECT MIN(date_value), MAX(date_value) FROM time_dimension")
        min_date, max_date = cursor.fetchone()
        logger.info(f"  Date range: {min_date} to {max_date}\n")
        
        # Statistics
        logger.info("="*80)
        logger.info("TIME DIMENSION STATISTICS")
        logger.info("="*80 + "\n")
        
        # Year breakdown
        year_query = """
        SELECT 
            year,
            COUNT(*) as total_days,
            SUM(is_business_day) as business_days,
            SUM(is_weekend) as weekend_days,
            SUM(is_holiday_india) as holidays
        FROM time_dimension
        GROUP BY year
        ORDER BY year
        """
        year_df = pd.read_sql_query(year_query, conn)
        logger.info("Days by Year:")
        logger.info(year_df.to_string(index=False))
        logger.info("\n")
        
        # Festival counts
        festival_query = """
        SELECT 
            SUM(is_diwali) as diwali_days,
            SUM(is_holi) as holi_days,
            SUM(is_christmas) as christmas_days,
            SUM(is_independence_day) as independence_days,
            SUM(is_republic_day) as republic_days,
            SUM(is_festival_season) as festival_season_days
        FROM time_dimension
        """
        festival_df = pd.read_sql_query(festival_query, conn)
        logger.info("Festival Days:")
        logger.info(festival_df.to_string(index=False))
        logger.info("\n")
        
        # Season breakdown
        season_query = """
        SELECT 
            season_name,
            COUNT(*) as days,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM time_dimension), 2) as percentage
        FROM time_dimension
        GROUP BY season_name
        ORDER BY days DESC
        """
        season_df = pd.read_sql_query(season_query, conn)
        logger.info("Days by Season:")
        logger.info(season_df.to_string(index=False))
        logger.info("\n")
        
        conn.close()
        
        logger.info("="*80)
        logger.info("[SUCCESS] TIME DIMENSION TABLE POPULATION COMPLETED")
        logger.info("="*80 + "\n")
        
        return True
        
    except Exception as e:
        logger.error(f"\n[ERROR] Failed to populate time dimension: {str(e)}")
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
    logger.info("POPULATE TIME DIMENSION TABLE")
    logger.info(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Database: {DB_PATH}")
    logger.info(f"Log File: {LOG_FILE}")
    logger.info(f"{'*'*80}\n")
    
    success = populate_time_dimension()
    
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
