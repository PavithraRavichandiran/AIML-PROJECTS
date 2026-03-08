# Executive Dashboard Configuration Guide: Power BI / Tableau
## Questions 1-5: Complete Field Mapping for Dashboard Development

**Date:** 2026-03-02  
**Database:** AmazonIndia.db (SQLite)  
**Target Tools:** Power BI Desktop, Tableau Desktop, Metabase  

---

## DASHBOARD OVERVIEW

| Question | Dashboard Name | Purpose | Key Users | Update Frequency |
|----------|---|---|---|---|
| **Q1** | Executive Summary Dashboard | KPIs, growth trends, category performance | C-Suite, Management | Daily |
| **Q2** | Real-time Business Performance Monitor | Current month tracking, targets, alerts | Operations Team | Real-time |
| **Q3** | Strategic Overview Dashboard | Market share, geographic expansion, health scores | Strategy, Finance | Weekly |
| **Q4** | Financial Performance Dashboard | Profitability, cost structure, forecasting | CFO, Finance Team | Weekly |
| **Q5** | Growth Analytics Dashboard | Customer cohorts, portfolio expansion, retention | Product, Growth Teams | Weekly |

---

# QUESTION 1: EXECUTIVE SUMMARY DASHBOARD

## Purpose
Display comprehensive KPIs with year-over-year comparisons and trend indicators.

## Data Sources

### Primary View: `vw_q1_executive_summary`
**Granularity:** Monthly × Years (132 rows total)

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `year` | Integer | Year dimension | 2025 |
| `month` | Integer | Month (1-12) | 12 |
| `month_name` | Text | Month display | December |
| `total_orders` | Integer | Number of orders | 45,230 |
| `active_customers` | Integer | Unique customers | 12,456 |
| `total_units_sold` | Integer | Number of units | 89,150 |
| `total_revenue_inr` | Decimal | Revenue in INR | 504,839,057.06 |
| `average_order_value_inr` | Decimal | AOV | 11,157.42 |
| `average_customer_value_inr` | Decimal | ACV | 40,542.31 |
| `prev_year_revenue_inr` | Decimal | Prior year revenue | 912,345,678.90 |
| `yoy_revenue_growth_pct` | Decimal | Year-over-year % | -44.83 |
| `avg_product_rating` | Decimal | Average rating | 4.2 |
| `digital_payment_penetration_pct` | Decimal | Digital % | 68.5 |
| `prime_revenue_mix_pct` | Decimal | Prime % of revenue | 42.3 |

### Supporting View: `vw_q1_top_categories`
**Granularity:** Monthly × Category × Subcategory (132 months × ~6 categories)

| Field | Type | Purpose |
|-------|------|---------|
| `year`, `month`, `month_name` | - | Time dimensions |
| `category`, `subcategory` | Text | Product categories |
| `orders` | Integer | Category orders |
| `customers` | Integer | Category customers |
| `revenue_inr` | Decimal | Category revenue |
| `revenue_share_pct` | Decimal | % of monthly revenue |
| `avg_order_value_inr` | Decimal | Category AOV |
| `rank_in_month` | Integer | 1=top, 2=second, etc. |

### Supporting View: `vw_q1_growth_rates`
**Granularity:** Monthly growth metrics

| Field | Type | Purpose |
|-------|------|---------|
| `mom_growth_pct` | Decimal | Month-over-month growth % |
| `qoq_growth_pct` | Decimal | Quarter-over-quarter growth % |
| `yoy_growth_pct` | Decimal | Year-over-year growth % |

---

## Dashboard Visuals Configuration

### Visual 1: KPI Cards (Top Section)
**Type:** Four separate KPI Tile cards

| Card | Source Field | Format | Target | Sparkline |
|------|---|---|---|---|
| Total Revenue | `total_revenue_inr` | ₹#,##0.0,, (Billions) | Current month | 12-month trend |
| Growth Rate | `yoy_revenue_growth_pct` | +/#.##% | YoY % | Monthly growth line |
| Active Customers | `active_customers` | #,##0 | Current month | 12-month trend |
| Average Order Value | `average_order_value_inr` | ₹#,##0 | Current month | 12-month trend |

**Filters:**
- Slicer: Year (2015-2025)
- Slicer: Month (Jan-Dec) - default to current

---

### Visual 2: Revenue Trend with Growth Rate
**Type:** Combo Chart (Line + Column)

| Axis/Field | Configuration |
|---|---|
| **X-Axis** | `month_name` (sorted by calendar) |
| **Column Values** | `total_revenue_inr` (scaled to billions) |
| **Line Values** | `yoy_revenue_growth_pct` |
| **Color Coding** | Green if YoY > 0, Red if < 0 |
| **Year Filter** | Slicer to select specific year |

**Interactions:**
- Clicking a month updates detail visuals below

---

### Visual 3: Top 5 Categories by Revenue
**Type:** Horizontal Bar Chart

| Field | Configuration |
|---|---|
| **Category** | `category` (from `vw_q1_top_categories`) |
| **Values** | `revenue_inr` (formatted as billions) |
| **Sort** | Descending by revenue |
| **Limit** | Top 5 per month |
| **Filter** | `rank_in_month <= 5` |

**Tooltip:**
- Category name
- Revenue amount
- Customer count
- Avg order value
- Revenue share %

---

### Visual 4: YoY Comparison Matrix
**Type:** Table/Matrix

| Rows | Columns | Values |
|------|---------|--------|
| `month_name` | Year (2024, 2025) | `total_revenue_inr` |
| | | `yoy_revenue_growth_pct` |

**Conditional Formatting:**
- Green background if growth > 0
- Red background if growth < 0
- Data bars for visual comparison

---

### Visual 5: Key Metrics Gauge
**Type:** Gauge Chart (Optional)

| Metric | Min | Target | Max |
|--------|-----|--------|-----|
| Prime Revenue Mix % | 0 | 50 | 100 |
| Digital Payment % | 0 | 75 | 100 |
| Avg Product Rating | 0 | 4.0 | 5.0 |

---

## SQL Queries for Initial Data Check

```sql
-- Verify view exists and has data
SELECT COUNT(*) FROM vw_q1_executive_summary;
-- Expected: 132 rows (12 months × 11 years)

-- Sample data
SELECT year, month, month_name, total_revenue_inr, yoy_revenue_growth_pct
FROM vw_q1_executive_summary
ORDER BY year DESC, month DESC
LIMIT 12;

-- Check top categories
SELECT year, month, category, revenue_inr, rank_in_month
FROM vw_q1_top_categories
WHERE rank_in_month <= 5
ORDER BY year DESC, month DESC, rank_in_month;
```

---

---

# QUESTION 2: REAL-TIME BUSINESS PERFORMANCE MONITOR

## Purpose
Track current month performance against targets with run-rate projections and alerts.

## Data Sources

### Primary View: `vw_q2_current_performance`
**Granularity:** Daily metrics for current month (December 2025)

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `year`, `month`, `month_name` | - | Time dimensions | 2025, 12, December |
| `day_of_month` | Integer | Day 1-31 | 15 |
| `daily_orders` | Integer | Orders received | 1,456 |
| `daily_customers` | Integer | Customers | 412 |
| `daily_revenue_inr` | Decimal | Daily revenue | 16,250,000 |
| `daily_aov_inr` | Decimal | Daily AOV | 11,164 |
| `cumulative_orders` | Integer | Month-to-date | 21,840 |
| `cumulative_revenue_inr` | Decimal | Month-to-date revenue | 243,750,000 |
| `target_daily_orders` | Integer | Daily target | 1,500 |
| `daily_target_achievement_pct` | Decimal | Achievement % | 97.1 |
| `performance_alert` | Text | CRITICAL/WARNING/ON_TRACK | ON_TRACK |

### Supporting View: `vw_q2_run_rate_forecast`
**Granularity:** Daily run-rate projections

| Field | Type | Purpose |
|-------|------|---------|
| `day_of_month` | Integer | Day number |
| `daily_revenue_inr` | Decimal | Actual daily revenue |
| `run_rate_monthly_revenue_inr` | Decimal | Projected full-month (extrapolated) |
| `run_rate_monthly_orders` | Integer | Projected full-month orders |
| `rolling_7day_avg_revenue` | Decimal | 7-day moving average |

### Supporting View: `vw_q2_acquisition_metrics`
**Granularity:** Monthly customer acquisition

| Field | Type | Purpose |
|-------|------|---------|
| `new_customers` | Integer | New customers acquired |
| `active_customers` | Integer | Total active |
| `customer_acquisition_value_inr` | Decimal | Revenue per new customer |
| `cac_equivalent_inr` | Decimal | Estimated CAC |
| `retention_ratio` | Decimal | Active / New ratio |

---

## Dashboard Visuals Configuration

### Visual 1: Performance vs Target - Big Number
**Type:** KPI Tiles (Actual vs Target)

| KPI | Source | Target Access | Alert Threshold |
|-----|--------|---|---|
| Daily Orders | `daily_orders` (latest) | `target_daily_orders` | > 20% below |
| Daily Revenue | `daily_revenue_inr` (latest) | Calculated from daily avg | > 20% below |
| Days to Target | Calculated | Days remaining in month | Show if at risk |

**Alert Logic:**
```
IF daily_target_achievement_pct < 80% THEN "CRITICAL RED"
ELSE IF daily_target_achievement_pct < 95% THEN "YELLOW WARNING"
ELSE "GREEN ON_TRACK"
```

---

### Visual 2: Month-to-Date Progress Chart
**Type:** Combination Chart

| Axis | Field | Format |
|------|-------|--------|
| **X-Axis** | `day_of_month` (1-31) | Day numbers |
| **Line 1** | `cumulative_revenue_inr` | Actual cumulative |
| **Line 2** | Target cumulative | Calculated (target daily × day) |
| **Area Fill** | Variance | Green (ahead) or red (behind) |

**Interaction:**
- Hovering on day shows daily breakdown
- Target line shows "on pace" projection

---

### Visual 3: Run-Rate Forecast Gauge
**Type:** Gauge + Indicator

| Metric | Current | Projected | Target | Status |
|--------|---------|-----------|--------|--------|
| Monthly Revenue | Cum. actual | Run-rate projection | Monthly target | Color coded |
| Total Orders | Cum. actual | Run-rate projection | Monthly target | Color coded |

**Logic:**
- If run-rate projects 90%+ of target = Green
- If run-rate projects 75-89% = Yellow
- If run-rate projects <75% = Red

---

### Visual 4: Daily Achievement Heatmap
**Type:** Heatmap / Matrix

| Rows | Columns | Values |
|------|---------|--------|
| `week_of_month` (Week 1, 2, 3, 4) | `day_name` (Mon-Sun) | `daily_target_achievement_pct` |

**Conditional Formatting:**
- Dark green: 100%+ achievement
- Light green: 80-100%
- Yellow: 60-80%
- Red: < 60%

---

### Visual 5: Customer Acquisition Metrics
**Type:** KPI Summary

| Metric | Source | Format | Trend |
|--------|--------|--------|-------|
| New Customers | `new_customers` | #,##0 | Sparkline |
| CAC Value | `cac_equivalent_inr` | ₹#,##0 | Sparkline |
| Retention Ratio | `retention_ratio` | #.##x | Trend color |

---

## Alert Setup (Power BI Premium / Tableau Data-Driven Alerts)

| Alert Name | Condition | Notification |
|---|---|---|
| Critical Performance Drop | daily_target_achievement_pct < 80 | Immediate |
| Revenue Below Forecast | daily_revenue_inr < run_rate × 0.9 | Hourly |
| Customer Acquisition Decline | new_customers < 30-day avg × 0.8 | Daily |

---

---

# QUESTION 3: STRATEGIC OVERVIEW DASHBOARD

##Purpose
High-level view of market position, geographic reach, and business health.

## Data Sources

### Primary View: `vw_q3_market_share`
**Granularity:** Monthly × Category

| Field | Type | Purpose |
|-------|------|---------|
| `year`, `month`, `month_name` | - | Time |
| `category` | Text | Product category |
| `category_revenue_inr` | Decimal | Category revenue |
| `category_orders` | Integer | Category orders |
| `category_customers` | Integer | Category customers |
| `market_share_pct` | Decimal | % of total revenue |
| `category_rank` | Integer | Rank in month (1 = top) |
| `yoy_market_share_change_pct` | Decimal | Share change YoY |

### View: `vw_q3_geographic_expansion`
**Granularity:** Monthly × State

| Field | Type | Purpose |
|-------|------|---------|
| `state` | Text | Customer state |
| `customers`, `orders` | Integer | State-level metrics |
| `revenue_inr` | Decimal | State revenue |
| `prime_penetration_pct` | Decimal | Prime % in state |
| `state_revenue_rank` | Integer | 1 = top state |
| `state_revenue_share_pct` | Decimal | % of national revenue |

### View: `vw_q3_business_health`
**Granularity:** Monthly overall health scorecard

| Field | Type | Purpose |
|-------|------|---------|
| `total_revenue_inr` | Decimal | Monthly revenue |
| `customer_growth_mom_pct` | Decimal | MoM customer growth |
| `active_products` | Integer | Active SKUs |
| `avg_product_rating` | Decimal | Avg rating (0-5) |
| `high_quality_rating_pct` | Decimal | % rated 4+ |
| `order_growth_mom_pct` | Decimal | MoM order growth |
| `digital_payment_pct` | Decimal | Digital payment % |
| `prime_revenue_mix_pct` | Decimal | Prime revenue % |

---

## Dashboard Visuals Configuration

### Visual 1: Market Share Distribution
**Type:** Pie or Donut Chart

| Configuration | Value |
|---|---|
| **Category/Slice** | `category` |
| **Values** | `market_share_pct` |
| **Sort** | Descending |
| **Limit** | Show top 6, group rest as "Other" |

**Tooltip:**
- Category name
- Revenue amount
- Revenue share %
- YoY change

---

### Visual 2: Category Performance Trend
**Type:** Multi-line Chart

| Configuration | Value |
|---|---|
| **X-Axis** | `month_name` |
| **Lines** | One per top category's `market_share_pct` |
| **Filter** | Top 5 categories by current revenue |
| **Period** | Last 24 months |

**Analysis:**
- Crossing lines = market share shifts
- Uptrend = category gaining share
- Downtrend = category losing share

---

### Visual 3: Geographic Heatmap
**Type:** Map or Table Heatmap

| Element | Configuration |
|---|---|
| **Geographic Level** | Indian states (can use map visual) |
| **Color Intensity** | `state_revenue_rank` (darker = higher rank) |
| **Alt Format** | Table sorted by `state_revenue_share_pct` |
| **Size/Marker** | `prime_penetration_pct` (larger = more Prime) |

**Top Left Table:**  
Top 10 states by revenue with Prime penetration

---

### Visual 4: Business Health Scorecard
**Type:** Card/Gauge Matrix

| Metric | Current | Status | Trend |
|--------|---------|--------|-------|
| Revenue | `total_revenue_inr` | Green/Yellow/Red | MoM arrow |
| Customer Growth | `customer_growth_mom_pct` | Green/Yellow/Red | Sparkline |
| Quality Rating | `avg_product_rating` | 0-5 stars | △▽ arrow |
| Digital Payment % | `digital_payment_pct` | 0-100% | Sparkline |
| Prime Mix | `prime_revenue_mix_pct` | 0-100% | Sparkline |

**Thresholds:**
- Revenue: Above budget = Green
- Growth: >5% = Green, 0-5% = Yellow, <0% = Red
- Rating: >4.0 = Green, 3.5-4.0 = Yellow, <3.5 = Red

---

### Visual 5: YoY Market Share Change
**Type:** Bar Chart (Horizontal)

| Configuration | Value |
|---|---|
| **Categories** | `category` |
| **Values** | `yoy_market_share_change_pct` |
| **Color** | Green if positive, Red if negative |
| **Sort** | By change (largest change first) |

**Analysis:**
- Positive bars = gaining share
- Negative bars = losing share
- Relative height = magnitude of change

---

---

# QUESTION 4: FINANCIAL PERFORMANCE DASHBOARD

## Purpose
Deep dive into profitability, cost structure, and financial forecasting.

## Data Sources

### Primary View: `vw_q4_financial_performance`
**Granularity:** Monthly × Category × Sub category

| Field | Type | Purpose |
|-------|------|---------|
| `year`, `month`, `month_name` | | Time |
| `category`, `subcategory` | Text | Product categorization |
| `orders`, `customers` | Integer | Volume metrics |
| `revenue_inr` | Decimal | Total revenue |
| `estimated_cogs_inr` | Decimal | COGS (50% of revenue) |
| `estimated_operating_cost_inr` | Decimal | OpEx (15% of revenue) |
| `estimated_gross_profit_inr` | Decimal | Revenue - COGS - OpEx |
| `gross_margin_pct` | Decimal | (Revenue - COGS) / Revenue × 100 |
| `net_margin_pct` | Decimal | (Revenue - COGS - OpEx) / Revenue × 100 |
| `revenue_per_order_inr` | Decimal | Revenue / Orders |

### View: `vw_q4_cost_structure`
**Granularity:** Monthly cost breakdown

| Field | Type | Purpose |
|-------|------|---------|
| `total_revenue_inr` | Decimal | Total revenue |
| `cogs_estimate_inr`, `cogs_pct_of_revenue` | | 50% |
| `operating_expense_estimate_inr`, `operating_pct_of_revenue` | | 15% |
| `marketing_estimate_inr`, `marketing_pct_of_revenue` | | 10% |
| `logistics_estimate_inr`, `logistics_pct_of_revenue` | | 8% |
| `tech_infrastructure_estimate_inr`, `tech_pct_of_revenue` | | 5% |
| `gross_profit_estimate_inr`, `gross_profit_pct_of_revenue` | | 12% |

### View: `vw_q4_financial_forecast`
**Granularity:** Monthly forecast vs actual

| Field | Type | Purpose |
|-------|------|---------|
| `month_sequence` | Integer | Sequential month number |
| `actual_revenue_inr` | Decimal | Actual revenue |
| `forecast_revenue_inr` | Decimal | Linear regression forecast |
| `variance_inr`, `variance_pct` | Decimal | Actual - Forecast |

---

## Dashboard Visuals Configuration

### Visual 1: Profitability Waterfall
**Type:** Waterfall Chart

| Step | Source | Format |
|------|--------|--------|
| 1. Revenue | `revenue_inr` | ₹ amount |
| 2. Less: COGS | `-estimated_cogs_inr` | Red/down |
| 3. = Gross Profit | `revenue_inr - estimated_cogs_inr` | Green |
| 4. Less: OpEx | `-estimated_operating_cost_inr` | Red |
| 5. = Net Profit | `estimated_gross_profit_inr` | Green |

**Period:** Latest month, with YoY comparison

---

### Visual 2: Cost Structure Pie
**Type:** Pie/Donut Chart

| Slice | Source | Color |
|-------|--------|-------|
| COGS | `cogs_pct_of_revenue` (50%) | Brown |
| Operating | `operating_pct_of_revenue` (15%) | Red |
| Marketing | `marketing_pct_of_revenue` (10%) | Orange |
| Logistics | `logistics_pct_of_revenue` (8%) | Yellow |
| Tech | `tech_pct_of_revenue` (5%) | Blue |
| Gross Profit | `gross_profit_pct_of_revenue` (12%) | Green |

**Tooltip:** Actual INR amounts + %

---

### Visual 3: Margin Trends by Category
**Type:** Line Chart

| Configuration | Value |
|---|---|
| **X-Axis** | `month_name` (12 months) |
| **Lines** | One per top category's `net_margin_pct` |
| **Filter** | Top 5 categories by revenue |
| **Target Line** | 12% (company target) |

**Analysis:**
- Lines above target = healthy categories
- Downtrend = margin pressure
- Uptrend = improving efficiency

---

### Visual 4: Profitability by Category Matrix
**Type:** Table/Matrix

| Rows | Columns | Values |
|------|---------|--------|
| `category` | `gross_margin_pct`, `net_margin_pct` | Percentage |

**Conditional Formatting:**
- >15% = Dark green
- 12-15% = Light green
- 10-12% = Yellow
- <10% = Red

**Sorting:** By net_margin descending

---

### Visual 5: Forecast vs Actual Accuracy
**Type:** Area Chart + Line

| Configuration | Value |
|---|---|
| **X-Axis** | `month_sequence` past 24 months |
| **Area** | `actual_revenue_inr` |
| **Line** | `forecast_revenue_inr` |
| **Fill Color** | Green if actual > forecast, red if below |

**Metrics Panel:**
- Average variance %
- MAPE (Mean Absolute Percentage Error)
- Forecast accuracy %

---

---

# QUESTION 5: GROWTH ANALYTICS DASHBOARD

## Purpose
Track customer acquisition, retention, and product portfolio expansion with predictive insights.

## Data Sources

### Primary View: `vw_q5_customer_cohorts`
**Granularity:** Cohort (acquisition month) × Observation month

| Field | Type | Purpose |
|-------|------|---------|
| `cohort_year`, `cohort_month`, `cohort_month_name` | | Customer acquisition cohort |
| `observation_year`, `observation_month` | | When we're observing |
| `cohort_size` | Integer | Customers in cohort |
| `active_in_period` | Integer | Active customers this month |
| `retention_rate_pct` | Decimal | Active / Cohort size × 100 |
| `revenue_inr` | Decimal | Cohort revenue |
| `months_since_cohort` | Integer | Age of cohort |

### View: `vw_q5_portfolio_expansion`
**Granularity:** Monthly portfolio metrics

| Field | Type | Purpose |
|-------|------|---------|
| `total_customers` | Integer | Total active customers |
| `active_products` | Integer | Active SKUs |
| `active_categories`, `active_subcategories` | Integer | Product variety |
| `customer_growth_mom_pct`, `customer_growth_yoy_pct` | Decimal | Growth rates |
| `product_growth_mom_pct` | Decimal | Product growth |
| `avg_product_rating` | Decimal | Quality metric |

### View: `vw_q5_strategic_initiatives`
**Granularity:** Category-level strategic performance

| Field | Type | Purpose |
|-------|------|---------|
| `category` | Text | Category being tracked |
| `revenue_inr`, `revenue_share_pct` | Decimal | Category performance |
| `prime_revenue_inr`, `prime_penetration_pct` | Decimal | Prime adoption |
| `category_mom_growth_pct`, `category_yoy_growth_pct` | Decimal | Growth metrics |
| `category_rank` | Integer | Rank in period |

### View: `vw_q5_retention_analysis`
**Granularity:** Monthly cohort health

| Field | Type | Purpose |
|-------|------|---------|
| `active_customers` | Integer | Customers active this month |
| `retained_customers` | Integer | Customers from prior month |
| `new_customers` | Integer | New this month |
| `churned_customers` | Integer | Left since prior month |
| `retention_rate_pct` | Decimal | Retained / Prior period |
| `churn_rate_pct` | Decimal | Churned / Prior period |

---

## Dashboard Visuals Configuration

### Visual 1: Cohort Retention Heatmap
**Type:** Matrix/Heatmap

| Rows | Columns | Values |
|------|---------|--------|
| `cohort_month_name` (2015 Jan - 2025 Dec) | `months_since_cohort` (0-24 months) | `retention_rate_pct` (0-100%) |

**Conditional Formatting:**
- Dark green: 80%+ retention
- Light green: 60-80%
- Yellow: 40-60%
- Red: <40%

**Interpretation:**
- Each row shows a cohort's lifespan
- Darker patterns = sticky cohorts
- Fading pattern = normal churn

---

### Visual 2: Customer Growth Trajectory
**Type:** Combo Chart

| Element | Source |
|---|---|
| **Column** | `total_customers` (absolute count) |
| **Line 1** | `customer_growth_mom_pct` |
| **Line 2** | `customer_growth_yoy_pct` |
| **X-Axis** | Last 36 months |

**Insights:**
- Column trend = customer base trend
- Line slopes = growth acceleration
- Crossing zero line =turnaround inflection points

---

### Visual 3: Product Portfolio Matrix
**Type:** Scatter + Table

**Scatter Plot:**
- **X-Axis:** `active_products` (portfolio size per month)
- **Y-Axis:** `avg_product_rating` (quality)
- **Size:** `total_customers` (bubble size)
- **Color:** `product_growth_mom_pct` (green=growth, red=decline)
- **Trend:** Upward-right = healthy (more products, maintained quality)

**Table Below:**
| Month | Products | Customers | Avg Rating | Categories |
|-------|----------|-----------|------------|------------|

---

### Visual 4: Category Growth Performance
**Type:** Horizontal Bar + Line Combo

| Configuration | Value |
|---|---|
| **Categories** | Top 10 categories by revenue |
| **Bar** | `category_revenue_share_pct` |
| **Line** | `category_yoy_growth_pct` |
| **Color** | Green if YoY > 0, red if < 0 |
| **Sort** | By YoY growth (fastest growing first) |

**Analysis:**
- Tall bars = high revenue
- Upward lines = growing faster YoY
- Downward lines = slowing, need attention

---

### Visual 5: Retention Funnel
**Type:** Funnel Chart + KPI Cards

**Funnel Stages (Current Month):**
1. Prior Month Active: `active_customers` (from previous month) - 100%
2. Retained: `retained_customers` - show %
3. New Acquired: `new_customers` - show % above funnel
4. Current Active: `active_customers` - show total

**KPI Cards:**
| Metric | Formula | Format |
|--------|---------|--------|
| Retention Rate | `retained_customers / prior_month_active` | ##.##% |
| Churn Rate | `churned_customers / prior_month_active` | ##.##% |
| Net Growth | `(retained + new - churned) / prior_month_active` | ##.##% |
| New Customer Ratio | `new_customers / active_customers` | ##.##% |

**Trend Arrows:**
- Retention: Green if stable/up, Red if down >5%
- Churn: Green if <5%, Red if >10%

---

### Visual 6: Prime Adoption by Category
**Type:** Bar Chart + Table

| Configuration | Value |
|---|---|
| **Categories** | All major categories |
| **Bar Length** | `prime_penetration_pct` |
| **Color Gradient** | Light blue (0%) to dark blue (100%) |
| **Sort** | Descending |

**Table:**
| Category | Prime % | Prime Revenue | Category Revenue | Status |
|----------|---------|----------------|------------------|--------|
| | `prime_penetration_pct` | `prime_revenue_inr` | `revenue_inr` | ↑/↓ trend |

---

---

## CONNECTION SETUP FOR BI TOOLS

### Power BI Desktop

1. **Get Data → SQLite Database**
   - File: `C:\Users\admin\Desktop\Amazon_India_Sales_Analytics\AmazonIndia.db`
   - Import mode: DirectQuery or Import (Import recommended for 132-792 row views)

2. **Table Selection:**
   - Select all 15 views (vw_q1_* through vw_q5_*)
   - Click "Transform Data" to preview

3. **Relationships:**
   - No relationships needed (views are pre-aggregated)
   - Each view is self-contained

4. **Measures to Create:**
```DAX
-- Revenue in Billions (for scaling)
RevenueBillions = SUMX(VALUES('vw_q1_executive_summary'[total_revenue_inr]), 'vw_q1_executive_summary'[total_revenue_inr])/1000000000

-- YoY Growth formatting
YoYGrowthTrend = IF([YoY %] > 0, "📈 " & FORMAT([YoY %], "0.00%"), "📉 " & FORMAT([YoY %], "0.00%"))

-- Target Achievement
TargetStatus = IF([daily_target_achievement_pct] >= 100, "✓ On Target", IF([daily_target_achievement_pct] >= 95, "⚠ Minor Miss", "🔴 Critical"))
```

### Tableau Desktop

1. **Connect → SQLite**
   - Server: `C:\Users\admin\Desktop\Amazon_India_Sales_Analytics\AmazonIndia.db`

2. **Data Source Setup:**
   - Drag each view to canvas
   - No joins needed (pre-aggregated views)

3. **Calculated Fields:**
```TABLEAU
// Revenue in Billions
[Revenue Billions] = [total_revenue_inr] / 1000000000

// Growth Indicator
[Growth Arrow] = IF [yoy_revenue_growth_pct] > 0 THEN "📈" ELSEIF [yoy_revenue_growth_pct] < 0 THEN "📉" ELSE "—" END

// Status Indicator
[Status] = IF [daily_target_achievement_pct] >= 100 THEN "ON TARGET" ELSEIF [daily_target_achievement_pct] >= 95 THEN "WARNING" ELSE "CRITICAL" END
```

### Refresh Schedule

- **Auto-refresh:** Configure daily refresh at 3:00 AM (1 hour after nightly KPI refresh at 2:00 AM)
- **Manual refresh:** Use CTRL+R in Power BI or refresh icon in Tableau
- **Cache:** Views have no long-running calculations, <1 second load time

---

## TROUBLESHOOTING

| Issue | Cause | Solution |
|-------|-------|----------|
| Missing data for current month | View filters for complete months | Use prior month for current analysis |
| NULLs in YoY growth | No prior year data (first 12 months) | Filter to year >= 2016 |
| Slow dashboard load | Database version | Update to SQLite 3.45+ |
| Stale data in dashboard | Cache not refreshed | Manual refresh or check nightly task logs |

---

**End of Configuration Guide**

*For updates or questions, contact Analytics team.*  
*Last Updated: 2026-03-02*
