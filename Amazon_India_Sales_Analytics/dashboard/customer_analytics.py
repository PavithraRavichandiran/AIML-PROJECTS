import streamlit as st
import pandas as pd
import plotly.express as px


def render_q11(
    rfm_dist: pd.DataFrame, behavioral: pd.DataFrame,
    ltv_buckets: pd.DataFrame, marketing_recs: pd.DataFrame
):
    st.subheader("Q11: Customer Segmentation Dashboard")
    if not rfm_dist.empty:
        fig = px.bar(rfm_dist, x="rfm_segment", y="customer_count",
                     title="Customers by RFM Segment", text="customer_count")
        st.plotly_chart(fig, use_container_width=True)
        fig2 = px.bar(rfm_dist, x="rfm_segment", y="avg_ltv",
                      title="Average Predicted LTV by Segment", text="avg_ltv")
        st.plotly_chart(fig2, use_container_width=True)
    if not behavioral.empty:
        fig3 = px.bar(behavioral, x="customer_segment", y="customer_count",
                      title="Behavioral Segment Counts")
        st.plotly_chart(fig3, use_container_width=True)
    if not ltv_buckets.empty:
        fig4 = px.pie(ltv_buckets, names="ltv_bucket", values="customers",
                      title="LTV Bucket Distribution")
        st.plotly_chart(fig4, use_container_width=True)
    if not marketing_recs.empty:
        st.write("Sample customers flagged for targeted marketing:")
        st.dataframe(marketing_recs.head(100))


def render_q12(
    journey_channels: pd.DataFrame,
    purchase_patterns: pd.DataFrame,
    category_transitions: pd.DataFrame,
    customer_evolution: pd.DataFrame
):
    st.subheader("Q12: Customer Journey Analytics Dashboard")
    if not journey_channels.empty:
        fig = px.bar(journey_channels, x="channel", y="new_customers",
                     title="Acquisition Channels (first orders)")
        st.plotly_chart(fig, use_container_width=True)
    if not purchase_patterns.empty:
        fig2 = px.line(purchase_patterns, x="months_since_first", y="avg_orders",
                       title="Average Orders by Months Since First Purchase", markers=True)
        st.plotly_chart(fig2, use_container_width=True)
    if not category_transitions.empty:
        fig3 = px.sunburst(category_transitions, path=["from_category", "to_category"],
                            values="customer_count",
                            title="Category Transition Flow")
        st.plotly_chart(fig3, use_container_width=True)
    if not customer_evolution.empty:
        fig4 = px.pie(customer_evolution, names="lifecycle_stage", values="customer_count",
                      title="Customer Lifecycle Stage Distribution")
        st.plotly_chart(fig4, use_container_width=True)


def render_q13(
    prime_mix: pd.DataFrame,
    prime_retention: pd.DataFrame,
    member_value: pd.DataFrame
):
    st.subheader("Q13: Prime Membership Analytics Dashboard")
    if not prime_mix.empty:
        fig = px.bar(prime_mix, x="is_prime_member", y="revenue_inr",
                     title="Revenue: Prime vs Non-Prime", text="revenue_inr")
        st.plotly_chart(fig, use_container_width=True)
    if not prime_retention.empty:
        fig2 = px.line(prime_retention, x="month", y="retention_rate_pct",
                       color="is_prime_member", title="Monthly Retention Rate by Prime Status")
        st.plotly_chart(fig2, use_container_width=True)
    if not member_value.empty:
        fig3 = px.bar(member_value, x="is_prime_member", y="avg_ltv",
                      title="Average LTV: Prime vs Non-Prime", text="avg_ltv")
        st.plotly_chart(fig3, use_container_width=True)


def render_q14(
    churn_pred: pd.DataFrame,
    strategy_effect: pd.DataFrame,
    lifecycle: pd.DataFrame
):
    st.subheader("Q14: Customer Retention Dashboard")
    if not churn_pred.empty:
        st.write("Top customers by predicted churn risk")
        st.dataframe(churn_pred.head(50))
    if not strategy_effect.empty:
        fig = px.bar(strategy_effect, x="loyalty_tier", y="customers",
                     title="Retention Strategy Effectiveness", text="avg_churn_risk")
        st.plotly_chart(fig, use_container_width=True)
    if not lifecycle.empty:
        fig2 = px.pie(lifecycle, names="account_age_stage", values="customers",
                      title="Customer Account Age Stages")
        st.plotly_chart(fig2, use_container_width=True)


def render_q15(
    age_category: pd.DataFrame,
    age_spending: pd.DataFrame,
    geo_age: pd.DataFrame,
    marketing_ops: pd.DataFrame
):
    st.subheader("Q15: Demographics & Behavior Dashboard")
    if not age_category.empty:
        fig = px.bar(age_category, x="age_group", y="revenue",
                     color="category", title="Revenue by Age Group and Category")
        st.plotly_chart(fig, use_container_width=True)
    if not age_spending.empty:
        fig2 = px.bar(age_spending, x="age_group", y="avg_spend",
                      title="Average Spend by Age Group")
        st.plotly_chart(fig2, use_container_width=True)
    if not geo_age.empty:
        fig3 = px.scatter(geo_age, x="state", y="revenue",
                          color="age_group", size="orders",
                          title="Geo‑Age Revenue Scatter")
        st.plotly_chart(fig3, use_container_width=True)
    if not marketing_ops.empty:
        st.write("High-value demographic opportunities")
        st.dataframe(marketing_ops.head(100))