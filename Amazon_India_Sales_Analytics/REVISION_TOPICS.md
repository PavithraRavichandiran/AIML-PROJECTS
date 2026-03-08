# 📚 Amazon India Sales Analytics - Complete Revision Topics

**Last Updated:** March 6, 2026  
**Project Type:** End-to-End Data Analytics & BI Dashboard  
**Tech Stack:** Python, SQL, Streamlit, Pandas, Plotly, SQLite

---

## 🎯 Overview of Project Scope

This is a **complete analytics platform** delivering:
- 25 analytical questions across 5 business domains
- Real-time Streamlit dashboard with multi-section navigation
- 5 Executive dashboards for Power BI/Tableau
- SQLite database with 15+ analytical views
- Python automation scripts for ETL and KPI refresh

**Key Statistics:**
- **Data**: 2015-2025 (11 years of Amazon India data)
- **Dashboard Questions**: Q1-Q25 (5 sections × 5 questions each)
- **SQL Views**: 25+ views across transactions, customers, products, time
- **Python Modules**: 9 core modules + 10+ support scripts

---

## 📖 SECTION 1: SQL & DATABASE FUNDAMENTALS

### 1.1 SQLite Basics
- [ ] Database concepts (tables, relationships, CRUD operations)
- [ ] SQLite commands and connection methods
- [ ] Creating and managing SQLite databases
- [ ] **Project Reference:** `AmazonIndia.sqbpro` (database file)

### 1.2 Table Design & Schema
- [ ] Data normalization principles
- [ ] Table relationships (PK, FK, constraints)
- [ ] **Project Tables:**
  - `transactions` - 10M+ rows (fact table)
  - `customers` - customer master data
  - `products` - product catalog
  - `time_dimension` - date/calendar table

### 1.3 SQL View Creation
- [ ] Views purpose and benefits
- [ ] CREATE VIEW syntax
- [ ] Materialized vs non-materialized views
- [ ] **Project Views** (15+ views):
  - Executive summary views (Q1-Q5): `vw_exec_*`, `vw_q1_*` through `vw_q5_*`
  - Derived analytical views: `vw_fact_sales_enriched`, `vw_rfm_*`
  - Dimension views: category, payment, prime membership

### 1.4 Complex SQL Queries
- [ ] JOIN operations (INNER, LEFT, RIGHT, FULL)
- [ ] Aggregate functions (SUM, COUNT, AVG, MAX, MIN)
- [ ] GROUP BY and HAVING clauses
- [ ] Window functions (ROW_NUMBER, RANK, LAG, LEAD)
- [ ] Common Table Expressions (CTEs / WITH clause)
- [ ] CASE statements and conditional logic

### 1.5 SQL Performance Optimization
- [ ] Indexing strategies
- [ ] Query optimization techniques
- [ ] Execution plans
- [ ] Avoiding N+1 queries

**Study Files:**
- [sql/create_transactions_table.sql](sql/create_transactions_table.sql)
- [sql/create_customers_table.sql](sql/create_customers_table.sql)
- [sql/create_products_table.sql](sql/create_products_table.sql)
- [sql/create_time_dimension_table.sql](sql/create_time_dimension_table.sql)
- [sql/dashboard_executive_views.sql](sql/dashboard_executive_views.sql)
- [sql/dashboard_executive_questions_1_5.sql](sql/dashboard_executive_questions_1_5.sql)
- [sql/dashboard_core_operations.sql](sql/dashboard_core_operations.sql)

---

## 📊 SECTION 2: DATA ANALYSIS & PANDAS

### 2.1 Pandas Fundamentals
- [ ] DataFrames and Series
- [ ] Loading data from CSV and databases
- [ ] Data indexing and selection
- [ ] **Project Usage:** Loading from `data/cleaned/` CSVs

### 2.2 Data Cleaning & Preprocessing
- [ ] Handling missing values (NaN, NULL)
- [ ] Data type conversions
- [ ] Duplicate detection and removal
- [ ] Outlier detection and handling
- [ ] **Project Reference:**
  - [notebooks/02_data_cleaning.ipynb](notebooks/02_data_cleaning.ipynb)
  - [notebooks/04_all_years_outlier_detection.ipynb](notebooks/04_all_years_outlier_detection.ipynb)
  - [notebooks/outliershandling.md](notebooks/outliershandling.md)

### 2.3 Exploratory Data Analysis (EDA)
- [ ] Descriptive statistics
- [ ] Distribution analysis
- [ ] Correlation analysis
- [ ] Data visualization during exploration
- [ ] **Project Reference:**
  - [notebooks/05_eda.ipynb](notebooks/05_eda.ipynb)
  - [notebooks/03_catalog_cleaning.ipynb](notebooks/03_catalog_cleaning.ipynb)

### 2.4 Time Series Analysis
- [ ] Time-based indexing and resampling
- [ ] Trend analysis
- [ ] Seasonal decomposition
- [ ] YoY and MoM growth calculations
- [ ] **Project Questions:**
  - Q1: Revenue Trend Analysis ([notebooks/Q01_Revenue_Trend_Analysis.ipynb](notebooks/Q01_Revenue_Trend_Analysis.ipynb))
  - Q2: Seasonal Patterns ([notebooks/Q02_Seasonal_Patterns_Analysis.ipynb](notebooks/Q02_Seasonal_Patterns_Analysis.ipynb))

### 2.5 Aggregation & Transformation
- [ ] GROUP BY operations
- [ ] Pivot tables and unstacking
- [ ] Merging and concatenating DataFrames
- [ ] Custom functions (apply, map, applymap)
- [ ] **Project Usage:** All data_loaders modules

### 2.6 Feature Engineering
- [ ] Creating new features from existing data
- [ ] Binning and categorization
- [ ] Encoding categorical variables
- [ ] **Project Example:** RFM (Recency, Frequency, Monetary) analysis

**Study Files:**
- [notebooks/01_data_understanding.ipynb](notebooks/01_data_understanding.ipynb)
- [notebooks/02_data_cleaning.ipynb](notebooks/02_data_cleaning.ipynb)
- [dashboard/data_loaders.py](dashboard/data_loaders.py)
- [dashboard/config.py](dashboard/config.py)

---

## 📈 SECTION 3: BUSINESS ANALYTICS & METRICS

### 3.1 Revenue Analytics
- [ ] Revenue calculation and forecasting
- [ ] YoY and MoM growth rates
- [ ] Revenue by category, payment method, geography
- [ ] **Project Questions:**
  - Q1: Executive Summary (Revenue, growth, customers, AOV)
  - Q6-Q10: Revenue Analytics ([notebooks/Q01_Revenue_Trend_Analysis.ipynb](notebooks/Q01_Revenue_Trend_Analysis.ipynb))

### 3.2 Customer Analytics
- [ ] Customer acquisition and retention
- [ ] RFM segmentation (Recency, Frequency, Monetary)
- [ ] Customer lifetime value (LTV)
- [ ] Churn analysis
- [ ] **Project Questions:**
  - Q11-Q15: Customer Analytics
  - [notebooks/Q03_Customer_Segmentation_RFM.ipynb](notebooks/Q03_Customer_Segmentation_RFM.ipynb)
  - [notebooks/Q03_Customer_Segmentation_Story.md](notebooks/Q03_Customer_Segmentation_Story.md)

### 3.3 Product & Category Analysis
- [ ] Product performance metrics
- [ ] Category mix and portfolio analysis
- [ ] Product demand and pricing relationships
- [ ] **Project Questions:**
  - Q5: Growth Analytics (cohorts, churn, portfolio)
  - Q16-Q20: Product & Inventory Analytics
  - [notebooks/Q05_Category_Performance_Analysis.ipynb](notebooks/Q05_Category_Performance_Analysis.ipynb)
  - [notebooks/Q10_Price_Demand_Analysis.ipynb](notebooks/Q10_Price_Demand_Analysis.ipynb)

### 3.4 Payment & Prime Membership Analysis
- [ ] Payment method evolution and trends
- [ ] Prime membership impact on sales
- [ ] Payment mix analysis
- [ ] **Project Questions:**
  - Q4: Financial Performance (margins, costs)
  - [notebooks/Q04_Payment_Method_Evolution.ipynb](notebooks/Q04_Payment_Method_Evolution.ipynb)
  - [notebooks/Q06_Prime_Membership_Impact.ipynb](notebooks/Q06_Prime_Membership_Impact.ipynb)

### 3.5 Geographic & Festival Analysis
- [ ] Geographic distribution (state, city, tier)
- [ ] Regional performance comparison
- [ ] Festival impact on sales
- [ ] **Project Questions:**
  - Q3: Strategic Overview (market share, geographic health)
  - [notebooks/Q07_Geographic_Analysis.ipynb](notebooks/Q07_Geographic_Analysis.ipynb)
  - [notebooks/Q08_Festival_Sales_Analysis.ipynb](notebooks/Q08_Festival_Sales_Analysis.ipynb)

### 3.6 Customer Demographics
- [ ] Age group analysis
- [ ] Demographic trends
- [ ] **Project Questions:**
  - Q9: Customer Age Group Analysis ([notebooks/Q09_Customer_Age_Group_Analysis.ipynb](notebooks/Q09_Customer_Age_Group_Analysis.ipynb))

**Study Files:**
- [EXECUTIVE_DASHBOARDS_DELIVERY_SUMMARY.md](EXECUTIVE_DASHBOARDS_DELIVERY_SUMMARY.md)
- [DASHBOARD_POWERBI_TABLEAU_MAPPING.md](DASHBOARD_POWERBI_TABLEAU_MAPPING.md)
- All Q*_*.ipynb notebook files

---

## 🎨 SECTION 4: DATA VISUALIZATION

### 4.1 Plotly Basics
- [ ] Chart types (bar, line, scatter, pie, sunburst, treemap)
- [ ] Creating and customizing plots with Plotly Express
- [ ] Plotly Graph Objects for advanced customization
- [ ] **Project Usage:** All dashboard modules use Plotly

### 4.2 Dashboard Design Principles
- [ ] KPI cards and metric displays
- [ ] Multi-chart layouts
- [ ] Color coding and conditional formatting
- [ ] Interactive filters and drill-down capabilities
- [ ] **Project Reference:**
  - [dashboard/revenue_analytics.py](dashboard/revenue_analytics.py)
  - [dashboard/customer_analytics.py](dashboard/customer_analytics.py)
  - [dashboard/product_inventory.py](dashboard/product_inventory.py)

### 4.3 Interactive Visualizations
- [ ] Hover tooltips and annotations
- [ ] Click-based drilling
- [ ] Dynamic filtering
- [ ] **Project Example:** Sunburst charts for category transitions

### 4.4 Visualization Best Practices
- [ ] Chart selection for different data types
- [ ] Color schemes and accessibility
- [ ] Avoiding chart junk
- [ ] Data-ink ratio optimization

### 4.5 Power BI/Tableau Setup
- [ ] Connecting to data sources
- [ ] Building visualizations
- [ ] Creating dashboards
- [ ] Applying filters and slicers
- [ ] **Project Reference:**
  - [EXECUTIVE_DASHBOARDS_USAGE_GUIDE.md](EXECUTIVE_DASHBOARDS_USAGE_GUIDE.md)
  - [DASHBOARD_POWERBI_TABLEAU_MAPPING.md](DASHBOARD_POWERBI_TABLEAU_MAPPING.md)

**Study Files:**
- [dashboard/revenue_analytics.py](dashboard/revenue_analytics.py) - Q6-Q10
- [dashboard/customer_analytics.py](dashboard/customer_analytics.py) - Q11-Q15
- [dashboard/product_inventory.py](dashboard/product_inventory.py) - Q16-Q20
- [dashboard/operations_logistics.py](dashboard/operations_logistics.py) - Q21-Q25
- [dashboard/executive_dashboard.py](dashboard/executive_dashboard.py) - Q1-Q5

---

## 🚀 SECTION 5: STREAMLIT DASHBOARD DEVELOPMENT

### 5.1 Streamlit Fundamentals
- [ ] Page structure and layout
- [ ] Widgets (buttons, sliders, multiselects, etc.)
- [ ] State management with `st.session_state`
- [ ] Caching with `@st.cache_data` and `@st.cache_resource`
- [ ] **Project Architecture:**
  - Main app: [dashboard/app.py](dashboard/app.py)
  - 5 rendering modules for different sections

### 5.2 Page Layout & Navigation
- [ ] Sidebar for controls and navigation
- [ ] Multi-section apps with radio buttons/tabs
- [ ] Column layouts and containers
- [ ] Columns and expanders
- [ ] **Project Example:** 5-section dashboard with section selector

### 5.3 Data Caching & Performance
- [ ] Caching strategies for database queries
- [ ] CSV file caching
- [ ] Session-based data persistence
- [ ] Query optimization
- [ ] **Project Implementation:**
  - `cached_load_data()`
  - `cached_load_q6_q10_data()`
  - `cached_load_q11_q15_data()`
  - `cached_load_q16_q20_data()`
  - `cached_load_q21_q25_data()`

### 5.4 Alerts & Notifications
- [ ] Toast notifications
- [ ] Warning and error messages
- [ ] Status handling (loading, success, error)
- [ ] **Project Reference:** [dashboard/alerts.py](dashboard/alerts.py)

### 5.5 Interactive Dashboards
- [ ] Creating responsive layouts
- [ ] Real-time data refresh
- [ ] User-driven filtering
- [ ] **Project Features:**
  - Per-section refresh capability
  - Real-time connectivity to SQLite + CSV
  - Interactive Plotly charts embedded in Streamlit

### 5.6 Streamlit Best Practices
- [ ] Code organization and modularization
- [ ] Error handling and validation
- [ ] Secrets management
- [ ] Production deployment

**Study Files:**
- [dashboard/app.py](dashboard/app.py) - Main entry point
- [dashboard/config.py](dashboard/config.py) - Configuration & utilities
- [dashboard/data_loaders.py](dashboard/data_loaders.py) - Caching functions
- [dashboard/utils.py](dashboard/utils.py) - Helper functions
- [dashboard/alerts.py](dashboard/alerts.py) - Alert system

---

## 🔧 SECTION 6: PYTHON SCRIPTING & AUTOMATION

### 6.1 Database Connection Management
- [ ] sqlite3 module usage
- [ ] Connection pooling concepts
- [ ] Query execution and cursor management
- [ ] **Project Usage:** Config and data loaders

### 6.2 ETL Scripting
- [ ] Data extraction from sources
- [ ] Data transformation and cleaning
- [ ] Data loading into database
- [ ] **Project Scripts:**
  - [scripts/populate_customers.py](scripts/populate_customers.py)
  - [scripts/populate_products.py](scripts/populate_products.py)
  - [scripts/populate_time_dimension.py](scripts/populate_time_dimension.py)
  - [scripts/bulk_insert_data.py](scripts/bulk_insert_data.py)

### 6.3 View Deployment Scripts
- [ ] Executing SQL from Python
- [ ] Validation and error handling
- [ ] Logging and reporting
- [ ] **Project Scripts:**
  - [scripts/deploy_views_quick.py](scripts/deploy_views_quick.py)
  - [scripts/deploy_executive_dashboards.py](scripts/deploy_executive_dashboards.py)

### 6.4 Data Validation & Testing
- [ ] Row count verification
- [ ] Sample data inspection
- [ ] Health check utilities
- [ ] **Project Testing:**
  - [scripts/validate_dashboard_views.py](scripts/validate_dashboard_views.py)
  - [scripts/validate_executive_views.py](scripts/validate_executive_views.py)
  - [check_data.py](check_data.py)
  - [test_loaders.py](test_loaders.py)

### 6.5 Scheduling & Automation
- [ ] Task scheduling with Windows Task Scheduler
- [ ] PowerShell scripts for automation
- [ ] Cron/scheduled job concepts
- [ ] **Project Reference:**
  - [scripts/setup_nightly_kpi_task.ps1](scripts/setup_nightly_kpi_task.ps1)
  - [scripts/refresh_kpis.py](scripts/refresh_kpis.py)

### 6.6 Error Handling & Logging
- [ ] Try-except blocks
- [ ] Custom exceptions
- [ ] Logging module usage
- [ ] **Project Implementation:** All scripts include error handling

**Study Files:**
- [scripts/deploy_views_quick.py](scripts/deploy_views_quick.py)
- [scripts/deploy_executive_dashboards.py](scripts/deploy_executive_dashboards.py)
- [scripts/validate_dashboard_views.py](scripts/validate_dashboard_views.py)
- [scripts/refresh_kpis.py](scripts/refresh_kpis.py)

---

## 📓 SECTION 7: JUPYTER NOTEBOOKS & ANALYSIS

### 7.1 Notebook Workflow
- [ ] Markdown vs code cells
- [ ] Cell execution and kernel management
- [ ] Output formatting and visualization
- [ ] Notebook organization

### 7.2 Data Understanding Phase
- [ ] Dataset overview and structure
- [ ] Column analysis and data types
- [ ] Missing value analysis
- [ ] **Project Notebook:**
  - [notebooks/01_data_understanding.ipynb](notebooks/01_data_understanding.ipynb)

### 7.3 Data Cleaning Phase
- [ ] Quality checks
- [ ] Handling inconsistencies
- [ ] Standardization
- [ ] **Project Notebooks:**
  - [notebooks/02_data_cleaning.ipynb](notebooks/02_data_cleaning.ipynb)
  - [notebooks/03_catalog_cleaning.ipynb](notebooks/03_catalog_cleaning.ipynb)
  - [notebooks/04_all_years_outlier_detection.ipynb](notebooks/04_all_years_outlier_detection.ipynb)

### 7.4 Exploratory Analysis
- [ ] Statistical summaries
- [ ] Distribution analysis
- [ ] Correlation studies
- [ ] **Project Notebook:**
  - [notebooks/05_eda.ipynb](notebooks/05_eda.ipynb)

### 7.5 Specific Domain Analyses
- [ ] Revenue trend analysis (Q1)
- [ ] Seasonal patterns (Q2)
- [ ] RFM segmentation (Q3)
- [ ] Payment evolution (Q4)
- [ ] Category performance (Q5)
- [ ] Prime membership impact (Q6)
- [ ] Geographic analysis (Q7)
- [ ] Festival analysis (Q8)
- [ ] Age group demographics (Q9)
- [ ] Price-demand relationships (Q10)

**Study Files:**
- [notebooks/Q01_Revenue_Trend_Analysis.ipynb](notebooks/Q01_Revenue_Trend_Analysis.ipynb)
- [notebooks/Q02_Seasonal_Patterns_Analysis.ipynb](notebooks/Q02_Seasonal_Patterns_Analysis.ipynb)
- [notebooks/Q03_Customer_Segmentation_RFM.ipynb](notebooks/Q03_Customer_Segmentation_RFM.ipynb)
- [notebooks/Q04_Payment_Method_Evolution.ipynb](notebooks/Q04_Payment_Method_Evolution.ipynb)
- [notebooks/Q05_Category_Performance_Analysis.ipynb](notebooks/Q05_Category_Performance_Analysis.ipynb)
- [notebooks/Q06_Prime_Membership_Impact.ipynb](notebooks/Q06_Prime_Membership_Impact.ipynb)
- [notebooks/Q07_Geographic_Analysis.ipynb](notebooks/Q07_Geographic_Analysis.ipynb)
- [notebooks/Q08_Festival_Sales_Analysis.ipynb](notebooks/Q08_Festival_Sales_Analysis.ipynb)
- [notebooks/Q09_Customer_Age_Group_Analysis.ipynb](notebooks/Q09_Customer_Age_Group_Analysis.ipynb)
- [notebooks/Q10_Price_Demand_Analysis.ipynb](notebooks/Q10_Price_Demand_Analysis.ipynb)

---

## 📚 SECTION 8: PROJECT DOCUMENTATION

### 8.1 Architecture & Design
- [ ] Project structure and organization
- [ ] Module responsibilities
- [ ] Data flow and dependencies
- [ ] **Project Reference:**
  - [QUICK_REFERENCE_INDEX.md](QUICK_REFERENCE_INDEX.md)
  - [EXECUTIVE_DASHBOARDS_DELIVERY_SUMMARY.md](EXECUTIVE_DASHBOARDS_DELIVERY_SUMMARY.md)

### 8.2 Configuration & Setup
- [ ] Environment setup and dependencies
- [ ] Database configuration
- [ ] File paths and constants
- [ ] **Project Reference:**
  - [dashboard/config.py](dashboard/config.py)
  - [EXECUTIVE_DASHBOARDS_USAGE_GUIDE.md](EXECUTIVE_DASHBOARDS_USAGE_GUIDE.md)

### 8.3 Data Mapping & Schema
- [ ] Table definitions and relationships
- [ ] Field-by-field mappings
- [ ] Data validation rules
- [ ] **Project Reference:**
  - [DASHBOARD_POWERBI_TABLEAU_MAPPING.md](DASHBOARD_POWERBI_TABLEAU_MAPPING.md)
  - [sql/](sql/) directory

### 8.4 Deployment & Validation
- [ ] View deployment process
- [ ] Health check procedures
- [ ] Data refresh strategy
- [ ] **Project Reference:**
  - [EXECUTIVE_DASHBOARDS_USAGE_GUIDE.md](EXECUTIVE_DASHBOARDS_USAGE_GUIDE.md)
  - Deployment scripts

---

## 🧪 SECTION 9: TECHNICAL SKILLS & TOOLS

### 9.1 Version Control (Git)
- [ ] Basic Git workflow (add, commit, push, pull)
- [ ] Branch management
- [ ] Merge conflicts
- [ ] Remote repositories

### 9.2 Python Ecosystem
- [ ] Virtual environments (venv, conda)
- [ ] Package management (pip, requirements.txt)
- [ ] Common libraries:
  - **pandas** - Data manipulation
  - **plotly** - Visualization
  - **streamlit** - Dashboard framework
  - **sqlite3** - Database connectivity

### 9.3 Windows & PowerShell
- [ ] PowerShell basics
- [ ] Script execution
- [ ] Task scheduling
- [ ] **Project Reference:**
  - [scripts/setup_nightly_kpi_task.ps1](scripts/setup_nightly_kpi_task.ps1)

### 9.4 Development Tools
- [ ] VS Code setup and extensions
- [ ] Jupyter Notebook environment
- [ ] SQLite browser/tools
- [ ] Streamlit debugging

### 9.5 Database Tools
- [ ] SQLite command-line
- [ ] Database browser tools
- [ ] Query testing
- [ ] View validation

---

## 🎓 LEARNING PATH RECOMMENDED ORDER

### Phase 1: Foundation (Weeks 1-2)
1. **SQL Basics** → Create tables, simple queries, JOINs
2. **Pandas Fundamentals** → DataFrames, loading, basic operations
3. **Project Structure** → Understand directory layout and data flow

### Phase 2: Data Work (Weeks 3-4)
1. **Data Cleaning & Validation** → Study notebooks 01-05
2. **Complex SQL** → Window functions, CTEs, aggregations
3. **Aggregation & Feature Engineering** → Study data_loaders.py

### Phase 3: Analytics (Weeks 5-6)
1. **Business Metrics** → Revenue, customer, product analytics
2. **Time Series Analysis** → Trends, seasonality, growth rates
3. **RFM & Segmentation** → Study Q11-Q15 notebooks

### Phase 4: Visualization (Weeks 7-8)
1. **Plotly Charting** → Different chart types and customization
2. **Dashboard Design** → Layout, KPIs, interactivity
3. **Streamlit Framework** → Widgets, caching, state management

### Phase 5: Integration (Weeks 9-10)
1. **Python Automation** → ETL scripts, deployment
2. **Dashboard Assembly** → app.py and section modules
3. **Testing & Validation** → Health checks, data validation

### Phase 6: Advanced (Weeks 11-12)
1. **Power BI/Tableau Setup** → Field mapping, visual configuration
2. **Performance Optimization** → Caching, query optimization
3. **Production Deployment** → Scheduling, logging, monitoring

---

## 💡 KEY CONCEPTS TO MASTER

### Core Analytics Concepts
- [ ] Revenue metrics and growth calculations (MoM, YoY)
- [ ] Customer segmentation (RFM analysis)
- [ ] Cohort analysis and retention
- [ ] Time-based aggregations (monthly, quarterly, yearly)
- [ ] Geographic and categorical analysis

### Technical Concepts
- [ ] Views and materialization in databases
- [ ] Caching strategies for performance
- [ ] Session state management in Streamlit
- [ ] Window functions for ranking and changes
- [ ] CTEs for complex query building

### Business Intelligence Concepts
- [ ] KPI definition and tracking
- [ ] Dashboard design principles
- [ ] Data quality and validation
- [ ] Automated reporting pipelines
- [ ] Alert systems

---

## 📋 QUICK CHECKLIST FOR PROJECT MASTERY

- [ ] Understand all 25 questions (Q1-Q25) and their business purpose
- [ ] Can execute SQL queries for each dashboard view
- [ ] Can explain the data flow from raw → cleaned → aggregated → visualized
- [ ] Can modify Streamlit components and layouts
- [ ] Can optimize slow queries or caching strategies
- [ ] Can deploy views and validate data
- [ ] Can explain RFM, seasonal patterns, geographic distribution
- [ ] Can choose appropriate chart types for different metrics
- [ ] Can set up Power BI or Tableau dashboards
- [ ] Can explain the purpose of each module in dashboard/
- [ ] Understand caching, session state, and performance considerations
- [ ] Can troubleshoot data issues and validate correctness

---

## 🔗 DOCUMENT CROSS-REFERENCE MAP

```
Project Entry Points:
├─ QUICK_REFERENCE_INDEX.md .................... START HERE
├─ EXECUTIVE_DASHBOARDS_DELIVERY_SUMMARY.md ... What's delivered
├─ EXECUTIVE_DASHBOARDS_USAGE_GUIDE.md ........ How to use
├─ DASHBOARD_POWERBI_TABLEAU_MAPPING.md ....... BI configuration
└─ REVISION_TOPICS.md (THIS FILE) ............. What to study

Technical Deep Dives:
├─ SQL Documents ─→ sql/*.sql files
├─ Notebooks ─────→ notebooks/*.ipynb files  
├─ Dashboards ───→ dashboard/*.py files
├─ Scripts ──────→ scripts/*.py files
└─ Data ─────────→ data/raw/ & data/cleaned/

By Business Domain:
├─ Revenue ──────→ Q1, Q6-Q10 + Revenue notebooks
├─ Customer ─────→ Q3, Q11-Q15 + Customer notebooks
├─ Product ──────→ Q5, Q16-Q20 + Category notebooks
├─ Operations ───→ Q2, Q21-Q25 + Operations module
└─ Executive ────→ Q1-Q5 + Executive dashboards
```

---

**Last Revision:** March 6, 2026
**Maintenance:** Update this file as new features or topics are added to the project
