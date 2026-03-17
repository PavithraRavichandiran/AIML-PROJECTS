import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
import streamlit as st
from data_loader import load_data
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Crime Overview", page_icon="📊", layout="wide")
st.title("📊 Crime Overview")
st.markdown("Distribution of crime types, arrest rates, and severity across Chicago.")
st.divider()

df = load_data()

# ── Filters ───────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    districts = ["All"] + sorted(df["district"].unique().tolist())
    sel_district = st.selectbox("District", districts)
    seasons = ["All"] + df["season"].unique().tolist()
    sel_season = st.selectbox("Season", seasons)
    top_n = st.slider("Top N Crime Types", 5, 31, 15)

filtered = df.copy()
if sel_district != "All":
    filtered = filtered[filtered["district"] == sel_district]
if sel_season != "All":
    filtered = filtered[filtered["season"] == sel_season]

# ── KPIs ──────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Crimes", f"{len(filtered):,}")
c2.metric("Arrest Rate", f"{filtered['arrest'].mean()*100:.1f}%")
c3.metric("Domestic Rate", f"{filtered['domestic'].mean()*100:.1f}%")
c4.metric("Avg Severity", f"{filtered['crime_severity_score'].mean():.2f}")

st.divider()

# ── Crime type bar chart ──────────────────────────────────────
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader(f"Top {top_n} Crime Types")
    crime_counts = filtered["primary_type"].value_counts().head(top_n).reset_index()
    crime_counts.columns = ["Crime Type", "Count"]
    fig = px.bar(crime_counts, x="Count", y="Crime Type", orientation="h",
                 color="Count", color_continuous_scale="Reds",
                 title=f"Top {top_n} Crime Types")
    fig.update_layout(height=500, showlegend=False,
                      yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Crime Share (Pie)")
    top5 = filtered["primary_type"].value_counts().head(6)
    others = len(filtered) - top5.sum()
    pie_data = pd.concat([top5, pd.Series({"OTHER": others})])
    fig2 = px.pie(values=pie_data.values, names=pie_data.index,
                  color_discrete_sequence=px.colors.sequential.RdBu,
                  title="Crime Type Distribution")
    fig2.update_layout(height=500)
    st.plotly_chart(fig2, use_container_width=True)

# ── Arrest rate by crime type ─────────────────────────────────
st.subheader("Arrest Rate by Crime Type (Top 15)")
top15 = filtered["primary_type"].value_counts().head(15).index
arrest_df = (filtered[filtered["primary_type"].isin(top15)]
             .groupby("primary_type")["arrest"]
             .mean().reset_index())
arrest_df.columns = ["Crime Type", "Arrest Rate"]
arrest_df["Arrest Rate %"] = (arrest_df["Arrest Rate"] * 100).round(1)
arrest_df = arrest_df.sort_values("Arrest Rate %", ascending=True)

fig3 = px.bar(arrest_df, x="Arrest Rate %", y="Crime Type", orientation="h",
              color="Arrest Rate %", color_continuous_scale="RdYlGn",
              title="Arrest Rate (%) by Crime Type")
fig3.add_vline(x=arrest_df["Arrest Rate %"].mean(), line_dash="dash",
               line_color="navy",
               annotation_text=f"Avg {arrest_df['Arrest Rate %'].mean():.1f}%")
fig3.update_layout(height=450, yaxis=dict(autorange="reversed"))
st.plotly_chart(fig3, use_container_width=True)

# ── Severity distribution ─────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("Crime Severity Distribution")
    sev = filtered["crime_severity_score"].value_counts().sort_index().reset_index()
    sev.columns = ["Severity Score", "Count"]
    fig4 = px.bar(sev, x="Severity Score", y="Count",
                  color="Severity Score", color_continuous_scale="YlOrRd",
                  title="Crimes by Severity Score (1=Minor, 10=Critical)")
    st.plotly_chart(fig4, use_container_width=True)

with col4:
    st.subheader("Domestic vs Non-Domestic")
    dom = filtered["domestic"].value_counts().reset_index()
    dom.columns = ["Domestic", "Count"]
    dom["Domestic"] = dom["Domestic"].map({True: "Domestic", False: "Non-Domestic"})
    fig5 = px.pie(dom, values="Count", names="Domestic",
                  color_discrete_map={"Domestic": "#e74c3c", "Non-Domestic": "#3498db"},
                  title="Domestic Incident Rate")
    st.plotly_chart(fig5, use_container_width=True)

# ── Raw data table ────────────────────────────────────────────
with st.expander("View Raw Data Sample (500 rows)"):
    st.dataframe(filtered.sample(min(500, len(filtered)))[
        ["date", "primary_type", "description", "district",
         "arrest", "domestic", "crime_severity_score", "season"]
    ].sort_values("date", ascending=False), use_container_width=True)
