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
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap

sns.set_theme(style="darkgrid")
os.makedirs("dr_plots", exist_ok=True)

print("=" * 60)
print("PATROLIQ - DIMENSIONALITY REDUCTION (Day 6 & 7)")
print("=" * 60)

df = pd.read_csv("chicago_crimes_clustered.csv", parse_dates=["date"])
print(f"\nLoaded: {df.shape[0]:,} rows x {df.shape[1]} columns")

# ── Feature matrix (22 numeric features) ─────────────────────
features = [
    "hour", "day_num", "month", "is_weekend",
    "crime_severity_score", "crime_type_encoded",
    "location_type_encoded", "latitude", "longitude",
    "beat", "district", "ward", "community_area",
    "lat_bin", "lon_bin", "lat_norm", "lon_norm",
    "geo_cluster", "temporal_cluster",
    "x_coordinate", "y_coordinate", "year"
]

# Keep only columns that exist
features = [f for f in features if f in df.columns]
print(f"\nUsing {len(features)} features: {features}")

# Sample for DR (t-SNE & UMAP are slow on large data)
SAMPLE_SIZE = 10000
sample_df = df.sample(SAMPLE_SIZE, random_state=42).copy()
X = sample_df[features].fillna(0).values

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print(f"\nSample size for DR: {SAMPLE_SIZE:,} records")

# ═══════════════════════════════════════════════════════════════
# PART 1 — PCA
# ═══════════════════════════════════════════════════════════════
print("\n--- PCA (Principal Component Analysis) ---")

# ── 1a. Full PCA — explained variance ────────────────────────
pca_full = PCA(random_state=42)
pca_full.fit(X_scaled)

cumvar = np.cumsum(pca_full.explained_variance_ratio_)
n_70 = np.argmax(cumvar >= 0.70) + 1
n_80 = np.argmax(cumvar >= 0.80) + 1
n_90 = np.argmax(cumvar >= 0.90) + 1

print(f"\n  Components needed:")
print(f"    70% variance -> {n_70} components")
print(f"    80% variance -> {n_80} components")
print(f"    90% variance -> {n_90} components")

# Scree plot
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].bar(range(1, len(pca_full.explained_variance_ratio_) + 1),
            pca_full.explained_variance_ratio_ * 100,
            color=sns.color_palette("Blues_r", len(features)), alpha=0.8)
axes[0].set_xlabel("Principal Component")
axes[0].set_ylabel("Explained Variance (%)")
axes[0].set_title("Scree Plot — Variance per Component")
axes[0].set_xlim(0.5, min(15, len(features)) + 0.5)

axes[1].plot(range(1, len(cumvar) + 1), cumvar * 100, "b-o", linewidth=2, markersize=4)
axes[1].axhline(y=70, color="green",  linestyle="--", alpha=0.7, label="70% threshold")
axes[1].axhline(y=80, color="orange", linestyle="--", alpha=0.7, label="80% threshold")
axes[1].axhline(y=90, color="red",    linestyle="--", alpha=0.7, label="90% threshold")
axes[1].axvline(x=n_70, color="green",  linestyle=":", alpha=0.5)
axes[1].axvline(x=n_80, color="orange", linestyle=":", alpha=0.5)
axes[1].set_xlabel("Number of Components")
axes[1].set_ylabel("Cumulative Variance (%)")
axes[1].set_title("Cumulative Explained Variance")
axes[1].legend(fontsize=9)

plt.suptitle("PCA — Explained Variance Analysis", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("dr_plots/01_pca_scree_variance.png", dpi=150)
plt.close()
print("\n  Saved: dr_plots/01_pca_scree_variance.png")

# ── 1b. PCA 2D — reduce to 2 components ──────────────────────
print("\n  Applying PCA -> 2 components...")
pca_2d = PCA(n_components=2, random_state=42)
X_pca = pca_2d.fit_transform(X_scaled)
var_explained = pca_2d.explained_variance_ratio_.sum() * 100
print(f"  Variance explained by 2 PCs: {var_explained:.1f}%")

sample_df["pca_1"] = X_pca[:, 0]
sample_df["pca_2"] = X_pca[:, 1]

# ── 1c. Feature importance (loadings) ────────────────────────
loadings = pd.DataFrame(
    np.abs(pca_2d.components_.T),
    index=features,
    columns=["PC1_loading", "PC2_loading"]
)
loadings["importance"] = loadings["PC1_loading"] + loadings["PC2_loading"]
loadings = loadings.sort_values("importance", ascending=False)

print("\n  Top 10 most important features:")
print(loadings.head(10)[["PC1_loading", "PC2_loading", "importance"]].round(4).to_string())

# Plot PCA 2D — colored by geo_cluster and crime type
fig, axes = plt.subplots(1, 3, figsize=(20, 6))

# By geo cluster
scatter1 = axes[0].scatter(X_pca[:, 0], X_pca[:, 1],
                           c=sample_df["geo_cluster"],
                           cmap="tab10", s=3, alpha=0.5)
axes[0].set_title(f"PCA 2D — by Geographic Cluster\n({var_explained:.1f}% variance)")
axes[0].set_xlabel(f"PC1 ({pca_2d.explained_variance_ratio_[0]*100:.1f}%)")
axes[0].set_ylabel(f"PC2 ({pca_2d.explained_variance_ratio_[1]*100:.1f}%)")
plt.colorbar(scatter1, ax=axes[0], label="Geo Cluster")

# By temporal cluster
scatter2 = axes[1].scatter(X_pca[:, 0], X_pca[:, 1],
                           c=sample_df["temporal_cluster"],
                           cmap="Set1", s=3, alpha=0.5)
axes[1].set_title(f"PCA 2D — by Temporal Cluster\n({var_explained:.1f}% variance)")
axes[1].set_xlabel(f"PC1 ({pca_2d.explained_variance_ratio_[0]*100:.1f}%)")
axes[1].set_ylabel(f"PC2 ({pca_2d.explained_variance_ratio_[1]*100:.1f}%)")
plt.colorbar(scatter2, ax=axes[1], label="Temporal Cluster")

# By crime severity
scatter3 = axes[2].scatter(X_pca[:, 0], X_pca[:, 1],
                           c=sample_df["crime_severity_score"],
                           cmap="YlOrRd", s=3, alpha=0.5)
axes[2].set_title(f"PCA 2D — by Crime Severity\n({var_explained:.1f}% variance)")
axes[2].set_xlabel(f"PC1 ({pca_2d.explained_variance_ratio_[0]*100:.1f}%)")
axes[2].set_ylabel(f"PC2 ({pca_2d.explained_variance_ratio_[1]*100:.1f}%)")
plt.colorbar(scatter3, ax=axes[2], label="Severity Score")

plt.suptitle("PCA 2D Visualization", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("dr_plots/02_pca_2d_scatter.png", dpi=150)
plt.close()
print("\n  Saved: dr_plots/02_pca_2d_scatter.png")

# Feature importance bar chart
fig, ax = plt.subplots(figsize=(12, 6))
top10 = loadings.head(10)
bars = ax.barh(top10.index, top10["importance"],
               color=sns.color_palette("Blues_r", 10))
ax.set_xlabel("Combined PC1 + PC2 Loading (Importance)")
ax.set_title("Top 10 Most Important Features Driving Crime Patterns (PCA)")
for bar, val in zip(bars, top10["importance"]):
    ax.text(bar.get_width() + 0.002, bar.get_y() + bar.get_height()/2,
            f"{val:.3f}", va="center", fontsize=9)
plt.tight_layout()
plt.savefig("dr_plots/03_pca_feature_importance.png", dpi=150)
plt.close()
print("  Saved: dr_plots/03_pca_feature_importance.png")

# PCA 3D
pca_3d = PCA(n_components=3, random_state=42)
X_pca3 = pca_3d.fit_transform(X_scaled)
var_3d = pca_3d.explained_variance_ratio_.sum() * 100
print(f"\n  PCA 3 components: {var_3d:.1f}% variance explained")

fig = plt.figure(figsize=(12, 5))
ax1 = fig.add_subplot(121, projection="3d")
sc = ax1.scatter(X_pca3[:, 0], X_pca3[:, 1], X_pca3[:, 2],
                 c=sample_df["geo_cluster"], cmap="tab10", s=2, alpha=0.4)
ax1.set_title(f"PCA 3D — Geo Clusters\n({var_3d:.1f}% variance)")
ax1.set_xlabel("PC1"); ax1.set_ylabel("PC2"); ax1.set_zlabel("PC3")

ax2 = fig.add_subplot(122, projection="3d")
sc2 = ax2.scatter(X_pca3[:, 0], X_pca3[:, 1], X_pca3[:, 2],
                  c=sample_df["crime_severity_score"], cmap="YlOrRd", s=2, alpha=0.4)
ax2.set_title(f"PCA 3D — Crime Severity\n({var_3d:.1f}% variance)")
ax2.set_xlabel("PC1"); ax2.set_ylabel("PC2"); ax2.set_zlabel("PC3")

plt.tight_layout()
plt.savefig("dr_plots/04_pca_3d.png", dpi=150)
plt.close()
print("  Saved: dr_plots/04_pca_3d.png")

# ═══════════════════════════════════════════════════════════════
# PART 2 — t-SNE
# ═══════════════════════════════════════════════════════════════
print("\n--- t-SNE Visualization ---")
print("  Running t-SNE (this takes ~2-3 min)...")

# Use PCA-reduced data as input to t-SNE for speed
pca_50 = PCA(n_components=min(50, len(features)), random_state=42)
X_pca50 = pca_50.fit_transform(X_scaled)

tsne = TSNE(n_components=2, perplexity=40, max_iter=1000,
            random_state=42, verbose=0)
X_tsne = tsne.fit_transform(X_pca50)

sample_df["tsne_1"] = X_tsne[:, 0]
sample_df["tsne_2"] = X_tsne[:, 1]
print("  t-SNE done.")

fig, axes = plt.subplots(1, 3, figsize=(20, 6))

scatter1 = axes[0].scatter(X_tsne[:, 0], X_tsne[:, 1],
                           c=sample_df["geo_cluster"],
                           cmap="tab10", s=4, alpha=0.6)
axes[0].set_title("t-SNE — by Geographic Cluster")
axes[0].set_xlabel("t-SNE 1"); axes[0].set_ylabel("t-SNE 2")
plt.colorbar(scatter1, ax=axes[0], label="Geo Cluster")

scatter2 = axes[1].scatter(X_tsne[:, 0], X_tsne[:, 1],
                           c=sample_df["temporal_cluster"],
                           cmap="Set1", s=4, alpha=0.6)
axes[1].set_title("t-SNE — by Temporal Cluster")
axes[1].set_xlabel("t-SNE 1"); axes[1].set_ylabel("t-SNE 2")
plt.colorbar(scatter2, ax=axes[1], label="Temporal Cluster")

scatter3 = axes[2].scatter(X_tsne[:, 0], X_tsne[:, 1],
                           c=sample_df["crime_severity_score"],
                           cmap="YlOrRd", s=4, alpha=0.6)
axes[2].set_title("t-SNE — by Crime Severity")
axes[2].set_xlabel("t-SNE 1"); axes[2].set_ylabel("t-SNE 2")
plt.colorbar(scatter3, ax=axes[2], label="Severity")

plt.suptitle("t-SNE 2D Visualization (n=10,000)", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("dr_plots/05_tsne_2d_scatter.png", dpi=150)
plt.close()
print("  Saved: dr_plots/05_tsne_2d_scatter.png")

# ═══════════════════════════════════════════════════════════════
# PART 3 — UMAP
# ═══════════════════════════════════════════════════════════════
print("\n--- UMAP Visualization ---")
print("  Running UMAP...")

reducer = umap.UMAP(n_components=2, n_neighbors=30, min_dist=0.1,
                    random_state=42, verbose=False)
X_umap = reducer.fit_transform(X_scaled)

sample_df["umap_1"] = X_umap[:, 0]
sample_df["umap_2"] = X_umap[:, 1]
print("  UMAP done.")

fig, axes = plt.subplots(1, 3, figsize=(20, 6))

scatter1 = axes[0].scatter(X_umap[:, 0], X_umap[:, 1],
                           c=sample_df["geo_cluster"],
                           cmap="tab10", s=4, alpha=0.6)
axes[0].set_title("UMAP — by Geographic Cluster")
axes[0].set_xlabel("UMAP 1"); axes[0].set_ylabel("UMAP 2")
plt.colorbar(scatter1, ax=axes[0], label="Geo Cluster")

scatter2 = axes[1].scatter(X_umap[:, 0], X_umap[:, 1],
                           c=sample_df["temporal_cluster"],
                           cmap="Set1", s=4, alpha=0.6)
axes[1].set_title("UMAP — by Temporal Cluster")
axes[1].set_xlabel("UMAP 1"); axes[1].set_ylabel("UMAP 2")
plt.colorbar(scatter2, ax=axes[1], label="Temporal Cluster")

scatter3 = axes[2].scatter(X_umap[:, 0], X_umap[:, 1],
                           c=sample_df["crime_severity_score"],
                           cmap="YlOrRd", s=4, alpha=0.6)
axes[2].set_title("UMAP — by Crime Severity")
axes[2].set_xlabel("UMAP 1"); axes[2].set_ylabel("UMAP 2")
plt.colorbar(scatter3, ax=axes[2], label="Severity")

plt.suptitle("UMAP 2D Visualization (n=10,000)", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("dr_plots/06_umap_2d_scatter.png", dpi=150)
plt.close()
print("  Saved: dr_plots/06_umap_2d_scatter.png")

# ═══════════════════════════════════════════════════════════════
# PART 4 — PCA vs t-SNE vs UMAP side-by-side comparison
# ═══════════════════════════════════════════════════════════════
print("\n  Generating comparison plot...")

fig, axes = plt.subplots(1, 3, figsize=(20, 6))
for ax, coords, title in zip(
    axes,
    [(X_pca[:, 0], X_pca[:, 1]), (X_tsne[:, 0], X_tsne[:, 1]), (X_umap[:, 0], X_umap[:, 1])],
    ["PCA", "t-SNE", "UMAP"]
):
    sc = ax.scatter(coords[0], coords[1],
                    c=sample_df["geo_cluster"], cmap="tab10", s=3, alpha=0.5)
    ax.set_title(f"{title} — Geographic Clusters")
    ax.set_xlabel(f"{title} Dim 1")
    ax.set_ylabel(f"{title} Dim 2")
    plt.colorbar(sc, ax=ax, label="Cluster")

plt.suptitle("DR Method Comparison: PCA vs t-SNE vs UMAP\n(colored by Geographic Cluster)",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("dr_plots/07_dr_comparison.png", dpi=150)
plt.close()
print("  Saved: dr_plots/07_dr_comparison.png")

# ── Save DR results ───────────────────────────────────────────
sample_df.to_csv("chicago_crimes_dr.csv", index=False)
print("\n  Saved: chicago_crimes_dr.csv")

# ═══════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("DIMENSIONALITY REDUCTION SUMMARY")
print("=" * 60)
print(f"\nFeatures used          : {len(features)}")
print(f"Sample size            : {SAMPLE_SIZE:,}")
print(f"\nPCA Results:")
print(f"  2 components         : {var_explained:.1f}% variance")
print(f"  3 components         : {var_3d:.1f}% variance")
print(f"  70% threshold        : {n_70} components")
print(f"  80% threshold        : {n_80} components")
print(f"\nTop 5 features by PCA importance:")
for i, (feat, row) in enumerate(loadings.head(5).iterrows(), 1):
    print(f"  {i}. {feat:<30} importance={row['importance']:.4f}")
print(f"\nt-SNE  : complete (perplexity=40, iter=1000)")
print(f"UMAP   : complete (n_neighbors=30, min_dist=0.1)")
print(f"\nAll plots saved in: dr_plots/")
print("Dimensionality Reduction complete!")
