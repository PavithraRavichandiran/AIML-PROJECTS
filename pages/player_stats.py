"""
Player Stats page for Cricbuzz LiveStats
"""
import streamlit as st
import pandas as pd
from config.api_keys import RAPID_API_KEY, RAPID_API_HOST
from utils.api_client import search_players as api_search_players
from utils.api_client import get_player_info as api_get_player_info
from utils.api_client import get_player_batting as api_get_player_batting
from utils.api_client import get_player_bowling as api_get_player_bowling
from utils.db_sync import save_player, get_sync_stats, bulk_import_top_players

HEADERS = {
    "x-rapidapi-key": RAPID_API_KEY,
    "x-rapidapi-host": RAPID_API_HOST
}

@st.cache_data(ttl=300)
def search_players(query: str):
    """Cached search for players by name"""
    return api_search_players(query, HEADERS)


@st.cache_data(ttl=300)
def get_player_info(player_id: int):
    """Cached fetch of player information"""
    return api_get_player_info(player_id, HEADERS)


@st.cache_data(ttl=300)
def get_player_batting(player_id: int):
    """Cached fetch of player batting statistics"""
    return api_get_player_batting(player_id, HEADERS)


@st.cache_data(ttl=300)
def get_player_bowling(player_id: int):
    """Cached fetch of player bowling statistics"""
    return api_get_player_bowling(player_id, HEADERS)


def render():
    """Render player stats page"""
    st.title("🎯 Cricket Player Statistics")
    # st.caption("Search players and view profile + detailed batting & bowling stats (RapidAPI)")
    
    # Show DB sync status with bulk import button
    col1, col2 = st.columns([3, 1])
    with col1:
        try:
            stats = get_sync_stats()
            st.caption(f"💾 Database: {stats['players']} players synced")
        except:
            pass
    
    with col2:
        if st.button("📥 Import Indian Players", help="Import Indian cricket team players from API"):
            with st.spinner("Importing players from API..."):
                try:
                    count = bulk_import_top_players(team_id=2, headers=HEADERS)
                    st.success(f"✓ Imported {count} players!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Import failed: {e}")

    query = st.text_input("Search player by name", placeholder="e.g., Virat Kohli")

    if query and len(query.strip()) < 3:
        st.info("Type at least 3 characters to search.")
        st.stop()

    if query:
        with st.spinner("Searching players..."):
            status, results = search_players(query.strip())

        if status != 200:
            st.error("Player search failed")
            st.write(results)
            st.stop()

        # --- IMPORTANT ---
        # Your search response structure may differ.
        # We'll try to extract a list of players safely.
        players = None
        if isinstance(results, dict):
            # common possibilities
            players = results.get("player") or results.get("players") or results.get("data") or results.get("result")
        if players is None and isinstance(results, list):
            players = results

        if not players:
            st.warning(f"❌ No players found for '{query}'")
            st.info("💡 **Suggestions:**\n- Try searching with the full name (e.g., 'Virat Kohli' instead of 'Virat')\n- Popular players: Virat Kohli, Rohit Sharma, Jasprit Bumrah, AB de Villiers")
            with st.expander("Debug search response"):
                st.json(results)
            st.stop()

        # Build dropdown options
        options = []
        for p in players:
            if not isinstance(p, dict):
                continue
            pid = p.get("id") or p.get("playerId")
            name = p.get("name") or p.get("fullName") or p.get("playerName") or "Unknown"
            team = p.get("teamName") or p.get("country") or ""
            if pid:
                options.append({"label": f"{name} {('- ' + team) if team else ''}", "id": int(pid)})

        if not options:
            st.warning("Players found but could not detect playerId fields. Open debug.")
            with st.expander("Debug search response"):
                st.json(results)
            st.stop()

        selected = st.selectbox("Select player", options, format_func=lambda x: x["label"])
        player_id = selected["id"]

        # Create three tabs for Profile, Batting, and Bowling
        tab1, tab2, tab3 = st.tabs(["👤 Profile", "🏏 Batting", "🎯 Bowling"])

        # Tab 1: Profile
        with tab1:
            with st.spinner("Loading profile..."):
                s1, info = get_player_info(player_id)

            if s1 != 200:
                st.error("Failed to load player profile")
                st.write(info)
            else:
                # Auto-sync: Save player to database
                try:
                    save_player(info)
                except Exception as e:
                    pass  # Silent fail to not disrupt UI
                # Profile Header with Image and Nickname
                if isinstance(info, dict):
                    profile_col1, profile_col2 = st.columns([1, 3])
                    
                    with profile_col1:
                        # Display player image if available
                        image_url =  info.get('image') 
                        if image_url:
                            st.image(image_url, width=150)
                        else:
                            st.markdown("📸 No Image")
                    
                    with profile_col2:
                        # Display player name and nickname
                        player_name = info.get('name')  or 'Unknown'
                        player_nickname = info.get('nickName')  or ''
                        
                        st.markdown(f"# {player_name}")
                        if player_nickname:
                            st.markdown(f"*Nickname: **{player_nickname}***")
                
                st.divider()
                st.subheader("👤 Personal Information")
                # Display common fields safely
                if isinstance(info, dict):
                    # Create three columns for different sections
                    col1, col2, col3 = st.columns(3)
                    
                    # Column 1: Cricket Details
                    with col1:
                        st.markdown("**🏏 Cricket Details**")
                        st.write(f"**Role:** {info.get('role') or info.get('playingRole') or '—'}")
                        st.write(f"**Batting Style:** {info.get('bat') or '—'}")
                        st.write(f"**Bowling Style:** {info.get('bowl') or '—'}")
                        st.write(f"**International Team:** {info.get('intlTeam') or '—'}")

                    
                    # Column 2: Personal Details
                    with col2:
                        st.markdown("**👤 Personal Details**")
                        st.write(f"**DOB:** {info.get('DoB') or info.get('dob') or '—'}")

                        st.write(f"**Birthplace:** {info.get('birthPlace') or info.get('country') or '—'}")
                        st.write(f"**Height:** {info.get('height') or '—'}")
                    
                    # Column 3: Teams Played For
                    with col3:
                        st.markdown("**⚽ Teams Played For**")
                        teams = info.get('teams') or info.get('teamsList') or []
                        if isinstance(teams, list):
                            for team in teams:
                                if isinstance(team, dict):
                                    st.write(f"• {team.get('name') or team.get('teamName') or '—'}")
                                else:
                                    st.write(f"• {team}")
                        elif isinstance(teams, str):
                            # If teams is a comma-separated string, split and display as list
                            team_list = [t.strip() for t in teams.split(',')]
                            for team in team_list:
                                st.write(f"• {team}")
                        else:
                            st.write(f"**Current Team:** {teams or '—'}")
                
                # Display Full Profile Link
                # Check for webURL in appIndex first (nested structure)
                app_index = info.get('appIndex') or {}
                profile_url = app_index.get('webURL') or info.get('webURL')
                
                if profile_url:
                    st.markdown("---")
                    st.markdown(f"[🔗 View Full Profile on Cricbuzz]({profile_url})")
                
                with st.expander("Debug profile JSON"):
                    st.json(info)

        # Tab 2: Batting Stats
        with tab2:
            with st.spinner("Loading batting stats..."):
                s2, bat = get_player_batting(player_id)

            if s2 != 200:
                st.error("Failed to load batting stats")
                st.write(bat)
            else:
                st.subheader("🏏 Batting Statistics")
                
                if isinstance(bat, dict):
                    # Extract headers and values
                    headers = bat.get('headers', [])
                    values = bat.get('values', [])
                    
                    if headers and values:
                        # Build DataFrame from the data
                        df_data = {}
                        for row in values:
                            row_values = row.get('values', [])
                            if row_values:
                                stat_name = row_values[0]  # First element is the stat name (ROWHEADER)
                                df_data[stat_name] = row_values[1:]  # Rest are the values for each format
                        
                        # Display overview for all formats
                        st.markdown("#### 📊 Overview ")
                        
                        for idx, format_name in enumerate(headers[1:]):
                            col1, col2, col3, col4 = st.columns(4)
                            
                            matches = df_data.get('Matches', ['—'])[idx] if idx < len(df_data.get('Matches', [])) else '—'
                            runs = df_data.get('Runs', ['—'])[idx] if idx < len(df_data.get('Runs', [])) else '—'
                            avg = df_data.get('Average', ['—'])[idx] if idx < len(df_data.get('Average', [])) else '—'
                            sr = df_data.get('SR', ['—'])[idx] if idx < len(df_data.get('SR', [])) else '—'
                            
                            with col1:
                                st.metric(f"Matches ({format_name})", matches)
                            with col2:
                                st.metric(f"Runs ({format_name})", runs)
                            with col3:
                                st.metric(f"Avg ({format_name})", avg)
                            with col4:
                                st.metric(f"SR ({format_name})", sr)
                        
                        st.divider()
                        
                        # Create DataFrame
                        df = pd.DataFrame(df_data, index=headers[1:]).T
                        df.index.name = "Statistics"
                        
                        st.markdown("#### 📈 Detailed Statistics")
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.json(bat)
                else:
                    st.json(bat)

        # Tab 3: Bowling Stats
        with tab3:
            with st.spinner("Loading bowling stats..."):
                s3, bowl = get_player_bowling(player_id)

            if s3 != 200:
                st.error("Failed to load bowling stats")
                st.write(bowl)
            else:
                st.subheader("🎯 Bowling Statistics")
                
                if isinstance(bowl, dict):
                    # Extract headers and values
                    headers = bowl.get('headers', [])
                    values = bowl.get('values', [])
                    
                    if headers and values:
                        # Build DataFrame from the data
                        df_data = {}
                        for row in values:
                            row_values = row.get('values', [])
                            if row_values:
                                stat_name = row_values[0]  # First element is the stat name (ROWHEADER)
                                df_data[stat_name] = row_values[1:]  # Rest are the values for each format
                        
                        # Display overview for all formats
                        st.markdown("#### 📊 Overview ")
                        
                        for idx, format_name in enumerate(headers[1:]):
                            col1, col2, col3, col4 = st.columns(4)
                            
                            matches = df_data.get('Matches', ['—'])[idx] if idx < len(df_data.get('Matches', [])) else '—'
                            wickets = df_data.get('Wickets', ['—'])[idx] if idx < len(df_data.get('Wickets', [])) else '—'
                            avg = df_data.get('Avg', ['—'])[idx] if idx < len(df_data.get('Avg', [])) else '—'
                            econ = df_data.get('Eco', ['—'])[idx] if idx < len(df_data.get('Eco', [])) else '—'
                            
                            with col1:
                                st.metric(f"Matches ({format_name})", matches)
                            with col2:
                                st.metric(f"Wickets ({format_name})", wickets)
                            with col3:
                                st.metric(f"Avg ({format_name})", avg)
                            with col4:
                                st.metric(f"Economy ({format_name})", econ)
                        
                        st.divider()
                        
                        # Create DataFrame
                        df = pd.DataFrame(df_data, index=headers[1:]).T
                        df.index.name = "Statistics"
                        
                        st.markdown("#### 📈 Detailed Statistics")
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.json(bowl)
                else:
                    st.json(bowl)
