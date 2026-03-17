"""
API client utilities for Cricbuzz LiveStats
"""
import requests


def fetch_live_scores(headers: dict):
    """
    Fetch live scores from Cricbuzz API
    
    Args:
        headers: API request headers
        
    Returns:
        dict: Response data or None
    """
    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    return None


def fetch_scorecard(match_id: int, headers: dict):
    """
    Fetch detailed scorecard for a match.
    Tries common Cricbuzz scorecard endpoints since different RapidAPI providers
    expose different paths.
    
    Args:
        match_id: Match ID from Cricbuzz API
        headers: API request headers
        
    Returns:
        tuple: (url, response_data) or (None, error_dict) if all endpoints fail
    """
    candidates = [
        f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{match_id}/hscard",
        f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{match_id}/scard",
    ]

    last_error = None
    for url in candidates:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return url, r.json()
        last_error = {"url": url, "status_code": r.status_code, "text": r.text[:400]}

    return None, last_error


def build_match_options(data: dict):
    """
    Parse live scores data and build formatted match options for selectbox
    
    Args:
        data: Raw API response data
        
    Returns:
        list: Match options with label, match_id, and matchInfo
    """
    match_options = []
    type_matches = data.get("typeMatches", [])

    for t in type_matches:
        for s in t.get("seriesMatches", []):
            wrapper = s.get("seriesAdWrapper")
            if not wrapper:
                continue

            for m in wrapper.get("matches", []):
                info = m.get("matchInfo", {})
                match_id = info.get("matchId")
                if not match_id:
                    continue

                team1 = info.get("team1", {}).get("teamName", "Team 1")
                team2 = info.get("team2", {}).get("teamName", "Team 2")
                label = f"{team1} vs {team2} — {info.get('matchDesc','')} ({info.get('state','')})"

                match_options.append({
                    "label": label,
                    "match_id": match_id,
                    "matchInfo": info
                })

    return match_options


def api_get(path: str, headers: dict, params: dict | None = None):
    """
    Generic API GET request handler for Cricbuzz endpoints
    
    Args:
        path: API endpoint path
        headers: API request headers
        params: Query parameters
        
    Returns:
        tuple: (status_code, response_data or error_text)
    """
    url = f"https://cricbuzz-cricket.p.rapidapi.com{path}"
    r = requests.get(url, headers=headers, params=params, timeout=20)
    return r.status_code, r.json() if r.status_code == 200 else r.text


def search_players(query: str, headers: dict):
    """
    Search for players by name
    
    Args:
        query: Player name search query
        headers: API request headers
        
    Returns:
        tuple: (status_code, search_results)
    """
    # Endpoint: /stats/v1/player/search with parameter plrN
    status, data = api_get("/stats/v1/player/search", headers=headers, params={"plrN": query})
    return status, data


def get_player_info(player_id: int, headers: dict):
    """
    Get player information
    
    Args:
        player_id: Player ID
        headers: API request headers
        
    Returns:
        tuple: (status_code, player_info)
    """
    # Endpoint: /stats/v1/player/{playerId}
    status, data = api_get(f"/stats/v1/player/{player_id}", headers=headers)
    return status, data


def get_player_batting(player_id: int, headers: dict):
    """
    Get player batting statistics
    
    Args:
        player_id: Player ID
        headers: API request headers
        
    Returns:
        tuple: (status_code, batting_stats)
    """
    # Endpoint: /stats/v1/player/{playerId}/batting
    status, data = api_get(f"/stats/v1/player/{player_id}/batting", headers=headers)
    return status, data


def get_player_bowling(player_id: int, headers: dict):
    """
    Get player bowling statistics
    
    Args:
        player_id: Player ID
        headers: API request headers
        
    Returns:
        tuple: (status_code, bowling_stats)
    """
    # Endpoint: /stats/v1/player/{playerId}/bowling
    status, data = api_get(f"/stats/v1/player/{player_id}/bowling", headers=headers)
    return status, data


def fetch_team_players(team_id: int, headers: dict):
    """
    Fetch all players from a specific team
    
    Args:
        team_id: Team ID (e.g., 2 for India)
        headers: API request headers
        
    Returns:
        tuple: (status_code, players_data)
    """
    # Endpoint: /teams/v1/{teamId}/players
    url = f"https://cricbuzz-cricket.p.rapidapi.com/teams/v1/{team_id}/players"
    r = requests.get(url, headers=headers, timeout=20)
    return r.status_code, r.json() if r.status_code == 200 else r.text
