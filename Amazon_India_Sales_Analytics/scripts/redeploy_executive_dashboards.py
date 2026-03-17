import re
import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "AmazonIndia.db"
SQL_DIR = ROOT / "sql"

def find_view_names(sql_text):
    # basic regex to find CREATE VIEW IF NOT EXISTS view_name
    pattern = re.compile(r"CREATE\s+VIEW(?:\s+IF\s+NOT\s+EXISTS)?\s+([a-zA-Z0-9_]+)", re.IGNORECASE)
    return pattern.findall(sql_text)

def drop_views(conn, view_names):
    cur = conn.cursor()
    for v in view_names:
        try:
            cur.execute(f"DROP VIEW IF EXISTS {v}")
        except Exception:
            # ignore individual drop failures
            pass
    conn.commit()

def main():
    sql_files = list((SQL_DIR).glob('*.sql'))
    all_views = []
    for f in sql_files:
        txt = f.read_text(encoding='utf-8')
        all_views += find_view_names(txt)
    all_views = sorted(set(all_views))

    print(f"Dropping {len(all_views)} views from {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    drop_views(conn, all_views)
    conn.close()

    print("Re-running deploy script...")
    subprocess.check_call(["python", "scripts/deploy_executive_dashboards.py"], cwd=str(ROOT))

if __name__ == '__main__':
    main()
