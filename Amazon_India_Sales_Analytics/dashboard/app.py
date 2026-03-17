from config import DB_PATH
from data_loaders import (
    cached_load_data, cached_load_q6_q10_data, cached_load_q11_q15_data, 
    cached_load_q16_q20_data, cached_load_q21_q25_data
)
from utils import month_sort_key, add_month_label
from alerts import render_alert_center
from executive_dashboard import render_q1, render_q2, render_q3, render_q4, render_q5
from revenue_analytics import render_q6, render_q7, render_q8, render_q9, render_q10
from customer_analytics import render_q11, render_q12, render_q13, render_q14, render_q15
from product_inventory import render_q16, render_q17, render_q18, render_q19, render_q20
from operations_logistics import render_q21, render_q22, render_q23, render_q24, render_q25
import streamlit as st


def main():
    col_title, col_refresh = st.columns([0.9, 0.1])
    with col_title:
        st.title("Amazon India Sales Analytics Dashboard")
    with col_refresh:
        st.write("")
        st.write("")
        if st.button("🔄", help="Refresh all dashboard data", key="refresh_icon"):
            st.toast("Refreshing all data...")
            st.session_state.data_loaded = False
            st.rerun()
    # st.caption("Structured for Questions 1-10 with section-based navigation, interactive filters, refresh controls, and KPI alerts")

    if not DB_PATH.exists():
        st.error(f"Database not found at: {DB_PATH}")
        st.stop()

    # Initialize session state for data caching
    # Load all data once and cache it in session_state to avoid reloading on every interaction
    if "data_loaded" not in st.session_state:
        try:
            with st.spinner("Loading dashboard data (first time)..."):
                # Load BASE data
                monthly, category, payment, prime = cached_load_data()
                geo_state, geo_city, geo_tier, price_discount, price_category, festival_metrics, festival_bda = cached_load_q6_q10_data()
                
                # Load Q11-Q15 data
                (q11_rfm, q11_behavior, q11_ltv, q11_marketing,
                 q11_journey_channels, q11_purchase_patterns, q11_category_transitions, q11_customer_evolution,
                 q11_prime_mix, q11_prime_retention, q11_member_value,
                 q11_churn_pred, q11_strategy_effect, q11_lifecycle,
                 q11_age_category, q11_age_spending, q11_geo_age, q11_marketing_ops) = cached_load_q11_q15_data()
                
                # Load Q16-Q20 data
                prod_perf, brand_perf, inventory_demand, ratings, new_launch = cached_load_q16_q20_data()
                
                # Load Q21-Q25 data
                delivery_perf, payment_analytics, return_cancellation, customer_service, supply_chain = cached_load_q21_q25_data()
                
                # Store everything in session_state
                st.session_state.monthly = monthly
                st.session_state.category = category
                st.session_state.payment = payment
                st.session_state.prime = prime
                st.session_state.geo_state = geo_state
                st.session_state.geo_city = geo_city
                st.session_state.geo_tier = geo_tier
                st.session_state.price_discount = price_discount
                st.session_state.price_category = price_category
                st.session_state.festival_metrics = festival_metrics
                st.session_state.festival_bda = festival_bda
                
                st.session_state.q11_rfm = q11_rfm
                st.session_state.q11_behavior = q11_behavior
                st.session_state.q11_ltv = q11_ltv
                st.session_state.q11_marketing = q11_marketing
                st.session_state.q11_journey_channels = q11_journey_channels
                st.session_state.q11_purchase_patterns = q11_purchase_patterns
                st.session_state.q11_category_transitions = q11_category_transitions
                st.session_state.q11_customer_evolution = q11_customer_evolution
                st.session_state.q11_prime_mix = q11_prime_mix
                st.session_state.q11_prime_retention = q11_prime_retention
                st.session_state.q11_member_value = q11_member_value
                st.session_state.q11_churn_pred = q11_churn_pred
                st.session_state.q11_strategy_effect = q11_strategy_effect
                st.session_state.q11_lifecycle = q11_lifecycle
                st.session_state.q11_age_category = q11_age_category
                st.session_state.q11_age_spending = q11_age_spending
                st.session_state.q11_geo_age = q11_geo_age
                st.session_state.q11_marketing_ops = q11_marketing_ops
                
                st.session_state.prod_perf = prod_perf
                st.session_state.brand_perf = brand_perf
                st.session_state.inventory_demand = inventory_demand
                st.session_state.ratings = ratings
                st.session_state.new_launch = new_launch
                
                st.session_state.delivery_perf = delivery_perf
                st.session_state.payment_analytics = payment_analytics
                st.session_state.return_cancellation = return_cancellation
                st.session_state.customer_service = customer_service
                st.session_state.supply_chain = supply_chain
                
                st.session_state.data_loaded = True
            st.toast("✅ All data loaded!")
        except Exception as exc:
            st.error("Dashboard data loading failed. Run KPI refresh and try again.")
            st.exception(exc)
            st.stop()
    
    # Retrieve data from session_state
    monthly = add_month_label(st.session_state.monthly)
    category = add_month_label(st.session_state.category)
    payment = add_month_label(st.session_state.payment)
    prime = add_month_label(st.session_state.prime)
    geo_state = st.session_state.geo_state
    geo_city = st.session_state.geo_city
    geo_tier = st.session_state.geo_tier
    price_discount = st.session_state.price_discount
    price_category = st.session_state.price_category
    festival_metrics = st.session_state.festival_metrics
    festival_bda = st.session_state.festival_bda
    
    df_rfm = st.session_state.q11_rfm
    df_behavior = st.session_state.q11_behavior
    df_ltv = st.session_state.q11_ltv
    df_marketing = st.session_state.q11_marketing
    journey_channels = st.session_state.q11_journey_channels
    purchase_patterns = st.session_state.q11_purchase_patterns
    category_transitions = st.session_state.q11_category_transitions
    customer_evolution = st.session_state.q11_customer_evolution
    prime_mix = st.session_state.q11_prime_mix
    prime_retention = st.session_state.q11_prime_retention
    member_value = st.session_state.q11_member_value
    churn_pred = st.session_state.q11_churn_pred
    strategy_effect = st.session_state.q11_strategy_effect
    lifecycle = st.session_state.q11_lifecycle
    age_category = st.session_state.q11_age_category
    age_spending = st.session_state.q11_age_spending
    geo_age = st.session_state.q11_geo_age
    marketing_ops = st.session_state.q11_marketing_ops
    
    prod_perf = st.session_state.prod_perf
    brand_perf = st.session_state.brand_perf
    inventory_demand = st.session_state.inventory_demand
    ratings = st.session_state.ratings
    new_launch = st.session_state.new_launch
    
    delivery_perf = st.session_state.delivery_perf
    payment_analytics = st.session_state.payment_analytics
    return_cancellation = st.session_state.return_cancellation
    customer_service = st.session_state.customer_service
    supply_chain = st.session_state.supply_chain

    # Dashboard feature controls
    st.sidebar.header("Dashboard Controls")
    section = st.sidebar.radio(
        "Select Section",
        [
            "1. Executive Dashboard ",
            "2. Revenue Analytics ",
            "3. Customer Analytics ",
            "4. Product & Inventory Analytics ",
            "5. Operations & Logistics ",
        ],
    )

    st.sidebar.caption("Real-time connectivity: live SQLite + CSV reads with per-session caching.")

    st.markdown("### KPI Alert Center")

    if section == "1. Executive Dashboard (Q1-Q5)":
        
        render_alert_center(monthly, price_discount)
        
        st.markdown("## Executive Dashboard (Questions 1-5)")
        # Section 1 Filters
        years = sorted(monthly["year"].unique().tolist())
        selected_year = st.sidebar.selectbox("Year", years, index=len(years) - 1)
        
        categories_all = sorted(category["category"].dropna().unique().tolist())
        selected_categories = st.sidebar.multiselect("Category Filter", categories_all, default=categories_all)
        
        monthly_y = month_sort_key(monthly[monthly["year"] == selected_year].copy())
        category_y = month_sort_key(category[(category["year"] == selected_year) & (category["category"].isin(selected_categories))].copy())
        payment_y = month_sort_key(payment[payment["year"] == selected_year].copy())
        prime_y = month_sort_key(prime[prime["year"] == selected_year].copy())
        
        q1, q2, q3, q4, q5 = st.tabs(
            [
                " Executive Summary",
                " Performance Monitor",
                " Strategic Overview",
                " Financial Performance",
                " Growth Analytics",
            ]
        )
        with q1:
            render_q1(monthly_y, category_y)
        with q2:
            render_q2(monthly_y)
        with q3:
            render_q3(monthly_y, category_y, payment_y)
        with q4:
            render_q4(monthly_y, category_y)
        with q5:
            render_q5(monthly_y, category_y, prime_y)

    elif section == "2. Revenue Analytics (Q6-Q10)":
        render_alert_center(monthly, price_discount)
        
        st.markdown("## Revenue Analytics (Questions 6-10)")
        # Section 2 Filters
        years = sorted(geo_state["year"].unique().tolist())
        selected_year = st.sidebar.selectbox("Year", years, index=len(years) - 1)
        
        categories_all = sorted(category["category"].dropna().unique().tolist())
        selected_categories = st.sidebar.multiselect("Category Filter", categories_all, default=categories_all)
        
        states_all = sorted(geo_state["state"].dropna().unique().tolist())
        selected_states = st.sidebar.multiselect("State Filter", states_all, default=states_all)
        
        category_y = month_sort_key(category[(category["year"] == selected_year) & (category["category"].isin(selected_categories))].copy())
        geo_state_y = geo_state[(geo_state["year"] == selected_year) & (geo_state["state"].isin(selected_states))].copy()
        geo_city_y = geo_city[geo_city["year"] == selected_year].copy()
        geo_tier_y = geo_tier[geo_tier["year"] <= selected_year].copy()
        
        q6, q7, q8, q9, q10 = st.tabs(
            [
                " Revenue Trend",
                " Category Performance",
                " Geographic Revenue",
                " Festival Sales",
                " Price Optimization",
            ]
        )
        with q6:
            render_q6(monthly)
        with q7:
            render_q7(category[category["category"].isin(selected_categories)])
        with q8:
            render_q8(geo_state[geo_state["state"].isin(selected_states)], geo_city, geo_tier_y)
        with q9:
            render_q9(festival_metrics, festival_bda)
        with q10:
            render_q10(price_discount, price_category[price_category["category"].isin(selected_categories)])

    elif section == "3. Customer Analytics (Q11-Q15)":
        render_alert_center(monthly, price_discount)
        
        st.markdown("## Customer Analytics (Questions 11-15)")
        # Section 3 Filters
        if "year" in df_rfm.columns:
            years_q11 = sorted(df_rfm["year"].unique().tolist())
            selected_year_q11 = st.sidebar.selectbox("Year", years_q11, index=len(years_q11) - 1, key="q11_year")
            df_rfm_filtered = df_rfm[df_rfm["year"] == selected_year_q11].copy() if "year" in df_rfm.columns else df_rfm
        else:
            df_rfm_filtered = df_rfm
        
        if "year" in age_category.columns:
            age_category_filtered = age_category[age_category["year"] == selected_year_q11].copy() if "year" in age_category.columns else age_category
        else:
            age_category_filtered = age_category
        
        q11, q12, q13, q14, q15 = st.tabs(
            [
                " Customer Segmentation",
                " Journey Analytics",
                " Prime Analytics",
                " Retention Dashboard",
                " Demographics & Behavior",
            ]
        )
        with q11:
            render_q11(df_rfm_filtered, df_behavior, df_ltv, df_marketing)
        with q12:
            render_q12(journey_channels, purchase_patterns, category_transitions, customer_evolution)
        with q13:
            render_q13(prime_mix, prime_retention, member_value)
        with q14:
            render_q14(churn_pred, strategy_effect, lifecycle)
        with q15:
            render_q15(age_category_filtered, age_spending, geo_age, marketing_ops)
            
    elif section == "4. Product & Inventory Analytics (Q16-Q20)":
        render_alert_center(monthly, price_discount)
        
        st.markdown("## Product & Inventory Analytics (Questions 16-20)")
        # Section 4 Filters
        categories_q16 = sorted(prod_perf["category"].dropna().unique().tolist()) if "category" in prod_perf.columns else []
        selected_categories_q16 = st.sidebar.multiselect("Category Filter", categories_q16, default=categories_q16, key="q16_category")
        
        brands_q16 = sorted(prod_perf["brand"].dropna().unique().tolist()) if "brand" in prod_perf.columns else []
        selected_brands_q16 = st.sidebar.multiselect("Brand Filter", brands_q16, default=brands_q16, key="q16_brand")
        
        prod_perf_filtered = prod_perf.copy()
        if selected_categories_q16 and "category" in prod_perf.columns:
            prod_perf_filtered = prod_perf_filtered[prod_perf_filtered["category"].isin(selected_categories_q16)]
        if selected_brands_q16 and "brand" in prod_perf_filtered.columns:
            prod_perf_filtered = prod_perf_filtered[prod_perf_filtered["brand"].isin(selected_brands_q16)]
        
        brand_perf_filtered = brand_perf.copy()
        if selected_categories_q16 and "category" in brand_perf.columns:
            brand_perf_filtered = brand_perf_filtered[brand_perf_filtered["category"].isin(selected_categories_q16)]
        if selected_brands_q16 and "brand" in brand_perf_filtered.columns:
            brand_perf_filtered = brand_perf_filtered[brand_perf_filtered["brand"].isin(selected_brands_q16)]
        
        q16, q17, q18, q19, q20 = st.tabs([
            " Product Performance",
            " Brand Analytics",
            " Inventory Optimization",
            " Ratings & Reviews",
            " New Product Launch",
        ])
        with q16:
            render_q16(prod_perf_filtered)
        with q17:
            render_q17(brand_perf_filtered)
        with q18:
            render_q18(inventory_demand)
        with q19:
            render_q19(ratings)
        with q20:
            render_q20(new_launch)
            
    elif section == "5. Operations & Logistics (Q21-Q25)":
        render_alert_center(monthly, price_discount)
        
        st.markdown("## Operations & Logistics Analytics (Questions 21-25)")
        # Section 5 Filters
        if "year" in delivery_perf.columns:
            years_q21 = sorted(delivery_perf["year"].unique().tolist())
            selected_year_q21 = st.sidebar.selectbox("Year", years_q21, index=len(years_q21) - 1, key="q21_year")
        else:
            selected_year_q21 = None
        
        states_q21 = sorted(delivery_perf["customer_state"].dropna().unique().tolist()) if "customer_state" in delivery_perf.columns else []
        selected_states_q21 = st.sidebar.multiselect("State Filter", states_q21, default=states_q21, key="q21_state")
        
        delivery_types_q21 = sorted(delivery_perf["delivery_type"].dropna().unique().tolist()) if "delivery_type" in delivery_perf.columns else []
        selected_delivery_types_q21 = st.sidebar.multiselect("Delivery Type Filter", delivery_types_q21, default=delivery_types_q21, key="q21_delivery")
        
        delivery_perf_filtered = delivery_perf.copy()
        if selected_year_q21 and "year" in delivery_perf.columns:
            delivery_perf_filtered = delivery_perf_filtered[delivery_perf_filtered["year"] == selected_year_q21]
        if selected_states_q21 and "customer_state" in delivery_perf_filtered.columns:
            delivery_perf_filtered = delivery_perf_filtered[delivery_perf_filtered["customer_state"].isin(selected_states_q21)]
        if selected_delivery_types_q21 and "delivery_type" in delivery_perf_filtered.columns:
            delivery_perf_filtered = delivery_perf_filtered[delivery_perf_filtered["delivery_type"].isin(selected_delivery_types_q21)]
        
        payment_analytics_filtered = payment_analytics.copy()
        if selected_year_q21 and "year" in payment_analytics.columns:
            payment_analytics_filtered = payment_analytics_filtered[payment_analytics_filtered["year"] == selected_year_q21]
        
        return_cancellation_filtered = return_cancellation.copy()
        if selected_year_q21 and "year" in return_cancellation.columns:
            return_cancellation_filtered = return_cancellation_filtered[return_cancellation_filtered["year"] == selected_year_q21]
        if selected_states_q21 and "customer_state" in return_cancellation_filtered.columns:
            return_cancellation_filtered = return_cancellation_filtered[return_cancellation_filtered["customer_state"].isin(selected_states_q21)]
        
        customer_service_filtered = customer_service.copy()
        if selected_year_q21 and "year" in customer_service.columns:
            customer_service_filtered = customer_service_filtered[customer_service_filtered["year"] == selected_year_q21]
        if selected_states_q21 and "customer_state" in customer_service_filtered.columns:
            customer_service_filtered = customer_service_filtered[customer_service_filtered["customer_state"].isin(selected_states_q21)]
        
        supply_chain_filtered = supply_chain.copy()
        if selected_year_q21 and "year" in supply_chain.columns:
            supply_chain_filtered = supply_chain_filtered[supply_chain_filtered["year"] == selected_year_q21]
        
        q21, q22, q23, q24, q25 = st.tabs([
            " Delivery Performance",
            " Payment Analytics",
            " Returns & Cancellations",
            " Customer Service",
            " Supply Chain",
        ])
        with q21:
            render_q21(delivery_perf_filtered)
        with q22:
            render_q22(payment_analytics_filtered)
        with q23:
            render_q23(return_cancellation_filtered)
        with q24:
            render_q24(customer_service_filtered)
        with q25:
            render_q25(supply_chain_filtered)


if __name__ == "__main__":
    main()
