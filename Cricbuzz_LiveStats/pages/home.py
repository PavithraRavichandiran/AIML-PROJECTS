"""
Home page for Cricbuzz LiveStats
"""
import streamlit as st
from utils.db_sync import get_sync_stats


def render():
    """Render home page"""
    
    # Hero Section
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1>🏏 Cricbuzz LiveStats</h1>
        <p style='font-size: 1.2rem; color: #666;'>Real-time Cricket Analytics & Data Management Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Database Stats Dashboard
    st.subheader("📊 Database Overview")
    try:
        stats = get_sync_stats()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="👥 Players",
                value=stats['players'],
                help="Total players in database"
            )
        
        with col2:
            st.metric(
                label="🏟️ Matches",
                value=stats['matches'],
                help="Total matches tracked"
            )
        
        with col3:
            st.metric(
                label="📋 Scorecards",
                value=stats['scorecards'],
                help="Total innings recorded"
            )
    except:
        st.info("Database statistics unavailable")
    
    st.divider()

    # Key Features with Icons
    st.subheader("✨ Key Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📡 Live Data Integration
        - Real-time match updates from Cricbuzz API
        - Auto-sync functionality for matches & scorecards
        - Detailed player profiles with statistics
        
        ### 📈 SQL Analytics Engine
        - 25 pre-built analytical queries
        - Custom query execution
        - Export results to CSV
        """)
    
    with col2:
        st.markdown("""
        ### 🛠️ Data Management
        - Full CRUD operations for players
        - Bulk import for Indian cricket stars
        - Smart ID auto-generation
        
        ### 🎨 Modern Interface
        - Responsive design
        - Toast notifications
        - Interactive data tables
        """)

    st.divider()

    # Quick Start Guide
    st.subheader("🚀 Quick Start Guide")
    
    with st.expander("1️⃣ Populate Database with Real Data", expanded=False):
        st.markdown("""
        **Step 1: Import Players**
        - Navigate to **Player Stats** page
        - Click **"📥 Import Top Indian Players"** button
        - ✅ 32 cricket stars added instantly!
        
        **Step 2: Sync Live Matches** *(Requires API quota)*
        - Go to **Live Scores** page
        - Click **"📥 Sync All Matches"** button
        - Fetches all current matches with scorecards
        
        """)
    
    with st.expander("2️⃣ Explore Analytics", expanded=False):
        st.markdown("""
        Go to **SQL Analytics** page and run queries:
        - **Q1**: View all Indian players
        - **Q2**: Recent matches
        - **Q3**: Top run scorers by team
        - **Q10**: Detailed scorecard analysis
        - Plus 21 more analytical queries!
        """)
    
    with st.expander("3️⃣ Manage Data with CRUD", expanded=False):
        st.markdown("""
        Visit **CRUD Operations** page to:
        - ➕ **Create**: Add new players with auto-generated IDs
        - 📄 **Read**: Search and view all players
        - ✏️ **Update**: Edit player information
        - 🗑️ **Delete**: Remove players (with confirmation)
        
        All operations show toast notifications for instant feedback!
        """)

    st.divider()

    # Tech Stack
    st.subheader("🔧 Tech Stack")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Frontend**
        - 🎨 Streamlit
        - 🐍 Python 3.11+
        - 📊 Pandas
        """)
    
    with col2:
        st.markdown("""
        **Backend**
        - 🗄️ SQLite Database
        - 🔌 RapidAPI
        - 🏏 Cricbuzz API
        """)
    
    with col3:
        st.markdown("""
        **Features**
        - 🔄 Auto-sync
        - 📥 Bulk Import
        - 🎯 CRUD Operations
        """)

    st.divider()

    # Project Structure
    with st.expander("📁 Project Structure"):
        st.code("""
Cricbuzz_LiveStats/
├── main.py                       # Application entry point
├── config/
│   └── api_keys.py              # RapidAPI configuration
├── pages/
│   ├── home.py                  # Home dashboard
│   ├── live_scores.py           # Live match tracking
│   ├── player_stats.py          # Player analytics
│   ├── sql_analytics.py         # 25 SQL queries
│   └── crud_operations.py       # Data management
├── utils/
│   ├── api_client.py            # API integration
│   ├── db_sync.py               # Database sync utilities
│   ├── db_connection.py         # Database connector
│   └── crud_players.py          # Player CRUD logic
├── db/
│   ├── cricbuzz.db              # SQLite database
│   ├── init_sqlite.py           # Database setup
│   └── sqlite_db.py             # Database utilities
└── data/                        # Data storage
        """, language="")

    st.divider()

    # Status & Limitations
    st.subheader("⚠️ Current Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("""
        **✅ Working Features**
        - Database with 36+ players
        - All 25 SQL queries functional
        - Complete CRUD operations
        - Auto-sync functionality
        - Toast notifications
        """)
    
    # with col2:
    #     st.warning("""
    #     **⚠️ Known Limitations**
    #     - API quota exhausted (free plan)
    #     - Limited match data (2 matches)
    #     - Live sync requires API quota
    #     - Sample data for demonstration
    #     """)

    st.divider()

    # Footer with metadata
    footer_col1, footer_col2, footer_col3 = st.columns(3)
    
    with footer_col1:
        st.caption("🏏 Cricbuzz LiveStats v2.0")
    
    with footer_col2:
        st.caption("Built with Streamlit & Python")
    
    with footer_col3:
        st.caption("© 2026 Real-time Cricket Analytics")

