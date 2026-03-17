import streamlit as st
from data_loader import load_data
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Geographic Hotspots", page_icon="🗺️", layout="wide")
st.title("🗺️ Geographic Crime Hotspots")
st.markdown("Explore crime clusters and hotspot zones across Chicago.")
st.divider()

df = load_data()

# ── Sidebar filters ───────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    crime_types = ["All"] + sorted(df["primary_type"].unique().tolist())
    sel_crime = st.selectbox("Crime Type", crime_types)
    sel_cluster = st.multiselect("Geo Cluster (Zone)", sorted(df["geo_cluster"].unique()),
                                  default=sorted(df["geo_cluster"].unique()))
    sample_size = st.slider("Map Sample Size", 5000, 50000, 20000, step=5000)

filtered = df.copy()
if sel_crime != "All":
    filtered = filtered[filtered["primary_type"] == sel_crime]
if sel_cluster:
    filtered = filtered[filtered["geo_cluster"].isin(sel_cluster)]

sample = filtered.sample(min(sample_size, len(filtered)), random_state=42)

# ── KPIs ──────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Filtered Crimes", f"{len(filtered):,}")
c2.metric("Zones Selected", len(sel_cluster))
c3.metric("Top District", f"District {filtered['district'].value_counts().idxmax()}")
c4.metric("Avg Severity", f"{filtered['crime_severity_score'].mean():.2f}")
st.divider()

# ── Tab layout ────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["Crime Scatter Map", "Cluster Heatmap", "District Analysis"])

with tab1:
    st.subheader("Crime Location Map — colored by Cluster Zone")
    fig = px.scatter_mapbox(
        sample,
        lat="latitude", lon="longitude",
        color="geo_cluster",
        color_continuous_scale="turbo",
        hover_data={"primary_type": True, "crime_severity_score": True,
                    "district": True, "hour": True, "date": True},
        zoom=10,
        center={"lat": 41.85, "lon": -87.65},
        opacity=0.5,
        title="Chicago Crime Hotspot Clusters",
        mapbox_style="carto-positron",
        size_max=5,
        height=600
    )
    fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Crime Density Heatmap")
    fig2 = px.density_mapbox(
        sample,
        lat="latitude", lon="longitude",
        z="crime_severity_score",
        radius=8,
        zoom=10,
        center={"lat": 41.85, "lon": -87.65},
        mapbox_style="carto-darkmatter",
        color_continuous_scale="YlOrRd",
        title="Crime Density Heatmap (weighted by severity)",
        height=600
    )
    fig2.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.subheader("Crime Distribution by District")

    col1, col2 = st.columns(2)

    with col1:
        dist_counts = filtered.groupby("district").size().reset_index(name="Count")
        dist_counts = dist_counts.sort_values("Count", ascending=False)
        fig3 = px.bar(dist_counts, x="district", y="Count",
                      color="Count", color_continuous_scale="Reds",
                      title="Total Crimes per District",
                      labels={"district": "District", "Count": "Crime Count"})
        fig3.update_layout(height=400)
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        dist_arrest = filtered.groupby("district")["arrest"].mean().reset_index()
        dist_arrest.columns = ["District", "Arrest Rate"]
        dist_arrest["Arrest Rate %"] = (dist_arrest["Arrest Rate"] * 100).round(1)
        dist_arrest = dist_arrest.sort_values("Arrest Rate %", ascending=False)
        fig4 = px.bar(dist_arrest, x="District", y="Arrest Rate %",
                      color="Arrest Rate %", color_continuous_scale="RdYlGn",
                      title="Arrest Rate (%) per District")
        fig4.update_layout(height=400)
        st.plotly_chart(fig4, use_container_width=True)

    # Cluster profile table
    st.subheader("Cluster Zone Profiles")
    cluster_profile = filtered.groupby("geo_cluster").agg(
        Total_Crimes=("id", "count"),
        Arrest_Rate=("arrest", lambda x: f"{x.mean()*100:.1f}%"),
        Avg_Severity=("crime_severity_score", lambda x: f"{x.mean():.2f}"),
        Top_Crime=("primary_type", lambda x: x.value_counts().idxmax()),
        Domestic_Rate=("domestic", lambda x: f"{x.mean()*100:.1f}%"),
    ).reset_index()
    cluster_profile.columns = ["Zone", "Total Crimes", "Arrest Rate",
                                "Avg Severity", "Top Crime Type", "Domestic Rate"]
    st.dataframe(cluster_profile, use_container_width=True)
