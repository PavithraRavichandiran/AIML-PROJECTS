import sys
sys.path.insert(0, r"c:\Users\admin\Desktop\Amazon_India_Sales_Analytics\dashboard")

from config import query_df, read_csv_df
import traceback

print("Testing load_data()...")
try:
    monthly = query_df(
        """
        SELECT year, month, month_name, quarter,
             revenue_inr, orders, unique_customers,
               avg_order_value_inr, mom_revenue_growth_pct,
               yoy_revenue_growth_pct
        FROM vw_exec_monthly_overview
        ORDER BY year, month
        """
    )
    print(f"✓ monthly: {len(monthly)} rows")
    
    category = query_df(
        """
         SELECT year, month, category, subcategory,
               revenue_inr, category_revenue_share_pct, category_rank_in_month
        FROM vw_exec_category_share
        WHERE category_rank_in_month <= 5
        ORDER BY year, month, category_rank_in_month
        """
    )
    print(f"✓ category: {len(category)} rows")
    
    payment = query_df(
        """
        SELECT year, month, month_name, payment_method,
               revenue_inr, payment_revenue_share_pct
        FROM vw_exec_payment_mix
        ORDER BY year, month
        """
    )
    print(f"✓ payment: {len(payment)} rows")
    
    prime = query_df(
        """
         SELECT year, month, month_name, member_type,
             revenue_inr, revenue_share_pct
        FROM vw_exec_prime_split
        ORDER BY year, month
        """
    )
    print(f"✓ prime: {len(prime)} rows")
    print("✓ load_data() PASSED")
except Exception as e:
    print(f"✗ load_data() FAILED: {e}")
    traceback.print_exc()

print("\nTesting load_q6_q10_data()...")
try:
    print("  Reading festival CSVs...")
    festival_metrics = read_csv_df("Q08_Festival_Performance_Metrics.csv")
    print(f"  ✓ festival_metrics: {len(festival_metrics)} rows")
    
    festival_bda = read_csv_df("Q08_Festival_Before_During_After.csv")
    print(f"  ✓ festival_bda: {len(festival_bda)} rows")
    print("✓ load_q6_q10_data() CSV part PASSED")
except Exception as e:
    print(f"✗ load_q6_q10_data() CSV part FAILED: {e}")
    traceback.print_exc()

print("\nTesting load_q11_q15_data()...")
try:
    rfm_dist = query_df("SELECT * FROM vw_q11_rfm_distribution")
    print(f"✓ rfm_dist: {len(rfm_dist)} rows")
    print("✓ load_q11_q15_data() PASSED")
except Exception as e:
    print(f"✗ load_q11_q15_data() FAILED: {e}")
    traceback.print_exc()

print("\nTesting load_q21_q25_data()...")
try:
    delivery_perf = query_df("SELECT * FROM vw_q21_delivery_performance")
    print(f"✓ delivery_perf: {len(delivery_perf)} rows")
    print("✓ load_q21_q25_data() PASSED")
except Exception as e:
    print(f"✗ load_q21_q25_data() FAILED: {e}")
    traceback.print_exc()
