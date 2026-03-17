#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Quick SQL view deployment script"""
import sqlite3
import pathlib

sql_file = pathlib.Path("sql/dashboard_executive_questions_1_5.sql")
if not sql_file.exists():
    print("ERROR: SQL file not found")
    exit(1)

sql_content = sql_file.read_text(encoding='utf-8')
conn = sqlite3.connect("AmazonIndia.db", timeout=120, isolation_level=None)
cursor = conn.cursor()

print("Executing SQL views...")

# Use executescript which properly handles multi-line statements
try:
    cursor.executescript(sql_content)
    conn.commit()
    print("SQL script executed successfully!")
except Exception as e:
    print(f"Error: {str(e)[:100]}")
    conn.rollback()

conn.commit()
views = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='view' AND name LIKE 'vw_q%'").fetchone()[0]
print(f"\nOK: {views} vw_q* views now in database")
conn.close()
