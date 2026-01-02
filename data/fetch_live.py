import requests
from datetime import datetime
from zoneinfo import ZoneInfo

_HEADERS = {"User-Agent": "Mozilla/5.0"}
NBA_SCOREBOARD = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
NBA_SUMMARY = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary"

def get_live_games():
    """
    Returns games for today's date (America/Los_Angeles) from ESPN scoreboard.
    Each item contains: gameId (ESPN event id), homeTricode, awayTricode, status.
    """
    today = datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y%m%d")

    r = requests.get(NBA_SCOREBOARD, headers=_HEADERS, params={"dates": today}, timeout=20)
    r.raise_for_status()
    j = r.json()

    out = []
    for ev in j.get("events", []) or []:
        comp = (ev.get("competitions") or [{}])[0]
        competitors = comp.get("competitors") or []
        home = next((c for c in competitors if c.get("homeAway") == "home"), None)
        away = next((c for c in competitors if c.get("homeAway") == "away"), None)

        out.append({
            "gameId": ev.get("id"),
            "homeTricode": (home or {}).get("team", {}).get("abbreviation", ""),
            "awayTricode": (away or {}).get("team", {}).get("abbreviation", ""),
            "status": (comp.get("status") or {}).get("type", {}).get("description", ""),
        })

    return out

def get_boxscore(game_id: str):
    """
    Returns ESPN summary JSON for a given event id.
    If unavailable, returns None.
    """
    r = requests.get(NBA_SUMMARY, headers=_HEADERS, params={"event": game_id}, timeout=20)
    if r.status_code in (404, 204):
        return None
    r.raise_for_status()
    return r.json()
