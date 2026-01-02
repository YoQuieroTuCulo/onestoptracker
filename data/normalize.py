def normalize_player_stats(players):
    rows = []
    for p in players:
        stats = p.get("statistics", {}) or {}
        rows.append({
            "name": p.get("name", ""),
            "team": p.get("teamTricode", ""),
            "FGA": stats.get("fieldGoalsAttempted", 0),
            "3PTA": stats.get("threePointersAttempted", 0),
            "TO": stats.get("turnovers", 0),
            "PTS": stats.get("points", 0),
        })
    return rows
