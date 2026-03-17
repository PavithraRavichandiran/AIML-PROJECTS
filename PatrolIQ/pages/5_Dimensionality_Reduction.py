import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
BASE_DIR = os.path.join(os.path.dirname(__file__), '..')

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import warnings
warnings.filterwarnings("ignore")

from data_loader import load_data

st.set_page_config(page_title="Dimensionality Reduction", page_icon="📉", layout="wide")
st.title("📉 Dimensionality Reduction")
st.markdown("PCA, t-SNE, and UMAP visualizations of high-dimensional crime patterns.")
st.divider()

DR_FEATURES = [
    "hour", "day_num", "month", "is_weekend",
    "crime_severity_score", "crime_type_encoded",
    "location_type_encoded", "latitude", "longitude",
    "beat", "district", "ward", "community_area",
    "lat_bin", "lon_bin", "lat_norm", "lon_norm",
    "geo_cluster", "temporal_cluster",
    "x_coordinate", "y_coordinate", "year"
]

SAMPLE_SIZE = 5000

COLOR_BY_OPTIONS = {
    "Geographic Cluster":  "geo_cluster",
    "Temporal Cluster":    "temporal_cluster",
    "Crime Severity":      "crime_severity_score",
    "District":            "district",
    "Hour of Day":         "hour",
    "Is Weekend":          "is_weekend",
}

@st.cache_data(show_spinner="Computing PCA, t-SNE, UMAP — runs once then cached...")
def compute_dr(sample_size=SAMPLE_SIZE):
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE

    df_full  = load_data()
    features = [f for f in DR_FEATURES if f in df_full.columns]
    sample   = df_full.sample(min(sample_size, len(df_full)), random_state=42).copy()
    X        = sample[features].fillna(0).values
    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # PCA 2D
    pca      = PCA(n_components=2, random_state=42)
    X_pca    = pca.fit_transform(X_scaled)
    var_2d   = pca.explained_variance_ratio_.sum() * 100
    pc1_var  = pca.explained_variance_ratio_[0] * 100
    pc2_var  = pca.explained_variance_ratio_[1] * 100

    # PCA full (for scree)
    pca_full = PCA(random_state=42).fit(X_scaled)
    cumvar   = np.cumsum(pca_full.explained_variance_ratio_)
    n_70     = int(np.argmax(cumvar >= 0.70) + 1)
    n_80     = int(np.argmax(cumvar >= 0.80) + 1)

    loadings = pd.DataFrame(
        np.abs(pca.components_.T),
        index=features, columns=["PC1", "PC2"]
    )
    loadings["importance"] = loadings["PC1"] + loadings["PC2"]
    loadings = loadings.sort_values("importance", ascending=False)

    # PCA 3D
    pca3   = PCA(n_components=3, random_state=42)
    X_pca3 = pca3.fit_transform(X_scaled)
    var_3d = pca3.explained_variance_ratio_.sum() * 100

    # t-SNE
    pca_pre = PCA(n_components=min(10, len(features)), random_state=42)
    X_pre   = pca_pre.fit_transform(X_scaled)
    tsne    = TSNE(n_components=2, perplexity=30, max_iter=500, random_state=42)
    X_tsne  = tsne.fit_transform(X_pre)

    # UMAP
    try:
        import umap
        reducer = umap.UMAP(n_components=2, n_neighbors=15,
                            min_dist=0.1, random_state=42)
        X_umap  = reducer.fit_transform(X_scaled)
    except Exception:
        X_umap  = X_tsne

    sample["pca_1"]  = X_pca[:, 0]
    sample["pca_2"]  = X_pca[:, 1]
    sample["pca3_1"] = X_pca3[:, 0]
    sample["pca3_2"] = X_pca3[:, 1]
    sample["pca3_3"] = X_pca3[:, 2]
    sample["tsne_1"] = X_tsne[:, 0]
    sample["tsne_2"] = X_tsne[:, 1]
    sample["umap_1"] = X_umap[:, 0]
    sample["umap_2"] = X_umap[:, 1]

    return {
        "df": sample, "var_2d": var_2d, "var_3d": var_3d,
        "pc1_var": pc1_var, "pc2_var": pc2_var,
        "n_70": n_70, "n_80": n_80,
        "loadings": loadings, "cumvar": cumvar,
        "scree": pca_full.explained_variance_ratio_ * 100,
    }

with st.spinner("Running dimensionality reduction..."):
    dr = compute_dr()

df_dr    = dr["df"]
loadings = dr["loadings"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("2 Components",  f"{dr['var_2d']:.1f}% variance")
c2.metric("3 Components",  f"{dr['var_3d']:.1f}% variance")
c3.metric("70% threshold", f"{dr['n_70']} components")
c4.metric("80% threshold", f"{dr['n_80']} components")
st.divider()

def make_scatter(df, x, y, color_col, title, xlabel, ylabel):
    is_cat = color_col in ["geo_cluster","temporal_cluster","district","is_weekend"]
    fig = px.scatter(
        df, x=x, y=y,
        color=df[color_col].astype(str) if is_cat else df[color_col],
        color_continuous_scale="YlOrRd" if not is_cat else None,
        opacity=0.6, title=title,
        labels={x: xlabel, y: ylabel}, height=520
    )
    fig.update_traces(marker=dict(size=4))
    return fig

tab1, tab2, tab3, tab4 = st.tabs(["PCA", "t-SNE", "UMAP", "Comparison"])

with tab1:
    st.subheader("PCA 2D Scatter")
    col_label = st.selectbox("Color by", list(COLOR_BY_OPTIONS.keys()), key="pca")
    st.plotly_chart(make_scatter(
        df_dr, "pca_1", "pca_2", COLOR_BY_OPTIONS[col_label],
        f"PCA 2D — {col_label} ({dr['var_2d']:.1f}% variance)",
        f"PC1 ({dr['pc1_var']:.1f}%)", f"PC2 ({dr['pc2_var']:.1f}%)"
    ), use_container_width=True)

    st.subheader("Top 10 Features by PCA Importance")
    fig_fi = px.bar(loadings.head(10).reset_index(),
                    x="importance", y="index", orientation="h",
                    color="importance", color_continuous_scale="Blues",
                    title="Feature Importance (PC1 + PC2 loadings)",
                    labels={"index": "Feature"})
    fig_fi.update_layout(height=400)
    st.plotly_chart(fig_fi, use_container_width=True)

    st.subheader("Scree Plot — Cumulative Variance")
    scree_df = pd.DataFrame({
        "Component":    range(1, len(dr["scree"]) + 1),
        "Cumulative %": np.cumsum(dr["scree"])
    })
    fig_scree = px.line(scree_df.head(15), x="Component", y="Cumulative %",
                        markers=True, title="Cumulative Explained Variance")
    fig_scree.add_hline(y=70, line_dash="dash", line_color="green",
                         annotation_text="70%")
    fig_scree.add_hline(y=80, line_dash="dash", line_color="orange",
                         annotation_text="80%")
    fig_scree.update_layout(height=350)
    st.plotly_chart(fig_scree, use_container_width=True)

with tab2:
    st.subheader("t-SNE 2D Scatter")
    col_label2 = st.selectbox("Color by", list(COLOR_BY_OPTIONS.keys()), key="tsne")
    st.plotly_chart(make_scatter(
        df_dr, "tsne_1", "tsne_2", COLOR_BY_OPTIONS[col_label2],
        f"t-SNE 2D — {col_label2}", "t-SNE Dim 1", "t-SNE Dim 2"
    ), use_container_width=True)
    st.caption("Parameters: perplexity=30, max_iter=500")

with tab3:
    st.subheader("UMAP 2D Scatter")
    col_label3 = st.selectbox("Color by", list(COLOR_BY_OPTIONS.keys()), key="umap")
    st.plotly_chart(make_scatter(
        df_dr, "umap_1", "umap_2", COLOR_BY_OPTIONS[col_label3],
        f"UMAP 2D — {col_label3}", "UMAP Dim 1", "UMAP Dim 2"
    ), use_container_width=True)
    st.caption("Parameters: n_neighbors=15, min_dist=0.1")

with tab4:
    st.subheader("PCA vs t-SNE vs UMAP — Side by Side")
    col_label4 = st.selectbox("Color by", list(COLOR_BY_OPTIONS.keys()), key="compare")
    col4 = COLOR_BY_OPTIONS[col_label4]
    is_cat = col4 in ["geo_cluster","temporal_cluster","district","is_weekend"]

    c1, c2, c3 = st.columns(3)
    for ax, (x, y), title in zip(
        [c1, c2, c3],
        [("pca_1","pca_2"), ("tsne_1","tsne_2"), ("umap_1","umap_2")],
        ["PCA", "t-SNE", "UMAP"]
    ):
        fig = px.scatter(
            df_dr, x=x, y=y,
            color=df_dr[col4].astype(str) if is_cat else df_dr[col4],
            color_continuous_scale="YlOrRd" if not is_cat else None,
            opacity=0.6, title=title, height=400
        )
        fig.update_traces(marker=dict(size=3))
        fig.update_layout(showlegend=False)
        ax.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    ### Method Comparison
    | Method | Strength | Limitation |
    |---|---|---|
    | **PCA** | Fast, interpretable, preserves global variance | Linear only |
    | **t-SNE** | Reveals local cluster structure | Slow, no global meaning |
    | **UMAP** | Fast + preserves local and global structure | Sensitive to hyperparameters |
    """)
