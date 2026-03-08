# Executive Dashboards - Implementation & Usage Guide

**Project:** Amazon India Sales Analytics  
**Date:** 2026-03-02  
**Dashboard Suite:** 5 Executive Dashboards (Questions 1-5)  
**Status:** SQL Views Created | Ready for Power BI/Tableau Import

---

## Quick Start (5 Minutes)

### Phase 1: Validate Dashboard Views (1 minute)
```bash
cd c:\Users\admin\Desktop\Amazon_India_Sales_Analytics
python scripts/validate_dashboard_views.py
```

Expected Output: ✓ ALL DASHBOARD VIEWS VALIDATED SUCCESSFULLY (15 views)

### Phase 2: Import Views into Power BI (2 minutes)
1. Open Power BI Desktop
2. **Get Data** → **SQLite Database**
3. Server: `C:\Users\admin\Desktop\Amazon_India_Sales_Analytics\AmazonIndia.db`
4. Load button → Select all 15 views (vw_q1_*, vw_q2_*, etc.)
5. Click **Load**

### Phase 3: Build First Dashboard (2 minutes)
1. Reference: [DASHBOARD_POWERBI_TABLEAU_MAPPING.md](DASHBOARD_POWERBI_TABLEAU_MAPPING.md)
2. Start with **Q1: Executive Summary**
3. Create 5 visuals following the field mapping guide
4. Set page-level filters for Year/Month

---

## Dashboard Overview

| # | Name | Purpose | Key Metrics | Users | Refresh |
|---|------|---------|---|---|---|
| **Q1** | Executive Summary Dashboard | Current KPIs & trends | Revenue, Growth, AOV, Top Categories | C-Suite, Management | Daily |
| **Q2** | Real-time Monitor | Month-to-date performance | Run-rate, Targets, Alerts, CAC | Operations, Sales | Real-time |
| **Q3** | Strategic Overview | Market position & health | Market Share, Geographic Reach, Business Health | Strategy, Board | Weekly |
| **Q4** | Financial Performance | Profitability analysis | Margins, Cost Structure, Forecasts | CFO, Finance | Weekly |
| **Q5** | Growth Analytics | Acquisition & retention | Cohorts, Churn, Portfolio Expansion | Product, Growth | Weekly |

---

## Database Connection Details

### SQLite Database Location
```
C:\Users\admin\Desktop\Amazon_India_Sales_Analytics\AmazonIndia.db
```

### Connection String (for automation/scripts)
```
sqlite:///C:\Users\admin\Desktop\Amazon_India_Sales_Analytics\AmazonIndia.db
```

### Available Views (15 total)

**Q1: Executive Summary Dashboard**
- `vw_q1_executive_summary` (132 rows) - Monthly KPIs
- `vw_q1_top_categories` (800 rows) - Category performance
- `vw_q1_growth_rates` (132 rows) - Growth trends

**Q2: Real-time Monitor**
- `vw_q2_current_performance` (31 rows) - Daily current month
- `vw_q2_run_rate_forecast` (31 rows) - Projections
- `vw_q2_acquisition_metrics` (12 rows) - CAC & retention

**Q3: Strategic Overview**
- `vw_q3_market_share` (800 rows) - Category share
- `vw_q3_geographic_expansion` (1,320 rows) - State-level data
- `vw_q3_business_health` (132 rows) - Health scorecard

**Q4: Financial Performance**
- `vw_q4_financial_performance` (800 rows) - Profitability
- `vw_q4_cost_structure` (132 rows) - Cost breakdown
- `vw_q4_financial_forecast` (132 rows) - Forecasts

**Q5: Growth Analytics**
- `vw_q5_customer_cohorts` (2,640 rows) - Cohort retention
- `vw_q5_portfolio_expansion` (132 rows) - Product expansion
- `vw_q5_strategic_initiatives` (800 rows) - Category initiatives
- `vw_q5_retention_analysis` (132 rows) - Churn metrics

**Total: 8,891 rows across 15 views**

---

## Power BI Setup Guide

### Step 1: Create New Report
```
File → New → Blank report
```

### Step 2: Connect to Database
```
Get Data → SQLite Database
  ↓
Browse to: C:\Users\admin\Desktop\Amazon_India_Sales_Analytics\AmazonIndia.db
  ↓
Select all 15 views → Load
```

### Step 3: Model Design (No relationships needed)
- Views are pre-aggregated
- Each view is self-contained
- No foreign key relationships required
- Set data types:
  - `*_inr` fields → Currency (₹ Indian Rupee)
  - `*_pct` fields → Percentage
  - `*_rating` fields → Decimal

### Step 4: Create Dashboard - Q1 Example
**Page Name:** "Executive Summary"

**Visual 1: KPI Card - Total Revenue**
- Values: SUM(total_revenue_inr) / 1,000,000,000
- Format: ₹ #.0,,"B"
- Filters: Year = 2025, Month = 12

**Visual 2: KPI Card - Growth Rate**
- Values: yoy_revenue_growth_pct
- Format: +/#.##%
- Conditional formatting: Green if >0, Red if <0

**Visual 3: KPI Card - Active Customers**
- Values: SUM(active_customers)
- Format: #,##0
- Filters: Year = 2025, Month = 12

**Visual 4: KPI Card - AOV**
- Values: average_order_value_inr
- Format: ₹ #,##0

**Visual 5: Combo Chart - Revenue Trend**
- X-Axis: month_name
- Columns: total_revenue_inr (sorted by month)
- Line: yoy_revenue_growth_pct
- Filters: Year = 2025

**Visual 6: Bar Chart - Top Categories**
- Category: category
- Values: SUM(revenue_inr)
- Sort: Descending
- Limit: Top 5

**Visual 7: Matrix - YoY Comparison**
- Rows: month_name
- Columns: year
- Values: total_revenue_inr

### Step 5: Add Slicers
```
Insert → Slicer → Select field:
  1. Year (from any Q1 view)
  2. Month (from any Q1 view)
  3. Category (from vw_q1_top_categories)
```

### Step 6: Publish to Service (Optional)
```
Publish → Select workspace → Enter credentials
```

---

## Tableau Setup Guide

### Step 1: Connect to Database
```
Tableau Desktop → Connect to data:
  Data Source: SQLite
  File: AmazonIndia.db
```

### Step 2: Import Views
- Tableau will auto-detect all views
- Drag-and-drop views onto canvas
- No joins needed

### Step 3: Create Calculated Fields
Example for Q1:
```
// Revenue in Billions
[Revenue_Billions] = [total_revenue_inr] / 1000000000

// Growth Arrow
[Growth_Trend] = IF [yoy_revenue_growth_pct] > 0 THEN "📈 Growing" ELSEIF [yoy_revenue_growth_pct] < 0 THEN "📉 Declining" ELSE "→ Stable" END
```

### Step 4: Build Sheets
Create separate sheets for each visual:
- Sheet: "KPI Summary" (cards)
- Sheet: "Revenue Trend" (line chart)
- Sheet: "Top Categories" (bar chart)
- etc.

### Step 5: Create Dashboard
```
Dashboard → New Dashboard
Drag sheets into layout
Add filters/parameters as needed
```

### Step 6: Publish to Tableau Server (Optional)
```
File → Publish to Tableau Online
```

---

## Data Refresh Strategy

### Automatic Refresh (Recommended)
**Nightly KPI Refresh Task**
- **Schedule:** Daily at 2:00 AM
- **Duration:** ~35 seconds
- **What's refreshed:** All 15 dashboard views
- **Status:** Check `kpi_refresh_runs` table in database

### Manual Refresh
```bash
# Command line
cd c:\Users\admin\Desktop\Amazon_India_Sales_Analytics
python scripts/refresh_kpis.py

# Output confirms:
# ✓ All KPI tables updated
# ✓ All dashboard views materialized
# ✓ Refresh completed in 35s
```

### Power BI Desktop Refresh
```
Home → Refresh → Refresh All
```

### Tableau Refresh
```
Data → Refresh All or Refresh Data Source
```

### Monitoring Refresh Health
```bash
python -c "
import sqlite3
conn = sqlite3.connect('AmazonIndia.db')
runs = __import__('pandas').read_sql_query(
    'SELECT run_id, started_at, duration_seconds, status FROM kpi_refresh_runs ORDER BY run_id DESC LIMIT 5',
    conn
)
print(runs)
conn.close()
"
```

---

## Dashboard Field Reference

### Common Fields Across Dashboards

| Field | Format | Range | Example | Usage |
|-------|--------|-------|---------|-------|
| `total_revenue_inr` | Currency ₹ | 200M-900M | 504.8B | Revenue totals |
| `yoy_revenue_growth_pct` | Percentage | -50% to +50% | -44.83% | Growth indicators |
| `active_customers` | Number | 5K-30K | 12,456 | Customer counts |
| `average_order_value_inr` | Currency ₹ | 8K-15K | 11,157 | AOV cards |
| `revenue_share_pct` | Percentage | 0-100% | 73.57% | Category share |
| `category_rank` | Number | 1-6 | 1 | Ranking |
| `year`, `month`, `month_name` | - | 2015-2025, 1-12 | 2025, 12, December | Dimensions |

### Aggregation by Question

**Q1: By Month × Year**
- Granularity: 132 rows (12 months × 11 years)
- Use: SUM for revenue/customers, AVG for rating/AOV

**Q2: By Day (Current Month)**
- Granularity: 31 rows (daily for December 2025)
- Use: SUM for cumulative, LAST for latest day

**Q3: By Month × State/Category**
- Granularity: ~2,100 rows
- Use: SUM by geography, GROUP by category

**Q4: By Month × Category**
- Granularity: ~800 rows
- Use: SUM for profitability, DIVIDE for margins

**Q5: By Cohort × Month**
- Granularity: ~2,600 rows
- Use: DIVIDE for retention rates, MOVING AVG for trends

---

## Troubleshooting

### Issue: "View Not Found" Error
**Cause:** Dashboard views not deployed yet  
**Solution:**
```bash
python scripts/deploy_executive_dashboards.py
# Wait for: ✓ Applied {N} views Successfully
```

### Issue: Slow Dashboard Performance
**Cause 1:** Importing all data into memory  
**Solution:** Use DirectQuery mode in Power BI
```
Home → Edit Queries → Source → Advanced Options → 
Set SQL Compatibility Level to SQL Server 2019
```

**Cause 2:** Large view with unnecessary filtering  
**Solution:** Add WHERE filters in SQL view definition
```sql
-- Original: 132 rows
SELECT * FROM vw_q1_executive_summary

-- Optimized: 36 rows (last 3 years)
SELECT * FROM vw_q1_executive_summary WHERE year >= 2023
```

### Issue: Stale Data in Dashboard
**Cause:** Refresh hasn't run yet  
**Solution:**
```bash
# Check last refresh
python -c "import sqlite3; conn=sqlite3.connect('AmazonIndia.db'); print(conn.execute('SELECT completed_at FROM kpi_refresh_runs ORDER BY run_id DESC LIMIT 1').fetchone()); conn.close()"

# Manual refresh
python scripts/refresh_kpis.py
```

### Issue: Database Locked Error
**Cause:** Nightly refresh running while import attempted  
**Solution:** 
- Wait 2 minutes (refresh is ~35 seconds)
- Or schedule imports for 3:00+ AM (after 2:00 AM refresh)

### Issue: Connection Refused / File Not Found
**Cause:** Database path hardcoded incorrectly  
**Solution:** 
- Verify database path in connection string
- Use complete absolute path: `C:\Users\admin\Desktop\Amazon_India_Sales_Analytics\AmazonIndia.db`

---

## Best Practices

### Visual Design
1. ✓ Use consistent color schemes (green=positive, red=negative)
2. ✓ Show YoY/MoM comparisons for growth context
3. ✓ Include sparklines for 12-month trends
4. ✓ Use tooltips for detailed breakdowns
5. ✓ Apply data formatting (₹ for currency, % for rates)

### Performance
1. ✓ Filter by year (typically current + prior year only)
2. ✓ Use DirectQuery for real-time dashboards (Q2)
3. ✓ Import mode for historical analysis (Q1, Q3, Q4, Q5)
4. ✓ Limit visuals per page (~6-8 on 1920×1080)
5. ✓ Pre-aggregate in views (already done)

### Data Accuracy
1. ✓ Validate monthly view totals against source facts
2. ✓ Check for NULL values in expected fields
3. ✓ Verify YoY calculation only includes complete months
4. ✓ Test growth rate calculations with sample dates
5. ✓ Run manual data audit monthly

### Security
1. ✓ Store database credentials in Power BI Data Gateway
2. ✓ Use Row-Level Security (RLS) for sensitive data
3. ✓ Publish dashboards to authorized workspaces only
4. ✓ Audit access logs in Tableau/Power BI Server
5. ✓ Encrypt database if shared across teams

---

## SQL View Deployment (If Needed)

The dashboard views should already be configured in your database. If you need to reapply them:

```bash
cd c:\Users\admin\Desktop\Amazon_India_Sales_Analytics

# Method 1: Using deployment script
python scripts/deploy_executive_dashboards.py

# Method 2: Manual SQL execution
python << 'SQL'
import sqlite3
sql_content = open('sql/dashboard_executive_questions_1_5.sql').read()
conn = sqlite3.connect('AmazonIndia.db')
conn.executescript(sql_content)
conn.commit()
conn.close()
print('Views deployed successfully')
SQL
```

---

## Key Contacts & Resources

**Documentation:**
- [DASHBOARD_POWERBI_TABLEAU_MAPPING.md](DASHBOARD_POWERBI_TABLEAU_MAPPING.md) - Complete field mapping
- [sql/dashboard_executive_questions_1_5.sql](sql/dashboard_executive_questions_1_5.sql) - SQL view definitions
- [scripts/validate_dashboard_views.py](scripts/validate_dashboard_views.py) - Validation utility

**Scripts:**
- `refresh_kpis.py` - Nightly refresh automation
- `validate_dashboard_views.py` - Health check utility
- `deploy_executive_dashboards.py` - View deployment

**Automation:**
- Task Scheduler: `AmazonIndia_KPI_Refresh_Nightly`  
- Time: Daily at 2:00 AM
- Duration: ~35 seconds

---

## Dashboard Checklist

### Pre-Launch Checklist
- [ ] All 15 views validated (`validate_dashboard_views.py`)
- [ ] Database connection tested in Power BI/Tableau
- [ ] Sample visuals created and formatted
- [ ] Slicers configured (Year, Month, Category)
- [ ] Data formatting applied (currency, percentages)
- [ ] Tooltips configured for detail drill-throughs
- [ ] Color schemes aligned with company branding
- [ ] Performance tested with full data load

### Post-Launch Checklist
- [ ] Dashboards published to team/organization
- [ ] Access permissions granted to end users
- [ ] Users trained on filter/slicer usage
- [ ] Refresh schedule verified nightly
- [ ] Alert rules configured in Power BI/Tableau
- [ ] Monthly audit of data accuracy
- [ ] Feedback collected from users
- [ ] Updates scheduled based on feedback

---

## Next Steps

1. **Immediate (Today):**
   - Run validator: `python scripts/validate_dashboard_views.py`
   - Import views into Power BI/Tableau
   - Create Q1 Executive Summary

2. **This Week:**
   - Build all 5 dashboards
   - Test with current month data (Dec 2025)
   - Configure auto-refresh

3. **Next Week:**
   - User training
   - Publish to Power BI/Tableau Server
   - Set up alerts & monitoring

4. **Ongoing:**
   - Weekly review of metrics
   - Monthly data audit
   - Quarterly dashboard enhancements

---

**Questions or Issues?**  
Contact the Analytics team or refer to the troubleshooting section above.

**Last Updated:** 2026-03-02  
**Next Review:** 2026-04-02
