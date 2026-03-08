-- ============================================================================
-- Amazon India Sales Analytics - Time Dimension Table (SQLite)
-- Purpose: Date dimension table for time-based analysis and reporting
-- Covers: 2015-2025 (Decade of sales data)
-- Database: SQLite 3
-- ============================================================================

CREATE TABLE time_dimension (
    -- Primary Keys & Date Identifiers
    date_id INTEGER PRIMARY KEY,
    date_value DATE NOT NULL UNIQUE,
    
    -- Year Components
    year INTEGER NOT NULL,
    year_name TEXT NOT NULL,
    
    -- Quarter Components
    quarter INTEGER NOT NULL,
    quarter_name TEXT NOT NULL,
    year_quarter TEXT NOT NULL,
    
    -- Month Components
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    month_short TEXT NOT NULL,
    month_full TEXT NOT NULL,
    year_month TEXT NOT NULL,
    
    -- Week Components
    ISO_week INTEGER,
    iso_week_name TEXT,
    fiscal_week INTEGER,
    week_of_year INTEGER,
    fiscal_year INTEGER,
    fiscal_quarter INTEGER,
    
    -- Day Components
    day INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name TEXT NOT NULL,
    day_short TEXT NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_year INTEGER NOT NULL,
    
    -- Business Day Indicators
    is_weekday INTEGER NOT NULL,
    is_weekend INTEGER NOT NULL,
    is_business_day INTEGER NOT NULL,
    is_holiday_india INTEGER DEFAULT 0,
    is_weekend_or_holiday INTEGER NOT NULL,
    
    -- Festival Indicators
    is_diwali INTEGER DEFAULT 0,
    is_holi INTEGER DEFAULT 0,
    is_christmas INTEGER DEFAULT 0,
    is_new_year INTEGER DEFAULT 0,
    is_independence_day INTEGER DEFAULT 0,
    is_republic_day INTEGER DEFAULT 0,
    is_gandhi_jayanti INTEGER DEFAULT 0,
    is_rakhi INTEGER DEFAULT 0,
    is_dussehra INTEGER DEFAULT 0,
    is_navratri INTEGER DEFAULT 0,
    is_onam INTEGER DEFAULT 0,
    is_pongal INTEGER DEFAULT 0,
    is_eid INTEGER DEFAULT 0,
    is_durga_puja INTEGER DEFAULT 0,
    
    -- Festival Season Flags
    festival_season TEXT,
    is_festival_season INTEGER DEFAULT 0,
    
    -- Shopping Season Indicators
    is_festive_shopping_season INTEGER DEFAULT 0,
    is_summer_season INTEGER DEFAULT 0,
    is_monsoon_season INTEGER DEFAULT 0,
    is_winter_season INTEGER DEFAULT 0,
    season_name TEXT,
    
    -- Holiday Flags
    holiday_name TEXT,
    is_public_holiday INTEGER DEFAULT 0,
    
    -- Academic/School Year Indicators
    fiscal_year_india INTEGER,
    is_fiscal_year_start INTEGER DEFAULT 0,
    is_fiscal_year_end INTEGER DEFAULT 0,
    
    -- For Time Series Analysis
    days_since_first_date INTEGER,
    days_until_year_end INTEGER,
    days_in_month INTEGER,
    days_in_year INTEGER,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CHECK(month >= 1 AND month <= 12),
    CHECK(quarter >= 1 AND quarter <= 4),
    CHECK(day >= 1 AND day <= 31),
    CHECK(day_of_week >= 0 AND day_of_week <= 6),
    CHECK(is_weekday IN (0, 1)),
    CHECK(is_weekend IN (0, 1)),
    CHECK(is_business_day IN (0, 1))
);

-- ============================================================================
-- TRIGGER - Prevent modification of historical data
-- ============================================================================
CREATE TRIGGER time_dimension_prevent_delete
BEFORE DELETE ON time_dimension
BEGIN
  SELECT RAISE(ABORT, 'Deletion from time_dimension is not allowed');
END;

-- ============================================================================
-- INDEXES - Optimized for Time-Based Queries
-- ============================================================================

-- 1. PRIMARY KEY & DATE INDEXES
-- date_id PRIMARY KEY is already created above
CREATE INDEX IF NOT EXISTS idx_date_value ON time_dimension(date_value);

-- 2. YEAR-BASED INDEXES
CREATE INDEX IF NOT EXISTS idx_year ON time_dimension(year);
CREATE INDEX IF NOT EXISTS idx_fiscal_year ON time_dimension(fiscal_year_india);

-- 3. QUARTER-BASED INDEXES
CREATE INDEX IF NOT EXISTS idx_quarter ON time_dimension(quarter);
CREATE INDEX IF NOT EXISTS idx_year_quarter ON time_dimension(year_quarter);
CREATE INDEX IF NOT EXISTS idx_fiscal_quarter ON time_dimension(fiscal_quarter);

-- 4. MONTH-BASED INDEXES
CREATE INDEX IF NOT EXISTS idx_month ON time_dimension(month);
CREATE INDEX IF NOT EXISTS idx_month_name ON time_dimension(month_name);
CREATE INDEX IF NOT EXISTS idx_year_month ON time_dimension(year_month);

-- 5. WEEK-BASED INDEXES
CREATE INDEX IF NOT EXISTS idx_iso_week ON time_dimension(ISO_week);
CREATE INDEX IF NOT EXISTS idx_fiscal_week ON time_dimension(fiscal_week);
CREATE INDEX IF NOT EXISTS idx_week_of_year ON time_dimension(week_of_year);

-- 6. DAY-BASED INDEXES
CREATE INDEX IF NOT EXISTS idx_day ON time_dimension(day);
CREATE INDEX IF NOT EXISTS idx_day_of_week ON time_dimension(day_of_week);
CREATE INDEX IF NOT EXISTS idx_day_of_month ON time_dimension(day_of_month);
CREATE INDEX IF NOT EXISTS idx_day_of_year ON time_dimension(day_of_year);

-- 7. BUSINESS DAY INDEXES
CREATE INDEX IF NOT EXISTS idx_is_weekday ON time_dimension(is_weekday);
CREATE INDEX IF NOT EXISTS idx_is_weekend ON time_dimension(is_weekend);
CREATE INDEX IF NOT EXISTS idx_is_business_day ON time_dimension(is_business_day);
CREATE INDEX IF NOT EXISTS idx_is_holiday_india ON time_dimension(is_holiday_india);

-- 8. FESTIVAL INDEXES
CREATE INDEX IF NOT EXISTS idx_is_diwali ON time_dimension(is_diwali);
CREATE INDEX IF NOT EXISTS idx_is_holi ON time_dimension(is_holi);
CREATE INDEX IF NOT EXISTS idx_is_christmas ON time_dimension(is_christmas);
CREATE INDEX IF NOT EXISTS idx_is_festival_season ON time_dimension(is_festival_season);
CREATE INDEX IF NOT EXISTS idx_festival_season ON time_dimension(festival_season);
CREATE INDEX IF NOT EXISTS idx_festival_name ON time_dimension(holiday_name);

-- 9. SHOPPING SEASON INDEXES
CREATE INDEX IF NOT EXISTS idx_is_festive_shopping ON time_dimension(is_festive_shopping_season);
CREATE INDEX IF NOT EXISTS idx_season_name ON time_dimension(season_name);
CREATE INDEX IF NOT EXISTS idx_summer_season ON time_dimension(is_summer_season);
CREATE INDEX IF NOT EXISTS idx_monsoon_season ON time_dimension(is_monsoon_season);
CREATE INDEX IF NOT EXISTS idx_winter_season ON time_dimension(is_winter_season);

-- 10. COMPOSITE INDEXES - For common time-based analysis
CREATE INDEX IF NOT EXISTS idx_year_month_value ON time_dimension(year, month, date_value);
CREATE INDEX IF NOT EXISTS idx_year_quarter_month ON time_dimension(year, quarter, month);
CREATE INDEX IF NOT EXISTS idx_date_weekday ON time_dimension(date_value, day_of_week);
CREATE INDEX IF NOT EXISTS idx_month_day_name ON time_dimension(month, day_name);
CREATE INDEX IF NOT EXISTS idx_fiscal_year_month ON time_dimension(fiscal_year_india, month);

-- 11. METRIC INDEXES
CREATE INDEX IF NOT EXISTS idx_days_since_first ON time_dimension(days_since_first_date);
CREATE INDEX IF NOT EXISTS idx_days_until_year_end ON time_dimension(days_until_year_end);

-- ============================================================================
-- TABLE STATISTICS & DOCUMENTATION
-- ============================================================================
/*
Time Dimension Table Design:

Columns Overview:
- Identifiers: 2 columns (date_id, date_value)
- Year: 2 columns
- Quarter: 3 columns
- Month: 5 columns
- Week: 4 columns
- Day: 4 columns
- Business Day: 4 columns
- Festivals (India): 15 columns
- Seasons: 6 columns
- Holidays: 2 columns
- Academic/Fiscal: 3 columns
- Time Series: 4 columns
- Metadata: 1 column
Total: 56 columns

Date Range: 2015-01-01 to 2025-12-31
Total Records: 4,018 days (approximately)

Festival Coverage (Indian):
- Diwali (Nov/Dec)
- Holi (Mar/Apr)
- Christmas (Dec 25)
- New Year (Jan 1)
- Independence Day (Aug 15)
- Republic Day (Jan 26)
- Gandhi Jayanti (Oct 2)
- Rakhi (Jul/Aug)
- Dussehra (Sep/Oct)
- Navratri (Sep/Oct)
- Onam (Aug/Sep)
- Pongal (Jan 15)
- Eid (Lunar calendar)
- Durga Puja (Sep/Oct)

Seasonal Mapping (India):
- Summer: Apr-May
- Monsoon: Jun-Sep
- Winter: Oct-Mar
- Festival Season: Oct-Dec (Diwali), Mar-Apr (Holi)

Index Strategy:
- Year/Month/Week/Day: Time series analysis
- Business Day: Excluding holidays, weekends
- Festivals: Festival sales analysis
- Seasons: Seasonal trend analysis
- Fiscal Year: Financial period analysis
- Composite: Multi-level time aggregations

Expected Usage Patterns:
1. Daily sales trends: idx_date_value
2. Year-over-year comparison: idx_year
3. Monthly/quarterly analysis: idx_year_month, idx_year_quarter
4. Festival impact analysis: idx_is_diwali, idx_festival_season
5. Weekday/weekend analysis: idx_is_weekday
6. Seasonal trends: idx_season_name
7. Public holiday impact: idx_is_holiday_india
*/

-- ============================================================================
-- SAMPLE VERIFICATION QUERIES
-- ============================================================================
/*
-- Check table structure
PRAGMA table_info(time_dimension);

-- Check indexes
PRAGMA index_list(time_dimension);

-- Sample data retrieval
SELECT * FROM time_dimension LIMIT 10;

-- Date range verification
SELECT 
    MIN(date_value) as earliest_date,
    MAX(date_value) as latest_date,
    COUNT(*) as total_days
FROM time_dimension;

-- Festival dates in dataset
SELECT 
    date_value,
    day_name,
    month_name,
    year,
    CASE 
        WHEN is_diwali = 1 THEN 'Diwali'
        WHEN is_holi = 1 THEN 'Holi'
        WHEN is_christmas = 1 THEN 'Christmas'
        WHEN is_new_year = 1 THEN 'New Year'
        WHEN is_independence_day = 1 THEN 'Independence Day'
        WHEN is_republic_day = 1 THEN 'Republic Day'
        ELSE 'Other'
    END as festival_name
FROM time_dimension
WHERE is_festival_season = 1 OR is_diwali = 1 OR is_holi = 1 OR is_christmas = 1
ORDER BY date_value;

-- Holidays summary
SELECT 
    year,
    holiday_name,
    date_value,
    day_name,
    COUNT(*) as count
FROM time_dimension
WHERE is_public_holiday = 1
GROUP BY year, holiday_name
ORDER BY date_value;

-- Business days analysis
SELECT 
    year,
    month,
    month_name,
    SUM(CASE WHEN is_business_day = 1 THEN 1 ELSE 0 END) as business_days,
    SUM(CASE WHEN is_weekend = 1 THEN 1 ELSE 0 END) as weekend_days,
    SUM(CASE WHEN is_holiday_india = 1 THEN 1 ELSE 0 END) as holidays,
    COUNT(*) as total_days
FROM time_dimension
GROUP BY year, month
ORDER BY year, month;

-- Seasonal analysis
SELECT 
    year,
    season_name,
    COUNT(*) as days_in_season,
    SUM(CASE WHEN is_festival_season = 1 THEN 1 ELSE 0 END) as festival_days
FROM time_dimension
WHERE year >= 2020
GROUP BY year, season_name
ORDER BY year, season_name;

-- Festival shopping season dates
SELECT 
    date_value,
    day_name,
    month_name,
    year,
    festival_season,
    CASE 
        WHEN is_diwali = 1 THEN 'Diwali Week'
        WHEN is_holi = 1 THEN 'Holi Week'
        WHEN is_navratri = 1 THEN 'Navratri'
        WHEN is_christmas = 1 THEN 'Christmas Week'
        ELSE 'Festival Season'
    END as event
FROM time_dimension
WHERE is_festive_shopping_season = 1 AND year = 2023
ORDER BY date_value;

-- Month details for reporting
SELECT 
    year_month,
    year,
    month,
    month_name,
    MIN(date_value) as month_start,
    MAX(date_value) as month_end,
    COUNT(*) as days_in_month,
    SUM(CASE WHEN is_business_day = 1 THEN 1 ELSE 0 END) as business_days,
    SUM(CASE WHEN is_festival_season = 1 THEN 1 ELSE 0 END) as festival_days
FROM time_dimension
GROUP BY year_month
ORDER BY year, month;

-- Year summary
SELECT 
    year,
    COUNT(*) as total_days,
    SUM(CASE WHEN is_business_day = 1 THEN 1 ELSE 0 END) as business_days,
    SUM(CASE WHEN is_weekend = 1 THEN 1 ELSE 0 END) as weekend_days,
    SUM(CASE WHEN is_holiday_india = 1 THEN 1 ELSE 0 END) as public_holidays,
    SUM(CASE WHEN is_festival_season = 1 THEN 1 ELSE 0 END) as festival_season_days
FROM time_dimension
GROUP BY year
ORDER BY year;
*/

-- ============================================================================
-- INSERT TIME DIMENSION DATA (Run separately or via Python/ETL)
-- ============================================================================
/*
NOTE: To populate this table, you have several options:

1. Python Script (Recommended):
   - Use pandas date_range() for 2015-2025
   - Add year, month, quarter, week calculations
   - Add Indian festival dates (lunar calendar-based)
   - Load into SQLite

2. SQLite Recursive CTE:
   - Generate dates recursively from 2015-01-01 to 2025-12-31
   - Calculate all date components
   - Insert into time_dimension

3. External Data Load:
   - Generate CSV from Python/Excel
   - Import into SQLite using .import command

Example Python Snippet:
```python
import pandas as pd
import sqlite3

# Create date range
dates = pd.date_range(start='2015-01-01', end='2025-12-31', freq='D')

# Create dataframe with all calculations
df = pd.DataFrame({
    'date_value': dates,
    'date_id': range(1, len(dates) + 1),
    'year': dates.year,
    'month': dates.month,
    'quarter': dates.quarter,
    'day_of_week': dates.dayofweek,
    'day_of_year': dates.dayofyear,
    # ... add more calculations
})

# Load into SQLite
conn = sqlite3.connect('amazon_india_analytics.db')
df.to_sql('time_dimension', conn, if_exists='append', index=False)
conn.close()
```
*/
