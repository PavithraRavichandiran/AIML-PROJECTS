from config import query_df, read_csv_df
import streamlit as st


def load_data():
    monthly = query_df(
        """
        SELECT year, month, month_name, quarter,
             revenue_inr, orders, unique_customers,
               avg_order_value_inr, mom_revenue_growth_pct,
               yoy_revenue_growth_pct
        FROM vw_exec_monthly_overview
        ORDER BY year, month
        """
    )
    category = query_df(
        """
         SELECT year, month, category, subcategory,
               revenue_inr, category_revenue_share_pct, category_rank_in_month
        FROM vw_exec_category_share
        WHERE category_rank_in_month <= 5
        ORDER BY year, month, category_rank_in_month
        """
    )
    payment = query_df(
        """
        SELECT year, month, month_name, payment_method,
               revenue_inr, payment_revenue_share_pct
        FROM vw_exec_payment_mix
        ORDER BY year, month
        """
    )
    prime = query_df(
        """
         SELECT year, month, month_name, member_type,
             revenue_inr, revenue_share_pct
        FROM vw_exec_prime_split
        ORDER BY year, month
        """
    )
    return monthly, category, payment, prime


def load_q6_q10_data():
    geo_state = query_df(
        """
        SELECT year, customer_state_dim AS state,
               SUM(final_amount_inr) AS revenue_inr,
               COUNT(DISTINCT customer_id) AS customers
        FROM vw_fact_sales_enriched
        WHERE customer_state_dim IS NOT NULL
        GROUP BY year, customer_state_dim
        ORDER BY year, revenue_inr DESC
        """
    )
    geo_city = query_df(
        """
        SELECT year, customer_city_dim AS city,
               SUM(final_amount_inr) AS revenue_inr,
               COUNT(DISTINCT customer_id) AS customers
        FROM vw_fact_sales_enriched
        WHERE customer_city_dim IS NOT NULL
        GROUP BY year, customer_city_dim
        ORDER BY year, revenue_inr DESC
        """
    )
    geo_tier = query_df(
        """
        SELECT year, customer_tier,
               SUM(final_amount_inr) AS revenue_inr,
               COUNT(DISTINCT customer_id) AS customers
        FROM vw_fact_sales_enriched
        GROUP BY year, customer_tier
        ORDER BY year, revenue_inr DESC
        """
    )
    price_discount = query_df(
        """
        SELECT ROUND(discount_percent, 1) AS discount_bucket,
               AVG(quantity) AS avg_qty,
               AVG(final_amount_inr) AS avg_revenue_per_txn,
               COUNT(*) AS transactions,
               SUM(final_amount_inr) AS total_revenue_inr
        FROM vw_fact_sales_enriched
        GROUP BY ROUND(discount_percent, 1)
        ORDER BY discount_bucket
        """
    )
    price_category = query_df(
        """
        SELECT category,
               AVG(product_list_price_inr) AS avg_list_price,
               AVG(discount_percent) AS avg_discount_pct,
               AVG(final_amount_inr) AS avg_realized_price,
               SUM(final_amount_inr) AS total_revenue_inr
        FROM vw_fact_sales_enriched
        GROUP BY category
        ORDER BY total_revenue_inr DESC
        """
    )

    festival_metrics = read_csv_df("Q08_Festival_Performance_Metrics.csv")
    festival_bda = read_csv_df("Q08_Festival_Before_During_After.csv")

    return geo_state, geo_city, geo_tier, price_discount, price_category, festival_metrics, festival_bda


# -----------------------------------------------------------------------------
# Additional data loaders for questions 11-15 (customer analytics)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def load_q11_q15_data():
    # segmentation views
    rfm_dist = query_df("SELECT * FROM vw_q11_rfm_distribution")
    behavioral = query_df("SELECT * FROM vw_q11_behavioral_segmentation")
    ltv_buckets = query_df("SELECT * FROM vw_q11_ltv_buckets")
    marketing_recs = query_df("SELECT * FROM vw_q11_marketing_recs")
    # journey analytics
    journey_channels = query_df("SELECT * FROM vw_q12_acquisition_channels")
    purchase_patterns = query_df("SELECT * FROM vw_q12_purchase_patterns")
    category_transitions = query_df("SELECT * FROM vw_q12_category_transitions")
    customer_evolution = query_df("SELECT * FROM vw_q12_customer_evolution")
    # prime membership analytics
    prime_mix = query_df("SELECT * FROM vw_q13_prime_mix")
    prime_retention = query_df("SELECT * FROM vw_q13_prime_retention")
    member_value = query_df("SELECT * FROM vw_q13_member_value")
    # retention and churn
    churn_pred = query_df("SELECT * FROM vw_q14_churn_prediction")
    strategy_effect = query_df("SELECT * FROM vw_q14_strategy_effectiveness")
    lifecycle = query_df("SELECT * FROM vw_q14_customer_lifecycle")
    # demographic & behavior
    age_category = query_df("SELECT * FROM vw_q15_age_category_preferences")
    age_spending = query_df("SELECT * FROM vw_q15_age_spending")
    geo_age = query_df("SELECT * FROM vw_q15_geographic_age")
    marketing_ops = query_df("SELECT * FROM vw_q15_marketing_opportunities")
    return (
        rfm_dist, behavioral, ltv_buckets, marketing_recs,
        journey_channels, purchase_patterns, category_transitions, customer_evolution,
        prime_mix, prime_retention, member_value,
        churn_pred, strategy_effect, lifecycle,
        age_category, age_spending, geo_age, marketing_ops
    )


def load_q16_q20_data():
    # product and brand performance
    prod_perf = query_df("SELECT * FROM vw_q16_product_performance")
    brand_perf = query_df("SELECT * FROM vw_q17_brand_performance")
    # inventory demand/time series
    inventory_demand = query_df("SELECT * FROM vw_q18_inventory_demand")
    # ratings and reviews
    ratings = query_df("SELECT * FROM vw_q19_ratings")
    # new product launch metrics
    new_launch = query_df("SELECT * FROM vw_q20_new_product_launch")
    return prod_perf, brand_perf, inventory_demand, ratings, new_launch


def load_q21_q25_data():
    # delivery performance
    delivery_perf = query_df("SELECT * FROM vw_q21_delivery_performance")
    # payment analytics
    payment_analytics = query_df("SELECT * FROM vw_q22_payment_analytics")
    # return & cancellation
    return_cancellation = query_df("SELECT * FROM vw_q23_return_cancellation")
    # customer service
    customer_service = query_df("SELECT * FROM vw_q24_customer_service")
    # supply chain
    supply_chain = query_df("SELECT * FROM vw_q25_supply_chain")
    return delivery_perf, payment_analytics, return_cancellation, customer_service, supply_chain


# ============================================================================
# Section-wise cached wrappers to cache per section independently
# ============================================================================
@st.cache_data
def cached_load_data():
    return load_data()

@st.cache_data
def cached_load_q6_q10_data():
    return load_q6_q10_data()

@st.cache_data
def cached_load_q11_q15_data():
    return load_q11_q15_data()

@st.cache_data
def cached_load_q16_q20_data():
    return load_q16_q20_data()

@st.cache_data
def cached_load_q21_q25_data():
    return load_q21_q25_data()
