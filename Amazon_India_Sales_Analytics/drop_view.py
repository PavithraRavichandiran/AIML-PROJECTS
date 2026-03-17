import sqlite3

db_path = "AmazonIndia.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Drop the problematic view
try:
    cursor.execute("DROP VIEW IF EXISTS vw_q22_payment_analytics;")
    conn.commit()
    print("✓ Dropped vw_q22_payment_analytics")
except Exception as e:
    print(f"Error dropping view: {e}")

conn.close()
