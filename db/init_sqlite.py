import sqlite3

DB_PATH = "db/cricbuzz.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS players (
        player_id INTEGER PRIMARY KEY,
        name TEXT,
        country TEXT,
        role TEXT,
        batting_style TEXT,
        bowling_style TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        match_id INTEGER PRIMARY KEY,
        series_name TEXT,
        match_desc TEXT,
        match_format TEXT,
        team1 TEXT,
        team2 TEXT,
        venue_ground TEXT,
        venue_city TEXT,
        status TEXT,
        start_date INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS scorecards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        innings_id INTEGER,
        bat_team TEXT,
        runs INTEGER,
        wickets INTEGER,
        overs REAL,
        runrate REAL,
        FOREIGN KEY (match_id) REFERENCES matches(match_id)
    )
    """)

    # No seed data - use API to import real players

    conn.commit()
    conn.close()
    print("SQLite DB initialized at", DB_PATH)

def clear_all_data():
    """Clear all data from database tables"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("DELETE FROM scorecards")
    cur.execute("DELETE FROM matches")
    cur.execute("DELETE FROM players")
    
    conn.commit()
    conn.close()
    print("All data cleared from database")

if __name__ == "__main__":
    main()
