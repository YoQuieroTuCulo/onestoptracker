import requests

NBA_SCOREBOARD_URL = "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"

def get_live_games():
    r = requests.get(NBA_SCOREBOARD_URL, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    return r.json()["scoreboard"]["games"]

def get_boxscore(game_id):
    url = f"https://cdn.nba.com/static/json/liveData/boxscore/boxscore_{game_id}.json"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    game = r.json()["game"]
    return game["homeTeam"], game["awayTeam"]
