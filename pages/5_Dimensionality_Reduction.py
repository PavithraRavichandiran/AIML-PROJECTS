import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

st.set_page_config(page_title="Dimensionality Reduction", page_icon="📉", layout="wide")
st.title("📉 Dimensionality Reduction")
st.markdown("PCA, t-SNE, and UMAP visualizations of high-dimensional crime patterns.")
st.divider()

@st.cache_data
def load_dr_data():
    try:
        return pd.read_csv("chicago_crimes_dr.csv")
    except:
        return None

dr_df = load_dr_data()

# ── PCA metrics ───────────────────────────────────────────────
st.subheader("PCA — Variance Explained")

c1, c2, c3, c4 = st.columns(4)
c1.metric("2 Components", "47.5% variance")
c2.metric("3 Components", "57.1% variance")
c3.metric("70% threshold", "6 components")
c4.metric("80% threshold", "7 components")

st.divider()

# ── Tabs ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["PCA", "t-SNE", "UMAP", "Comparison"])

COLOR_BY_OPTIONS = {
    "Geographic Cluster": "geo_cluster",
    "Temporal Cluster": "temporal_cluster",
    "Crime Severity": "crime_severity_score",
    "District": "district",
    "Hour of Day": "hour",
    "Is Weekend": "is_weekend",
}

with tab1:
    st.subheader("PCA 2D Scatter")
    color_by_label = st.selectbox("Color by", list(COLOR_BY_OPTIONS.keys()), key="pca_color")
    color_col = COLOR_BY_OPTIONS[color_by_label]

    if dr_df is not None and "pca_1" in dr_df.columns:
        fig = px.scatter(dr_df, x="pca_1", y="pca_2",
                         color=dr_df[color_col].astype(str) if color_col in ["geo_cluster","temporal_cluster","district","is_weekend"] else dr_df[color_col],
                         color_continuous_scale="YlOrRd" if color_col not in ["geo_cluster","temporal_cluster"] else None,
                         opacity=0.5,
                         title=f"PCA 2D — colored by {color_by_label}",
                         labels={"pca_1": "PC1 (40.7%)", "pca_2": "PC2 (11.3%)"},
                         height=550)
        fig.update_traces(marker=dict(size=3))
        st.plotly_chart(fig, use_container_width=True)

        # Feature importance
        st.subheader("Top 10 Features by PCA Importance")
        try:
            fi = pd.read_csv("dr_plots/../pca_feature_importance.csv") if os.path.exists("pca_feature_importance.csv") else None
        except:
            fi = None

        if fi is None:
            # Rebuild from plot image
            st.image("dr_plots/03_pca_feature_importance.png",
                     caption="Feature Importance (PCA loadings)", use_container_width=True)
        else:
            fig_fi = px.bar(fi.head(10), x="importance", y=fi.columns[0],
                            orientation="h", color="importance",
                            color_continuous_scale="Blues",
                            title="Top Features Driving Crime Patterns")
            st.plotly_chart(fig_fi, use_container_width=True)

        # Scree plot image
        st.subheader("Scree Plot & Cumulative Variance")
        st.image("dr_plots/01_pca_scree_variance.png",
                 caption="PCA Scree Plot", use_container_width=True)
    else:
        st.warning("Run dimensionality_reduction.py first to generate PCA results.")

with tab2:
    st.subheader("t-SNE 2D Scatter")
    color_by_label2 = st.selectbox("Color by", list(COLOR_BY_OPTIONS.keys()), key="tsne_color")
    color_col2 = COLOR_BY_OPTIONS[color_by_label2]

    if dr_df is not None and "tsne_1" in dr_df.columns:
        fig2 = px.scatter(dr_df, x="tsne_1", y="tsne_2",
                          color=dr_df[color_col2].astype(str) if color_col2 in ["geo_cluster","temporal_cluster","district","is_weekend"] else dr_df[color_col2],
                          color_continuous_scale="YlOrRd" if color_col2 not in ["geo_cluster","temporal_cluster"] else None,
                          opacity=0.5,
                          title=f"t-SNE 2D — colored by {color_by_label2}",
                          labels={"tsne_1": "t-SNE Dim 1", "tsne_2": "t-SNE Dim 2"},
                          height=550)
        fig2.update_traces(marker=dict(size=3))
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("Parameters: perplexity=40, max_iter=1000 | KL Divergence: 1.6489")
    else:
        st.warning("Run dimensionality_reduction.py first to generate t-SNE results.")

with tab3:
    st.subheader("UMAP 2D Scatter")
    color_by_label3 = st.selectbox("Color by", list(COLOR_BY_OPTIONS.keys()), key="umap_color")
    color_col3 = COLOR_BY_OPTIONS[color_by_label3]

    if dr_df is not None and "umap_1" in dr_df.columns:
        fig3 = px.scatter(dr_df, x="umap_1", y="umap_2",
                          color=dr_df[color_col3].astype(str) if color_col3 in ["geo_cluster","temporal_cluster","district","is_weekend"] else dr_df[color_col3],
                          color_continuous_scale="YlOrRd" if color_col3 not in ["geo_cluster","temporal_cluster"] else None,
                          opacity=0.5,
                          title=f"UMAP 2D — colored by {color_by_label3}",
                          labels={"umap_1": "UMAP Dim 1", "umap_2": "UMAP Dim 2"},
                          height=550)
        fig3.update_traces(marker=dict(size=3))
        st.plotly_chart(fig3, use_container_width=True)
        st.caption("Parameters: n_neighbors=30, min_dist=0.1")
    else:
        st.warning("Run dimensionality_reduction.py first to generate UMAP results.")

with tab4:
    st.subheader("PCA vs t-SNE vs UMAP — Side by Side")
    st.image("dr_plots/07_dr_comparison.png",
             caption="Comparison: PCA vs t-SNE vs UMAP (colored by geographic cluster)",
             use_container_width=True)

    st.markdown("""
    ### Key Observations
    | Method | Strength | Limitation |
    |---|---|---|
    | **PCA** | Fast, interpretable, preserves global variance | Linear only — misses complex structure |
    | **t-SNE** | Reveals local cluster structure clearly | Slow, non-deterministic, no global meaning |
    | **UMAP** | Fast + preserves both local and global structure | Sensitive to hyperparameters |
    """)
