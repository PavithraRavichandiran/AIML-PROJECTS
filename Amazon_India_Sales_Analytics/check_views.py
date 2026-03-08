import sqlite3

db_path = "AmazonIndia.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check views
cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name;")
views = cursor.fetchall()
print(f"Total views found: {len(views)}\n")
print("Views:")
for view in views:
    print(f"  - {view[0]}")

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()
print(f"\nTotal tables found: {len(tables)}\n")
print("Tables:")
for table in tables:
    print(f"  - {table[0]}")

conn.close()
