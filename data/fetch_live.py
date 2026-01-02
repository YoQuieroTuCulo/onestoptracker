import requests
from datetime import datetime, timedelta

_HEADERS = {"User-Agent": "Mozilla/5.0"}

def _fmt_date(d: datetime) -> str:
    return d.strftime("%Y%m%d")

def _get_scoreboard(date_yyyymmdd: str):
    # Example: https://data.nba.net/prod/v2/20260101/scoreboard.json
    url = f"https://data.nba.net/prod/v2/{date_yyyymmdd}/scoreboard.json"
    r = requests.get(url, headers=_HEADERS, timeout=20)
    if r.status_code != 200:
        return None
    return r.json()

def get_live_games():
    """
    Returns games for today (and yesterday as fallback for timezone/late games),
    each game includes a 'date' field used for the boxscore URL.
    """
    today = datetime.utcnow()
    dates = [_fmt_date(today), _fmt_date(today - timedelta(days=1))]

    games_out = []
    for d in dates:
        sb = _get_scoreboard(d)
        if not sb:
            continue

        # sb structure: {"games": [...]}
        games = sb.get("games", [])
        for g in games:
            home = g.get("hTeam", {}) or {}
            away = g.get("vTeam", {}) or {}

            games_out.append({
                "gameId": g.get("gameId"),
                "date": d,
                "homeTricode": home.get("triCode"),
                "awayTricode": away.get("triCode"),
                "statusNum": g.get("statusNum"),  # 1 pre, 2 live, 3 final
            })

    # De-dupe in case a game appears in both date pulls
    seen = set()
    deduped = []
    for g in games_out:
        gid = g.get("gameId")
        if not gid or gid in seen:
            continue
        seen.add(gid)
        deduped.append(g)

    return deduped

def get_boxscore(game_id: str, date_yyyymmdd: str):
    """
    data.nba.net boxscore:
    https://data.nba.net/prod/v1/{date}/{gameId}_boxscore.json
    Returns (homeTeamDict, awayTeamDict) OR (None, None) if unavailable.
    """
    url = f"https://data.nba.net/prod/v1/{date_yyyymmdd}/{game_id}_boxscore.json"
    r = requests.get(url, headers=_HEADERS, timeout=20)

    # Not available yet / date mismatch / pregame feed delay
    if r.status_code in (404, 204):
        return None, None

    # Temporary server issues
    if r.status_code in (500, 502, 503, 504):
        return None, None

    r.raise_for_status()
    j = r.json()

    # structure: {"basicGameData":..., "stats": {"activePlayers":[...]}, "hTeam":..., "vTeam":...}
    home = j.get("hTeam", {}) or {}
    away = j.get("vTeam", {}) or {}
    players = j.get("stats", {}).get("activePlayers", []) or []

    return {"teamTricode": home.get("triCode"), "players": players, "side": "home"}, \
           {"teamTricode": away.get("triCode"), "players": [], "side": "away"}
