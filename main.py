"""
Cricbuzz LiveStats - Real-time Cricket Analytics Dashboard
Main entry point for the Streamlit application
"""
import streamlit as st
import sys
import os
from datetime import datetime

# Import page modules
from pages import home, live_scores, player_stats, sql_analytics, crud_operations

# Page configuration
st.set_page_config(page_title="Cricbuzz LiveStats", layout="wide")

# Hide default Streamlit navigation
hide_streamlit_style = """
<style>
[data-testid="stSidebarNav"] {
    display: none;
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🏏 Cricket Dashboard")

pages = {
    "🏠 Home": home,
    "📊 Live Scores": live_scores,
    "👤 Player Stats": player_stats,
    "📈 SQL Analytics": sql_analytics,
    "⚙️ CRUD Operations": crud_operations
}

choice = st.sidebar.selectbox("Choose a page", list(pages.keys()))

# Page descriptions
page_info = {
    "🏠 Home": [
        "📌 Overview of the application",
        "📌 Quick stats and metrics",
        "📌 Getting started guide",
        "📌 Feature highlights"
    ],
    "📊 Live Scores": [
        "📌 Real-time match updates",
        "📌 Live scorecard data",
        "📌 Team performance metrics",
        "📌 Recent match results"
    ],
    "👤 Player Stats": [
        "📌 Individual player statistics",
        "📌 Career records & achievements",
        "📌 Performance analytics",
        "📌 Player comparison tools"
    ],
    "📈 SQL Analytics": [
        "📌 25 pre-built SQL queries",
        "📌 Basic to advanced analytics",
        "📌 Custom query execution",
        "📌 Export results to CSV"
    ],
    "⚙️ CRUD Operations": [
        "📌 Create new records",
        "📌 Read existing data",
        "📌 Update player/match info",
        "📌 Delete records"
    ]
}

# Display page information in sidebar
if choice in page_info:
    st.sidebar.divider()
    st.sidebar.markdown(f"** {choice}**")
    for point in page_info[choice]:
        st.sidebar.markdown(point)

# Debug Info Section
st.sidebar.divider()
with st.sidebar.expander("🐛 Debug Info", expanded=False):
    st.markdown("**System Information**")
    st.markdown(f"- Python: `{sys.version.split()[0]}`")
    st.markdown(f"- Streamlit: `{st.__version__}`")
    st.markdown(f"- OS: `{os.name}`")
    
    st.markdown("**Session Details**")
    st.markdown(f"- Active Page: `{choice}`")
    st.markdown(f"- Session State Keys: `{len(st.session_state)}`")
    st.markdown(f"- Timestamp: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`")
    
    st.markdown("**Database**")
    db_path = "db/cricbuzz.db"
    db_exists = os.path.exists(db_path)
    st.markdown(f"- DB Status: `{'✅ Connected' if db_exists else '❌ Not Found'}`")
    st.markdown(f"- DB Path: `{db_path}`")
    if db_exists:
        db_size = os.path.getsize(db_path) / 1024  # KB
        st.markdown(f"- DB Size: `{db_size:.2f} KB`")

# Route to selected page
if choice in pages:
    pages[choice].render()

