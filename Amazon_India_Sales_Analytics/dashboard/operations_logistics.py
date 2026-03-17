import streamlit as st
import pandas as pd
import plotly.express as px


def render_q21(delivery_perf: pd.DataFrame):
    st.subheader("Q21: Delivery Performance Dashboard")
    if delivery_perf.empty:
        st.info("No delivery performance data available.")
        return

    # Geographic performance
    state_perf = delivery_perf.groupby('customer_state').agg({
        'total_orders': 'sum',
        'avg_delivery_days': 'mean',
        'on_time_delivery_pct': 'mean'
    }).reset_index()

    fig = px.bar(state_perf, x='customer_state', y='on_time_delivery_pct',
                 title='On-Time Delivery Rate by State', color='avg_delivery_days')
    st.plotly_chart(fig, use_container_width=True)

    # Delivery type analysis
    type_perf = delivery_perf.groupby('delivery_type').agg({
        'total_orders': 'sum',
        'avg_delivery_days': 'mean',
        'on_time_delivery_pct': 'mean'
    }).reset_index()

    fig2 = px.pie(type_perf, values='total_orders', names='delivery_type',
                  title='Orders by Delivery Type')
    st.plotly_chart(fig2, use_container_width=True)


def render_q22(payment_analytics: pd.DataFrame):
    st.subheader("Q22: Payment Analytics Dashboard")
    if payment_analytics.empty:
        st.info("No payment analytics data.")
        return

    # Payment method trends
    method_trend = payment_analytics.groupby(['year', 'month', 'payment_method']).agg({
        'transactions': 'sum',
        'revenue_inr': 'sum'
    }).reset_index()

    fig = px.line(method_trend, x='month', y='transactions', color='payment_method',
                  facet_col='year', title='Payment Method Transaction Trends')
    st.plotly_chart(fig, use_container_width=True)

    # Payment share
    latest = payment_analytics.sort_values(['year', 'month'], ascending=False).groupby('payment_method').first().reset_index()
    fig2 = px.pie(latest, values='payment_share_pct', names='payment_method',
                  title='Current Payment Method Share')
    st.plotly_chart(fig2, use_container_width=True)


def render_q23(return_cancellation: pd.DataFrame):
    st.subheader("Q23: Return & Cancellation Dashboard")
    if return_cancellation.empty:
        st.info("No return data.")
        return

    # Category-wise return rates
    cat_returns = return_cancellation.groupby('category').agg({
        'total_orders': 'sum',
        'returned_orders': 'sum',
        'return_rate_pct': 'mean',
        'return_value_lost_inr': 'sum'
    }).reset_index()

    fig = px.bar(cat_returns, x='category', y='return_rate_pct',
                 title='Return Rate by Category', color='return_value_lost_inr')
    st.plotly_chart(fig, use_container_width=True)

    # Return trends over time
    time_returns = return_cancellation.groupby(['year', 'month']).agg({
        'return_rate_pct': 'mean'
    }).reset_index()

    fig2 = px.line(time_returns, x='month', y='return_rate_pct',
                   color='year', title='Return Rate Trends')
    st.plotly_chart(fig2, use_container_width=True)


def render_q24(customer_service: pd.DataFrame):
    st.subheader("Q24: Customer Service Dashboard")
    if customer_service.empty:
        st.info("No customer service data.")
        return

    # Satisfaction by state
    state_sat = customer_service.groupby('customer_state').agg({
        'avg_customer_satisfaction': 'mean',
        'low_satisfaction_pct': 'mean',
        'delayed_delivery_pct': 'mean'
    }).reset_index()

    fig = px.scatter(state_sat, x='avg_customer_satisfaction', y='low_satisfaction_pct',
                     size='delayed_delivery_pct', hover_data=['customer_state'],
                     title='Customer Satisfaction vs Issues by State')
    st.plotly_chart(fig, use_container_width=True)

    # Satisfaction trends
    time_sat = customer_service.groupby(['year', 'month']).agg({
        'avg_customer_satisfaction': 'mean'
    }).reset_index()

    fig2 = px.line(time_sat, x='month', y='avg_customer_satisfaction',
                   color='year', title='Customer Satisfaction Trends')
    st.plotly_chart(fig2, use_container_width=True)


def render_q25(supply_chain: pd.DataFrame):
    st.subheader("Q25: Supply Chain Dashboard")
    if supply_chain.empty:
        st.info("No supply chain data.")
        return

    # Brand performance
    brand_perf = supply_chain.groupby('brand').agg({
        'total_revenue_inr': 'sum',
        'on_time_delivery_pct': 'mean',
        'avg_delivery_days': 'mean',
        'products_supplied': 'sum'
    }).reset_index()

    fig = px.scatter(brand_perf, x='on_time_delivery_pct', y='total_revenue_inr',
                     size='products_supplied', hover_data=['brand'],
                     title='Brand Performance: Delivery vs Revenue')
    st.plotly_chart(fig, use_container_width=True)

    # Category supply chain efficiency
    cat_supply = supply_chain.groupby('category').agg({
        'avg_delivery_days': 'mean',
        'on_time_delivery_pct': 'mean'
    }).reset_index()

    fig2 = px.bar(cat_supply, x='category', y='on_time_delivery_pct',
                  title='On-Time Delivery by Category', color='avg_delivery_days')
    st.plotly_chart(fig2, use_container_width=True)