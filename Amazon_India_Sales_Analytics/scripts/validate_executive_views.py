import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "AmazonIndia.db"


def main() -> None:
    conn = sqlite3.connect(str(DB_PATH))

    views = [
        "vw_exec_monthly_overview",
        "vw_exec_prime_split",
        "vw_exec_payment_mix",
        "vw_exec_category_share",
        "vw_exec_festival_impact",
    ]

    print("Executive view counts:")
    for view_name in views:
        count = conn.execute(f"SELECT COUNT(1) FROM {view_name}").fetchone()[0]
        print(f"  {view_name}: {count:,}")

    print("\nLatest overview sample:")
    rows = conn.execute(
        """
        SELECT year, month, revenue_inr, mom_revenue_growth_pct, yoy_revenue_growth_pct
        FROM vw_exec_monthly_overview
        ORDER BY year DESC, month DESC
        LIMIT 3
        """
    ).fetchall()

    for row in rows:
        print(row)

    conn.close()


if __name__ == "__main__":
    main()
