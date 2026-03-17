"""
Amazon India Sales Analytics - KPI Refresh Runner
Purpose: One-click KPI refresh with file + database run logging.
"""

from datetime import datetime
from pathlib import Path
import logging
import sqlite3
import sys
import traceback

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "AmazonIndia.db"
SQL_PACK_PATH = BASE_DIR / "sql" / "dashboard_core_operations.sql"
EXECUTIVE_SQL_PACK_PATH = BASE_DIR / "sql" / "dashboard_executive_views.sql"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / f"kpi_refresh_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def ensure_run_log_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS kpi_refresh_runs (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            status TEXT NOT NULL,
            duration_seconds REAL,
            daily_rows INTEGER,
            monthly_rows INTEGER,
            category_rows INTEGER,
            audit_rows INTEGER,
            error_message TEXT,
            log_file TEXT
        )
        """
    )
    conn.commit()


def create_run(conn: sqlite3.Connection, started_at: str) -> int:
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO kpi_refresh_runs (started_at, status, log_file)
        VALUES (?, 'RUNNING', ?)
        """,
        (started_at, str(LOG_FILE)),
    )
    conn.commit()
    return cursor.lastrowid


def finalize_run_success(
    conn: sqlite3.Connection,
    run_id: int,
    completed_at: str,
    duration_seconds: float,
    daily_rows: int,
    monthly_rows: int,
    category_rows: int,
    audit_rows: int,
) -> None:
    conn.execute(
        """
        UPDATE kpi_refresh_runs
        SET completed_at = ?,
            status = 'SUCCESS',
            duration_seconds = ?,
            daily_rows = ?,
            monthly_rows = ?,
            category_rows = ?,
            audit_rows = ?
        WHERE run_id = ?
        """,
        (
            completed_at,
            duration_seconds,
            daily_rows,
            monthly_rows,
            category_rows,
            audit_rows,
            run_id,
        ),
    )
    conn.commit()


def finalize_run_failed(
    conn: sqlite3.Connection,
    run_id: int,
    completed_at: str,
    duration_seconds: float,
    error_message: str,
) -> None:
    conn.execute(
        """
        UPDATE kpi_refresh_runs
        SET completed_at = ?,
            status = 'FAILED',
            duration_seconds = ?,
            error_message = ?
        WHERE run_id = ?
        """,
        (completed_at, duration_seconds, error_message[:2000], run_id),
    )
    conn.commit()


def get_counts(conn: sqlite3.Connection) -> tuple[int, int, int, int]:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM vw_bi_daily_kpi")
    daily_rows = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM vw_bi_monthly_kpi")
    monthly_rows = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM vw_bi_category_kpi")
    category_rows = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM data_quality_audit")
    audit_rows = cursor.fetchone()[0]

    return daily_rows, monthly_rows, category_rows, audit_rows


def run_refresh() -> int:
    start_dt = datetime.now()
    started_at = start_dt.isoformat(timespec="seconds")

    logger.info("=" * 80)
    logger.info("KPI REFRESH STARTED")
    logger.info(f"Database: {DB_PATH}")
    logger.info(f"SQL pack: {SQL_PACK_PATH}")
    logger.info(f"Executive SQL pack: {EXECUTIVE_SQL_PACK_PATH}")
    logger.info(f"File log: {LOG_FILE}")
    logger.info("=" * 80)

    if not DB_PATH.exists():
        logger.error(f"Database not found: {DB_PATH}")
        return 1

    if not SQL_PACK_PATH.exists():
        logger.error(f"SQL pack not found: {SQL_PACK_PATH}")
        return 1

    conn = sqlite3.connect(str(DB_PATH), timeout=300)
    run_id = None

    try:
        ensure_run_log_table(conn)
        run_id = create_run(conn, started_at)
        logger.info(f"Created run log entry: run_id={run_id}")

        sql_script = SQL_PACK_PATH.read_text(encoding="utf-8")
        conn.executescript(sql_script)

        if EXECUTIVE_SQL_PACK_PATH.exists():
            executive_sql_script = EXECUTIVE_SQL_PACK_PATH.read_text(encoding="utf-8")
            conn.executescript(executive_sql_script)
            logger.info("Applied executive dashboard SQL views")
        else:
            logger.info("Executive SQL pack not found; skipping executive view refresh")

        conn.commit()

        daily_rows, monthly_rows, category_rows, audit_rows = get_counts(conn)

        end_dt = datetime.now()
        completed_at = end_dt.isoformat(timespec="seconds")
        duration_seconds = round((end_dt - start_dt).total_seconds(), 3)

        finalize_run_success(
            conn,
            run_id,
            completed_at,
            duration_seconds,
            daily_rows,
            monthly_rows,
            category_rows,
            audit_rows,
        )

        logger.info("KPI refresh completed successfully")
        logger.info(f"Duration: {duration_seconds}s")
        logger.info(f"vw_bi_daily_kpi rows: {daily_rows:,}")
        logger.info(f"vw_bi_monthly_kpi rows: {monthly_rows:,}")
        logger.info(f"vw_bi_category_kpi rows: {category_rows:,}")
        logger.info(f"data_quality_audit rows: {audit_rows:,}")
        logger.info("=" * 80)
        return 0

    except Exception as ex:
        end_dt = datetime.now()
        completed_at = end_dt.isoformat(timespec="seconds")
        duration_seconds = round((end_dt - start_dt).total_seconds(), 3)

        error_message = f"{str(ex)}\n{traceback.format_exc()}"
        logger.error("KPI refresh failed")
        logger.error(error_message)

        if run_id is not None:
            finalize_run_failed(conn, run_id, completed_at, duration_seconds, str(ex))

        logger.info("=" * 80)
        return 1

    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(run_refresh())
