"""
app.py — EMIPredict AI  |  Streamlit Home Page
================================================
Multi-page Streamlit application entry point.
Pages are in the /pages folder and appear in the sidebar automatically.
"""

import streamlit as st
import json, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="EMIPredict AI",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Header ─────────────────────────────────────────────────────────
st.title("💳 EMIPredict AI")
st.subheader("Intelligent Financial Risk Assessment Platform")
st.markdown("---")

# ── Project Overview ───────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### What This Platform Does
    EMIPredict AI uses **machine learning** to help financial institutions
    assess loan risk in real time.

    **Two predictions in one shot:**
    - ✅ **EMI Eligibility** — Is the applicant Eligible, High-Risk, or Not Eligible?
    - 💰 **Max Monthly EMI** — What is the maximum safe EMI amount (₹)?

    **Dataset:** 400,000 realistic financial profiles across 5 lending scenarios
    """)

with col2:
    st.markdown("""
    ### Navigate Using the Sidebar
    | Page | What You'll Find |
    |------|-----------------|
    | 📊 EDA | Data distributions, correlations, insights |
    | 🔮 Prediction | Enter applicant details → instant prediction |
    | 📈 Model Performance | Compare all 10 trained ML models |
    | 🗄️ Data Management | View, filter, add, edit, delete records |
    """)

st.markdown("---")

# ── Dataset Stats ──────────────────────────────────────────────────
st.markdown("### 📦 Dataset Overview")
cols = st.columns(5)
scenarios = {
    "E-commerce Shopping": "80,000",
    "Home Appliances": "80,000",
    "Vehicle": "80,000",
    "Personal Loan": "80,000",
    "Education": "80,000",
}
for col, (name, cnt) in zip(cols, scenarios.items()):
    col.metric(name, cnt, "records")

st.markdown("---")

# ── Model Status ───────────────────────────────────────────────────
st.markdown("### 🤖 Model Status")

metrics_path = os.path.join(BASE_DIR, 'models', 'model_metrics.json')
if os.path.exists(metrics_path):
    with open(metrics_path) as f:
        metrics = json.load(f)

    best_clf = metrics['best_classifier']
    best_reg = metrics['best_regressor']
    clf_m    = metrics['classification'][best_clf]
    reg_m    = metrics['regression'][best_reg]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Best Classifier",   best_clf)
    c2.metric("Classifier Accuracy", f"{clf_m['val_accuracy']:.2%}")
    c3.metric("Best Regressor",    best_reg)
    c4.metric("Regressor R²",      f"{reg_m['val_r2']:.4f}")

    st.success("✅ Models are trained and ready.  Head to **🔮 Prediction** to try them!")
else:
    st.warning("""
    ⚠️ Models not found.  Run the training pipeline first:
    ```
    python train.py
    ```
    Then refresh this page.
    """)

st.markdown("---")

# ── Pipeline Architecture ──────────────────────────────────────────
st.markdown("### 🏗️ Pipeline Architecture")
st.code("""
Dataset (400K Records)
        ↓
Step 1: Data Quality Assessment  (missing values, duplicates, distributions)
        ↓
Step 2: Feature Engineering       (13 derived financial ratios + composite score)
        ↓
Step 3: Preprocessing             (LabelEncoding + StandardScaling)
        ↓
Step 4: Train / Val / Test Split  (70% / 15% / 15%, stratified)
        ↓
Step 5: Classification Training   (5 models → MLflow tracking)
        ↓
Step 6: Regression Training       (5 models → MLflow tracking)
        ↓
Step 7: Best Model Selection & Save
        ↓
Streamlit Cloud Deployment
""", language="text")

st.markdown("---")
st.caption("EMIPredict AI · Built with Python, scikit-learn, XGBoost, MLflow & Streamlit · Domain: FinTech & Banking")
