"""
Live Scores page for Cricbuzz LiveStats
"""
import streamlit as st
from utils.api_client import  fetch_live_scores, fetch_scorecard, build_match_options
from config.api_keys import RAPID_API_KEY, RAPID_API_HOST
from utils.db_sync import save_match, save_scorecard, get_sync_stats, bulk_sync_matches, bulk_sync_scorecards


def render():
    """Render live scores page"""
    st.title("📡 Cricbuzz Live Match Dashboard")
    
    # Show DB sync status with bulk import button
    col1, col2 = st.columns([3, 1])
    with col1:
        try:
            stats = get_sync_stats()
            st.caption(f"💾 Database: {stats['matches']} matches | {stats['scorecards']} scorecards | {stats['players']} players")
        except:
            pass
    
    with col2:
        if st.button("📥 Sync All Matches", help="Save all live matches to database"):
            st.session_state.bulk_sync_triggered = True

    # Setup headers
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }

    # Fetch live Scores
    data = fetch_live_scores(headers)
    
    if data is None:
        st.error("Failed to fetch live match data")
        st.stop()

    # st.success("Live match data fetched successfully!")
    # st.caption("Data source: Cricbuzz API via RapidAPI")

    # with st.expander("🔍 Debug: Show Raw JSON"):
    #     st.json(data)

    type_matches = data.get("typeMatches", [])
    if not type_matches:
        st.warning("No live scores available right now (typeMatches empty).")
        st.stop()

    # Build match options
    match_options = build_match_options(data)

    if not match_options:
        st.warning("Matches found, but could not extract matchId. Check Debug JSON.")
        st.stop()
    
    # Bulk sync if button clicked
    if st.session_state.get("bulk_sync_triggered", False):
        with st.spinner(f"Syncing {len(match_options)} matches..."):
            try:
                # Save all matches
                match_count = bulk_sync_matches(match_options)
                
                # Fetch and save scorecards for all matches
                scorecards_data = []
                progress_bar = st.progress(0)
                for idx, match_opt in enumerate(match_options):
                    match_id = match_opt.get("match_id")
                    if match_id:
                        url, result = fetch_scorecard(match_id, headers)
                        if url:
                            scorecards_data.append((match_id, result))
                    progress_bar.progress((idx + 1) / len(match_options))
                
                scorecard_count = bulk_sync_scorecards(scorecards_data)
                
                st.success(f"✓ Synced {match_count} matches and {scorecard_count} innings!")
                st.session_state.bulk_sync_triggered = False
                st.rerun()
            except Exception as e:
                st.error(f"Sync failed: {e}")
                st.session_state.bulk_sync_triggered = False

    # Select match
    selected = st.selectbox(
        "🎯 Select a match",
        options=match_options,
        format_func=lambda x: x["label"]
    )

    info = selected["matchInfo"]
    
    # Auto-sync: Save match to database
    try:
        save_match(info)
    except Exception as e:
        pass  # Silent fail to not disrupt UI

    # Show match details with team names as subheader
    team1 = info.get("team1", {}).get("teamName", "Team 1")
    team2 = info.get("team2", {}).get("teamName", "Team 2")
    st.subheader(f"🏏 {team1} vs {team2}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("🏆 Series:", info.get("seriesName"))
        st.write("🎯 Match:", info.get("matchDesc"))
        st.write("📋 Format:", info.get("matchFormat"))
    
    with col2:
        venue = info.get("venueInfo", {})
        st.write("🏟️ Venue:", venue.get("ground"))
        st.write("🌆 City:", venue.get("city"))
        st.write("🔴 Status:", info.get("status"))
        st.write("📍 State:", info.get("state"))

    # Fetch scorecard data to show current score
    match_id = selected["match_id"]
    url, result = fetch_scorecard(match_id, headers)
    
    if url is not None:
        score_data = result
        
        # Auto-sync: Save scorecard to database
        try:
            save_scorecard(match_id, score_data)
        except Exception as e:
            pass  # Silent fail to not disrupt UI
        innings_list = score_data.get("scorecard", [])
        
        if innings_list:
            # Display Current Score Summary
            st.subheader("📊 Current Score ")
            score_data_dict = {}
            
            for inn in innings_list:
                team = inn.get("batteamname", "Team")
                score = inn.get("score")
                wkts = inn.get("wickets")
                overs = inn.get("overs")
                rr = inn.get("runrate")
                
                score_data_dict[team] = {
                    "Runs": score,
                    "Wickets": wkts,
                    "Overs": overs,
                    "Run Rate": rr
                }
            
            if score_data_dict:
                import pandas as pd
                df = pd.DataFrame(score_data_dict)
                st.dataframe(df, use_container_width=True)

    # Fetch and display scorecard
    st.subheader("📌 Detailed Scorecard")

    if st.button("📥 Load Full Scorecard"):
        st.session_state.scorecard_loaded = True

    # Only fetch scorecard if button is clicked
    if st.session_state.get("scorecard_loaded", False):
        match_id = selected["match_id"]
        url, result = fetch_scorecard(match_id, headers)
        
        if url is None:
            st.error("Could not fetch scorecard from any endpoint.")
            st.write("Last error:", result)
            st.stop()
        
        score_data = result
        show_debug = False

        innings_list = score_data.get("scorecard", [])
        if not innings_list:
            st.warning("No innings found in scorecard response.")
            if show_debug:
                st.json(score_data)
            st.stop()

        st.divider()

        # Loop through all innings
        for innings_idx, inn in enumerate(innings_list, 1):
            team = inn.get("batteamname", "Team")
            score = inn.get("score")
            wkts = inn.get("wickets")
            overs = inn.get("overs")
            rr = inn.get("runrate")

            st.markdown(f"### 🏏 {innings_idx}st Innings - {team}")
            st.write(f"**{team}** — {score}/{wkts} ({overs} ov)  |  Run Rate: {rr}")

            # Extras
            extras = inn.get("extras", {})
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("📊 **Extras & Total:**")
                
                st.write("Byes:", extras.get("byes", 0))
                st.write("Leg Byes:", extras.get("legbyes", 0))
                st.write("Wides:", extras.get("wides", 0))
                st.write("No Balls:", extras.get("noballs", 0))
                st.write("Penalty:", extras.get("penalty", 0))

            with col2:
                st.metric("Total Extras", extras.get("total", 0))
                st.metric("Total Score", score)
            

            # Batsmen table
            st.markdown("##### 🧍 Batsmen")
            batsmen = inn.get("batsman", [])
            if batsmen:
                bat_rows = []
                for b in batsmen:
                    bat_rows.append({
                        "Name": b.get("name"),
                        "Runs": b.get("runs"),
                        "Balls": b.get("balls"),
                        "4s": b.get("fours"),
                        "6s": b.get("sixes"),
                        "SR": b.get("strkrate"),
                        "Status": b.get("outdec")
                    })
                st.dataframe(bat_rows, use_container_width=True)
            else:
                st.info("No batsmen data found.")

            # Bowlers table
            st.markdown("##### 🎯 Bowlers")
            bowlers = inn.get("bowler", [])
            if bowlers:
                bowl_rows = []
                for bw in bowlers:
                    bowl_rows.append({
                        "Name": bw.get("name"),
                        "Overs": bw.get("overs"),
                        "Maidens": bw.get("maidens"),
                        "Runs": bw.get("runs"),
                        "Wickets": bw.get("wickets"),
                        "Economy": bw.get("economy")
                    })
                st.dataframe(bowl_rows, use_container_width=True)
            else:
                st.info("No bowlers data found.")
            
            st.divider()
