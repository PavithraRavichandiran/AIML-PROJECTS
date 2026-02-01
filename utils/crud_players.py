import pandas as pd
import sqlite3

DB_PATH = "db/cricbuzz.db"

def get_next_player_id() -> int:
    """Get the next available player ID"""
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("SELECT MAX(player_id) FROM players")
        max_id = cur.fetchone()[0]
        return (max_id or 0) + 1
    finally:
        conn.close()

def fetch_players(search: str = "") -> pd.DataFrame:
    """Fetch players with optional search filter"""
    sql = """
    SELECT player_id, name, country, role, batting_style, bowling_style
    FROM players
    """
    params = ()
    if search.strip():
        sql += " WHERE name LIKE ? OR country LIKE ? OR role LIKE ?"
        like = f"%{search.strip()}%"
        params = (like, like, like)
    sql += " ORDER BY name;"
    
    conn = sqlite3.connect(DB_PATH)
    try:
        return pd.read_sql_query(sql, conn, params=params)
    finally:
        conn.close()

def create_player(player_id: int, name: str, country: str, role: str, batting_style: str, bowling_style: str):
    """Create a new player"""
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO players (player_id, name, country, role, batting_style, bowling_style)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (player_id, name, country, role, batting_style, bowling_style))
        conn.commit()
    finally:
        conn.close()

def update_player(player_id: int, name: str, country: str, role: str, batting_style: str, bowling_style: str):
    """Update an existing player"""
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE players
            SET name = ?, country = ?, role = ?, batting_style = ?, bowling_style = ?
            WHERE player_id = ?
        """, (name, country, role, batting_style, bowling_style, player_id))
        conn.commit()
    finally:
        conn.close()

def delete_player(player_id: int):
    """Delete a player"""
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM players WHERE player_id = ?", (player_id,))
        conn.commit()
    finally:
        conn.close()
