import sqlite3
import pandas as pd

DB_PATH = "db/cricbuzz.db"

def run_query(sql: str):
    conn = sqlite3.connect(DB_PATH)
    try:
        return pd.read_sql_query(sql, conn)
    finally:
        conn.close()
