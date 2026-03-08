# Executive Dashboards - Quick Reference Index

## 📋 Main Documentation Files

### 1. **START HERE** → [EXECUTIVE_DASHBOARDS_DELIVERY_SUMMARY.md](EXECUTIVE_DASHBOARDS_DELIVERY_SUMMARY.md)
- Overview of all 5 dashboards
- What's been delivered
- Quick file reference
- Deployment checklist

### 2. Implementation Guide → [EXECUTIVE_DASHBOARDS_USAGE_GUIDE.md](EXECUTIVE_DASHBOARDS_USAGE_GUIDE.md)
- 5-minute quick start
- Power BI step-by-step setup
- Tableau step-by-step setup
- Data refresh strategy
- Troubleshooting

### 3. Visual Configuration → [DASHBOARD_POWERBI_TABLEAU_MAPPING.md](DASHBOARD_POWERBI_TABLEAU_MAPPING.md)
- Detailed field-by-field mapping
- Visual types (charts, cards, tables)
- Color coding and formatting
- SQL validation queries
- Sample data with expected ranges

---

## 📊 The 5 Dashboards

| # | Name | Purpose | Key Metrics | Users |
|---|------|---------|---|---|
| **Q1** | [Executive Summary](DASHBOARD_POWERBI_TABLEAU_MAPPING.md#question-1-executive-summary-dashboard) | Current KPIs & growth | Revenue, Growth %, Customers, AOV | C-Suite |
| **Q2** | [Real-time Monitor](DASHBOARD_POWERBI_TABLEAU_MAPPING.md#question-2-real-time-business-performance-monitor) | Month-to-date tracking | Run-rate, Targets, Alerts | Operations |
| **Q3** | [Strategic Overview](DASHBOARD_POWERBI_TABLEAU_MAPPING.md#question-3-strategic-overview-dashboard) | Market position | Market Share, Geographic, Health | Strategy |
| **Q4** | [Financial Performance](DASHBOARD_POWERBI_TABLEAU_MAPPING.md#question-4-financial-performance-dashboard) | Profitability & costs | Margins, Cost Structure, Forecasts | Finance |
| **Q5** | [Growth Analytics](DASHBOARD_POWERBI_TABLEAU_MAPPING.md#question-5-growth-analytics-dashboard) | Acquisition & retention | Cohorts, Churn, Portfolio | Product |

---

## 🔧 SQL & Automation

### SQL Views Definition
- **File:** `sql/dashboard_executive_questions_1_5.sql` (647 lines)
- **Contains:** 15 pre-built views (8,294 rows total)
- **Deploy:** Run `scripts/deploy_views_quick.py` or `scripts/deploy_executive_dashboards.py`

### Python Scripts
```
scripts/deploy_views_quick.py                 ← Quick deployment
scripts/deploy_executive_dashboards.py        ← Full deployment with reporting
scripts/validate_dashboard_views.py           ← Health check utility
scripts/refresh_kpis.py                       ← Nightly refresh (auto-scheduled)
```

---

## 🚀 Quick Start (5 Minutes)

### 1. Deploy Views
```bash
cd c:\Users\admin\Desktop\Amazon_India_Sales_Analytics
python scripts/deploy_views_quick.py
```

### 2. Validate  
```bash
python scripts/validate_dashboard_views.py
```

### 3. Import to Power BI
```
Get Data → SQLite Database → AmazonIndia.db → Load all views
```

### 4. Build Dashboard
See [DASHBOARD_POWERBI_TABLEAU_MAPPING.md](DASHBOARD_POWERBI_TABLEAU_MAPPING.md) → Q1 Section

---

## 📁 File Structure

```
c:\Users\admin\Desktop\Amazon_India_Sales_Analytics\
├── EXECUTIVE_DASHBOARDS_DELIVERY_SUMMARY.md  ← DELIVERY SUMMARY
├── EXECUTIVE_DASHBOARDS_USAGE_GUIDE.md       ← HOW-TO GUIDE
├── DASHBOARD_POWERBI_TABLEAU_MAPPING.md      ← FIELD REFERENCE
├── QUICK_REFERENCE_INDEX.md                  ← YOU ARE HERE
├── AmazonIndia.db                             ← SQLite Database
│
├── sql/
│   └── dashboard_executive_questions_1_5.sql ← 15 View Definitions
│
└── scripts/
    ├── deploy_views_quick.py                 ← Deploy Script
    ├── deploy_executive_dashboards.py        ← Full Deploy Script
    ├── validate_dashboard_views.py           ← Validator Script
    └── refresh_kpis.py                       ← Auto-refresh (scheduled)
```

---

## 📊 View Details

### Q1: Executive Summary (3 views, 1,064 rows)
- `vw_q1_executive_summary` - Monthly KPIs
- `vw_q1_top_categories` - Category rankings  
- `vw_q1_growth_rates` - Growth trends

### Q2: Real-time Monitor (3 views, 74 rows)
- `vw_q2_current_performance` - Daily current month
- `vw_q2_run_rate_forecast` - Run-rate projections
- `vw_q2_acquisition_metrics` - CAC metrics

### Q3: Strategic Overview (3 views, 2,252 rows)
- `vw_q3_market_share` - Category share analysis
- `vw_q3_geographic_expansion` - State-level metrics
- `vw_q3_business_health` - Comprehensive scorecard

### Q4: Financial Performance (3 views, 1,064 rows)
- `vw_q4_financial_performance` - Profitability
- `vw_q4_cost_structure` - Cost breakdown
- `vw_q4_financial_forecast` - Forecasts

### Q5: Growth Analytics (4 views, 3,840 rows)
- `vw_q5_customer_cohorts` - Retention heatmap
- `vw_q5_portfolio_expansion` - Growth metrics
- `vw_q5_strategic_initiatives` - Category growth
- `vw_q5_retention_analysis` - Churn metrics

---

## 🔌 Database Connection

**Location:** `C:\Users\admin\Desktop\Amazon_India_Sales_Analytics\AmazonIndia.db`

**Connection String:**
```
sqlite:///C:\Users\admin\Desktop\Amazon_India_Sales_Analytics\AmazonIndia.db
```

**Auto-Refresh:** Daily at 2:00 AM (35 seconds)

---

## 📖 Documentation Map

| Need | File | Section |
|------|------|---------|
| Overview | DELIVERY_SUMMARY.md | Any |
| Quick Start | USAGE_GUIDE.md | Quick Start |
| Power BI Setup | USAGE_GUIDE.md | Power BI Setup |
| Tableau Setup | USAGE_GUIDE.md | Tableau Setup |
| Visual Config | POWERBI_TABLEAU_MAPPING.md | Q1-Q5 Sections |
| Field Details | POWERBI_TABLEAU_MAPPING.md | Data Sources Sections |
| Troubleshooting | USAGE_GUIDE.md | Troubleshooting |
| Best Practices | USAGE_GUIDE.md | Best Practices |
| SQL Reference | sql/dashboard_executive_questions_1_5.sql | Any |

---

## ✓ Deployment Checklist

- [ ] Read [DELIVERY_SUMMARY.md](EXECUTIVE_DASHBOARDS_DELIVERY_SUMMARY.md)
- [ ] Run `python scripts/deploy_views_quick.py`
- [ ] Run `python scripts/validate_dashboard_views.py` (verify all 15 views)
- [ ] Import views into Power BI/Tableau
- [ ] Create Q1 dashboard following mapping guide
- [ ] Test with current month data
- [ ] Configure refresh schedule
- [ ] Build remaining dashboards (Q2-Q5)
- [ ] Train users
- [ ] Publish to organization (optional)

---

## 🆘 Common Issues

| Issue | Solution |
|-------|----------|
| Views not found | Run `deploy_views_quick.py` |
| Database locked | Wait 2 minutes, then retry |
| Slow performance | Use DirectQuery mode in Power BI |
| Missing data | Check nightly refresh logs |
| Connection failed | Verify database path in connection string |

✓ See [USAGE_GUIDE.md](EXECUTIVE_DASHBOARDS_USAGE_GUIDE.md) for detailed troubleshooting

---

## 📞 Support

**Power BI Questions:**
→ [POWERBI_TABLEAU_MAPPING.md](DASHBOARD_POWERBI_TABLEAU_MAPPING.md) Power BI Section

**Tableau Questions:**
→ [POWERBI_TABLEAU_MAPPING.md](DASHBOARD_POWERBI_TABLEAU_MAPPING.md) Tableau Section

**General Questions:**
→ [USAGE_GUIDE.md](EXECUTIVE_DASHBOARDS_USAGE_GUIDE.md) Full guide

**SQL Reference:**
→ [sql/dashboard_executive_questions_1_5.sql](sql/dashboard_executive_questions_1_5.sql)

---

## Status: ✓ READY FOR USE

All 5 executive dashboards are defined, documented, and ready for immediate deployment.

**Next Step:** Read [DELIVERY_SUMMARY.md](EXECUTIVE_DASHBOARDS_DELIVERY_SUMMARY.md) for overview, then [USAGE_GUIDE.md](EXECUTIVE_DASHBOARDS_USAGE_GUIDE.md) for implementation.

---

*Created: 2026-03-02*  
*Questions 1-5 Executive Dashboards*  
*Amazon India Sales Analytics*
