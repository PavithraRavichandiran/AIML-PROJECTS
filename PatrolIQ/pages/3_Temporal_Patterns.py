import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
import streamlit as st
from data_loader import load_data
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Temporal Patterns", page_icon="⏱️", layout="wide")
st.title("⏱️ Temporal Crime Patterns")
st.markdown("Hourly, daily, monthly, and seasonal crime trends.")
st.divider()

df = load_data()

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    crime_types = ["All"] + sorted(df["primary_type"].unique().tolist())
    sel_crime = st.selectbox("Crime Type", crime_types)
    districts = ["All"] + sorted(df["district"].unique().tolist())
    sel_district = st.selectbox("District", districts)

filtered = df.copy()
if sel_crime != "All":
    filtered = filtered[filtered["primary_type"] == sel_crime]
if sel_district != "All":
    filtered = filtered[filtered["district"] == sel_district]

# ── KPIs ──────────────────────────────────────────────────────
hourly    = filtered.groupby("hour").size()
daily     = filtered.groupby("day_of_week").size()
monthly   = filtered.groupby("month").size()
seasonal  = filtered.groupby("season").size()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Peak Hour",   f"{hourly.idxmax()}:00")
c2.metric("Peak Day",    daily.idxmax())
c3.metric("Peak Month",  monthly.idxmax())
c4.metric("Peak Season", seasonal.idxmax())
st.divider()

# ── Hourly trend ──────────────────────────────────────────────
st.subheader("Crimes by Hour of Day")
hourly_df = hourly.reset_index()
hourly_df.columns = ["Hour", "Crimes"]
fig1 = px.line(hourly_df, x="Hour", y="Crimes",
               markers=True, line_shape="spline",
               color_discrete_sequence=["crimson"],
               title="Crime Volume by Hour (0-23)")
fig1.add_vline(x=hourly.idxmax(), line_dash="dash", line_color="navy",
               annotation_text=f"Peak: {hourly.idxmax()}:00",
               annotation_position="top right")
fig1.update_layout(height=350)
st.plotly_chart(fig1, use_container_width=True)

# ── Day & Month ───────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Crimes by Day of Week")
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    daily_df = filtered.groupby("day_of_week").size().reindex(day_order).reset_index()
    daily_df.columns = ["Day", "Crimes"]
    daily_df["Weekend"] = daily_df["Day"].isin(["Saturday", "Sunday"])
    fig2 = px.bar(daily_df, x="Day", y="Crimes",
                  color="Weekend",
                  color_discrete_map={True: "#e74c3c", False: "#3498db"},
                  title="Crime by Day (red = weekend)")
    fig2.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("Crimes by Month")
    month_names = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                   7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
    monthly_df = filtered.groupby("month").size().reset_index()
    monthly_df.columns = ["Month", "Crimes"]
    monthly_df["Month Name"] = monthly_df["Month"].map(month_names)
    fig3 = px.bar(monthly_df, x="Month Name", y="Crimes",
                  color="Crimes", color_continuous_scale="YlOrRd",
                  title="Crime by Month",
                  category_orders={"Month Name": list(month_names.values())})
    fig3.update_layout(height=350)
    st.plotly_chart(fig3, use_container_width=True)

# ── Heatmap: hour vs day ──────────────────────────────────────
st.subheader("Crime Heatmap: Hour of Day vs Day of Week")
pivot = filtered.pivot_table(index="day_of_week", columns="hour",
                              values="id", aggfunc="count")
pivot = pivot.reindex(day_order).fillna(0)

fig4 = px.imshow(pivot,
                 color_continuous_scale="YlOrRd",
                 title="Crime Intensity: Hour x Day (darker = more crimes)",
                 labels={"x": "Hour of Day", "y": "Day of Week", "color": "Crimes"},
                 aspect="auto",
                 height=350)
st.plotly_chart(fig4, use_container_width=True)

# ── Seasonal & Temporal clusters ─────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("Crimes by Season")
    season_df = filtered.groupby("season").size().reset_index()
    season_df.columns = ["Season", "Crimes"]
    season_colors = {"Winter":"#3498db","Spring":"#2ecc71",
                     "Summer":"#e74c3c","Fall":"#f39c12"}
    fig5 = px.pie(season_df, values="Crimes", names="Season",
                  color="Season", color_discrete_map=season_colors,
                  title="Seasonal Crime Distribution")
    st.plotly_chart(fig5, use_container_width=True)

with col4:
    st.subheader("Temporal Cluster Labels")
    tcluster_df = filtered["temporal_label"].value_counts().reset_index()
    tcluster_df.columns = ["Cluster", "Count"]
    fig6 = px.bar(tcluster_df, x="Cluster", y="Count",
                  color="Count", color_continuous_scale="Blues",
                  title="Temporal Crime Pattern Clusters")
    fig6.update_layout(xaxis_tickangle=-15)
    st.plotly_chart(fig6, use_container_width=True)

# ── Weekend vs Weekday ────────────────────────────────────────
st.subheader("Weekend vs Weekday — Hourly Pattern")
wknd  = filtered[filtered["is_weekend"] == 1].groupby("hour").size().reset_index()
wkday = filtered[filtered["is_weekend"] == 0].groupby("hour").size().reset_index()
wknd.columns  = ["Hour", "Crimes"]
wkday.columns = ["Hour", "Crimes"]
wknd["Type"]  = "Weekend"
wkday["Type"] = "Weekday"

combined = pd.concat([wknd, wkday])
fig7 = px.line(combined, x="Hour", y="Crimes", color="Type",
               markers=True, line_shape="spline",
               color_discrete_map={"Weekend":"#e74c3c","Weekday":"#3498db"},
               title="Hourly Pattern: Weekend vs Weekday")
fig7.update_layout(height=350)
st.plotly_chart(fig7, use_container_width=True)
