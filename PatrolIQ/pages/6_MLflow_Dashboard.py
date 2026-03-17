import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="MLflow Dashboard", page_icon="🧪", layout="wide")
st.title("🧪 MLflow Experiment Dashboard")
st.markdown("Model tracking, experiment comparison, and best model selection.")
st.divider()

@st.cache_data
def load_results():
    try:
        return pd.read_csv(os.path.join(BASE_DIR, "mlflow_results_summary.csv"))
    except:
        return None

results = load_results()

if results is None:
    st.error("mlflow_results_summary.csv not found. Run mlflow_tracking.py first.")
    st.stop()

# ── KPIs ──────────────────────────────────────────────────────
best_sil = results["silhouette"].max()
best_run = results.loc[results["silhouette"].idxmax(), "run_name"]
total    = len(results)
geo_best = results[results["task"] == "geographic"]["silhouette"].max()
temp_best= results[results["task"] == "temporal"]["silhouette"].max()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Runs", total)
c2.metric("Best Run", best_run)
c3.metric("Best Geo Silhouette", f"{geo_best:.4f}")
c4.metric("Best Temporal Silhouette", f"{temp_best:.4f}")

st.divider()

# ── Filter by task ────────────────────────────────────────────
with st.sidebar:
    st.header("Filter Runs")
    task_filter = st.multiselect("Task", results["task"].unique().tolist(),
                                  default=results["task"].unique().tolist())
    algo_filter = st.multiselect("Algorithm", results["algorithm"].unique().tolist(),
                                  default=results["algorithm"].unique().tolist())

filtered_r = results[
    (results["task"].isin(task_filter)) &
    (results["algorithm"].isin(algo_filter))
].copy()

# ── Silhouette comparison ─────────────────────────────────────
st.subheader("Silhouette Score — All Runs")
filtered_sorted = filtered_r.sort_values("silhouette", ascending=False)
fig1 = px.bar(filtered_sorted, x="run_name", y="silhouette",
              color="algorithm",
              title="Silhouette Score Comparison (higher = better)",
              labels={"run_name": "Run", "silhouette": "Silhouette Score"},
              height=400)
fig1.add_hline(y=0.5, line_dash="dash", line_color="red",
               annotation_text="Target: 0.5", annotation_position="top right")
fig1.update_layout(xaxis_tickangle=-35)
st.plotly_chart(fig1, use_container_width=True)

# ── DBI comparison ────────────────────────────────────────────
st.subheader("Davies-Bouldin Index — All Runs")
fig2 = px.bar(filtered_sorted, x="run_name", y="dbi",
              color="algorithm",
              title="Davies-Bouldin Index (lower = better)",
              labels={"run_name": "Run", "dbi": "DBI"},
              height=400)
fig2.update_layout(xaxis_tickangle=-35)
st.plotly_chart(fig2, use_container_width=True)

# ── Scatter: Silhouette vs DBI ────────────────────────────────
st.subheader("Silhouette vs DBI — Trade-off View")
fig3 = px.scatter(filtered_r, x="silhouette", y="dbi",
                  color="algorithm", text="run_name",
                  size=[10]*len(filtered_r),
                  title="Silhouette vs DBI (top-right is ideal: high sil, low DBI)",
                  labels={"silhouette":"Silhouette Score","dbi":"Davies-Bouldin Index"},
                  height=450)
fig3.add_hline(y=1.0, line_dash="dot", line_color="gray", opacity=0.4)
fig3.add_vline(x=0.5, line_dash="dot", line_color="green", opacity=0.4,
               annotation_text="Target sil=0.5")
fig3.update_traces(textposition="top center", textfont_size=8)
st.plotly_chart(fig3, use_container_width=True)

# ── Inertia for K-Means ───────────────────────────────────────
kmeans_geo = results[(results["algorithm"] == "KMeans") &
                     (results["task"] == "geographic")].copy()
if not kmeans_geo.empty and "inertia" in kmeans_geo.columns:
    st.subheader("K-Means Inertia vs K (Elbow Method)")
    fig4 = px.line(kmeans_geo.sort_values("n_clusters"),
                   x="n_clusters", y="inertia",
                   markers=True, line_shape="linear",
                   color_discrete_sequence=["crimson"],
                   title="Inertia vs Number of Clusters",
                   labels={"n_clusters":"K","inertia":"Inertia"},
                   height=350)
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ── Full results table ────────────────────────────────────────
st.subheader("All Experiment Runs")
display_cols = ["run_name", "algorithm", "task", "n_clusters", "silhouette", "dbi"]
st.dataframe(filtered_r[display_cols].sort_values("silhouette", ascending=False).round(4),
             use_container_width=True)

st.divider()
st.info("To view full MLflow UI with artifacts and model registry, run: `mlflow ui` in the terminal and open http://localhost:5000")
