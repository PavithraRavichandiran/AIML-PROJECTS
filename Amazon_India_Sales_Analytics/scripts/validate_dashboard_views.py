#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dashboard Views Validator
Validates all Question 1-5 dashboard views and provides summary statistics.

Location: scripts/validate_dashboard_views.py
Usage: python scripts/validate_dashboard_views.py
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = "AmazonIndia.db"

# Expected view names and approximate row counts
DASHBOARD_VIEWS = {
    "Q1: Executive Summary Dashboard": [
        ("vw_q1_executive_summary", 132, "Monthly × Years"),
        ("vw_q1_top_categories", 800, "Monthly × Categories"),
        ("vw_q1_growth_rates", 132, "Monthly growth metrics"),
    ],
    "Q2: Real-time Performance Monitor": [
        ("vw_q2_current_performance", 31, "Daily metrics for current month"),
        ("vw_q2_run_rate_forecast", 31, "Daily run-rate projections"),
        ("vw_q2_acquisition_metrics", 12, "Monthly acquisition metrics"),
    ],
    "Q3: Strategic Overview Dashboard": [
        ("vw_q3_market_share", 800, "Monthly × Categories"),
        ("vw_q3_geographic_expansion", 1320, "Monthly × States"),
        ("vw_q3_business_health", 132, "Monthly health scorecard"),
    ],
    "Q4: Financial Performance Dashboard": [
        ("vw_q4_financial_performance", 800, "Monthly × Category × Subcategory"),
        ("vw_q4_cost_structure", 132, "Monthly cost breakdown"),
        ("vw_q4_financial_forecast", 132, "Monthly forecast vs actual"),
    ],
    "Q5: Growth Analytics Dashboard": [
        ("vw_q5_customer_cohorts", 2640, "Cohort × Observation month"),
        ("vw_q5_portfolio_expansion", 132, "Monthly portfolio metrics"),
        ("vw_q5_strategic_initiatives", 800, "Monthly × Category initiative"),
        ("vw_q5_retention_analysis", 132, "Monthly cohort health"),
    ],
    "Q11: Customer Segmentation Dashboard": [
        ("vw_q11_rfm_distribution", 10, "RFM segment counts"),
        ("vw_q11_behavioral_segmentation", 10, "Behavioral segments"),
        ("vw_q11_ltv_buckets", 3, "LTV buckets"),
        ("vw_q11_marketing_recs", 100, "Sample marketing targets"),
    ],
    "Q12: Customer Journey Analytics Dashboard": [
        ("vw_q12_acquisition_channels", 10, "Channels counts"),
        ("vw_q12_purchase_patterns", 24, "Months since first purchase"),
        ("vw_q12_category_transitions", 50, "Category moves"),
        ("vw_q12_customer_evolution", 3, "Lifecycle counts"),
    ],
    "Q13: Prime Membership Analytics Dashboard": [
        ("vw_q13_prime_mix", 2, "Prime vs non-prime summary"),
        ("vw_q13_prime_retention", 24, "Monthly prime retention"),
        ("vw_q13_member_value", 2, "LTV by prime status"),
    ],
    "Q14: Customer Retention Dashboard": [
        ("vw_q14_churn_prediction", 100, "High churn risk list"),
        ("vw_q14_strategy_effectiveness", 10, "Strategy performance"),
        ("vw_q14_customer_lifecycle", 3, "Account age stages"),
    ],
    "Q15: Demographics & Behavior Dashboard": [
        ("vw_q15_age_category_preferences", 50, "Age x Category revenue"),
        ("vw_q15_age_spending", 10, "Age spend patterns"),
        ("vw_q15_geographic_age", 100, "State x Age revenue"),
        ("vw_q15_marketing_opportunities", 100, "Top demographics"),
    ],
    "Q16: Product Performance Dashboard": [
        ("vw_q16_product_performance", 1000, "Products by revenue"),
    ],
    "Q17: Brand Analytics Dashboard": [
        ("vw_q17_brand_performance", 500, "Brand × category revenue"),
    ],
    "Q18: Inventory Optimization Dashboard": [
        ("vw_q18_inventory_demand", 10000, "Product-month demand"),
    ],
    "Q19: Product Rating & Review Dashboard": [
        ("vw_q19_ratings", 2000, "Product rating summary"),
    ],
    "Q20: New Product Launch Dashboard": [
        ("vw_q20_new_product_launch", 2000, "Products since launch"),
    ],
}

def validate_views():
    """Validate all dashboard views exist and have data."""
    try:
        if not Path(DB_PATH).exists():
            print(f"ERROR: Database not found at {DB_PATH}")
            return False
        
        conn = sqlite3.connect(DB_PATH, timeout=60)
        cursor = conn.cursor()
        
        print("=" * 100)
        print("DASHBOARD VIEWS VALIDATION REPORT")
        print("=" * 100)
        print(f"Database: {DB_PATH}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        total_views = 0
        found_views = 0
        total_rows = 0
        
        # Check each dashboard question
        for dashboard_name, views in DASHBOARD_VIEWS.items():
            print(f"\n{dashboard_name}")
            print("-" * 100)
            
            for view_name, expected_approx, description in views:
                total_views += 1
                try:
                    # Check if view exists
                    cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='view' AND name='{view_name}'")
                    exists = cursor.fetchone()[0] > 0
                    
                    if exists:
                        # Get row count
                        count = cursor.execute(f"SELECT COUNT(*) FROM {view_name}").fetchone()[0]
                        found_views += 1
                        total_rows += count
                        
                        # Check if reasonably close to expected
                        variance_pct = abs(count - expected_approx) / max(expected_approx, 1) * 100
                        status = "OK" if variance_pct < 30 else "?" if count > 0 else "MISSING"
                        
                        print(f"  {status:7} {view_name:40} {count:>10,} rows (expected ~{expected_approx:,}) - {description}")
                    else:
                        print(f"  MISSING {view_name:40} NOT FOUND - {description}")
                
                except Exception as e:
                    print(f"  ERROR  {view_name:40} ERROR: {str(e)[:50]}")
        
        # Summary Statistics
        print("\n" + "=" * 100)
        print("SUMMARY STATISTICS")
        print("=" * 100)
        print(f"Total Views Expected:  {total_views}")
        print(f"Views Found:           {found_views} ({found_views/total_views*100:.1f}%)")
        print(f"Missing Views:         {total_views - found_views}")
        print(f"Total Rows Across All: {total_rows:,}")
        print()
        
        if found_views == total_views:
            print("OK: ALL DASHBOARD VIEWS VALIDATED SUCCESSFULLY")
            status = True
        elif found_views >= total_views * 0.8:
            print(f"PARTIAL: {found_views}/{total_views} views found")
            status = True
        else:
            print(f"CRITICAL: Only {found_views}/{total_views} views found")
            status = False
        
        # Sample Data Preview
        if found_views > 0:
            print("\n" + "=" * 100)
            print("SAMPLE DATA PREVIEW")
            print("=" * 100)
            
            # Q1 Executive Summary
            print("\nQ1: Executive Summary (Latest 3 Months)")
            try:
                rows = cursor.execute("""
                    SELECT year, month, month_name, 
                           ROUND(total_revenue_inr/1e9, 2) as revenue_b,
                           ROUND(yoy_revenue_growth_pct, 2) as yoy_pct,
                           active_customers, average_order_value_inr
                    FROM vw_q1_executive_summary 
                    ORDER BY year DESC, month DESC 
                    LIMIT 3
                """).fetchall()
                
                for row in rows:
                    print(f"  {row[0]}-{row[1]:02d} ({row[2]:3}): Revenue=₹{row[3]:.1f}B | YoY={row[4]:>7.2f}% | Customers={row[5]:>8,} | AOV=₹{row[6]:>8,.0f}")
            except Exception as e:
                print(f"  (Preview unavailable: {str(e)[:40]})")
            
            # Q3 Business Health
            print("\nQ3: Business Health (Latest 3 Months)")
            try:
                rows = cursor.execute("""
                    SELECT year, month, month_name,
                           active_customers,
                           ROUND(total_revenue_inr/1e9, 2) as revenue_b,
                           ROUND(avg_product_rating, 2) as rating,
                           ROUND(digital_payment_pct, 1) as digital_pct
                    FROM vw_q3_business_health 
                    ORDER BY year DESC, month DESC 
                    LIMIT 3
                """).fetchall()
                
                for row in rows:
                    print(f"  {row[0]}-{row[1]:02d} ({row[2]:3}): Customers={row[3]:>8,} | Revenue=₹{row[4]:.1f}B | Rating={row[5]:>4.2f}★ | Digital={row[6]:>5.1f}%")
            except Exception as e:
                print(f"  (Preview unavailable: {str(e)[:40]})")
            
            # Q5 Customer Growth
            print("\nQ5: Portfolio Expansion (Latest 3 Months)")
            try:
                rows = cursor.execute("""
                    SELECT year, month, month_name,
                           total_customers,
                           active_products,
                           ROUND(customer_growth_yoy_pct, 2) as cust_yoy_pct,
                           ROUND(avg_product_rating, 2) as rating
                    FROM vw_q5_portfolio_expansion 
                    ORDER BY year DESC, month DESC 
                    LIMIT 3
                """).fetchall()
                
                for row in rows:
                    print(f"  {row[0]}-{row[1]:02d} ({row[2]:3}): Customers={row[3]:>8,} | Products={row[4]:>5,} | YoY Growth={row[5]:>7.2f}% | Rating={row[6]:>4.2f}★")
            except Exception as e:
                print(f"  (Preview unavailable: {str(e)[:40]})")
        
        conn.close()
        
        # Next Steps
        print("\n" + "=" * 100)
        print("NEXT STEPS")
        print("=" * 100)
        if status:
            print("""
1. POWER BI SETUP:
   - Open Power BI Desktop
   - Get Data → SQLite Database
   - Select database: AmazonIndia.db
   - Import all 15 views
   - Refer to: DASHBOARD_POWERBI_TABLEAU_MAPPING.md for visual configuration

2. TABLEAU SETUP:
   - Open Tableau Desktop
   - Connect → SQLite
   - Select: AmazonIndia.db
   - Drag views to dashboard canvas
   - Use field mapping guide for visual setup

3. DAILY REFRESH:
   - Dashboard data auto-refreshes nightly at 2:00 AM
   - Task scheduler: AmazonIndia_KPI_Refresh_Nightly
   - Manual refresh: python scripts/refresh_kpis.py

4. DOCUMENTATION:
   - Read: DASHBOARD_POWERBI_TABLEAU_MAPPING.md
   - SQL References: sql/dashboard_executive_questions_1_5.sql
   """)
        else:
            print("\n⚠ Please deploy dashboard views first:")
            print("  python scripts/deploy_executive_dashboards.py")
        
        return status
    
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = validate_views()
    sys.exit(0 if success else 1)
