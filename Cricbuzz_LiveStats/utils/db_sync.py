"""
Database sync utilities for saving live API data to SQLite
"""
import sqlite3
from datetime import datetime

DB_PATH = "db/cricbuzz.db"


def save_match(match_info: dict):
    """
    Save or update match data to the database
    
    Args:
        match_info: Match information dictionary from API
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    try:
        match_id = match_info.get("matchId")
        if not match_id:
            return
        
        cur.execute("""
        INSERT OR REPLACE INTO matches 
        (match_id, series_name, match_desc, match_format, team1, team2, 
         venue_ground, venue_city, status, start_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            match_id,
            match_info.get("seriesName"),
            match_info.get("matchDesc"),
            match_info.get("matchFormat"),
            match_info.get("team1", {}).get("teamName"),
            match_info.get("team2", {}).get("teamName"),
            match_info.get("venueInfo", {}).get("ground"),
            match_info.get("venueInfo", {}).get("city"),
            match_info.get("status"),
            match_info.get("startDate")
        ))
        
        conn.commit()
    finally:
        conn.close()


def save_scorecard(match_id: int, scorecard_data: dict):
    """
    Save scorecard innings data to the database
    
    Args:
        match_id: Match ID
        scorecard_data: Scorecard data from API
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    try:
        innings_list = scorecard_data.get("scorecard", [])
        
        # Delete existing scorecard data for this match
        cur.execute("DELETE FROM scorecards WHERE match_id = ?", (match_id,))
        
        # Insert new scorecard data
        for innings_idx, inn in enumerate(innings_list, 1):
            cur.execute("""
            INSERT INTO scorecards 
            (match_id, innings_id, bat_team, runs, wickets, overs, runrate)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                match_id,
                innings_idx,
                inn.get("batteamname"),
                inn.get("score"),
                inn.get("wickets"),
                inn.get("overs"),
                inn.get("runrate")
            ))
        
        conn.commit()
    finally:
        conn.close()


def save_player(player_info: dict):
    """
    Save or update player data to the database
    
    Args:
        player_info: Player information dictionary from API
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    try:
        player_id = player_info.get("id") or player_info.get("playerId")
        if not player_id:
            return
        
        cur.execute("""
        INSERT OR REPLACE INTO players 
        (player_id, name, country, role, batting_style, bowling_style)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            player_id,
            player_info.get("name"),
            player_info.get("intlTeam") or player_info.get("country"),
            player_info.get("role") or player_info.get("playingRole"),
            player_info.get("bat") or player_info.get("batting_style"),
            player_info.get("bowl") or player_info.get("bowling_style")
        ))
        
        conn.commit()
    finally:
        conn.close()


def get_sync_stats():
    """
    Get database sync statistics
    
    Returns:
        dict: Count of records in each table
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    try:
        stats = {}
        
        cur.execute("SELECT COUNT(*) FROM players")
        stats['players'] = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM matches")
        stats['matches'] = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM scorecards")
        stats['scorecards'] = cur.fetchone()[0]
        
        return stats
    finally:
        conn.close()


def clear_all_players():
    """
    Clear all players from the database
    
    Returns:
        int: Number of players deleted
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT COUNT(*) FROM players")
        count = cur.fetchone()[0]
        
        cur.execute("DELETE FROM players")
        conn.commit()
        
        return count
    finally:
        conn.close()


def bulk_import_top_players(team_id: int = 2, headers: dict = None):
    """
    Bulk import players from a team using the Cricbuzz API
    
    Args:
        team_id: Team ID (default: 2 for India)
        headers: API request headers
    
    Returns:
        int: Number of players imported
    """
    from utils.api_client import fetch_team_players
    
    if not headers:
        from config.api_keys import RAPID_API_KEY, RAPID_API_HOST
        headers = {
            "x-rapidapi-key": RAPID_API_KEY,
            "x-rapidapi-host": RAPID_API_HOST
        }
    
    # Fetch players from API
    status, data = fetch_team_players(team_id, headers)
    
    if status != 200:
        raise Exception(f"Failed to fetch players from API: {status} - {data}")
    
    # Parse the response to extract players
    players = []
    if isinstance(data, dict):
        # Try different possible response structures
        player_list = data.get("player") or data.get("players") or data.get("data") or []
    elif isinstance(data, list):
        player_list = data
    else:
        player_list = []
    
    if not player_list:
        raise Exception("No players found in API response")
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    try:
        count = 0
        for p in player_list:
            # Extract player information from API response
            player_id = p.get("id") or p.get("playerId")
            name = p.get("name") or p.get("fullName")
            
            if not player_id or not name:
                continue
            
            country = p.get("country") or p.get("intlTeam") or "India"
            role = p.get("role") or p.get("playingRole") or "Player"
            batting_style = p.get("bat") or p.get("batting_style") or p.get("battingStyle")
            bowling_style = p.get("bowl") or p.get("bowling_style") or p.get("bowlingStyle")
            
            cur.execute("""
            INSERT OR REPLACE INTO players 
            (player_id, name, country, role, batting_style, bowling_style)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (player_id, name, country, role, batting_style, bowling_style))
            count += 1
        
        conn.commit()
        return count
    finally:
        conn.close()


def bulk_sync_matches(match_options: list):
    """
    Bulk save all matches from live scores API
    
    Args:
        match_options: List of match options from build_match_options()
    
    Returns:
        int: Number of matches saved
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    try:
        count = 0
        for match_opt in match_options:
            info = match_opt.get("matchInfo", {})
            match_id = info.get("matchId")
            if not match_id:
                continue
            
            cur.execute("""
            INSERT OR REPLACE INTO matches 
            (match_id, series_name, match_desc, match_format, team1, team2, 
             venue_ground, venue_city, status, start_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                match_id,
                info.get("seriesName"),
                info.get("matchDesc"),
                info.get("matchFormat"),
                info.get("team1", {}).get("teamName"),
                info.get("team2", {}).get("teamName"),
                info.get("venueInfo", {}).get("ground"),
                info.get("venueInfo", {}).get("city"),
                info.get("status"),
                info.get("startDate")
            ))
            count += 1
        
        conn.commit()
        return count
    finally:
        conn.close()


def bulk_sync_scorecards(scorecards_data: list):
    """
    Bulk save scorecards for multiple matches
    
    Args:
        scorecards_data: List of tuples (match_id, scorecard_dict)
    
    Returns:
        int: Number of innings saved
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    try:
        count = 0
        for match_id, scorecard_data in scorecards_data:
            if not scorecard_data:
                continue
                
            innings_list = scorecard_data.get("scorecard", [])
            
            # Delete existing scorecard data for this match
            cur.execute("DELETE FROM scorecards WHERE match_id = ?", (match_id,))
            
            # Insert new scorecard data
            for innings_idx, inn in enumerate(innings_list, 1):
                cur.execute("""
                INSERT INTO scorecards 
                (match_id, innings_id, bat_team, runs, wickets, overs, runrate)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    match_id,
                    innings_idx,
                    inn.get("batteamname"),
                    inn.get("score"),
                    inn.get("wickets"),
                    inn.get("overs"),
                    inn.get("runrate")
                ))
                count += 1
        
        conn.commit()
        return count
    finally:
        conn.close()
