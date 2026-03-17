import streamlit as st
import pandas as pd
import plotly.express as px
from utils import add_month_label


def render_q1(monthly_y: pd.DataFrame, category_y: pd.DataFrame):
    st.subheader("Q1: Executive Summary Dashboard")

    latest = monthly_y.iloc[-1]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"₹{latest['revenue_inr']:,.0f}")
    col2.metric("Growth Rate (YoY)", f"{(latest['yoy_revenue_growth_pct'] if pd.notna(latest['yoy_revenue_growth_pct']) else 0.0):.2f}%")
    col3.metric("Active Customers", f"{int(latest['unique_customers']):,}")
    col4.metric("Average Order Value", f"₹{latest['avg_order_value_inr']:,.0f}")

    c1, c2 = st.columns((2, 1))
    with c1:
        fig_rev = px.line(monthly_y, x="month_label", y="revenue_inr", markers=True, title="Revenue Trend")
        fig_rev.update_layout(yaxis_title="Revenue (INR)", xaxis_title="Month")
        st.plotly_chart(fig_rev, use_container_width=True)
    with c2:
        fig_growth = px.bar(
            monthly_y,
            x="month_label",
            y="yoy_revenue_growth_pct",
            title="Year-over-Year Growth %",
            color="yoy_revenue_growth_pct",
            color_continuous_scale="RdYlGn",
        )
        st.plotly_chart(fig_growth, use_container_width=True)

    if not category_y.empty:
        latest_month = int(category_y["month"].max())
        top_cat = category_y[category_y["month"] == latest_month].sort_values("category_rank_in_month").head(10)
        fig_cat = px.bar(
            top_cat,
            y="subcategory",
            x="revenue_inr",
            orientation="h",
            text="category_revenue_share_pct",
            title=f"Top Performing Categories (Month {latest_month})",
        )
        fig_cat.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        st.plotly_chart(fig_cat, use_container_width=True)


def render_q2(monthly_y: pd.DataFrame):
    st.subheader("Q2: Business Performance Monitor")

    latest = monthly_y.iloc[-1]
    target = monthly_y["revenue_inr"].median()
    achievement = (latest["revenue_inr"] / target * 100) if target else 0
    run_rate = monthly_y["revenue_inr"].tail(3).mean()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Current Month Revenue", f"₹{latest['revenue_inr']:,.0f}")
    k2.metric("Target Revenue", f"₹{target:,.0f}")
    k3.metric("Target Achievement", f"{achievement:.1f}%")
    k4.metric("Revenue Run-Rate", f"₹{run_rate:,.0f}")

    alert = "ON_TRACK"
    if achievement < 80:
        alert = "CRITICAL"
    elif achievement < 95:
        alert = "WARNING"
    st.info(f"Performance Alert: {alert}")

    fig_target = px.line(
        monthly_y,
        x="month_label",
        y=["revenue_inr"],
        title="Revenue vs Baseline Target",
    )
    fig_target.add_hline(y=target, line_dash="dash", annotation_text="Target")
    st.plotly_chart(fig_target, use_container_width=True)


def render_q3(monthly_y: pd.DataFrame, category_y: pd.DataFrame, payment_y: pd.DataFrame):
    st.subheader("Q3: Strategic Overview Dashboard")

    if not category_y.empty:
        share_latest_month = int(category_y["month"].max())
        share_df = category_y[category_y["month"] == share_latest_month].copy()
        share_df = share_df.groupby("category", as_index=False)["revenue_inr"].sum()
        fig_share = px.pie(share_df, names="category", values="revenue_inr", title=f"Market Share by Category (Month {share_latest_month})")
        st.plotly_chart(fig_share, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig_health = px.line(
            monthly_y,
            x="month_label",
            y=["revenue_inr", "unique_customers"],
            title="Business Health Indicators (Revenue & Customers)",
        )
        st.plotly_chart(fig_health, use_container_width=True)
    with c2:
        if not payment_y.empty:
            pm = int(payment_y["month"].max())
            pay_df = payment_y[payment_y["month"] == pm].sort_values("payment_revenue_share_pct", ascending=False).head(8)
            fig_pay = px.bar(pay_df, x="payment_method", y="payment_revenue_share_pct", title=f"Payment Mix Positioning (Month {pm})")
            st.plotly_chart(fig_pay, use_container_width=True)


def render_q4(monthly_y: pd.DataFrame, category_y: pd.DataFrame):
    st.subheader("Q4: Financial Performance Dashboard")

    fin = monthly_y.copy()
    fin["cogs_inr"] = fin["revenue_inr"] * 0.50
    fin["opex_inr"] = fin["revenue_inr"] * 0.15
    fin["gross_profit_inr"] = fin["revenue_inr"] - fin["cogs_inr"] - fin["opex_inr"]
    fin["net_margin_pct"] = fin["gross_profit_inr"] * 100.0 / fin["revenue_inr"]

    f1, f2, f3 = st.columns(3)
    latest = fin.iloc[-1]
    f1.metric("Revenue", f"₹{latest['revenue_inr']:,.0f}")
    f2.metric("Estimated Gross Profit", f"₹{latest['gross_profit_inr']:,.0f}")
    f3.metric("Estimated Net Margin", f"{latest['net_margin_pct']:.2f}%")

    c1, c2 = st.columns(2)
    with c1:
        fig_margin = px.line(fin, x="month_label", y="net_margin_pct", title="Net Margin Trend")
        st.plotly_chart(fig_margin, use_container_width=True)
    with c2:
        if not category_y.empty:
            cm = int(category_y["month"].max())
            cat_rev = category_y[category_y["month"] == cm].groupby("category", as_index=False)["revenue_inr"].sum()
            fig_cat = px.bar(cat_rev, x="category", y="revenue_inr", title=f"Revenue Breakdown by Category (Month {cm})")
            st.plotly_chart(fig_cat, use_container_width=True)

    # Simple forecast (3-point moving average)
    forecast_val = fin["revenue_inr"].tail(3).mean()
    st.metric("Next-Month Forecast (Simple Run-Rate)", f"₹{forecast_val:,.0f}")


def render_q5(monthly_y: pd.DataFrame, category_y: pd.DataFrame, prime_y: pd.DataFrame):
    st.subheader("Q5: Growth Analytics Dashboard")

    g1, g2, g3 = st.columns(3)
    latest = monthly_y.iloc[-1]
    g1.metric("Customer Base", f"{int(latest['unique_customers']):,}")
    g2.metric("Customer YoY Growth", f"{(latest['yoy_revenue_growth_pct'] if pd.notna(latest['yoy_revenue_growth_pct']) else 0.0):.2f}%")

    if not category_y.empty:
        portfolio = category_y.groupby(["year", "month"], as_index=False)["subcategory"].nunique()
        portfolio = add_month_label(portfolio)
        latest_port = int(portfolio.iloc[-1]["subcategory"])
    else:
        portfolio = pd.DataFrame(columns=["month_label", "subcategory"])
        latest_port = 0
    g3.metric("Active Portfolio (Subcategories)", f"{latest_port:,}")

    c1, c2 = st.columns(2)
    with c1:
        fig_cust = px.line(monthly_y, x="month_label", y="unique_customers", markers=True, title="Customer Growth Trend")
        st.plotly_chart(fig_cust, use_container_width=True)
    with c2:
        if not portfolio.empty:
            fig_port = px.line(portfolio, x="month_label", y="subcategory", markers=True, title="Product Portfolio Expansion")
            fig_port.update_layout(yaxis_title="Unique Subcategories")
            st.plotly_chart(fig_port, use_container_width=True)

    if not prime_y.empty:
        latest_m = int(prime_y["month"].max())
        p = prime_y[prime_y["month"] == latest_m]
        fig_prime = px.pie(p, names="member_type", values="revenue_inr", title=f"Strategic Initiative: Prime Mix (Month {latest_m})")
        st.plotly_chart(fig_prime, use_container_width=True)