# PatrolIQ - Project Notes & Reference

---

## Day 2 — Data Cleaning Summary

### Dataset
- **Source:** Chicago Data Portal (Crimes 2001 to Present)
- **Raw records fetched:** 500,000
- **Final clean records:** 497,889
- **Final columns:** 28

### Cleaning Steps
| Step | Detail | Records Affected |
|---|---|---|
| Duplicates removed | By `case_number` | 50 rows |
| Missing coordinates dropped | `latitude`, `longitude`, `x_coordinate`, `y_coordinate` | 2,061 rows |
| `location_description` nulls | Filled with `"UNKNOWN"` | 2,204 rows |
| `ward` nulls | Filled with median | 1 row |
| `community_area` nulls | Filled with median | 3 rows |
| Geographic bounds validation | Chicago lat/lon bounds check | 0 outliers found |
| String cleaning | Stripped & uppercased text columns | All rows |
| Dropped columns | `location`, `updated_on` | — |

### Engineered Features Added
| Feature | Description |
|---|---|
| `hour` | Hour of day (0–23) |
| `day_of_week` | Day name (Monday–Sunday) |
| `day_num` | Day number (0=Mon, 6=Sun) |
| `month` | Month number (1–12) |
| `month_name` | Month name |
| `is_weekend` | 1 if Saturday/Sunday, else 0 |
| `season` | Winter / Spring / Summer / Fall |
| `crime_severity_score` | 1 (minor) to 10 (critical) based on crime type |

### Final Data Quality
- **Missing values:** 0
- **Date range:** 2024-02-19 to 2026-03-08
- **Saved file:** `chicago_crimes_clean.csv`

---

## Day 3 — EDA Insights

### Overview
| Metric | Value |
|---|---|
| Total crimes analysed | 497,889 |
| Unique crime types | 31 |
| Police districts | 23 |
| Average severity score | 5.08 / 10 |

### Crime Distribution
| Rank | Crime Type | Count | % of Total |
|---|---|---|---|
| 1 | THEFT | 115,965 | 23.3% |
| 2 | BATTERY | 89,626 | 18.0% |
| 3 | CRIMINAL DAMAGE | 55,064 | 11.1% |
| 4 | ASSAULT | 45,292 | 9.1% |
| 5 | MOTOR VEHICLE THEFT | 38,869 | 7.8% |
| 6 | OTHER OFFENSE | 33,906 | 6.8% |
| 7 | DECEPTIVE PRACTICE | 30,575 | 6.1% |
| 8 | BURGLARY | 18,877 | 3.8% |
| 9 | ROBBERY | 14,480 | 2.9% |
| 10 | NARCOTICS | 13,708 | 2.8% |

### Temporal Patterns
| Pattern | Finding |
|---|---|
| Peak hour | **Midnight (0:00)** — highest crime volume |
| Safest hour | Early morning (~5:00 AM) |
| Peak day | **Friday** |
| Peak month | **July** |
| Peak season | **Summer** |
| Weekend effect | Slightly higher crime on weekends |

### Geographic Patterns
| District | Crimes |
|---|---|
| District 8 (top) | 32,585 |
| Crime concentrated in | South & West Chicago |

### Arrest & Domestic Analysis
| Metric | Value |
|---|---|
| Overall arrest rate | **14.9%** (very low) |
| Domestic incident rate | **18.8%** |
| Highest arrest rate crime | NARCOTICS, PROSTITUTION |
| Lowest arrest rate crime | THEFT, CRIMINAL DAMAGE |

### Plots Generated (in `eda_plots/`)
| File | Content |
|---|---|
| `01_crime_type_distribution.png` | All 31 crime types ranked |
| `02_temporal_patterns.png` | Hour / Day / Month / Season charts |
| `03_geographic_distribution.png` | Crime scatter map + district bar chart |
| `04_arrest_domestic_rates.png` | Arrest rates by top 15 crime types |
| `05_heatmap_hour_day.png` | Hour vs Day of week heatmap |
| `06_severity_distribution.png` | Severity score distribution |

---

## Day 4 — Feature Engineering
- Script: `clustering.py` (feature engineering included at top)
- Output: `chicago_crimes_clustered.csv`

### New Features Created
| Feature | Description |
|---|---|
| `crime_type_encoded` | Label-encoded primary_type (integer) |
| `location_type_encoded` | Label-encoded location_description (integer) |
| `lat_bin` | Latitude divided into 20 grid bins |
| `lon_bin` | Longitude divided into 20 grid bins |
| `grid_cell` | Combined lat_bin + lon_bin as city grid ID |
| `lat_norm` | Standardized latitude (mean=0, std=1) |
| `lon_norm` | Standardized longitude (mean=0, std=1) |

---

## Day 5 — Clustering Analysis
- Script: `clustering.py`
- Output: `chicago_crimes_clustered.csv`
- Plots: `clustering_plots/`

### Geographic Clustering — Algorithm Comparison

| Algorithm | Silhouette | DBI | Clusters | Notes |
|---|---|---|---|---|
| **K-Means (Geo)** | **0.3984** | 0.8502 | 7 | **Best — selected for deployment** |
| DBSCAN (Geo) | -0.0170 | 0.4529 | 10 | 868 noise points (0.9%) |
| Hierarchical (Geo) | 0.3411 | 0.8158 | 7 | Run on 5,000-record sample |

> **Decision:** K-Means selected as best geographic algorithm (highest silhouette).
> Note: Silhouette scores are below 0.5 target due to overlapping urban crime spread — this is normal for real-world city crime data.

### Temporal Clustering

| Algorithm | Silhouette | DBI | Clusters |
|---|---|---|---|
| K-Means (Temporal) | 0.2374 | 1.3976 | 4 |

### Temporal Cluster Profiles (mean feature values)

| Cluster | Peak Hour | is_weekend | Month | Label |
|---|---|---|---|---|
| 0 | 12:00 | 1.0 (weekend) | Jun | Weekend Afternoon Crime |
| 1 | 16:00 | 0.0 (weekday) | Sep | Weekday Evening Crime |
| 2 | 15:00 | 0.0 (weekday) | Mar | Weekday Afternoon Crime |
| 3 | 03:00 | 0.0 (weekday) | Jun | **Late Night Crime** |

### Key Findings
- 7 distinct geographic crime hotspot zones identified across Chicago
- District 8 is the highest-crime district (32,585 crimes)
- Late-night crime cluster (3 AM) is a distinct pattern — primarily weekday
- DBSCAN found 10 natural density zones with only 0.9% noise (outlier crimes)
- Hierarchical clustering confirms South/West Chicago as nested high-crime areas

### Plots Generated (`clustering_plots/`)
| File | Content |
|---|---|
| `A1_elbow_method.png` | Elbow curve — K=2 to 11 |
| `A2_kmeans_geographic.png` | 7 K-Means crime hotspot zones on map |
| `A3_dbscan_geographic.png` | DBSCAN density clusters + noise points |
| `A4_hierarchical_geographic.png` | Dendrogram + hierarchical zone map |
| `B1_temporal_clustering.png` | 4 time-based crime pattern profiles |
| `C1_algorithm_comparison.png` | Silhouette & DBI bar chart comparison |

---

## Day 6 & 7 — Dimensionality Reduction
- Script: `dimensionality_reduction.py`
- Output: `chicago_crimes_dr.csv`
- Plots: `dr_plots/`

### PCA Results

| Components | Variance Explained |
|---|---|
| 2 components | 47.5% |
| 3 components | 57.1% |
| 6 components | **70%** threshold |
| 7 components | **80%** threshold |
| 10 components | **90%** threshold |

### Top 5 Features Driving Crime Patterns (PCA Importance)

| Rank | Feature | Importance Score |
|---|---|---|
| 1 | `longitude` / `lon_norm` | 0.6645 |
| 2 | `lon_bin` | 0.6613 |
| 3 | `x_coordinate` | 0.6605 |
| 4 | `community_area` | 0.5837 |
| 5 | `latitude` / `lat_norm` | 0.5424 |

> **Key insight:** Geographic features (location) dominate crime patterns — where a crime happens is the strongest predictor, confirming that spatial clustering is the right approach.

### t-SNE
- Perplexity: 40, Iterations: 1000
- Shows distinct geographic cluster separation in 2D space

### UMAP
- n_neighbors: 30, min_dist: 0.1
- Faster than t-SNE, preserves both local and global structure

### Plots Generated (`dr_plots/`)
| File | Content |
|---|---|
| `01_pca_scree_variance.png` | Scree plot + cumulative variance curve |
| `02_pca_2d_scatter.png` | PCA 2D — colored by cluster, temporal, severity |
| `03_pca_feature_importance.png` | Top 10 features by PCA loading importance |
| `04_pca_3d.png` | PCA 3D scatter plots |
| `05_tsne_2d_scatter.png` | t-SNE 2D — colored by cluster, temporal, severity |
| `06_umap_2d_scatter.png` | UMAP 2D — colored by cluster, temporal, severity |
| `07_dr_comparison.png` | Side-by-side PCA vs t-SNE vs UMAP comparison |

## Day 8 — MLflow Integration
- Script: `mlflow_tracking.py`
- Output: `mlflow_results_summary.csv`
- Tracking UI: run `mlflow ui` then open `http://localhost:5000`
- Experiment name: `PatrolIQ_Crime_Analysis`
- Total runs logged: **15**

### All Runs (sorted by Silhouette)

| Run Name | Silhouette | DBI | Clusters |
|---|---|---|---|
| **KMeans_Geo_K3** | **0.4273** | 0.8618 | 3 — Best Geo |
| KMeans_Geo_K11 | 0.4126 | 0.7863 | 11 |
| KMeans_Geo_K9 | 0.4045 | 0.7971 | 9 |
| KMeans_Geo_K5 | 0.3907 | 0.8326 | 5 |
| KMeans_Geo_K7 | 0.3898 | 0.8563 | 7 |
| Hierarchical_K7 | 0.3549 | 0.8913 | 7 |
| **KMeans_Temporal_K3** | **0.2463** | 1.5838 | 3 — Best Temporal |
| KMeans_Temporal_K5 | 0.2413 | 1.2587 | 5 |
| KMeans_Temporal_K4 | 0.2365 | 1.4158 | 4 |
| DBSCAN_eps0.12 | 0.1324 | 0.4059 | 6 |
| DBSCAN_eps0.05 | -0.3021 | 1.0869 | 55 |
| DBSCAN_eps0.08 | -0.4623 | 1.3595 | 12 |
| PCA_22_to_2 | — | — | 52.0% variance (2 components) |
| tSNE_2D | — | — | KL Divergence: 1.6489 |
| UMAP_2D | — | — | n_neighbors=30, min_dist=0.1 |

### Key Findings
- **Best geographic model:** KMeans K=3 (silhouette=0.4273)
- **Best temporal model:** KMeans K=3 (silhouette=0.2463)
- **PCA:** 52% variance in 2 components, 70% in 5 components
- **DBSCAN** works best at eps=0.12 (only 0.8% noise, 6 natural zones)
- All models, parameters, metrics and artifacts stored in `mlruns/`

## Day 9 — Streamlit App
- Main script: `app.py`
- Pages folder: `pages/`
- Run: `streamlit run app.py`
- Local URL: `http://localhost:8501`

### Pages Built
| File | Page | Content |
|---|---|---|
| `app.py` | Home | KPIs, navigation guide |
| `pages/1_Crime_Overview.py` | Crime Overview | Type distribution, arrest rates, severity |
| `pages/2_Geographic_Hotspots.py` | Geographic Hotspots | Interactive scatter map, density heatmap, district analysis |
| `pages/3_Temporal_Patterns.py` | Temporal Patterns | Hourly/daily/monthly/seasonal charts, heatmap |
| `pages/4_Clustering_Analysis.py` | Clustering Analysis | Algorithm comparison, cluster zone profiles |
| `pages/5_Dimensionality_Reduction.py` | Dimensionality Reduction | Interactive PCA/t-SNE/UMAP plots |
| `pages/6_MLflow_Dashboard.py` | MLflow Dashboard | Experiment runs, silhouette/DBI comparison |

### Key Features
- Sidebar filters on every page (crime type, district, season)
- Interactive Plotly charts (hover, zoom, filter)
- Mapbox maps for geographic visualization
- All pages load from cached CSVs (fast)
