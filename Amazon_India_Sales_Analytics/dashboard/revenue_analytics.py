import streamlit as st
import pandas as pd
import plotly.express as px
from utils import add_month_label


def render_q6(monthly_all: pd.DataFrame):
    st.subheader("Q6: Revenue Trend Analysis Dashboard")

    period = st.radio("Select Time Period", ["Monthly", "Quarterly", "Yearly"], horizontal=True, key="q6_period")
    years_available = sorted(monthly_all["year"].unique().tolist())
    selected_years = st.multiselect("Select Years", years_available, default=years_available[-3:], key="q6_years")
    base = monthly_all[monthly_all["year"].isin(selected_years)].copy()

    if period == "Monthly":
        trend = base.groupby(["year", "month", "month_label"], as_index=False).agg(
            revenue_inr=("revenue_inr", "sum"),
            orders=("orders", "sum")
        )
        x_col = "month_label"
    elif period == "Quarterly":
        trend = base.groupby(["year", "quarter"], as_index=False).agg(revenue_inr=("revenue_inr", "sum"), orders=("orders", "sum"))
        trend["period_label"] = trend["year"].astype(str) + "-Q" + trend["quarter"].astype(str)
        x_col = "period_label"
    else:
        trend = base.groupby(["year"], as_index=False).agg(revenue_inr=("revenue_inr", "sum"), orders=("orders", "sum"))
        trend["period_label"] = trend["year"].astype(str)
        x_col = "period_label"

    fig_rev = px.line(trend, x=x_col, y="revenue_inr", markers=True, title=f"{period} Revenue Pattern")
    st.plotly_chart(fig_rev, use_container_width=True)

    seasonality = base.groupby("month_name", as_index=False).agg(revenue_inr=("revenue_inr", "mean"))
    seasonality["month_order"] = pd.to_datetime(seasonality["month_name"], format="%B").dt.month
    seasonality = seasonality.sort_values("month_order")
    fig_season = px.bar(seasonality, x="month_name", y="revenue_inr", title="Seasonal Variation (Avg Revenue by Month)")
    st.plotly_chart(fig_season, use_container_width=True)

    forecast = trend.copy()
    forecast["forecast_revenue_inr"] = forecast["revenue_inr"].rolling(3, min_periods=1).mean()
    fig_fc = px.line(forecast, x=x_col, y=["revenue_inr", "forecast_revenue_inr"], title="Revenue Forecast (3-Period Moving Average)")
    st.plotly_chart(fig_fc, use_container_width=True)


def render_q7(category_all: pd.DataFrame):
    st.subheader("Q7: Category Performance Dashboard")

    cat_group = category_all.groupby(["year", "category"], as_index=False).agg(
        revenue_inr=("revenue_inr", "sum"),
        revenue_share_pct=("category_revenue_share_pct", "mean")
    )
    latest_year = int(cat_group["year"].max())
    current = cat_group[cat_group["year"] == latest_year].sort_values("revenue_inr", ascending=False)

    fig_contrib = px.bar(current, x="category", y="revenue_inr", title=f"Revenue Contribution by Category ({latest_year})")
    st.plotly_chart(fig_contrib, use_container_width=True)

    fig_share = px.line(cat_group, x="year", y="revenue_share_pct", color="category", markers=True, title="Category Market Share Trend")
    st.plotly_chart(fig_share, use_container_width=True)

    category_choice = st.selectbox("Drill Down Category", sorted(category_all["category"].unique().tolist()), key="q7_cat")
    drill = category_all[category_all["category"] == category_choice].groupby(["year", "subcategory"], as_index=False).agg(
        revenue_inr=("revenue_inr", "sum")
    )
    fig_drill = px.bar(drill, x="subcategory", y="revenue_inr", color="year", barmode="group", title=f"Drill-Down: {category_choice} Subcategory Revenue")
    st.plotly_chart(fig_drill, use_container_width=True)

    # proxy profitability: realized margin ratio from revenue share concentration
    top2_share = current.head(2)["revenue_inr"].sum() * 100.0 / current["revenue_inr"].sum()
    st.metric("Top-2 Category Revenue Concentration", f"{top2_share:.2f}%")


def render_q8(geo_state: pd.DataFrame, geo_city: pd.DataFrame, geo_tier: pd.DataFrame):
    st.subheader("Q8: Geographic Revenue Analysis Dashboard")

    latest_year = int(geo_state["year"].max())
    state_latest = geo_state[geo_state["year"] == latest_year].sort_values("revenue_inr", ascending=False).head(15)
    city_latest = geo_city[geo_city["year"] == latest_year].sort_values("revenue_inr", ascending=False).head(15)
    tier_trend = geo_tier.groupby(["year", "customer_tier"], as_index=False).agg(revenue_inr=("revenue_inr", "sum"))

    c1, c2 = st.columns(2)
    with c1:
        fig_state = px.bar(state_latest, x="state", y="revenue_inr", title=f"State-wise Revenue ({latest_year})")
        st.plotly_chart(fig_state, use_container_width=True)
    with c2:
        fig_city = px.bar(city_latest, x="city", y="revenue_inr", title=f"City-wise Revenue ({latest_year})")
        st.plotly_chart(fig_city, use_container_width=True)

    fig_tier = px.line(tier_trend, x="year", y="revenue_inr", color="customer_tier", markers=True, title="Tier-wise Growth Pattern")
    st.plotly_chart(fig_tier, use_container_width=True)

    state_latest = state_latest.copy()
    state_latest["penetration_proxy"] = state_latest["revenue_inr"] / state_latest["customers"].clip(lower=1)
    opp = state_latest.sort_values("penetration_proxy", ascending=False).head(5)
    st.dataframe(opp[["state", "revenue_inr", "customers", "penetration_proxy"]], use_container_width=True)
    st.caption("Market penetration opportunity proxy = revenue per customer.")


def render_q9(festival_metrics: pd.DataFrame, festival_bda: pd.DataFrame):
    st.subheader("Q9: Festival Sales Analytics Dashboard")

    top_festival = festival_metrics.sort_values("total_revenue", ascending=False).head(10)
    fig_fest = px.bar(top_festival, x="festival", y="total_revenue", title="Festival Revenue Performance", text="revenue_pct")
    fig_fest.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    st.plotly_chart(fig_fest, use_container_width=True)

    period_perf = festival_bda.groupby(["festival", "period"], as_index=False).agg(revenue=("revenue", "sum"))
    fig_period = px.bar(period_perf, x="festival", y="revenue", color="period", barmode="group", title="Campaign Effectiveness: Before vs During vs After")
    st.plotly_chart(fig_period, use_container_width=True)

    promo = festival_bda.groupby("period", as_index=False).agg(
        avg_order_value=("avg_order_value", "mean"),
        daily_revenue=("daily_revenue", "mean")
    )
    fig_promo = px.bar(promo, x="period", y="daily_revenue", title="Promotional Impact (Average Daily Revenue by Period)")
    st.plotly_chart(fig_promo, use_container_width=True)


def render_q10(price_discount: pd.DataFrame, price_category: pd.DataFrame):
    st.subheader("Q10: Price Optimization Dashboard")

    high_volume = price_discount[price_discount["transactions"] >= 100]
    fig_elasticity = px.scatter(
        high_volume,
        x="discount_bucket",
        y="avg_qty",
        size="transactions",
        color="avg_revenue_per_txn",
        title="Price Elasticity Proxy (Discount vs Quantity)",
    )
    st.plotly_chart(fig_elasticity, use_container_width=True)

    fig_discount = px.line(
        high_volume,
        x="discount_bucket",
        y="total_revenue_inr",
        markers=True,
        title="Discount Effectiveness (Revenue by Discount Bucket)",
    )
    st.plotly_chart(fig_discount, use_container_width=True)

    fig_comp = px.bar(
        price_category,
        x="category",
        y=["avg_list_price", "avg_realized_price"],
        barmode="group",
        title="Category Pricing Comparison (List vs Realized)",
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    best_bucket = high_volume.sort_values("total_revenue_inr", ascending=False).head(1)
    if not best_bucket.empty:
        row = best_bucket.iloc[0]
        st.metric("Best Revenue Discount Bucket", f"{row['discount_bucket']:.1f}%", f"₹{row['total_revenue_inr']:,.0f}")