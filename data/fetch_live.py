import requests

NBA_SCOREBOARD_URL = "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"

_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://www.nba.com/",
    "Origin": "https://www.nba.com",
}

def get_live_games():
    r = requests.get(NBA_SCOREBOARD_URL, headers=_HEADERS, timeout=20)
    r.raise_for_status()
    return r.json()["scoreboard"]["games"]

def get_boxscore(game_id: str):
    """
    Returns (homeTeam, awayTeam) dicts.
    If the boxscore is not available yet (404) or temporarily blocked, returns (None, None).
    """
    url = f"https://cdn.nba.com/static/json/liveData/boxscore/boxscore_{game_id}.json"
    r = requests.get(url, headers=_HEADERS, timeout=20)

    # Boxscore not available yet for scheduled games
    if r.status_code == 404:
        return None, None

    # Temporary protection / rate limiting
    if r.status_code in (403, 429, 500, 502, 503, 504):
        return None, None

    # For anything else, raise so we can see it in logs if needed
    r.raise_for_status()

    game = r.json()["game"]
    return game["homeTeam"], game["awayTeam"]
