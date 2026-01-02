def normalize_player_stats(players):
    """
    data.nba.net activePlayers format.
    """
    rows = []
    for p in players:
        # data.nba.net uses different keys than cdn.nba.com
        name = f"{p.get('firstName','').strip()} {p.get('lastName','').strip()}".strip()
        team = p.get("teamTriCode") or p.get("teamTricode") or ""

        stats = p.get("statistics", {}) or p.get("stats", {}) or {}

        # data.nba.net typically uses these keys:
        fgm = int(stats.get("fgm", 0) or 0)
        fga = int(stats.get("fga", 0) or 0)
        tpm = int(stats.get("tpm", 0) or 0)
        tpa = int(stats.get("tpa", 0) or 0)
        ftm = int(stats.get("ftm", 0) or 0)
        fta = int(stats.get("fta", 0) or 0)

        rows.append({
            "name": name,
            "team": team,

            "MIN": stats.get("min", "0"),
            "PTS": int(stats.get("points", 0) or 0),

            "FGM": fgm, "FGA": fga,
            "3PM": tpm, "3PA": tpa,
            "FTM": ftm, "FTA": fta,

            "OREB": int(stats.get("offReb", 0) or 0),
            "DREB": int(stats.get("defReb", 0) or 0),
            "REB": int(stats.get("totReb", 0) or 0),

            "AST": int(stats.get("assists", 0) or 0),
            "STL": int(stats.get("steals", 0) or 0),
            "BLK": int(stats.get("blocks", 0) or 0),

            "TO": int(stats.get("turnovers", 0) or 0),
            "PF": int(stats.get("pFouls", 0) or 0),
        })

    return rows
