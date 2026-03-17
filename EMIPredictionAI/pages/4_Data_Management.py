"""
pages/4_Data_Management.py — CRUD Operations
=============================================
Full Create / Read / Update / Delete interface for the EMI dataset.

OPERATIONS:
  📋 View   — browse, filter, search records
  ➕ Add    — add a new financial record
  ✏️ Edit   — modify an existing record by index
  🗑️ Delete — remove a record by index
  ⬇️ Download — export filtered data as CSV
"""

import streamlit as st
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(page_title="Data Management | EMIPredict AI", page_icon="🗄️", layout="wide")
st.title("🗄️ Data Management")
st.markdown("Full CRUD operations on the EMI dataset.")
st.markdown("---")

DATA_PATH = os.path.join(BASE_DIR, 'data', 'EMI_dataset.csv')

# ── Load / Save helpers ────────────────────────────────────────────
@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH):
        return None
    df = pd.read_csv(DATA_PATH, low_memory=False)
    for col in ['age', 'monthly_salary', 'bank_balance']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['gender'] = df['gender'].str.strip().str.title().replace({'F': 'Female', 'M': 'Male'})
    return df

def save_data(df: pd.DataFrame):
    df.to_csv(DATA_PATH, index=False)
    st.cache_data.clear()   # force reload next time

if not os.path.exists(DATA_PATH):
    st.error("Dataset not found.  Please ensure `data/EMI_dataset.csv` is present.")
    st.stop()

df = load_data()

# ══════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs(["📋 View & Filter", "➕ Add Record", "✏️ Edit Record", "🗑️ Delete Record"])

# ──────────────────────────────────────────────────────────────────
# TAB 1 — VIEW & FILTER
# ──────────────────────────────────────────────────────────────────
with tab1:
    st.markdown("### Browse & Filter Records")

    col1, col2, col3 = st.columns(3)
    scenario_filter = col1.multiselect(
        "EMI Scenario", options=df['emi_scenario'].unique(), default=list(df['emi_scenario'].unique())
    )
    eligibility_filter = col2.multiselect(
        "Eligibility", options=df['emi_eligibility'].unique(), default=list(df['emi_eligibility'].unique())
    )
    salary_range = col3.slider(
        "Monthly Salary Range (₹)", int(df['monthly_salary'].min()), int(df['monthly_salary'].max()),
        (int(df['monthly_salary'].min()), int(df['monthly_salary'].max())), step=5_000
    )

    filtered = df[
        df['emi_scenario'].isin(scenario_filter) &
        df['emi_eligibility'].isin(eligibility_filter) &
        df['monthly_salary'].between(salary_range[0], salary_range[1])
    ].reset_index(drop=True)

    st.markdown(f"**{len(filtered):,}** records match your filters  (total: {len(df):,})")

    # Pagination
    PAGE_SIZE = 50
    total_pages = max(1, (len(filtered) - 1) // PAGE_SIZE + 1)
    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
    start = (page - 1) * PAGE_SIZE
    st.dataframe(filtered.iloc[start: start + PAGE_SIZE], use_container_width=True)
    st.caption(f"Page {page} of {total_pages}  |  Showing rows {start}–{min(start+PAGE_SIZE, len(filtered))}")

    # Download
    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        "⬇️ Download Filtered Data as CSV", data=csv,
        file_name='emi_filtered.csv', mime='text/csv'
    )

# ──────────────────────────────────────────────────────────────────
# TAB 2 — ADD RECORD
# ──────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("### ➕ Add a New Financial Record")
    with st.form("add_form"):
        c1, c2, c3, c4 = st.columns(4)
        age            = c1.number_input("Age",           25, 60,   value=30)
        gender         = c2.selectbox("Gender",           ['Male', 'Female'])
        marital_status = c3.selectbox("Marital Status",   ['Single', 'Married'])
        education      = c4.selectbox("Education",        ['High School', 'Graduate', 'Post Graduate', 'Professional'])

        c1, c2, c3, c4 = st.columns(4)
        monthly_salary      = c1.number_input("Monthly Salary (₹)",   15_000, 200_000, value=50_000, step=1_000)
        employment_type     = c2.selectbox("Employment Type",          ['Private', 'Government', 'Self-employed'])
        years_of_employment = c3.number_input("Years Employed",        0, 35, value=5)
        company_type        = c4.selectbox("Company Type",             ['Large Corporation', 'MNC', 'SME', 'Government', 'Startup'])

        c1, c2, c3, c4 = st.columns(4)
        house_type   = c1.selectbox("House Type",  ['Rented', 'Own', 'Family'])
        monthly_rent = c2.number_input("Monthly Rent (₹)",   0, 50_000, value=10_000, step=500)
        family_size  = c3.number_input("Family Size",         1, 7, value=3)
        dependents   = c4.number_input("Dependents",          0, 5, value=1)

        c1, c2, c3, c4, c5 = st.columns(5)
        school_fees            = c1.number_input("School Fees",       0, 20_000, value=2_000)
        college_fees           = c2.number_input("College Fees",      0, 30_000, value=0)
        travel_expenses        = c3.number_input("Travel Expenses",   500, 15_000, value=3_000)
        groceries_utilities    = c4.number_input("Groceries/Utils",   2_000, 40_000, value=8_000)
        other_monthly_expenses = c5.number_input("Other Expenses",    500, 20_000, value=2_000)

        c1, c2, c3, c4, c5 = st.columns(5)
        existing_loans     = c1.selectbox("Existing Loans",  ['No', 'Yes'])
        current_emi_amount = c2.number_input("Current EMI (₹)", 0, 60_000, value=0)
        credit_score       = c3.number_input("Credit Score",   300, 850, value=700)
        bank_balance       = c4.number_input("Bank Balance (₹)", 1_000, 2_000_000, value=100_000, step=5_000)
        emergency_fund     = c5.number_input("Emergency Fund (₹)", 0, 1_000_000, value=50_000, step=5_000)

        c1, c2, c3 = st.columns(3)
        emi_scenario     = c1.selectbox("EMI Scenario", ['E-commerce Shopping EMI', 'Home Appliances EMI', 'Vehicle EMI', 'Personal Loan EMI', 'Education EMI'])
        requested_amount = c2.number_input("Requested Amount (₹)", 10_000, 1_500_000, value=300_000, step=10_000)
        requested_tenure = c3.number_input("Tenure (months)",      3, 84, value=24)

        c1, c2 = st.columns(2)
        emi_eligibility  = c1.selectbox("EMI Eligibility (target)", ['Eligible', 'High_Risk', 'Not_Eligible'])
        max_monthly_emi  = c2.number_input("Max Monthly EMI (₹)",    500, 50_000, value=10_000, step=500)

        submitted_add = st.form_submit_button("➕ Add Record", use_container_width=True)

    if submitted_add:
        new_row = {
            'age': age, 'gender': gender, 'marital_status': marital_status,
            'education': education, 'monthly_salary': monthly_salary,
            'employment_type': employment_type, 'years_of_employment': years_of_employment,
            'company_type': company_type, 'house_type': house_type,
            'monthly_rent': monthly_rent, 'family_size': family_size,
            'dependents': dependents, 'school_fees': school_fees,
            'college_fees': college_fees, 'travel_expenses': travel_expenses,
            'groceries_utilities': groceries_utilities,
            'other_monthly_expenses': other_monthly_expenses,
            'existing_loans': existing_loans, 'current_emi_amount': current_emi_amount,
            'credit_score': credit_score, 'bank_balance': bank_balance,
            'emergency_fund': emergency_fund, 'emi_scenario': emi_scenario,
            'requested_amount': requested_amount, 'requested_tenure': requested_tenure,
            'emi_eligibility': emi_eligibility, 'max_monthly_emi': max_monthly_emi,
        }
        new_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_data(new_df)
        st.success(f"✅ Record added! Dataset now has {len(new_df):,} rows.")
        st.rerun()

# ──────────────────────────────────────────────────────────────────
# TAB 3 — EDIT RECORD
# ──────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("### ✏️ Edit an Existing Record")
    edit_idx = st.number_input("Row index to edit", min_value=0, max_value=len(df)-1, value=0, step=1)

    if edit_idx < len(df):
        row = df.iloc[edit_idx].to_dict()
        st.markdown(f"**Editing row {edit_idx}:**")
        st.dataframe(pd.DataFrame([row]), use_container_width=True)

        with st.form("edit_form"):
            c1, c2 = st.columns(2)
            new_salary    = c1.number_input("Monthly Salary (₹)", 15_000, 200_000,
                                             value=int(row.get('monthly_salary', 50_000)), step=1_000)
            new_credit    = c2.number_input("Credit Score",        300, 850,
                                             value=int(row.get('credit_score', 700)))
            c1, c2 = st.columns(2)
            new_eligib    = c1.selectbox("EMI Eligibility", ['Eligible', 'High_Risk', 'Not_Eligible'],
                                          index=['Eligible', 'High_Risk', 'Not_Eligible'].index(
                                              row.get('emi_eligibility', 'Eligible')))
            new_max_emi   = c2.number_input("Max Monthly EMI (₹)", 500, 50_000,
                                             value=int(row.get('max_monthly_emi', 10_000)), step=500)

            submitted_edit = st.form_submit_button("💾 Save Changes", use_container_width=True)

        if submitted_edit:
            df.at[edit_idx, 'monthly_salary']   = new_salary
            df.at[edit_idx, 'credit_score']      = new_credit
            df.at[edit_idx, 'emi_eligibility']   = new_eligib
            df.at[edit_idx, 'max_monthly_emi']   = new_max_emi
            save_data(df)
            st.success(f"✅ Row {edit_idx} updated.")
            st.rerun()

# ──────────────────────────────────────────────────────────────────
# TAB 4 — DELETE RECORD
# ──────────────────────────────────────────────────────────────────
with tab4:
    st.markdown("### 🗑️ Delete a Record")
    del_idx = st.number_input("Row index to delete", min_value=0, max_value=len(df)-1, value=0, step=1)

    if del_idx < len(df):
        st.dataframe(pd.DataFrame([df.iloc[del_idx].to_dict()]), use_container_width=True)

    if st.button(f"🗑️ Delete Row {del_idx}", type="primary"):
        new_df = df.drop(index=del_idx).reset_index(drop=True)
        save_data(new_df)
        st.success(f"✅ Row {del_idx} deleted.  Dataset now has {len(new_df):,} rows.")
        st.rerun()
