"""
SQL Analytics page for Cricbuzz LiveStats
25 Cricket Analytics Queries
"""
import streamlit as st
import time
from utils.db_connection import run_query


def render():
    """Render SQL analytics page with 25 cricket queries"""
    
    st.title("📈 SQL Analytics")
    # st.markdown("*25 Cricket Analytics Queries*")
    
    # Show database stats with clear button
    from utils.db_sync import get_sync_stats, clear_all_players
    try:
        stats = get_sync_stats()
        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption(f"💾 Database: {stats['players']} players | {stats['matches']} matches | {stats['scorecards']} scorecards")
        with col2:
            if st.button("🗑️ Clear All Players", help="Delete all players from database"):
                count = clear_all_players()
                st.success(f"✓ Cleared {count} players")
                st.rerun()
    except:
        pass
    
    st.divider()
    
    # All queries in a single dictionary for dropdown
    all_queries = {
        "Q1 - Players by Country": "SELECT player_id, name, role, batting_style, bowling_style FROM players WHERE country = 'India' ORDER BY name;",
        "Q2 - Recent Matches": "SELECT match_id, match_desc, team1, team2, venue_ground, venue_city, start_date FROM matches ORDER BY start_date DESC LIMIT 20;",
        "Q3 - Top 10 Run Scorers": "SELECT bat_team, SUM(runs) AS total_runs, ROUND(AVG(runs), 2) AS avg_runs FROM scorecards GROUP BY bat_team ORDER BY total_runs DESC LIMIT 10;",
        "Q4 - Matches by City": "SELECT venue_city, COUNT(*) AS match_count FROM matches WHERE venue_city IS NOT NULL GROUP BY venue_city ORDER BY match_count DESC;",
        "Q5 - Team Match Count": "SELECT team1, COUNT(*) AS matches_played FROM matches GROUP BY team1 ORDER BY matches_played DESC;",
        "Q6 - Players by Role Count": "SELECT role, COUNT(*) AS player_count FROM players WHERE role IS NOT NULL GROUP BY role ORDER BY player_count DESC;",
        "Q7 - Matches by Format": "SELECT match_format, COUNT(*) AS total_matches FROM matches WHERE match_format IS NOT NULL GROUP BY match_format ORDER BY total_matches DESC;",
        "Q8 - Series by Name": "SELECT DISTINCT series_name, COUNT(*) AS series_count FROM matches GROUP BY series_name ORDER BY series_count DESC;",
        "Q9 - All Matches Played": "SELECT match_id, series_name, team1, team2, match_format, venue_city FROM matches ORDER BY match_id DESC LIMIT 50;",
        "Q10 - Scorecard Details": "SELECT match_id, innings_id, bat_team, runs, wickets, overs, runrate FROM scorecards ORDER BY match_id DESC, innings_id LIMIT 50;",
        "Q11 - High Scoring Innings (50+)": "SELECT match_id, bat_team, runs, wickets, overs FROM scorecards WHERE runs >= 50 ORDER BY runs DESC LIMIT 30;",
        "Q12 - Matches by Team": "SELECT team1, COUNT(*) AS matches_as_team1, (SELECT COUNT(*) FROM matches m2 WHERE m2.team2 = matches.team1) AS matches_as_team2 FROM matches GROUP BY team1 ORDER BY matches_as_team1 DESC;",
        "Q13 - Average Runs by Team": "SELECT bat_team, ROUND(AVG(runs), 2) AS avg_runs, COUNT(*) AS innings_count FROM scorecards GROUP BY bat_team ORDER BY avg_runs DESC;",
        "Q14 - Wickets Lost Analysis": "SELECT bat_team, ROUND(AVG(wickets), 2) AS avg_wickets_lost, COUNT(*) AS innings_count FROM scorecards GROUP BY bat_team ORDER BY avg_wickets_lost DESC;",
        "Q15 - Economy Rate Analysis": "SELECT bat_team, ROUND(AVG(runrate), 2) AS avg_run_rate FROM scorecards GROUP BY bat_team ORDER BY avg_run_rate DESC;",
        "Q16 - Match Format Distribution": "SELECT match_format, COUNT(*) AS total_matches FROM matches WHERE match_format IS NOT NULL GROUP BY match_format;",
        "Q17 - Players by Country": "SELECT country, COUNT(*) AS player_count FROM players WHERE country IS NOT NULL GROUP BY country ORDER BY player_count DESC;",
        "Q18 - Player Roles Distribution": "SELECT role, COUNT(*) AS total_players FROM players GROUP BY role ORDER BY total_players DESC;",
        "Q19 - Batting Styles": "SELECT batting_style, COUNT(*) AS count FROM players WHERE batting_style IS NOT NULL GROUP BY batting_style ORDER BY count DESC;",
        "Q20 - Bowling Styles": "SELECT bowling_style, COUNT(*) AS count FROM players WHERE bowling_style IS NOT NULL GROUP BY bowling_style ORDER BY count DESC;",
        "Q21 - Highest Individual Score": "SELECT match_id, bat_team, MAX(runs) AS highest_score FROM scorecards GROUP BY match_id ORDER BY highest_score DESC LIMIT 20;",
        "Q22 - Best Run Rates": "SELECT bat_team, match_id, runrate FROM scorecards ORDER BY runrate DESC LIMIT 20;",
        "Q23 - Close Matches (Low Wickets)": "SELECT match_id, team1, team2, COUNT(*) AS innings_with_low_wickets FROM (SELECT m.match_id, m.team1, m.team2 FROM matches m JOIN scorecards s ON m.match_id = s.match_id WHERE s.wickets < 3) GROUP BY match_id, team1, team2 LIMIT 30;",
        "Q24 - Teams Performance": "SELECT team1, COUNT(*) AS team1_matches FROM matches GROUP BY team1 UNION SELECT team2, COUNT(*) AS team2_matches FROM matches GROUP BY team2 ORDER BY 2 DESC;",
        "Q25 - Complete Match Overview": "SELECT m.match_id, m.series_name, m.team1, m.team2, m.match_format, m.venue_city, COUNT(s.innings_id) AS total_innings, SUM(s.runs) AS total_runs FROM matches m LEFT JOIN scorecards s ON m.match_id = s.match_id GROUP BY m.match_id ORDER BY m.match_id DESC LIMIT 30;"
    }
    
    # Dropdown to select query
    pick = st.selectbox("Choose a query", list(all_queries.keys()))
    
    # View Query toggle
    view_query = st.checkbox("🔍 View Query")
    
    if view_query:
        sql = st.text_area("SQL", value=all_queries[pick], height=160)
    else:
        sql = all_queries[pick]
    
    # Execute query button with red color
    if st.button("▶️ Execute Query", type="primary", use_container_width=False):
        try:
            start_time = time.time()
            df = run_query(sql)
            execution_time = time.time() - start_time
            
            st.success(f"✓ Query executed in {execution_time:.2f}s | {len(df)} rows")
            st.dataframe(df, use_container_width=True)
            
            # Download option
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="query_results.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(str(e))
