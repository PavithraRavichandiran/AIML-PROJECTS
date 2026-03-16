"""
train.py — EMIPredict AI
=========================
Full ML training pipeline with MLflow experiment tracking.

PIPELINE STEPS:
  Step 1 → Load data & quality check (missing values, duplicates, distributions)
  Step 2 → Feature Engineering  (10 derived financial ratios + composite score)
  Step 3 → Preprocessing         (label encoding, standard scaling)
  Step 4 → Train/Val/Test split  (70% / 15% / 15%, stratified)
  Step 5 → Train 5 Classification models + log to MLflow
  Step 6 → Train 5 Regression models    + log to MLflow
  Step 7 → Select best models, save models + preprocessor to disk

Models trained:
  Classification: Logistic Regression, Decision Tree, Random Forest,
                  Gradient Boosting, XGBoost
  Regression    : Linear Regression, Decision Tree, Random Forest,
                  Gradient Boosting, XGBoost
"""

import os
import json
import time
import pickle
import warnings
import numpy as np
import pandas as pd
warnings.filterwarnings('ignore')

import mlflow
import mlflow.sklearn
import mlflow.xgboost

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import (RandomForestClassifier, RandomForestRegressor,
                               GradientBoostingClassifier, GradientBoostingRegressor)
from xgboost import XGBClassifier, XGBRegressor

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    mean_squared_error, mean_absolute_error, r2_score,
    mean_absolute_percentage_error,
)


# ══════════════════════════════════════════════════════════════════
# STEP 1 — DATA LOADING & QUALITY ASSESSMENT
# ══════════════════════════════════════════════════════════════════
def load_and_assess(filepath: str) -> pd.DataFrame:
    """
    Loads the CSV, prints a quality report:
      - Shape (rows × columns)
      - Real-world data cleaning (type coercion, gender normalisation)
      - Missing values (imputed with median / mode)
      - Duplicate rows
      - Target variable distributions
    """
    print("\n" + "=" * 60)
    print("STEP 1 — DATA LOADING & QUALITY ASSESSMENT")
    print("=" * 60)

    print(f"  Loading {filepath} ...")
    df = pd.read_csv(filepath, low_memory=False)
    print(f"  ✓ Loaded  : {df.shape[0]:,} rows x {df.shape[1]} columns")

    # ── Real-world data cleaning ──────────────────────────────────

    # 1. Columns stored as strings that should be numeric
    for col in ['age', 'monthly_salary', 'bank_balance']:
        if df[col].dtype == object:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            print(f"  ✓ Converted '{col}' from string to numeric")

    # 2. Normalise gender values (Female/FEMALE/female/F → Female)
    if 'gender' in df.columns:
        df['gender'] = df['gender'].str.strip().str.title()
        df['gender'] = df['gender'].replace({'F': 'Female', 'M': 'Male'})
        print(f"  ✓ Normalised gender  → unique values: {sorted(df['gender'].dropna().unique())}")

    # ── Missing values ────────────────────────────────────────────
    missing = df.isnull().sum()
    if missing.sum() == 0:
        print("  ✓ Missing values : None")
    else:
        print(f"  Imputing missing values:")
        print(missing[missing > 0].to_string())
        df[df.select_dtypes(include='number').columns] = \
            df.select_dtypes(include='number').fillna(df.median(numeric_only=True))
        for c in df.select_dtypes('object').columns:
            df[c].fillna(df[c].mode()[0], inplace=True)
        print("  ✓ Missing values imputed (median for numbers, mode for categories)")

    # Duplicates
    dupes = df.duplicated().sum()
    if dupes > 0:
        df = df.drop_duplicates()
        print(f"  ✓ Removed {dupes} duplicate rows → new shape {df.shape}")
    else:
        print(f"  ✓ Duplicate rows : 0")

    # Target distribution
    print("\n  Classification target — emi_eligibility:")
    print(df['emi_eligibility'].value_counts().to_string())

    print("\n  Regression target — max_monthly_emi:")
    print(f"    min={df['max_monthly_emi'].min():,}  "
          f"mean={df['max_monthly_emi'].mean():.0f}  "
          f"max={df['max_monthly_emi'].max():,}")

    return df


# ══════════════════════════════════════════════════════════════════
# STEP 2 — FEATURE ENGINEERING
# ══════════════════════════════════════════════════════════════════
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates 10 new derived features that capture financial health better
    than raw columns alone.  Each new feature is explained below.
    """
    print("\n" + "=" * 60)
    print("STEP 2 — FEATURE ENGINEERING")
    print("=" * 60)

    df = df.copy()

    expense_cols = [
        'monthly_rent', 'school_fees', 'college_fees',
        'travel_expenses', 'groceries_utilities', 'other_monthly_expenses'
    ]

    # 1. Total fixed monthly expenses (excludes existing EMI)
    df['total_fixed_expenses'] = df[expense_cols].sum(axis=1)
    print("  ✓ total_fixed_expenses       = sum of all non-EMI monthly costs")

    # 2. Total monthly obligations (fixed + existing EMI)
    df['total_monthly_obligations'] = df['total_fixed_expenses'] + df['current_emi_amount']
    print("  ✓ total_monthly_obligations  = fixed expenses + current EMI")

    # 3. Disposable income
    df['disposable_income'] = df['monthly_salary'] - df['total_monthly_obligations']
    print("  ✓ disposable_income          = salary − obligations")

    # 4. Debt-to-income ratio  (key risk metric; >0.5 is risky)
    df['debt_to_income_ratio'] = (
        df['total_monthly_obligations'] / df['monthly_salary']
    ).clip(0, 2)
    print("  ✓ debt_to_income_ratio       = obligations / salary  [capped 0–2]")

    # 5. Expense-to-income ratio (fixed living costs vs salary)
    df['expense_to_income_ratio'] = (
        df['total_fixed_expenses'] / df['monthly_salary']
    ).clip(0, 2)
    print("  ✓ expense_to_income_ratio    = fixed expenses / salary")

    # 6. Estimated requested monthly EMI (simple P/tenure, no interest)
    df['requested_monthly_emi'] = df['requested_amount'] / df['requested_tenure']
    print("  ✓ requested_monthly_emi      = requested_amount / tenure")

    # 7. Affordability ratio (>1 means person can likely afford it)
    df['affordability_ratio'] = (
        df['disposable_income'] / (df['requested_monthly_emi'] + 1)
    ).clip(-10, 50)
    print("  ✓ affordability_ratio        = disposable_income / requested_monthly_emi")

    # 8. Loan burden ratio (how much of salary is already in EMI)
    df['loan_burden_ratio'] = (
        df['current_emi_amount'] / df['monthly_salary']
    ).clip(0, 1)
    print("  ✓ loan_burden_ratio          = current_emi / salary")

    # 9. Savings ratio (months of salary in bank)
    df['savings_ratio'] = (
        df['bank_balance'] / df['monthly_salary']
    ).clip(0, 50)
    print("  ✓ savings_ratio              = bank_balance / salary")

    # 10. Emergency coverage (months of expenses covered by emergency fund)
    df['emergency_months'] = (
        df['emergency_fund'] / (df['total_monthly_obligations'] + 1)
    ).clip(0, 24)
    print("  ✓ emergency_months           = emergency_fund / monthly_obligations")

    # 11. Salary per dependent  (purchasing power after family obligations)
    df['salary_per_dependent'] = df['monthly_salary'] / (df['dependents'] + 1)
    print("  ✓ salary_per_dependent       = salary / (dependents + 1)")

    # 12. Credit score category (binned)
    df['credit_category'] = pd.cut(
        df['credit_score'],
        bins=[299, 549, 649, 699, 749, 850],
        labels=['Very Poor', 'Poor', 'Fair', 'Good', 'Excellent']
    ).astype(str)
    print("  ✓ credit_category            = binned credit score (5 bands)")

    # 13. Financial stability score (composite 0–100)
    df['financial_stability_score'] = (
        (df['credit_score'] / 850)                               * 40 +
        (1 - df['debt_to_income_ratio'].clip(0, 1))              * 30 +
        (df['savings_ratio'].clip(0, 12) / 12)                   * 20 +
        (df['emergency_months'].clip(0, 6) / 6)                  * 10
    )
    print("  ✓ financial_stability_score  = composite score (0–100)")

    print(f"\n  Features before engineering : 27  →  after : {len(df.columns)}")
    return df


# ══════════════════════════════════════════════════════════════════
# STEP 3 — PREPROCESSING
# ══════════════════════════════════════════════════════════════════
def preprocess(df: pd.DataFrame):
    """
    1. Encodes all categorical columns with LabelEncoder
    2. Encodes classification target with LabelEncoder
    3. Scales all features with StandardScaler (mean=0, std=1)
    Returns X, y_clf, y_reg, and a 'preprocessor' dict for later
    inference use.
    """
    print("\n" + "=" * 60)
    print("STEP 3 — PREPROCESSING  (Encoding + Scaling)")
    print("=" * 60)

    df = df.copy()

    TARGET_CLF = 'emi_eligibility'
    TARGET_REG = 'max_monthly_emi'

    categorical_cols = [
        'gender', 'marital_status', 'education', 'employment_type',
        'company_type', 'house_type', 'existing_loans', 'emi_scenario',
        'credit_category'
    ]

    # ── Encode classification target ─────────────────────────────
    le_target = LabelEncoder()
    y_clf = le_target.fit_transform(df[TARGET_CLF])
    print(f"  ✓ Classification target encoded:")
    for cls, code in zip(le_target.classes_, le_target.transform(le_target.classes_)):
        print(f"      {cls} → {code}")

    # ── Regression target (already numeric) ──────────────────────
    y_reg = df[TARGET_REG].values
    print(f"  ✓ Regression target : max_monthly_emi (unchanged)")

    # ── Encode categorical features ──────────────────────────────
    print("\n  Encoding categorical features ...")
    encoders = {}
    for col in categorical_cols:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le
            print(f"      {col:30s} → {len(le.classes_)} classes")

    # ── Build feature matrix ─────────────────────────────────────
    drop_cols = [TARGET_CLF, TARGET_REG]
    feature_cols = [c for c in df.columns if c not in drop_cols]
    X = df[feature_cols].copy()

    # ── Scale features ───────────────────────────────────────────
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=feature_cols)
    print(f"\n  ✓ StandardScaler applied to {len(feature_cols)} features")
    print(f"    (each feature now has mean≈0, std≈1)")

    preprocessor = {
        'encoders': encoders,
        'scaler': scaler,
        'label_encoder': le_target,
        'feature_cols': feature_cols,
        'categorical_cols': categorical_cols,
    }

    return X_scaled, y_clf, y_reg, preprocessor, feature_cols


# ══════════════════════════════════════════════════════════════════
# STEP 4 — DATA SPLITTING
# ══════════════════════════════════════════════════════════════════
def split_data(X, y_clf, y_reg):
    """
    Stratified 70 / 15 / 15 split.
    Stratification ensures all 3 eligibility classes appear in
    each split in the same proportion as the full dataset.
    """
    print("\n" + "=" * 60)
    print("STEP 4 — TRAIN / VALIDATION / TEST SPLIT  (70 / 15 / 15)")
    print("=" * 60)

    X_train, X_tmp, yc_train, yc_tmp, yr_train, yr_tmp = train_test_split(
        X, y_clf, y_reg, test_size=0.30, random_state=42, stratify=y_clf
    )
    X_val, X_test, yc_val, yc_test, yr_val, yr_test = train_test_split(
        X_tmp, yc_tmp, yr_tmp, test_size=0.50, random_state=42, stratify=yc_tmp
    )

    print(f"  Train      : {len(X_train):,} rows")
    print(f"  Validation : {len(X_val):,} rows")
    print(f"  Test       : {len(X_test):,} rows")
    print(f"  ✓ Stratified split — class ratios preserved in each split")

    return X_train, X_val, X_test, yc_train, yc_val, yc_test, yr_train, yr_val, yr_test


# ══════════════════════════════════════════════════════════════════
# STEP 5 — CLASSIFICATION MODEL TRAINING
# ══════════════════════════════════════════════════════════════════
def train_classifiers(X_train, X_val, X_test, yc_train, yc_val, yc_test):
    """
    Trains 5 classification models, logs everything to MLflow,
    returns the best model (highest weighted F1) and all results.

    Metrics logged per model:
      val_accuracy, val_precision, val_recall, val_f1, val_roc_auc,
      test_accuracy
    """
    print("\n" + "=" * 60)
    print("STEP 5 — CLASSIFICATION MODEL TRAINING  (5 models)")
    print("=" * 60)
    print("  Predicting: emi_eligibility  (Eligible / High_Risk / Not_Eligible)")

    models = {
        'Logistic Regression':  LogisticRegression(max_iter=1000, random_state=42, n_jobs=-1),
        'Decision Tree':        DecisionTreeClassifier(max_depth=12, random_state=42),
        'Random Forest':        RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1),
        'Gradient Boosting':    GradientBoostingClassifier(n_estimators=50, subsample=0.8, random_state=42),
        'XGBoost':              XGBClassifier(n_estimators=100, random_state=42,
                                              use_label_encoder=False, eval_metric='mlogloss', n_jobs=-1),
    }

    results = {}
    mlflow.set_experiment("EMIPredict_Classification")

    for name, model in models.items():
        print(f"\n  ▶ Training {name} ...")
        t0 = time.time()

        with mlflow.start_run(run_name=name):
            model.fit(X_train, yc_train)

            y_pred = model.predict(X_val)
            y_prob = model.predict_proba(X_val) if hasattr(model, 'predict_proba') else None

            acc  = accuracy_score(yc_val, y_pred)
            prec = precision_score(yc_val, y_pred, average='weighted', zero_division=0)
            rec  = recall_score(yc_val, y_pred, average='weighted', zero_division=0)
            f1   = f1_score(yc_val, y_pred, average='weighted', zero_division=0)
            roc  = roc_auc_score(yc_val, y_prob, multi_class='ovr', average='weighted') if y_prob is not None else 0.0

            test_acc = accuracy_score(yc_test, model.predict(X_test))

            mlflow.log_params({'model': name})
            mlflow.log_metrics({
                'val_accuracy':  round(acc, 4),
                'val_precision': round(prec, 4),
                'val_recall':    round(rec, 4),
                'val_f1':        round(f1, 4),
                'val_roc_auc':   round(roc, 4),
                'test_accuracy': round(test_acc, 4),
            })
            mlflow.sklearn.log_model(model, name.replace(' ', '_'))

        elapsed = time.time() - t0
        results[name] = {
            'model': model, 'val_accuracy': acc, 'val_precision': prec,
            'val_recall': rec, 'val_f1': f1, 'val_roc_auc': roc,
            'test_accuracy': test_acc,
        }
        print(f"    Accuracy={acc:.4f}  F1={f1:.4f}  ROC-AUC={roc:.4f}  ({elapsed:.1f}s)")

    best_name = max(results, key=lambda x: results[x]['val_f1'])
    print(f"\n  ★ Best Classifier → {best_name}  (F1={results[best_name]['val_f1']:.4f})")
    return results[best_name]['model'], best_name, results


# ══════════════════════════════════════════════════════════════════
# STEP 6 — REGRESSION MODEL TRAINING
# ══════════════════════════════════════════════════════════════════
def train_regressors(X_train, X_val, X_test, yr_train, yr_val, yr_test):
    """
    Trains 5 regression models, logs everything to MLflow,
    returns best model (lowest RMSE) and all results.

    Metrics logged per model:
      val_rmse, val_mae, val_r2, val_mape, test_rmse
    """
    print("\n" + "=" * 60)
    print("STEP 6 — REGRESSION MODEL TRAINING  (5 models)")
    print("=" * 60)
    print("  Predicting: max_monthly_emi  (₹500 – ₹50,000)")

    models = {
        'Linear Regression':        LinearRegression(n_jobs=-1),
        'Decision Tree Regressor':  DecisionTreeRegressor(max_depth=12, random_state=42),
        'Random Forest Regressor':  RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1),
        'Gradient Boosting Regressor': GradientBoostingRegressor(n_estimators=50, subsample=0.8, random_state=42),
        'XGBoost Regressor':        XGBRegressor(n_estimators=100, random_state=42, n_jobs=-1),
    }

    results = {}
    mlflow.set_experiment("EMIPredict_Regression")

    for name, model in models.items():
        print(f"\n  ▶ Training {name} ...")
        t0 = time.time()

        with mlflow.start_run(run_name=name):
            model.fit(X_train, yr_train)

            y_pred = model.predict(X_val)
            rmse = np.sqrt(mean_squared_error(yr_val, y_pred))
            mae  = mean_absolute_error(yr_val, y_pred)
            r2   = r2_score(yr_val, y_pred)
            mape = mean_absolute_percentage_error(yr_val, y_pred) * 100

            test_rmse = np.sqrt(mean_squared_error(yr_test, model.predict(X_test)))

            mlflow.log_params({'model': name})
            mlflow.log_metrics({
                'val_rmse':  round(rmse, 2),
                'val_mae':   round(mae, 2),
                'val_r2':    round(r2, 4),
                'val_mape':  round(mape, 2),
                'test_rmse': round(test_rmse, 2),
            })
            mlflow.sklearn.log_model(model, name.replace(' ', '_'))

        elapsed = time.time() - t0
        results[name] = {
            'model': model, 'val_rmse': rmse, 'val_mae': mae,
            'val_r2': r2, 'val_mape': mape, 'test_rmse': test_rmse,
        }
        print(f"    RMSE=₹{rmse:.0f}  MAE=₹{mae:.0f}  R²={r2:.4f}  ({elapsed:.1f}s)")

    best_name = min(results, key=lambda x: results[x]['val_rmse'])
    print(f"\n  ★ Best Regressor → {best_name}  (RMSE=₹{results[best_name]['val_rmse']:.0f})")
    return results[best_name]['model'], best_name, results


# ══════════════════════════════════════════════════════════════════
# STEP 7 — SAVE MODELS & ARTIFACTS
# ══════════════════════════════════════════════════════════════════
def save_artifacts(best_clf, best_clf_name, clf_results,
                   best_reg, best_reg_name, reg_results,
                   preprocessor, feature_cols):
    print("\n" + "=" * 60)
    print("STEP 7 — SAVING MODELS & ARTIFACTS")
    print("=" * 60)

    os.makedirs('models', exist_ok=True)

    with open('models/best_classifier.pkl', 'wb') as f:
        pickle.dump(best_clf, f)
    print(f"  ✓ Saved: models/best_classifier.pkl  [{best_clf_name}]")

    with open('models/best_regressor.pkl', 'wb') as f:
        pickle.dump(best_reg, f)
    print(f"  ✓ Saved: models/best_regressor.pkl   [{best_reg_name}]")

    with open('models/preprocessor.pkl', 'wb') as f:
        pickle.dump(preprocessor, f)
    print("  ✓ Saved: models/preprocessor.pkl     [encoders + scaler + label_encoder]")

    # Save all model metrics for the dashboard
    metrics = {
        'classification': {
            name: {k: v for k, v in m.items() if k != 'model'}
            for name, m in clf_results.items()
        },
        'regression': {
            name: {k: v for k, v in m.items() if k != 'model'}
            for name, m in reg_results.items()
        },
        'best_classifier': best_clf_name,
        'best_regressor':  best_reg_name,
    }
    with open('models/model_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    print("  ✓ Saved: models/model_metrics.json   [all metrics for dashboard]")

    with open('models/feature_names.json', 'w') as f:
        json.dump(list(feature_cols), f)
    print(f"  ✓ Saved: models/feature_names.json  [{len(feature_cols)} features]")


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════
def main():
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    print("\n" + "=" * 60)
    print("  EMIPredict AI - ML Training Pipeline")
    print("=" * 60)

    mlflow.set_tracking_uri("./mlruns")

    # Step 1
    df = load_and_assess('data/EMI_dataset.csv')

    # Step 2
    df = engineer_features(df)

    # Step 3
    X, y_clf, y_reg, preprocessor, feature_cols = preprocess(df)

    # Step 4
    (X_train, X_val, X_test,
     yc_train, yc_val, yc_test,
     yr_train, yr_val, yr_test) = split_data(X, y_clf, y_reg)

    # Step 5
    best_clf, best_clf_name, clf_results = train_classifiers(
        X_train, X_val, X_test, yc_train, yc_val, yc_test
    )

    # Step 6
    best_reg, best_reg_name, reg_results = train_regressors(
        X_train, X_val, X_test, yr_train, yr_val, yr_test
    )

    # Step 7
    save_artifacts(best_clf, best_clf_name, clf_results,
                   best_reg, best_reg_name, reg_results,
                   preprocessor, feature_cols)

    print("\n" + "=" * 60)
    print("  TRAINING COMPLETE")
    print("=" * 60)
    print(f"\n  Best Classifier : {best_clf_name}")
    print(f"    Accuracy      : {clf_results[best_clf_name]['val_accuracy']:.4f}")
    print(f"    F1 Score      : {clf_results[best_clf_name]['val_f1']:.4f}")
    print(f"    ROC-AUC       : {clf_results[best_clf_name]['val_roc_auc']:.4f}")
    print(f"\n  Best Regressor  : {best_reg_name}")
    print(f"    RMSE          : ₹{reg_results[best_reg_name]['val_rmse']:.0f}")
    print(f"    MAE           : ₹{reg_results[best_reg_name]['val_mae']:.0f}")
    print(f"    R²            : {reg_results[best_reg_name]['val_r2']:.4f}")
    print("\n  ➡  Run:  streamlit run app.py")


if __name__ == '__main__':
    main()
