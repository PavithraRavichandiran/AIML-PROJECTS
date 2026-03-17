"""
BI Connection Setup Helper for Amazon India Sales Analytics
Purpose: Validate BI-facing views and print ready-to-use connection info.
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / 'AmazonIndia.db'


def main():
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    checks = {
        'vw_bi_daily_kpi': 'SELECT COUNT(*) FROM vw_bi_daily_kpi',
        'vw_bi_monthly_kpi': 'SELECT COUNT(*) FROM vw_bi_monthly_kpi',
        'vw_bi_category_kpi': 'SELECT COUNT(*) FROM vw_bi_category_kpi',
        'vw_fact_sales_enriched': 'SELECT COUNT(*) FROM vw_fact_sales_enriched',
        'data_quality_audit': 'SELECT COUNT(*) FROM data_quality_audit'
    }

    print('\n' + '=' * 80)
    print('BI LAYER VALIDATION')
    print('=' * 80)

    for name, query in checks.items():
        cur.execute(query)
        count = cur.fetchone()[0]
        print(f'{name:25s} -> {count:,} rows')

    print('\n' + '=' * 80)
    print('CONNECTION SETUP (Visualization Tools)')
    print('=' * 80)
    print(f'SQLite database file: {DB_PATH}')
    print('\nPower BI Desktop:')
    print('  Get Data -> SQLite database -> select AmazonIndia.db')
    print('  Import these views: vw_bi_daily_kpi, vw_bi_monthly_kpi, vw_bi_category_kpi, vw_fact_sales_enriched')

    print('\nTableau:')
    print('  Connect -> To a Server -> SQLite -> select AmazonIndia.db')
    print('  Use views prefixed with vw_bi_ for dashboard visuals')

    print('\nMetabase/Superset (via SQLite connector):')
    print('  Point connection to AmazonIndia.db')
    print('  Use vw_bi_monthly_kpi as primary KPI model')

    print('\nRecommended default visuals:')
    print('  1) Revenue trend by year-month (vw_bi_monthly_kpi)')
    print('  2) Category contribution waterfall (vw_bi_category_kpi)')
    print('  3) Prime vs non-prime revenue split (vw_fact_sales_enriched)')

    conn.close()


if __name__ == '__main__':
    main()
