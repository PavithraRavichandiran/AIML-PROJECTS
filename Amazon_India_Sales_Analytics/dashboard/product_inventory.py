import streamlit as st
import pandas as pd
import plotly.express as px


def render_q16(prod_perf: pd.DataFrame):
    st.subheader("Q16: Product Performance Dashboard")
    if prod_perf.empty:
        st.info("No product performance data available.")
        return

    top_n = st.slider("Show top N products by revenue", 5, 50, 10)
    df = prod_perf.sort_values("revenue_inr", ascending=False).head(top_n)

    st.dataframe(df[['product_id','product_name','category','brand','revenue_inr','units_sold','avg_rating','return_rate_pct']])
    fig = px.bar(df, x='product_name', y='revenue_inr', color='category', title='Top Products by Revenue')
    st.plotly_chart(fig, use_container_width=True)


def render_q17(brand_perf: pd.DataFrame):
    st.subheader("Q17: Brand Analytics Dashboard")
    if brand_perf.empty:
        st.info("No brand performance data.")
        return

    cat_choice = st.selectbox("Filter by category (optional)", ['All'] + sorted(brand_perf['category'].dropna().unique().tolist()))
    df = brand_perf.copy()
    if cat_choice != 'All':
        df = df[df['category'] == cat_choice]

    fig = px.treemap(df, path=['category','brand'], values='revenue_inr', title='Brand Market Share by Category')
    st.plotly_chart(fig, use_container_width=True)


def render_q18(inventory_demand: pd.DataFrame):
    st.subheader("Q18: Inventory Optimization Dashboard")
    if inventory_demand.empty:
        st.info("No inventory demand data.")
        return

    prod_choice = st.selectbox("Select product for demand trend", ['All'] + sorted(inventory_demand['product_id'].unique().tolist()))
    df = inventory_demand.copy()
    if prod_choice != 'All':
        df = df[df['product_id'] == prod_choice]

    df['period'] = df['year'] + '-' + df['month']
    fig = px.line(df, x='period', y='units_sold', color='product_id', title='Units Sold Over Time')
    st.plotly_chart(fig, use_container_width=True)


def render_q19(ratings: pd.DataFrame):
    st.subheader("Q19: Product Rating & Review Dashboard")
    if ratings.empty:
        st.info("No rating data.")
        return

    fig = px.histogram(ratings, x='avg_product_rating', nbins=20, title='Distribution of Average Product Ratings')
    st.plotly_chart(fig, use_container_width=True)

    top_pos = ratings.sort_values('positive_pct', ascending=False).head(10)
    st.write("Top 10 products by positive review percentage")
    st.dataframe(top_pos[['product_id','product_name','avg_product_rating','positive_pct']])


def render_q20(new_launch: pd.DataFrame):
    st.subheader("Q20: New Product Launch Dashboard")
    if new_launch.empty:
        st.info("No launch data.")
        return

    recent = new_launch.sort_values('launch_date', ascending=False).head(20)
    st.dataframe(recent[['product_id','product_name','launch_date','revenue_since_launch','orders_since_launch','days_since_launch']])

    fig = px.scatter(recent, x='days_since_launch', y='revenue_since_launch', size='orders_since_launch', hover_data=['product_name'], title='Launch Performance (recent 20)')
    st.plotly_chart(fig, use_container_width=True)