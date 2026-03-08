import sqlite3

db_path = "AmazonIndia.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check transactions table row count
cursor.execute("SELECT COUNT(*) FROM transactions;")
trans_count = cursor.fetchone()[0]
print(f"Transactions table rows: {trans_count}")

# Try the first query from load_data()
try:
    cursor.execute("""
        SELECT year, month, month_name, quarter,
             revenue_inr, orders, unique_customers,
               avg_order_value_inr, mom_revenue_growth_pct,
               yoy_revenue_growth_pct
        FROM vw_exec_monthly_overview
        ORDER BY year, month
        LIMIT 5
    """)
    rows = cursor.fetchall()
    print(f"\nvw_exec_monthly_overview - rows returned: {len(rows)}")
    if rows:
        print("Sample data:", rows[0])
except Exception as e:
    print(f"Error querying vw_exec_monthly_overview: {e}")

# Check if vw_fact_sales_enriched exists and has data
try:
    cursor.execute("SELECT COUNT(*) FROM vw_fact_sales_enriched;")
    count = cursor.fetchone()[0]
    print(f"\nvw_fact_sales_enriched - rows: {count}")
except Exception as e:
    print(f"Error with vw_fact_sales_enriched: {e}")

conn.close()
