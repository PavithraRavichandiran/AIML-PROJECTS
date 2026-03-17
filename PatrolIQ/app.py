import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from data_loader import load_data

st.set_page_config(
    page_title="PatrolIQ - Smart Safety Analytics",
    page_icon="🚔",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🚔 PatrolIQ - Smart Safety Analytics Platform")
st.markdown("### Urban Crime Intelligence | Chicago Police Department")
st.divider()

col1, col2, col3, col4 = st.columns(4)

import pandas as pd

df = load_data()

col1.metric("Total Crimes Analysed", f"{len(df):,}")
col2.metric("Crime Types", df["primary_type"].nunique())
col3.metric("Police Districts", df["district"].nunique())
col4.metric("Avg Severity Score", f"{df['crime_severity_score'].mean():.2f} / 10")

st.divider()

st.markdown("""
## Navigate Using the Sidebar

| Page | Description |
|---|---|
| **Crime Overview** | Crime type distribution, top crimes, arrest rates |
| **Geographic Hotspots** | Interactive crime maps and cluster zones |
| **Temporal Patterns** | Hourly, daily, seasonal crime trends |
| **Clustering Analysis** | K-Means, DBSCAN, Hierarchical results |
| **Dimensionality Reduction** | PCA, t-SNE, UMAP visualizations |
| **MLflow Dashboard** | Experiment tracking and model comparison |
""")

st.divider()
st.markdown("""
**Domain:** Public Safety & Urban Analytics
**Dataset:** Chicago Crimes 2024–2026 (500K records)
**Project:** GUVI | HCL Capstone — PatrolIQ
""")
