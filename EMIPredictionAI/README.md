# EMIPredict AI — Intelligent Financial Risk Assessment Platform

A comprehensive FinTech platform that uses machine learning to predict **EMI eligibility** and **maximum safe EMI amount** for loan applicants, built with Python, Streamlit, MLflow, and XGBoost.

---

## Live App

> Deployed on Streamlit Cloud: *(add your public URL here after deployment)*

---

## Problem Statement

People struggle to pay EMI due to poor financial planning and inadequate risk assessment. EMIPredict AI solves this by providing data-driven insights for better loan decisions using 400,000 realistic financial records.

---

## Features

- **Dual ML prediction**: Classification (EMI eligibility) + Regression (max EMI amount)
- **5 Classification models** tracked in MLflow: Logistic Regression, Decision Tree, Random Forest, Gradient Boosting, XGBoost
- **5 Regression models** tracked in MLflow: Linear Regression, Decision Tree, Random Forest, Gradient Boosting, XGBoost
- **MLflow Model Registry** for best model version control
- **Interactive EDA** with Plotly visualisations
- **Full CRUD operations** on the financial dataset
- **Real-time predictions** with confidence breakdown

---

## Dataset

| Property | Value |
|---|---|
| Total Records | 400,000 |
| Input Features | 22 financial & demographic variables |
| Target Variables | 2 (Classification + Regression) |
| EMI Scenarios | 5 lending categories |

**EMI Scenarios:** E-commerce Shopping, Home Appliances, Vehicle, Personal Loan, Education

---

## Tech Stack

`Python` · `Streamlit` · `scikit-learn` · `XGBoost` · `MLflow` · `Pandas` · `Plotly`

---

## Project Structure

```
EMIPredictionAI/
├── app.py                    # Home page — pipeline overview & model status
├── pages/
│   ├── 1_EDA.py              # Exploratory Data Analysis
│   ├── 2_Prediction.py       # Real-time EMI prediction form
│   ├── 3_Model_Performance.py# MLflow model comparison dashboard
│   └── 4_Data_Management.py  # CRUD operations on dataset
├── train.py                  # Full ML training pipeline with MLflow tracking
├── data/
│   └── EMI_dataset.csv       # 400K financial records
├── models/
│   ├── best_classifier.pkl   # Best trained classification model
│   ├── best_regressor.pkl    # Best trained regression model
│   ├── preprocessor.pkl      # Encoders + scaler
│   ├── model_metrics.json    # All 10 model metrics for dashboard
│   └── feature_names.json    # Feature column order
├── requirements.txt
└── .streamlit/
    └── config.toml           # Streamlit Cloud configuration
```

---

## ML Pipeline (train.py)

```
Dataset (400K Records)
        ↓
Step 1: Data Quality Assessment  (missing values, duplicates, type coercion)
        ↓
Step 2: Feature Engineering       (13 derived financial ratios + composite score)
        ↓
Step 3: Preprocessing             (LabelEncoding + StandardScaling)
        ↓
Step 4: Train / Val / Test Split  (70% / 15% / 15%, stratified)
        ↓
Step 5: Train 5 Classification Models  → MLflow tracking
        ↓
Step 6: Train 5 Regression Models      → MLflow tracking
        ↓
Step 7: Save Best Models + MLflow Model Registry
```

---

## Feature Engineering (13 derived features)

| Feature | Formula |
|---|---|
| total_fixed_expenses | sum of all non-EMI monthly costs |
| total_monthly_obligations | fixed expenses + current EMI |
| disposable_income | salary − obligations |
| debt_to_income_ratio | obligations / salary |
| expense_to_income_ratio | fixed expenses / salary |
| requested_monthly_emi | requested_amount / tenure |
| affordability_ratio | disposable_income / requested_monthly_emi |
| loan_burden_ratio | current_emi / salary |
| savings_ratio | bank_balance / salary |
| emergency_months | emergency_fund / monthly_obligations |
| salary_per_dependent | salary / (dependents + 1) |
| credit_category | binned credit score (5 bands) |
| financial_stability_score | composite score (0–100) |

---

## Model Evaluation Metrics

**Classification:** Accuracy, Precision, Recall, F1-Score, ROC-AUC

**Regression:** RMSE, MAE, R², MAPE

---

## How to Run Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train models (generates models/ artifacts)
python train.py

# 3. Launch Streamlit app
streamlit run app.py

# 4. View MLflow experiment tracking
mlflow ui --backend-store-uri ./mlruns
# Open: http://localhost:5000
```

---

## Streamlit Cloud Deployment

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set **Main file path**: `app.py`
5. Click **Deploy**

---

## Domain

**FinTech & Banking** — GUVI | HCL Capstone Project
