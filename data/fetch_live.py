import requests

NBA_SCOREBOARD_URL = "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"
_HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_live_games():
    """Returns list of live/today games from NBA scoreboard feed."""
    r = requests.get(NBA_SCOREBOARD_URL, headers=_HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()["scoreboard"]["games"]

def get_boxscore(game_id: str):
    """Returns (homeTeam, awayTeam) dicts from NBA boxscore feed."""
    url = f"https://cdn.nba.com/static/json/liveData/boxscore/boxscore_{game_id}.json"
    r = requests.get(url, headers=_HEADERS, timeout=15)
    r.raise_for_status()
    game = r.json()["game"]
    return game["homeTeam"], game["awayTeam"]
