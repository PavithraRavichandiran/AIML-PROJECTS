# EMIPredict AI — Intelligent Financial Risk Assessment Platform

A machine learning platform that predicts **EMI loan eligibility** and **maximum safe monthly EMI amount** across 5 lending scenarios.

## Results

| Task | Best Model | Score |
|------|-----------|-------|
| Classification (Eligibility) | XGBoost | Accuracy: 98.60% · F1: 98.58% · ROC-AUC: 99.93% |
| Regression (Max EMI ₹) | XGBoost | RMSE: ₹695 · MAE: ₹252 · R²: 0.9920 |

## Pipeline

```
404,800 records → Data Cleaning → 13 Engineered Features → Encoding + Scaling
→ 70/15/15 Split → 5 Classifiers + 5 Regressors (MLflow) → Streamlit App
```

## Streamlit Pages

| Page | Description |
|------|-------------|
| 📊 EDA | Distributions, correlations, scenario breakdown |
| 🔮 Prediction | Real-time eligibility + max EMI from applicant profile |
| 📈 Model Performance | Compare all 10 models with charts |
| 🗄️ Data Management | CRUD operations on the dataset |

## How to Run

```bash
pip install -r requirements.txt
python train.py
streamlit run app.py
# MLflow UI
mlflow server --backend-store-uri ./mlruns --port 5000
```

> Place `emi_prediction_dataset.csv` in `data/` before running `train.py`.

**Tech Stack:** Python · scikit-learn · XGBoost · MLflow · Streamlit · Plotly
