import streamlit as st
from data_loader import load_data
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Clustering Analysis", page_icon="🔵", layout="wide")
st.title("🔵 Clustering Analysis")
st.markdown("K-Means, DBSCAN, and Hierarchical clustering results and comparisons.")
st.divider()

@st.cache_data
def load_mlflow_results():
    try:
        return pd.read_csv("mlflow_results_summary.csv")
    except:
        return None

df       = load_data()
results  = load_mlflow_results()

# ── Algorithm comparison ──────────────────────────────────────
st.subheader("Algorithm Performance Comparison")

if results is not None:
    geo_res = results[results["task"] == "geographic"].copy()

    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.bar(geo_res.sort_values("silhouette", ascending=False),
                      x="run_name", y="silhouette",
                      color="silhouette", color_continuous_scale="RdYlGn",
                      title="Silhouette Score (higher = better, target >= 0.5)")
        fig1.add_hline(y=0.5, line_dash="dash", line_color="red",
                       annotation_text="Target: 0.5")
        fig1.update_layout(xaxis_tickangle=-30, height=400)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.bar(geo_res.sort_values("dbi"),
                      x="run_name", y="dbi",
                      color="dbi", color_continuous_scale="RdYlGn_r",
                      title="Davies-Bouldin Index (lower = better)")
        fig2.update_layout(xaxis_tickangle=-30, height=400)
        st.plotly_chart(fig2, use_container_width=True)

    # Full results table
    with st.expander("Full MLflow Results Table"):
        st.dataframe(results[["run_name","algorithm","task","n_clusters",
                               "silhouette","dbi"]].round(4),
                     use_container_width=True)
else:
    st.warning("Run mlflow_tracking.py first to see comparison results.")

st.divider()

# ── Geographic cluster explorer ───────────────────────────────
st.subheader("Geographic Cluster Zone Explorer")

sample = df.sample(min(30000, len(df)), random_state=42)

col3, col4 = st.columns([3, 2])

with col3:
    fig3 = px.scatter_mapbox(
        sample,
        lat="latitude", lon="longitude",
        color=sample["geo_cluster"].astype(str),
        hover_data={"primary_type": True, "district": True,
                    "crime_severity_score": True},
        zoom=10,
        center={"lat": 41.85, "lon": -87.65},
        mapbox_style="carto-positron",
        opacity=0.5,
        title="K-Means Geographic Clusters (7 Zones)",
        height=500
    )
    fig3.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Cluster Zone Profiles")
    profile = df.groupby("geo_cluster").agg(
        Crimes=("id", "count"),
        Arrest_Rate=("arrest", "mean"),
        Avg_Severity=("crime_severity_score", "mean"),
        Top_Crime=("primary_type", lambda x: x.value_counts().idxmax()),
    ).round(3).reset_index()
    profile["Arrest_Rate"] = (profile["Arrest_Rate"] * 100).round(1).astype(str) + "%"
    profile.columns = ["Zone", "Crimes", "Arrest Rate", "Avg Severity", "Top Crime"]
    st.dataframe(profile, use_container_width=True, height=400)

st.divider()

# ── Temporal cluster analysis ─────────────────────────────────
st.subheader("Temporal Pattern Clusters")

col5, col6 = st.columns(2)

with col5:
    temporal_profile = df.groupby("temporal_label").agg(
        Crimes=("id", "count"),
        Avg_Hour=("hour", "mean"),
        Weekend_Pct=("is_weekend", "mean"),
        Avg_Severity=("crime_severity_score", "mean")
    ).round(2).reset_index()
    temporal_profile["Weekend_Pct"] = (temporal_profile["Weekend_Pct"]*100).round(1).astype(str)+"%"
    temporal_profile.columns = ["Cluster", "Crimes", "Avg Hour", "Weekend %", "Avg Severity"]

    fig4 = px.bar(temporal_profile, x="Cluster", y="Crimes",
                  color="Avg Severity", color_continuous_scale="YlOrRd",
                  title="Temporal Cluster Sizes")
    fig4.update_layout(height=350, xaxis_tickangle=-15)
    st.plotly_chart(fig4, use_container_width=True)

with col6:
    # Hour distribution per temporal cluster
    tcluster_hour = df.groupby(["temporal_label", "hour"]).size().reset_index(name="Crimes")
    fig5 = px.line(tcluster_hour, x="hour", y="Crimes",
                   color="temporal_label", markers=False,
                   line_shape="spline",
                   title="Hourly Pattern by Temporal Cluster")
    fig5.update_layout(height=350)
    st.plotly_chart(fig5, use_container_width=True)

st.dataframe(temporal_profile, use_container_width=True)

st.divider()

# ── Elbow method plot ─────────────────────────────────────────
st.subheader("Elbow Method — Choosing Optimal K")
try:
    img = open("clustering_plots/A1_elbow_method.png", "rb").read()
    st.image(img, caption="Elbow Method: K vs Inertia", use_container_width=True)
except:
    st.info("Run clustering.py to generate elbow plot.")
