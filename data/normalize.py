def normalize_player_stats(players):
    rows = []
    for p in players:
        stats = p.get("statistics", {}) or {}

        fgm = stats.get("fieldGoalsMade", 0)
        fga = stats.get("fieldGoalsAttempted", 0)
        tpm = stats.get("threePointersMade", 0)
        tpa = stats.get("threePointersAttempted", 0)
        ftm = stats.get("freeThrowsMade", 0)
        fta = stats.get("freeThrowsAttempted", 0)

        rows.append({
            "name": p.get("name", ""),
            "team": p.get("teamTricode", ""),

            # Core scoring
            "PTS": stats.get("points", 0),

            # Shooting
            "FGM": fgm,
            "FGA": fga,
            "3PM": tpm,
            "3PA": tpa,
            "FTM": ftm,
            "FTA": fta,

            # Rebounds
            "OREB": stats.get("reboundsOffensive", 0),
            "DREB": stats.get("reboundsDefensive", 0),
            "REB": stats.get("reboundsTotal", 0),

            # Playmaking / defense
            "AST": stats.get("assists", 0),
            "STL": stats.get("steals", 0),
            "BLK": stats.get("blocks", 0),

            # Mistakes / fouls
            "TO": stats.get("turnovers", 0),
            "PF": stats.get("foulsPersonal", 0),

            # Minutes
            "MIN": stats.get("minutes", 0),
        })
    return rows
