import streamlit as st
import pandas as pd


def render_alert_center(monthly: pd.DataFrame, price_discount: pd.DataFrame):
    if monthly is None:
        return
    
    st.subheader("Automated KPI Alert System")

    latest = monthly.sort_values(["year", "month"]).iloc[-1]
    alerts = []

    yoy = latest["yoy_revenue_growth_pct"] if pd.notna(latest["yoy_revenue_growth_pct"]) else 0.0
    mom = latest["mom_revenue_growth_pct"] if pd.notna(latest["mom_revenue_growth_pct"]) else 0.0

    if yoy < -10:
        alerts.append(("critical", f"YoY revenue decline is {yoy:.2f}% (threshold: -10%)."))
    elif yoy < 0:
        alerts.append(("warning", f"YoY revenue is negative at {yoy:.2f}%."))

    if mom < -8:
        alerts.append(("warning", f"MoM revenue drop is {mom:.2f}% (watch closely)."))

    if price_discount is not None and not price_discount.empty:
        high_volume = price_discount[price_discount["transactions"] >= 100]
        if not high_volume.empty:
            best_bucket = high_volume.loc[high_volume["total_revenue_inr"].idxmax()]
            if best_bucket["discount_bucket"] > 30:
                alerts.append(("warning", f"Best revenue discount bucket is high at {best_bucket['discount_bucket']:.1f}% — margin risk."))

    if not alerts:
        st.success("All key KPIs are within expected operating thresholds.")
        return

    for level, msg in alerts:
        if level == "critical":
            st.error(msg)
        elif level == "warning":
            st.warning(msg)
        else:
            st.info(msg)