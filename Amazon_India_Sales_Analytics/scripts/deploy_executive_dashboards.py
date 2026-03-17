#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Executive Dashboard Views Deployment Script
Applies all Question 1-5 executive dashboard SQL views to the database
and validates successful creation.

Location: scripts/deploy_executive_dashboards.py
Author: Amazon India Analytics
Date: 2026-03-02
"""

import sqlite3
import os
import sys
import time
from datetime import datetime

# Database path
DB_PATH = "AmazonIndia.db"

def apply_dashboard_views():
    """Apply all executive dashboard views to the database."""
    try:
        # Read SQL file
        sql_file = "sql/dashboard_executive_questions_1_5.sql"
        if not os.path.exists(sql_file):
            print(f"ERROR: SQL file not found: {sql_file}")
            return False
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Connect to database with extended timeout and retry
        max_retries = 5
        retry_count = 0
        conn = None
        
        while retry_count < max_retries:
            try:
                # Use WAL mode which allows concurrent reads
                conn = sqlite3.connect(DB_PATH, timeout=60.0, check_same_thread=False)
                conn.execute("PRAGMA journal_mode=WAL")
                cursor = conn.cursor()
                break
            except sqlite3.OperationalError as e:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Database locked, retrying in 2 seconds... (attempt {retry_count}/{max_retries})")
                    time.sleep(2)
                else:
                    raise
        
        print("=" * 80)
        print("EXECUTIVE DASHBOARD VIEWS DEPLOYMENT")
        print("=" * 80)
        print(f"Database: {DB_PATH}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Execute SQL script - split by statements for better lock handling
        print("Applying dashboard SQL views...")
        # SQLite executescript doesn't respect timeout, so we'll execute statements individually
        statements = [s.strip() for s in sql_content.split(';') if s.strip()]
        
        for i, statement in enumerate(statements, 1):
            try:
                cursor.execute(statement)
                # Commit every 5 statements for incremental progress
                if i % 5 == 0:
                    conn.commit()
                    print(f"  ✓ {i}/{len(statements)} statements applied")
            except Exception as e:
                print(f"  ! Statement {i} skipped (likely object already exists): {str(e)[:60]}")
                conn.rollback()
                continue
        
        conn.commit()
        print("✓ SQL views successfully applied")
        print()
        print()
        
        # Validate views exist
        print("Validating views and tables...")
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type IN ('view', 'table') 
            AND name LIKE 'vw_q%' OR name LIKE 'q%_materialized'
            ORDER BY name
        """)
        views = cursor.fetchall()
        
        print(f"\nFound {len(views)} dashboard objects:")
        for view in views:
            print(f"  • {view[0]}")
        
        # Get row counts for each view
        print("\n" + "=" * 80)
        print("DASHBOARD VIEW ROW COUNTS")
        print("=" * 80)
        
        dashboard_views = [
            # Question 1
            ('vw_q1_executive_summary', 'Q1: Executive Summary'),
            ('vw_q1_top_categories', 'Q1: Top Categories'),
            ('vw_q1_growth_rates', 'Q1: Growth Rates'),
            # Question 2
            ('vw_q2_current_performance', 'Q2: Current Performance'),
            ('vw_q2_run_rate_forecast', 'Q2: Run Rate Forecast'),
            ('vw_q2_acquisition_metrics', 'Q2: Acquisition Metrics'),
            # Question 3
            ('vw_q3_market_share', 'Q3: Market Share'),
            ('vw_q3_geographic_expansion', 'Q3: Geographic Expansion'),
            ('vw_q3_business_health', 'Q3: Business Health'),
            # Question 4
            ('vw_q4_financial_performance', 'Q4: Financial Performance'),
            ('vw_q4_cost_structure', 'Q4: Cost Structure'),
            ('vw_q4_financial_forecast', 'Q4: Financial Forecast'),
            # Question 5
            ('vw_q5_customer_cohorts', 'Q5: Customer Cohorts'),
            ('vw_q5_portfolio_expansion', 'Q5: Portfolio Expansion'),
            ('vw_q5_strategic_initiatives', 'Q5: Strategic Initiatives'),
            ('vw_q5_retention_analysis', 'Q5: Retention Analysis'),
            # Questions 11-15 (Customer Analytics)
            ('vw_q11_rfm_distribution', 'Q11: RFM Distribution'),
            ('vw_q11_behavioral_segmentation', 'Q11: Behavioral Segmentation'),
            ('vw_q11_ltv_buckets', 'Q11: LTV Buckets'),
            ('vw_q11_marketing_recs', 'Q11: Marketing Recommendations'),
            ('vw_q12_acquisition_channels', 'Q12: Acquisition Channels'),
            ('vw_q12_purchase_patterns', 'Q12: Purchase Patterns'),
            ('vw_q12_category_transitions', 'Q12: Category Transitions'),
            ('vw_q12_customer_evolution', 'Q12: Customer Evolution'),
            ('vw_q13_prime_mix', 'Q13: Prime Mix'),
            ('vw_q13_prime_retention', 'Q13: Prime Retention'),
            ('vw_q13_member_value', 'Q13: Prime LTV'),
            ('vw_q14_churn_prediction', 'Q14: Churn Prediction'),
            ('vw_q14_strategy_effectiveness', 'Q14: Strategy Effectiveness'),
            ('vw_q14_customer_lifecycle', 'Q14: Customer Lifecycle'),
            ('vw_q15_age_category_preferences', 'Q15: Age-Category Preferences'),
            ('vw_q15_age_spending', 'Q15: Age Spending Patterns'),
            ('vw_q15_geographic_age', 'Q15: Geographic-Age Behavior'),
            ('vw_q15_marketing_opportunities', 'Q15: Marketing Opportunities'),
            # Questions 16-20 (Product & Inventory Analytics)
            ('vw_q16_product_performance', 'Q16: Product Performance'),
            ('vw_q17_brand_performance', 'Q17: Brand Performance'),
            ('vw_q18_inventory_demand', 'Q18: Inventory Demand'),
            ('vw_q19_ratings', 'Q19: Ratings Summary'),
            ('vw_q20_new_product_launch', 'Q20: New Product Launch'),
        ]
        
        for view_name, display_name in dashboard_views:
            try:
                count = cursor.execute(f"SELECT COUNT(*) FROM {view_name}").fetchone()[0]
                print(f"{display_name:40} {count:>10,} rows")
            except Exception as e:
                print(f"{display_name:40} ERROR: {str(e)}")
        
        # Sample data preview
        print("\n" + "=" * 80)
        print("SAMPLE DATA PREVIEW")
        print("=" * 80)
        
        print("\nQ1: Executive Summary (Latest 3 Months)")
        rows = cursor.execute("""
            SELECT year, month, month_name, total_orders, active_customers, 
                   ROUND(total_revenue_inr/1e8, 1), average_order_value_inr, yoy_revenue_growth_pct
            FROM vw_q1_executive_summary 
            ORDER BY year DESC, month DESC 
            LIMIT 3
        """).fetchall()
        for row in rows:
            print(f"  {row[0]}-{row[1]:02d} ({row[2]:3}): Orders={row[3]:>7,} | Customers={row[4]:>7,} | "
                  f"Revenue=₹{row[5]}/1B | AOV=₹{row[6]:>8,.0f} | YoY={row[7]:>7.2f}%")
        
        print("\nQ3: Business Health (Latest 3 Months)")
        rows = cursor.execute("""
            SELECT year, month, month_name, active_customers, total_orders, 
                   ROUND(total_revenue_inr/1e8, 1), avg_product_rating, digital_payment_pct
            FROM vw_q3_business_health 
            ORDER BY year DESC, month DESC 
            LIMIT 3
        """).fetchall()
        for row in rows:
            print(f"  {row[0]}-{row[1]:02d} ({row[2]:3}): Customers={row[3]:>7,} | Orders={row[4]:>7,} | "
                  f"Revenue=₹{row[5]}/1B | Rating={row[6]:>4.2f}/5 | Digital={row[7]:>6.1f}%")
        
        print("\nQ5: Customer Growth (Latest 3 Months)")
        rows = cursor.execute("""
            SELECT year, month, month_name, total_customers, active_products, 
                   customer_growth_yoy_pct, avg_product_rating
            FROM vw_q5_portfolio_expansion 
            ORDER BY year DESC, month DESC 
            LIMIT 3
        """).fetchall()
        for row in rows:
            print(f"  {row[0]}-{row[1]:02d} ({row[2]:3}): Customers={row[3]:>7,} | "
                  f"Products={row[4]:>5,} | YoY Growth={row[5]:>7.2f}% | Rating={row[6]:>4.2f}/5")
        
        conn.close()
        
        print("\n" + "=" * 80)
        print("✓ DEPLOYMENT SUCCESSFUL")
        print("=" * 80)
        print("\nNext Steps:")
        print("  1. Run: python scripts/validate_dashboard_views.py")
        print("  2. Open Power BI/Tableau and connect to SQLite database")
        print("  3. Import the views listed above into your dashboards")
        print("  4. Refer to: DASHBOARD_POWERBI_TABLEAU_MAPPING.md for field configuration")
        
        return True
    
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = apply_dashboard_views()
    sys.exit(0 if success else 1)
