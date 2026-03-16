"""
pages/2_Prediction.py — Real-Time EMI Prediction
=================================================
User fills in all 22 financial features → two instant predictions:
  1. EMI Eligibility  (Eligible / High_Risk / Not_Eligible)
  2. Max Monthly EMI  (₹ amount)

HOW IT WORKS:
  1. Raw inputs are collected from the Streamlit form
  2. Feature engineering is applied (same as training)
  3. Categorical columns are encoded using the saved LabelEncoders
  4. All features are scaled using the saved StandardScaler
  5. Predictions are returned from the saved best models
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle, json, os

st.set_page_config(page_title="Prediction | EMIPredict AI", page_icon="🔮", layout="wide")
st.title("🔮 Real-Time EMI Prediction")
st.markdown("Fill in the applicant's financial profile below.")
st.markdown("---")

# ── Load Models & Preprocessor ─────────────────────────────────────
@st.cache_resource
def load_models():
    with open('models/best_classifier.pkl', 'rb') as f:
        clf = pickle.load(f)
    with open('models/best_regressor.pkl', 'rb') as f:
        reg = pickle.load(f)
    with open('models/preprocessor.pkl', 'rb') as f:
        pre = pickle.load(f)
    with open('models/feature_names.json') as f:
        feature_cols = json.load(f)
    with open('models/model_metrics.json') as f:
        metrics = json.load(f)
    return clf, reg, pre, feature_cols, metrics

if not os.path.exists('models/best_classifier.pkl'):
    st.error("Models not found.  Run `python generate_dataset.py` then `python train.py` first.")
    st.stop()

clf, reg, pre, feature_cols, metrics = load_models()

# ── Feature Engineering (mirrors train.py exactly) ─────────────────
def engineer_single(raw: dict) -> pd.DataFrame:
    """Apply the same feature engineering used during training to one record."""
    df = pd.DataFrame([raw])

    expense_cols = ['monthly_rent', 'school_fees', 'college_fees',
                    'travel_expenses', 'groceries_utilities', 'other_monthly_expenses']

    df['total_fixed_expenses']       = df[expense_cols].sum(axis=1)
    df['total_monthly_obligations']  = df['total_fixed_expenses'] + df['current_emi_amount']
    df['disposable_income']          = df['monthly_salary'] - df['total_monthly_obligations']
    df['debt_to_income_ratio']       = (df['total_monthly_obligations'] / df['monthly_salary']).clip(0, 2)
    df['expense_to_income_ratio']    = (df['total_fixed_expenses'] / df['monthly_salary']).clip(0, 2)
    df['requested_monthly_emi']      = df['requested_amount'] / df['requested_tenure']
    df['affordability_ratio']        = (df['disposable_income'] / (df['requested_monthly_emi'] + 1)).clip(-10, 50)
    df['loan_burden_ratio']          = (df['current_emi_amount'] / df['monthly_salary']).clip(0, 1)
    df['savings_ratio']              = (df['bank_balance'] / df['monthly_salary']).clip(0, 50)
    df['emergency_months']           = (df['emergency_fund'] / (df['total_monthly_obligations'] + 1)).clip(0, 24)
    df['salary_per_dependent']       = df['monthly_salary'] / (df['dependents'] + 1)

    df['credit_category'] = pd.cut(
        df['credit_score'],
        bins=[299, 549, 649, 699, 749, 850],
        labels=['Very Poor', 'Poor', 'Fair', 'Good', 'Excellent']
    ).astype(str)

    df['financial_stability_score'] = (
        (df['credit_score'] / 850)                            * 40 +
        (1 - df['debt_to_income_ratio'].clip(0, 1))           * 30 +
        (df['savings_ratio'].clip(0, 12) / 12)                * 20 +
        (df['emergency_months'].clip(0, 6) / 6)               * 10
    )
    return df


def predict_from_raw(raw: dict):
    """Full inference pipeline: raw dict → predictions."""
    df = engineer_single(raw)

    # Encode categoricals using saved encoders
    for col, le in pre['encoders'].items():
        if col in df.columns:
            val = str(df[col].iloc[0])
            # Filter out nan/NaN classes from dirty training data
            valid_classes = [c for c in le.classes_ if str(c).lower() != 'nan']
            if val in le.classes_:
                df[col] = le.transform([val])[0]
            elif valid_classes:
                df[col] = le.transform([valid_classes[0]])[0]  # safe fallback
            else:
                df[col] = 0

    # Align columns to training order
    X = df[feature_cols].values

    # Scale
    X_scaled = pre['scaler'].transform(X)

    # Predict
    elig_code = clf.predict(X_scaled)[0]
    elig_proba = clf.predict_proba(X_scaled)[0]
    elig_label = pre['label_encoder'].inverse_transform([elig_code])[0]
    max_emi    = reg.predict(X_scaled)[0]

    return elig_label, elig_proba, max_emi, df


# ══════════════════════════════════════════════════════════════════
# INPUT FORM
# ══════════════════════════════════════════════════════════════════
with st.form("prediction_form"):
    st.markdown("#### 👤 Personal Demographics")
    c1, c2, c3, c4 = st.columns(4)
    age            = c1.number_input("Age",           min_value=25,  max_value=60,  value=35)
    gender         = c2.selectbox("Gender",           ['Male', 'Female'])
    marital_status = c3.selectbox("Marital Status",   ['Single', 'Married'])
    education      = c4.selectbox("Education",        ['High School', 'Graduate', 'Post Graduate', 'Professional'])

    st.markdown("#### 💼 Employment & Income")
    c1, c2, c3, c4 = st.columns(4)
    monthly_salary       = c1.number_input("Monthly Salary (₹)", min_value=15_000, max_value=200_000, value=50_000, step=1_000)
    employment_type      = c2.selectbox("Employment Type", ['Private', 'Government', 'Self-employed'])
    years_of_employment  = c3.number_input("Years of Employment", min_value=0, max_value=35, value=5)
    company_type         = c4.selectbox("Company Type", ['Large Indian', 'MNC', 'Mid-size', 'Small', 'Startup'])

    st.markdown("#### 🏠 Housing & Family")
    c1, c2, c3, c4 = st.columns(4)
    house_type   = c1.selectbox("House Type",  ['Rented', 'Own', 'Family'])
    monthly_rent = c2.number_input("Monthly Rent (₹)", min_value=0, max_value=50_000, value=10_000, step=500)
    family_size  = c3.number_input("Family Size",  min_value=1, max_value=7, value=3)
    dependents   = c4.number_input("Dependents",   min_value=0, max_value=5, value=1)

    st.markdown("#### 📋 Monthly Expenses (₹)")
    c1, c2, c3, c4, c5 = st.columns(5)
    school_fees            = c1.number_input("School Fees",        min_value=0, max_value=20_000, value=2_000, step=500)
    college_fees           = c2.number_input("College Fees",       min_value=0, max_value=30_000, value=0,     step=500)
    travel_expenses        = c3.number_input("Travel Expenses",    min_value=500, max_value=15_000, value=3_000, step=500)
    groceries_utilities    = c4.number_input("Groceries/Utilities", min_value=2_000, max_value=40_000, value=8_000, step=500)
    other_monthly_expenses = c5.number_input("Other Expenses",     min_value=500, max_value=20_000, value=2_000, step=500)

    st.markdown("#### 🏦 Financial Status & Credit")
    c1, c2, c3, c4, c5 = st.columns(5)
    existing_loans     = c1.selectbox("Existing Loans", ['No', 'Yes'])
    current_emi_amount = c2.number_input("Current EMI (₹)", min_value=0, max_value=60_000, value=0, step=500)
    credit_score       = c3.number_input("Credit Score",   min_value=300, max_value=850, value=700)
    bank_balance       = c4.number_input("Bank Balance (₹)", min_value=1_000, max_value=2_000_000, value=100_000, step=5_000)
    emergency_fund     = c5.number_input("Emergency Fund (₹)", min_value=0, max_value=1_000_000, value=50_000, step=5_000)

    st.markdown("#### 📝 Loan Application")
    c1, c2, c3 = st.columns(3)
    emi_scenario      = c1.selectbox("EMI Scenario", [
        'E-commerce Shopping EMI', 'Home Appliances EMI',
        'Vehicle EMI', 'Personal Loan EMI', 'Education EMI'
    ])
    requested_amount  = c2.number_input("Requested Amount (₹)", min_value=10_000, max_value=1_500_000, value=300_000, step=10_000)
    requested_tenure  = c3.number_input("Requested Tenure (months)", min_value=3, max_value=84, value=24)

    submitted = st.form_submit_button("🔮 Predict", use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# PREDICTION OUTPUT
# ══════════════════════════════════════════════════════════════════
if submitted:
    raw = dict(
        age=age, gender=gender, marital_status=marital_status, education=education,
        monthly_salary=monthly_salary, employment_type=employment_type,
        years_of_employment=years_of_employment, company_type=company_type,
        house_type=house_type, monthly_rent=monthly_rent,
        family_size=family_size, dependents=dependents,
        school_fees=school_fees, college_fees=college_fees,
        travel_expenses=travel_expenses, groceries_utilities=groceries_utilities,
        other_monthly_expenses=other_monthly_expenses,
        existing_loans=existing_loans, current_emi_amount=current_emi_amount,
        credit_score=credit_score, bank_balance=bank_balance,
        emergency_fund=emergency_fund, emi_scenario=emi_scenario,
        requested_amount=requested_amount, requested_tenure=requested_tenure,
    )

    elig_label, elig_proba, max_emi, engineered_df = predict_from_raw(raw)

    st.markdown("---")
    st.markdown("## 🎯 Prediction Results")

    color_map = {'Eligible': '🟢', 'High_Risk': '🟡', 'Not_Eligible': '🔴'}
    icon = color_map.get(elig_label, '⚪')

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### EMI Eligibility")
        if elig_label == 'Eligible':
            st.success(f"{icon}  **{elig_label}** — Low risk, comfortable EMI affordability")
        elif elig_label == 'High_Risk':
            st.warning(f"{icon}  **{elig_label}** — Marginal case; higher interest rates may apply")
        else:
            st.error(f"{icon}  **{elig_label}** — High risk; loan not recommended")

        # Class probabilities
        st.markdown("**Confidence Breakdown:**")
        classes = pre['label_encoder'].classes_
        for cls, prob in zip(classes, elig_proba):
            st.progress(float(prob), text=f"{cls}: {prob:.1%}")

    with col2:
        st.markdown("### Maximum Monthly EMI")
        max_emi_clipped = int(np.clip(max_emi, 500, 50_000))
        st.metric("Safe Max EMI", f"₹{max_emi_clipped:,}", help="Maximum safe EMI this applicant can handle monthly")

        req_emi = requested_amount / requested_tenure
        st.metric("Requested Monthly EMI", f"₹{req_emi:,.0f}", help="requested_amount / tenure")

        if req_emi <= max_emi_clipped:
            st.success(f"✅ Requested EMI is within safe limits (+₹{max_emi_clipped - req_emi:,.0f} headroom)")
        else:
            st.error(f"❌ Requested EMI exceeds safe limit by ₹{req_emi - max_emi_clipped:,.0f}")

    # ── Derived Metrics ───────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📊 Computed Financial Metrics")
    disp = float(engineered_df['disposable_income'].iloc[0])
    dti  = float(engineered_df['debt_to_income_ratio'].iloc[0])
    fss  = float(engineered_df['financial_stability_score'].iloc[0])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Disposable Income",         f"₹{disp:,.0f}")
    m2.metric("Debt-to-Income Ratio",      f"{dti:.2%}")
    m3.metric("Financial Stability Score", f"{fss:.1f} / 100")
    m4.metric("Emergency Fund Coverage",   f"{float(engineered_df['emergency_months'].iloc[0]):.1f} months")
