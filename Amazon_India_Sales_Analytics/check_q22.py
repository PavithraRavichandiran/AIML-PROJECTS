import sqlite3

db_path = "AmazonIndia.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check the schema of vw_q22_payment_analytics
try:
    cursor.execute("PRAGMA table_info(vw_q22_payment_analytics);")
    columns = cursor.fetchall()
    print("vw_q22_payment_analytics columns:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
except Exception as e:
    print(f"Error: {e}")

# Try to get sample data
try:
    cursor.execute("SELECT * FROM vw_q22_payment_analytics LIMIT 5;")
    rows = cursor.fetchall()
    print(f"\nRows: {len(rows)}")
    if rows:
        print("Sample:", rows[0])
except Exception as e:
    print(f"Error querying view: {e}")

conn.close()
