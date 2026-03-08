import sqlite3

db_path = "AmazonIndia.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if vw_q22_payment_analytics exists now
try:
    cursor.execute("SELECT * FROM vw_q22_payment_analytics LIMIT 3;")
    rows = cursor.fetchall()
    col_names = [desc[0] for desc in cursor.description]
    print("✓ vw_q22_payment_analytics exists")
    print(f"Columns: {col_names}")
    print(f"Sample rows: {len(rows)}")
    if rows:
        print(f"First row: {rows[0]}")
except Exception as e:
    print(f"✗ Error: {e}")

conn.close()
