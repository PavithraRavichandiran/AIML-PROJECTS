import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
import warnings
warnings.filterwarnings("ignore")

from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.metrics import silhouette_score, davies_bouldin_score
from scipy.cluster.hierarchy import dendrogram, linkage

sns.set_theme(style="darkgrid")
os.makedirs("clustering_plots", exist_ok=True)

print("=" * 60)
print("PATROLIQ - FEATURE ENGINEERING + CLUSTERING")
print("=" * 60)

df = pd.read_csv("chicago_crimes_clean.csv", parse_dates=["date"])
print(f"\nLoaded: {df.shape[0]:,} rows x {df.shape[1]} columns")

# ═══════════════════════════════════════════════════════════════
# DAY 4 — FEATURE ENGINEERING
# ═══════════════════════════════════════════════════════════════
print("\n--- DAY 4: FEATURE ENGINEERING ---")

# Encode categorical columns
le = LabelEncoder()
df["crime_type_encoded"]     = le.fit_transform(df["primary_type"])
df["location_type_encoded"]  = le.fit_transform(df["location_description"])

# Coordinate binning (divide city into grid cells)
df["lat_bin"] = pd.cut(df["latitude"],  bins=20, labels=False)
df["lon_bin"] = pd.cut(df["longitude"], bins=20, labels=False)
df["grid_cell"] = df["lat_bin"].astype(str) + "_" + df["lon_bin"].astype(str)

# Normalize geographic coordinates
scaler_geo = StandardScaler()
df[["lat_norm", "lon_norm"]] = scaler_geo.fit_transform(df[["latitude", "longitude"]])

print("  Created: crime_type_encoded, location_type_encoded")
print("  Created: lat_bin, lon_bin, grid_cell")
print("  Created: lat_norm, lon_norm (standardized)")

# ── Feature sets for clustering ───────────────────────────────
# Geographic features
geo_features = ["latitude", "longitude"]

# Temporal features
temporal_features = ["hour", "day_num", "month", "is_weekend", "crime_severity_score"]

# Combined features
combined_features = [
    "lat_norm", "lon_norm",
    "hour", "day_num", "month", "is_weekend",
    "crime_severity_score", "crime_type_encoded"
]

# Sample for faster clustering (use 50K for DBSCAN/Hierarchical)
FULL_SAMPLE  = 100000
SMALL_SAMPLE = 10000

geo_df    = df[geo_features].sample(FULL_SAMPLE, random_state=42)
temp_df   = df[temporal_features].sample(FULL_SAMPLE, random_state=42)
small_df  = df[combined_features].sample(SMALL_SAMPLE, random_state=42)

scaler = StandardScaler()
geo_scaled     = scaler.fit_transform(geo_df)
temp_scaled    = scaler.fit_transform(temp_df)
small_scaled   = scaler.fit_transform(small_df)

print(f"\n  Prepared:")
print(f"    Geographic sample  : {FULL_SAMPLE:,} records")
print(f"    Temporal sample    : {FULL_SAMPLE:,} records")
print(f"    Combined (small)   : {SMALL_SAMPLE:,} records")

# ═══════════════════════════════════════════════════════════════
# DAY 5 — CLUSTERING
# ═══════════════════════════════════════════════════════════════
print("\n--- DAY 5: CLUSTERING ANALYSIS ---")
results = {}

# ─────────────────────────────────────────────────────────────
# PART A: GEOGRAPHIC CRIME HOTSPOT CLUSTERING
# ─────────────────────────────────────────────────────────────
print("\n[A] GEOGRAPHIC CRIME HOTSPOT CLUSTERING")

# ── A1. Elbow Method to choose K ─────────────────────────────
print("\n  [A1] Elbow Method for optimal K...")
inertias = []
k_range = range(2, 12)
for k in k_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(geo_scaled)
    inertias.append(km.inertia_)

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(k_range, inertias, "bo-", linewidth=2, markersize=6)
ax.set_xlabel("Number of Clusters (K)")
ax.set_ylabel("Inertia")
ax.set_title("Elbow Method - Optimal K for Geographic Clustering")
ax.axvline(x=7, color="red", linestyle="--", alpha=0.7, label="Chosen K=7")
ax.legend()
plt.tight_layout()
plt.savefig("clustering_plots/A1_elbow_method.png", dpi=150)
plt.close()
print("    Saved: clustering_plots/A1_elbow_method.png")

# ── A2. K-Means Clustering ────────────────────────────────────
print("\n  [A2] K-Means Geographic Clustering (K=7)...")
K = 7
kmeans_geo = KMeans(n_clusters=K, random_state=42, n_init=10)
geo_df = geo_df.copy()
geo_df["kmeans_cluster"] = kmeans_geo.fit_predict(geo_scaled)

sil_kmeans = silhouette_score(geo_scaled, geo_df["kmeans_cluster"], sample_size=5000)
dbi_kmeans = davies_bouldin_score(geo_scaled, geo_df["kmeans_cluster"])
results["KMeans_Geo"] = {"silhouette": sil_kmeans, "dbi": dbi_kmeans, "n_clusters": K}

print(f"    Silhouette Score : {sil_kmeans:.4f}")
print(f"    Davies-Bouldin   : {dbi_kmeans:.4f}")
print(f"    Clusters found   : {K}")

# Plot
fig, ax = plt.subplots(figsize=(12, 8))
colors = plt.cm.tab10(np.linspace(0, 1, K))
for cluster in range(K):
    mask = geo_df["kmeans_cluster"] == cluster
    ax.scatter(geo_df.loc[mask, "longitude"], geo_df.loc[mask, "latitude"],
               s=0.8, alpha=0.4, color=colors[cluster], label=f"Zone {cluster+1}")
# Plot centroids
centers = kmeans_geo.cluster_centers_
# Inverse transform centroids back to lat/lon
centers_orig = scaler_geo.inverse_transform(centers)
ax.scatter(centers_orig[:, 1], centers_orig[:, 0],
           s=200, c="black", marker="*", zorder=5, label="Centroids")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_title(f"K-Means Geographic Crime Hotspots (K={K})\nSilhouette={sil_kmeans:.3f} | DBI={dbi_kmeans:.3f}")
ax.legend(markerscale=5, fontsize=8)
plt.tight_layout()
plt.savefig("clustering_plots/A2_kmeans_geographic.png", dpi=150)
plt.close()
print("    Saved: clustering_plots/A2_kmeans_geographic.png")

# ── A3. DBSCAN Clustering ─────────────────────────────────────
print("\n  [A3] DBSCAN Geographic Clustering...")
dbscan_geo = DBSCAN(eps=0.08, min_samples=50, n_jobs=-1)
geo_df["dbscan_cluster"] = dbscan_geo.fit_predict(geo_scaled)

n_clusters_dbscan = len(set(geo_df["dbscan_cluster"])) - (1 if -1 in geo_df["dbscan_cluster"].values else 0)
n_noise = (geo_df["dbscan_cluster"] == -1).sum()
noise_pct = n_noise / len(geo_df) * 100

# Silhouette only on non-noise points
non_noise_mask = geo_df["dbscan_cluster"] != -1
if non_noise_mask.sum() > 1 and n_clusters_dbscan > 1:
    sil_dbscan = silhouette_score(geo_scaled[non_noise_mask], geo_df.loc[non_noise_mask, "dbscan_cluster"], sample_size=5000)
    dbi_dbscan = davies_bouldin_score(geo_scaled[non_noise_mask], geo_df.loc[non_noise_mask, "dbscan_cluster"])
else:
    sil_dbscan = dbi_dbscan = 0.0

results["DBSCAN_Geo"] = {"silhouette": sil_dbscan, "dbi": dbi_dbscan, "n_clusters": n_clusters_dbscan}

print(f"    Clusters found   : {n_clusters_dbscan}")
print(f"    Noise points     : {n_noise:,} ({noise_pct:.1f}%)")
print(f"    Silhouette Score : {sil_dbscan:.4f}")
print(f"    Davies-Bouldin   : {dbi_dbscan:.4f}")

fig, ax = plt.subplots(figsize=(12, 8))
unique_clusters = sorted(geo_df["dbscan_cluster"].unique())
cmap = plt.cm.tab20(np.linspace(0, 1, max(len(unique_clusters), 1)))
for i, cluster in enumerate(unique_clusters):
    mask = geo_df["dbscan_cluster"] == cluster
    color = "lightgray" if cluster == -1 else cmap[i % len(cmap)]
    label = "Noise" if cluster == -1 else f"Zone {cluster+1}"
    ax.scatter(geo_df.loc[mask, "longitude"], geo_df.loc[mask, "latitude"],
               s=0.5, alpha=0.3 if cluster == -1 else 0.5,
               color=color, label=label)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_title(f"DBSCAN Geographic Crime Clusters\n{n_clusters_dbscan} clusters | {n_noise:,} noise points ({noise_pct:.1f}%)")
plt.tight_layout()
plt.savefig("clustering_plots/A3_dbscan_geographic.png", dpi=150)
plt.close()
print("    Saved: clustering_plots/A3_dbscan_geographic.png")

# ── A4. Hierarchical Clustering ───────────────────────────────
print("\n  [A4] Hierarchical Clustering (sample=5000)...")
hier_sample = geo_scaled[:5000]
hier_labels_df = geo_df.iloc[:5000].copy()

hier = AgglomerativeClustering(n_clusters=7, linkage="ward")
hier_labels_df["hier_cluster"] = hier.fit_predict(hier_sample)

sil_hier = silhouette_score(hier_sample, hier_labels_df["hier_cluster"], sample_size=2000)
dbi_hier = davies_bouldin_score(hier_sample, hier_labels_df["hier_cluster"])
results["Hierarchical_Geo"] = {"silhouette": sil_hier, "dbi": dbi_hier, "n_clusters": 7}

print(f"    Silhouette Score : {sil_hier:.4f}")
print(f"    Davies-Bouldin   : {dbi_hier:.4f}")

# Dendrogram (tiny subsample)
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

dend_sample = geo_scaled[:300]
Z = linkage(dend_sample, method="ward")
dendrogram(Z, ax=axes[0], truncate_mode="level", p=5,
           color_threshold=0.7 * max(Z[:, 2]))
axes[0].set_title("Dendrogram (300-record sample)")
axes[0].set_xlabel("Sample Index")
axes[0].set_ylabel("Distance")

colors = plt.cm.tab10(np.linspace(0, 1, 7))
for cluster in range(7):
    mask = hier_labels_df["hier_cluster"] == cluster
    axes[1].scatter(hier_labels_df.loc[mask, "longitude"], hier_labels_df.loc[mask, "latitude"],
                    s=5, alpha=0.5, color=colors[cluster], label=f"Zone {cluster+1}")
axes[1].set_title(f"Hierarchical Clusters (n=5,000)\nSilhouette={sil_hier:.3f}")
axes[1].set_xlabel("Longitude")
axes[1].set_ylabel("Latitude")
axes[1].legend(markerscale=2, fontsize=8)

plt.suptitle("Hierarchical Clustering - Geographic Crime Zones", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("clustering_plots/A4_hierarchical_geographic.png", dpi=150)
plt.close()
print("    Saved: clustering_plots/A4_hierarchical_geographic.png")

# ─────────────────────────────────────────────────────────────
# PART B: TEMPORAL PATTERN CLUSTERING
# ─────────────────────────────────────────────────────────────
print("\n[B] TEMPORAL PATTERN CLUSTERING")

print("\n  [B1] K-Means Temporal Clustering (K=4)...")
K_temp = 4
kmeans_temp = KMeans(n_clusters=K_temp, random_state=42, n_init=10)
temp_df = temp_df.copy()
temp_df["temporal_cluster"] = kmeans_temp.fit_predict(temp_scaled)

sil_temp = silhouette_score(temp_scaled, temp_df["temporal_cluster"], sample_size=5000)
dbi_temp = davies_bouldin_score(temp_scaled, temp_df["temporal_cluster"])
results["KMeans_Temporal"] = {"silhouette": sil_temp, "dbi": dbi_temp, "n_clusters": K_temp}

print(f"    Silhouette Score : {sil_temp:.4f}")
print(f"    Davies-Bouldin   : {dbi_temp:.4f}")

# Temporal cluster profile
temp_profile = temp_df.groupby("temporal_cluster")[temporal_features].mean().round(2)
print("\n  Temporal Cluster Profiles (mean values):")
print(temp_profile.to_string())

# Label clusters by peak hour
cluster_labels = {}
for cluster in range(K_temp):
    peak_h = temp_profile.loc[cluster, "hour"]
    if peak_h < 6:
        cluster_labels[cluster] = "Late Night Crime"
    elif peak_h < 12:
        cluster_labels[cluster] = "Morning Crime"
    elif peak_h < 18:
        cluster_labels[cluster] = "Afternoon Crime"
    else:
        cluster_labels[cluster] = "Evening Crime"

temp_df["temporal_label"] = temp_df["temporal_cluster"].map(cluster_labels)

# Plots
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Hour distribution per cluster
for cluster in range(K_temp):
    mask = temp_df["temporal_cluster"] == cluster
    hour_dist = temp_df.loc[mask, "hour"].value_counts().sort_index()
    axes[0].plot(hour_dist.index, hour_dist.values, linewidth=2,
                 label=cluster_labels[cluster], marker="o", markersize=3)
axes[0].set_title(f"Temporal Clusters: Crime by Hour\n(Silhouette={sil_temp:.3f})")
axes[0].set_xlabel("Hour of Day")
axes[0].set_ylabel("Crime Count")
axes[0].legend()

# Cluster sizes
cluster_sizes = temp_df["temporal_label"].value_counts()
axes[1].bar(cluster_sizes.index, cluster_sizes.values,
            color=sns.color_palette("muted", len(cluster_sizes)))
axes[1].set_title("Temporal Cluster Sizes")
axes[1].set_xlabel("Cluster")
axes[1].set_ylabel("Count")
axes[1].tick_params(axis="x", rotation=15)
axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

plt.suptitle("Temporal Crime Pattern Clustering", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("clustering_plots/B1_temporal_clustering.png", dpi=150)
plt.close()
print("    Saved: clustering_plots/B1_temporal_clustering.png")

# ─────────────────────────────────────────────────────────────
# PART C: ALGORITHM COMPARISON
# ─────────────────────────────────────────────────────────────
print("\n[C] ALGORITHM COMPARISON")

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

algorithms = list(results.keys())
silhouettes = [results[a]["silhouette"] for a in algorithms]
dbis = [results[a]["dbi"] for a in algorithms]

colors_bar = ["#2ecc71" if s >= 0.5 else "#f39c12" if s >= 0.3 else "#e74c3c" for s in silhouettes]

bars = axes[0].bar(algorithms, silhouettes, color=colors_bar)
axes[0].axhline(y=0.5, color="red", linestyle="--", linewidth=1.5, label="Target: 0.5")
axes[0].set_title("Silhouette Score Comparison\n(Higher is better, target >= 0.5)")
axes[0].set_ylabel("Silhouette Score")
axes[0].tick_params(axis="x", rotation=20)
axes[0].legend()
for bar, val in zip(bars, silhouettes):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                 f"{val:.3f}", ha="center", va="bottom", fontweight="bold")

bars2 = axes[1].bar(algorithms, dbis, color=sns.color_palette("Blues_r", len(algorithms)))
axes[1].set_title("Davies-Bouldin Index Comparison\n(Lower is better)")
axes[1].set_ylabel("Davies-Bouldin Index")
axes[1].tick_params(axis="x", rotation=20)
for bar, val in zip(bars2, dbis):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                 f"{val:.3f}", ha="center", va="bottom", fontweight="bold")

plt.suptitle("Clustering Algorithm Performance Comparison", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("clustering_plots/C1_algorithm_comparison.png", dpi=150)
plt.close()
print("    Saved: clustering_plots/C1_algorithm_comparison.png")

# ─────────────────────────────────────────────────────────────
# PART D: ASSIGN BEST CLUSTERS TO FULL DATASET & SAVE
# ─────────────────────────────────────────────────────────────
print("\n[D] Assigning best geographic clusters to full dataset...")

# Best geo algorithm = highest silhouette
best_geo_algo = max(["KMeans_Geo", "DBSCAN_Geo", "Hierarchical_Geo"],
                    key=lambda a: results[a]["silhouette"])
print(f"    Best geographic algorithm: {best_geo_algo}")

# Assign K-Means clusters to full dataset (most practical)
full_geo_scaled = scaler.fit_transform(df[geo_features])
df["geo_cluster"] = KMeans(n_clusters=K, random_state=42, n_init=10).fit_predict(full_geo_scaled)

# Assign temporal clusters to full dataset
full_temp_scaled = scaler.fit_transform(df[temporal_features])
df["temporal_cluster"] = KMeans(n_clusters=K_temp, random_state=42, n_init=10).fit_predict(full_temp_scaled)
df["temporal_label"] = df["temporal_cluster"].map(cluster_labels)

df.to_csv("chicago_crimes_clustered.csv", index=False)
print("    Saved: chicago_crimes_clustered.csv")

# ─────────────────────────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("CLUSTERING SUMMARY")
print("=" * 60)
print(f"\n{'Algorithm':<25} {'Silhouette':>12} {'DBI':>10} {'Clusters':>10}")
print("-" * 60)
for algo, metrics in results.items():
    flag = " <-- BEST" if algo == best_geo_algo else ""
    print(f"{algo:<25} {metrics['silhouette']:>12.4f} {metrics['dbi']:>10.4f} {metrics['n_clusters']:>10}{flag}")

print(f"\nBest algorithm : {best_geo_algo}")
print(f"All plots saved in: clustering_plots/")
print("Clustering complete!")
