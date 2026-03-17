"""
pages/1_EDA.py — Exploratory Data Analysis
===========================================
Loads the dataset and shows:
  - Target class distribution (pie + bar)
  - EMI scenario breakdown
  - Salary & credit score distributions
  - Correlation heatmap of numerical features
  - Financial risk analysis by eligibility class
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="EDA | EMIPredict AI", page_icon="📊", layout="wide")
st.title("📊 Exploratory Data Analysis")
st.markdown("---")

# ── Load Data ──────────────────────────────────────────────────────
@st.cache_data
def load_data():
    path = 'data/EMI_dataset.csv'
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path, low_memory=False)
    # Fix real-world data types (stored as strings in source CSV)
    for col in ['age', 'monthly_salary', 'bank_balance']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    # Normalise gender casing
    df['gender'] = df['gender'].str.strip().str.title().replace({'F': 'Female', 'M': 'Male'})
    # Fill missing numerics with median
    df[df.select_dtypes(include='number').columns] = \
        df.select_dtypes(include='number').fillna(df.median(numeric_only=True))
    # Add derived features for analysis
    expense_cols = ['monthly_rent', 'school_fees', 'college_fees',
                    'travel_expenses', 'groceries_utilities', 'other_monthly_expenses']
    df['total_expenses']       = df[expense_cols].sum(axis=1) + df['current_emi_amount']
    df['disposable_income']    = df['monthly_salary'] - df['total_expenses']
    df['debt_to_income_ratio'] = (df['total_expenses'] / df['monthly_salary']).clip(0, 2)
    return df

df = load_data()

if df is None:
    st.error("Dataset not found.  Run `python generate_dataset.py` first.")
    st.stop()

# ── Overview Metrics ───────────────────────────────────────────────
st.markdown("### Quick Stats")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Records",   f"{len(df):,}")
c2.metric("Features",        "22 + 2 targets")
c3.metric("EMI Scenarios",   "5")
c4.metric("Avg Salary",      f"₹{df['monthly_salary'].mean():,.0f}")
c5.metric("Avg Credit Score",f"{df['credit_score'].mean():.0f}")

st.markdown("---")

# ── Row 1: Target Distribution ─────────────────────────────────────
st.markdown("### 🎯 EMI Eligibility Distribution")
col1, col2 = st.columns(2)

with col1:
    counts = df['emi_eligibility'].value_counts().reset_index()
    counts.columns = ['Eligibility', 'Count']
    fig = px.pie(counts, values='Count', names='Eligibility',
                 color_discrete_sequence=px.colors.qualitative.Set2,
                 title="Overall Eligibility Split")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    sc_elig = df.groupby(['emi_scenario', 'emi_eligibility']).size().reset_index(name='Count')
    fig = px.bar(sc_elig, x='emi_scenario', y='Count', color='emi_eligibility',
                 barmode='group', title="Eligibility by EMI Scenario",
                 color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_xaxes(tickangle=15)
    st.plotly_chart(fig, use_container_width=True)

# ── Row 2: Salary & Credit Score ───────────────────────────────────
st.markdown("### 💰 Salary & Credit Score Distributions")
col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(df, x='monthly_salary', color='emi_eligibility',
                       nbins=60, barmode='overlay', opacity=0.7,
                       title="Monthly Salary Distribution by Eligibility",
                       labels={'monthly_salary': 'Monthly Salary (₹)'},
                       color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.histogram(df, x='credit_score', color='emi_eligibility',
                       nbins=60, barmode='overlay', opacity=0.7,
                       title="Credit Score Distribution by Eligibility",
                       labels={'credit_score': 'Credit Score'},
                       color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig, use_container_width=True)

# ── Row 3: Employment & Education ──────────────────────────────────
st.markdown("### 👤 Demographics & Employment")
col1, col2 = st.columns(2)

with col1:
    emp_counts = df['employment_type'].value_counts().reset_index()
    emp_counts.columns = ['Employment Type', 'Count']
    fig = px.bar(emp_counts, x='Employment Type', y='Count',
                 color='Employment Type', title="Employment Type Distribution",
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    edu_elig = df.groupby(['education', 'emi_eligibility']).size().reset_index(name='Count')
    fig = px.bar(edu_elig, x='education', y='Count', color='emi_eligibility',
                 barmode='stack', title="Education Level vs Eligibility",
                 color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig, use_container_width=True)

# ── Row 4: Financial Risk Metrics ──────────────────────────────────
st.markdown("### 📉 Financial Risk Analysis")
col1, col2 = st.columns(2)

with col1:
    fig = px.box(df, x='emi_eligibility', y='debt_to_income_ratio',
                 color='emi_eligibility',
                 title="Debt-to-Income Ratio by Eligibility Class",
                 labels={'debt_to_income_ratio': 'Debt-to-Income Ratio'},
                 color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.scatter(
        df.sample(5000, random_state=42),
        x='monthly_salary', y='credit_score',
        color='emi_eligibility', opacity=0.5,
        title="Salary vs Credit Score (5K sample)",
        labels={'monthly_salary': 'Monthly Salary (₹)', 'credit_score': 'Credit Score'},
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Row 5: Max Monthly EMI Distribution ───────────────────────────
st.markdown("### 💳 Max Monthly EMI Distribution")
col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(df, x='max_monthly_emi', nbins=80,
                       title="Max Monthly EMI Distribution",
                       labels={'max_monthly_emi': 'Max Monthly EMI (₹)'},
                       color_discrete_sequence=['#636EFA'])
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.box(df, x='emi_scenario', y='max_monthly_emi',
                 color='emi_scenario',
                 title="Max EMI by Scenario",
                 labels={'max_monthly_emi': 'Max Monthly EMI (₹)'},
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_xaxes(tickangle=20)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ── Correlation Heatmap ────────────────────────────────────────────
st.markdown("### 🔥 Correlation Heatmap")
num_cols = [
    'monthly_salary', 'credit_score', 'bank_balance', 'emergency_fund',
    'current_emi_amount', 'monthly_rent', 'family_size', 'dependents',
    'years_of_employment', 'requested_amount', 'requested_tenure',
    'debt_to_income_ratio', 'disposable_income', 'max_monthly_emi',
]
corr = df[num_cols].corr().round(2)

fig = px.imshow(
    corr, text_auto=True, aspect='auto',
    color_continuous_scale='RdBu_r',
    title="Correlation Matrix — Numerical Features",
    zmin=-1, zmax=1,
)
fig.update_layout(height=600)
st.plotly_chart(fig, use_container_width=True)

# ── Raw Data Preview ────────────────────────────────────────────────
st.markdown("### 🗂️ Raw Data Preview")
st.dataframe(df.head(100), use_container_width=True)
st.caption(f"Showing 100 of {len(df):,} records")
