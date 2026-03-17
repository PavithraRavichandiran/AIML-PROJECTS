import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
import os
import warnings
import json
warnings.filterwarnings("ignore")

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score, davies_bouldin_score
import umap

print("=" * 60)
print("PATROLIQ - MLFLOW EXPERIMENT TRACKING (Day 8)")
print("=" * 60)

# ── Setup MLflow ──────────────────────────────────────────────
EXPERIMENT_NAME = "PatrolIQ_Crime_Analysis"
mlflow.set_tracking_uri("mlruns")
mlflow.set_experiment(EXPERIMENT_NAME)
print(f"\nMLflow experiment : {EXPERIMENT_NAME}")
print(f"Tracking URI      : mlruns/")

# ── Load data ─────────────────────────────────────────────────
df = pd.read_csv("chicago_crimes_clustered.csv", parse_dates=["date"])
print(f"Loaded            : {df.shape[0]:,} rows x {df.shape[1]} columns")

features = [
    "hour", "day_num", "month", "is_weekend",
    "crime_severity_score", "crime_type_encoded",
    "location_type_encoded", "latitude", "longitude",
    "beat", "district", "ward", "community_area",
    "lat_bin", "lon_bin", "lat_norm", "lon_norm",
    "x_coordinate", "y_coordinate", "year"
]
features = [f for f in features if f in df.columns]

GEO_FEATURES  = ["latitude", "longitude"]
TEMP_FEATURES = ["hour", "day_num", "month", "is_weekend", "crime_severity_score"]
SAMPLE_GEO    = 50000
SAMPLE_TEMP   = 50000
SAMPLE_DR     = 5000

scaler = StandardScaler()

geo_data  = df[GEO_FEATURES].sample(SAMPLE_GEO, random_state=42)
temp_data = df[TEMP_FEATURES].sample(SAMPLE_TEMP, random_state=42)
dr_data   = df[features].sample(SAMPLE_DR, random_state=42).fillna(0)

geo_scaled  = scaler.fit_transform(geo_data)
temp_scaled = scaler.fit_transform(temp_data)
dr_scaled   = scaler.fit_transform(dr_data)

all_results = []

# ═══════════════════════════════════════════════════════════════
# RUN 1-5: K-MEANS GEOGRAPHIC (K = 3,5,7,9,11)
# ═══════════════════════════════════════════════════════════════
print("\n--- K-Means Geographic Clustering ---")

for k in [3, 5, 7, 9, 11]:
    with mlflow.start_run(run_name=f"KMeans_Geo_K{k}"):
        model = KMeans(n_clusters=k, random_state=42, n_init=10, max_iter=300)
        labels = model.fit_predict(geo_scaled)

        sil = silhouette_score(geo_scaled, labels, sample_size=3000, random_state=42)
        dbi = davies_bouldin_score(geo_scaled, labels)
        inertia = model.inertia_

        # Log params
        mlflow.log_params({
            "algorithm":    "KMeans",
            "task":         "geographic_clustering",
            "n_clusters":   k,
            "n_init":       10,
            "max_iter":     300,
            "features":     str(GEO_FEATURES),
            "sample_size":  SAMPLE_GEO,
            "random_state": 42
        })

        # Log metrics
        mlflow.log_metrics({
            "silhouette_score":    round(sil, 4),
            "davies_bouldin_index": round(dbi, 4),
            "inertia":             round(inertia, 2),
        })

        # Log model
        mlflow.sklearn.log_model(model, artifact_path=f"kmeans_k{k}")

        # Log cluster size distribution as artifact
        sizes = pd.Series(labels).value_counts().sort_index()
        sizes_dict = sizes.to_dict()
        with open(f"cluster_sizes_k{k}.json", "w") as f:
            json.dump(sizes_dict, f)
        mlflow.log_artifact(f"cluster_sizes_k{k}.json")
        os.remove(f"cluster_sizes_k{k}.json")

        run_id = mlflow.active_run().info.run_id
        all_results.append({
            "run_name": f"KMeans_Geo_K{k}", "run_id": run_id,
            "algorithm": "KMeans", "task": "geographic",
            "n_clusters": k, "silhouette": sil, "dbi": dbi, "inertia": inertia
        })

        print(f"  K={k:2d} | Silhouette={sil:.4f} | DBI={dbi:.4f} | Inertia={inertia:,.0f}")

# ═══════════════════════════════════════════════════════════════
# RUN 6-8: DBSCAN GEOGRAPHIC (varying eps)
# ═══════════════════════════════════════════════════════════════
print("\n--- DBSCAN Geographic Clustering ---")

for eps in [0.05, 0.08, 0.12]:
    with mlflow.start_run(run_name=f"DBSCAN_Geo_eps{eps}"):
        model = DBSCAN(eps=eps, min_samples=50, n_jobs=-1)
        labels = model.fit_predict(geo_scaled)

        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise    = int((labels == -1).sum())
        noise_pct  = round(n_noise / len(labels) * 100, 2)

        non_noise  = labels != -1
        if non_noise.sum() > 1 and n_clusters > 1:
            sil = silhouette_score(geo_scaled[non_noise], labels[non_noise],
                                   sample_size=3000, random_state=42)
            dbi = davies_bouldin_score(geo_scaled[non_noise], labels[non_noise])
        else:
            sil = dbi = 0.0

        mlflow.log_params({
            "algorithm":   "DBSCAN",
            "task":        "geographic_clustering",
            "eps":         eps,
            "min_samples": 50,
            "features":    str(GEO_FEATURES),
            "sample_size": SAMPLE_GEO,
        })
        mlflow.log_metrics({
            "silhouette_score":     round(sil, 4),
            "davies_bouldin_index": round(dbi, 4),
            "n_clusters_found":     n_clusters,
            "noise_points":         n_noise,
            "noise_pct":            noise_pct,
        })

        run_id = mlflow.active_run().info.run_id
        all_results.append({
            "run_name": f"DBSCAN_eps{eps}", "run_id": run_id,
            "algorithm": "DBSCAN", "task": "geographic",
            "n_clusters": n_clusters, "silhouette": sil, "dbi": dbi, "inertia": None
        })

        print(f"  eps={eps} | Clusters={n_clusters} | Noise={noise_pct:.1f}% | Silhouette={sil:.4f}")

# ═══════════════════════════════════════════════════════════════
# RUN 9: HIERARCHICAL CLUSTERING
# ═══════════════════════════════════════════════════════════════
print("\n--- Hierarchical Geographic Clustering ---")

HIER_SAMPLE = 5000
hier_data   = geo_scaled[:HIER_SAMPLE]

with mlflow.start_run(run_name="Hierarchical_Geo_K7"):
    model = AgglomerativeClustering(n_clusters=7, linkage="ward")
    labels = model.fit_predict(hier_data)

    sil = silhouette_score(hier_data, labels, sample_size=2000, random_state=42)
    dbi = davies_bouldin_score(hier_data, labels)

    mlflow.log_params({
        "algorithm":   "AgglomerativeClustering",
        "task":        "geographic_clustering",
        "n_clusters":  7,
        "linkage":     "ward",
        "features":    str(GEO_FEATURES),
        "sample_size": HIER_SAMPLE,
    })
    mlflow.log_metrics({
        "silhouette_score":     round(sil, 4),
        "davies_bouldin_index": round(dbi, 4),
    })
    mlflow.sklearn.log_model(model, artifact_path="hierarchical_k7")

    run_id = mlflow.active_run().info.run_id
    all_results.append({
        "run_name": "Hierarchical_K7", "run_id": run_id,
        "algorithm": "Hierarchical", "task": "geographic",
        "n_clusters": 7, "silhouette": sil, "dbi": dbi, "inertia": None
    })
    print(f"  K=7 | Silhouette={sil:.4f} | DBI={dbi:.4f}")

# ═══════════════════════════════════════════════════════════════
# RUN 10-12: K-MEANS TEMPORAL (K = 3,4,5)
# ═══════════════════════════════════════════════════════════════
print("\n--- K-Means Temporal Clustering ---")

for k in [3, 4, 5]:
    with mlflow.start_run(run_name=f"KMeans_Temporal_K{k}"):
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = model.fit_predict(temp_scaled)

        sil     = silhouette_score(temp_scaled, labels, sample_size=3000, random_state=42)
        dbi     = davies_bouldin_score(temp_scaled, labels)
        inertia = model.inertia_

        mlflow.log_params({
            "algorithm":   "KMeans",
            "task":        "temporal_clustering",
            "n_clusters":  k,
            "n_init":      10,
            "features":    str(TEMP_FEATURES),
            "sample_size": SAMPLE_TEMP,
        })
        mlflow.log_metrics({
            "silhouette_score":     round(sil, 4),
            "davies_bouldin_index": round(dbi, 4),
            "inertia":              round(inertia, 2),
        })
        mlflow.sklearn.log_model(model, artifact_path=f"kmeans_temporal_k{k}")

        run_id = mlflow.active_run().info.run_id
        all_results.append({
            "run_name": f"KMeans_Temporal_K{k}", "run_id": run_id,
            "algorithm": "KMeans_Temporal", "task": "temporal",
            "n_clusters": k, "silhouette": sil, "dbi": dbi, "inertia": inertia
        })
        print(f"  K={k} | Silhouette={sil:.4f} | DBI={dbi:.4f}")

# ═══════════════════════════════════════════════════════════════
# RUN 13: PCA DIMENSIONALITY REDUCTION
# ═══════════════════════════════════════════════════════════════
print("\n--- PCA Dimensionality Reduction ---")

with mlflow.start_run(run_name="PCA_22_to_2"):
    pca = PCA(n_components=2, random_state=42)
    pca.fit(dr_scaled)

    var_2d     = float(pca.explained_variance_ratio_.sum())
    pc1_var    = float(pca.explained_variance_ratio_[0])
    pc2_var    = float(pca.explained_variance_ratio_[1])

    pca_full   = PCA(random_state=42).fit(dr_scaled)
    cum_var    = np.cumsum(pca_full.explained_variance_ratio_)
    n_70       = int(np.argmax(cum_var >= 0.70) + 1)
    n_80       = int(np.argmax(cum_var >= 0.80) + 1)

    mlflow.log_params({
        "algorithm":       "PCA",
        "task":            "dimensionality_reduction",
        "n_components":    2,
        "n_features_in":   len(features),
        "sample_size":     SAMPLE_DR,
    })
    mlflow.log_metrics({
        "explained_variance_2d":  round(var_2d, 4),
        "pc1_variance":           round(pc1_var, 4),
        "pc2_variance":           round(pc2_var, 4),
        "components_for_70pct":   n_70,
        "components_for_80pct":   n_80,
    })
    mlflow.sklearn.log_model(pca, artifact_path="pca_2d")

    # Log feature importance as artifact
    loadings = pd.DataFrame(
        np.abs(pca.components_.T),
        index=features[:len(pca.components_.T)],
        columns=["PC1", "PC2"]
    )
    loadings["importance"] = loadings["PC1"] + loadings["PC2"]
    loadings.sort_values("importance", ascending=False).to_csv("pca_feature_importance.csv")
    mlflow.log_artifact("pca_feature_importance.csv")
    os.remove("pca_feature_importance.csv")

    print(f"  2 components: {var_2d*100:.1f}% variance | PC1={pc1_var*100:.1f}% | PC2={pc2_var*100:.1f}%")
    print(f"  70% threshold: {n_70} components | 80%: {n_80} components")

# ═══════════════════════════════════════════════════════════════
# RUN 14: t-SNE
# ═══════════════════════════════════════════════════════════════
print("\n--- t-SNE ---")

with mlflow.start_run(run_name="tSNE_2D"):
    # Pre-reduce with PCA before t-SNE
    pca_pre   = PCA(n_components=min(10, len(features)), random_state=42)
    X_pre     = pca_pre.fit_transform(dr_scaled)
    pre_var   = float(pca_pre.explained_variance_ratio_.sum())

    tsne = TSNE(n_components=2, perplexity=30, max_iter=500, random_state=42)
    X_tsne = tsne.fit_transform(X_pre)

    kl_div = float(tsne.kl_divergence_)

    mlflow.log_params({
        "algorithm":          "TSNE",
        "task":               "dimensionality_reduction",
        "n_components":       2,
        "perplexity":         30,
        "max_iter":           500,
        "pca_preprocessing":  True,
        "pca_components":     min(10, len(features)),
        "sample_size":        SAMPLE_DR,
    })
    mlflow.log_metrics({
        "kl_divergence":          round(kl_div, 4),
        "pca_preprocessing_var":  round(pre_var, 4),
    })
    print(f"  KL Divergence: {kl_div:.4f} | PCA pre-variance: {pre_var*100:.1f}%")

# ═══════════════════════════════════════════════════════════════
# RUN 15: UMAP
# ═══════════════════════════════════════════════════════════════
print("\n--- UMAP ---")

with mlflow.start_run(run_name="UMAP_2D"):
    reducer = umap.UMAP(n_components=2, n_neighbors=30,
                        min_dist=0.1, random_state=42)
    X_umap = reducer.fit_transform(dr_scaled)

    mlflow.log_params({
        "algorithm":    "UMAP",
        "task":         "dimensionality_reduction",
        "n_components": 2,
        "n_neighbors":  30,
        "min_dist":     0.1,
        "sample_size":  SAMPLE_DR,
    })
    mlflow.log_metrics({
        "n_neighbors":  30,
        "min_dist":     0.1,
    })
    print(f"  UMAP complete (n_neighbors=30, min_dist=0.1)")

# ═══════════════════════════════════════════════════════════════
# MODEL REGISTRY — Register best models
# ═══════════════════════════════════════════════════════════════
print("\n--- Registering Best Models ---")

results_df = pd.DataFrame(all_results)

# Best geographic clustering
geo_results = results_df[results_df["task"] == "geographic"].copy()
best_geo    = geo_results.loc[geo_results["silhouette"].idxmax()]
print(f"  Best Geo Clustering : {best_geo['run_name']} (silhouette={best_geo['silhouette']:.4f})")

# Best temporal clustering
temp_results = results_df[results_df["task"] == "temporal"].copy()
best_temp    = temp_results.loc[temp_results["silhouette"].idxmax()]
print(f"  Best Temporal       : {best_temp['run_name']} (silhouette={best_temp['silhouette']:.4f})")

# Save comparison table
results_df.to_csv("mlflow_results_summary.csv", index=False)
print("\n  Saved: mlflow_results_summary.csv")

# ═══════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("MLFLOW EXPERIMENT SUMMARY")
print("=" * 60)
print(f"\nTotal runs logged : {len(all_results) + 3}")  # +3 for PCA/tSNE/UMAP
print(f"Experiment        : {EXPERIMENT_NAME}")
print(f"Tracking UI       : run `mlflow ui` then open http://localhost:5000")

print(f"\n{'Run Name':<30} {'Silhouette':>12} {'DBI':>10} {'Clusters':>10}")
print("-" * 65)
for _, row in results_df.sort_values("silhouette", ascending=False).iterrows():
    flag = " <--BEST" if row["run_name"] == best_geo["run_name"] and row["task"] == "geographic" else ""
    print(f"  {row['run_name']:<28} {row['silhouette']:>12.4f} {row['dbi'] if row['dbi'] else 0.0:>10.4f} {row['n_clusters']:>10}{flag}")

print("\nMLflow tracking complete!")
