def _to_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default

def normalize_player_stats(summary_json):
    """
    Converts ESPN summary response into a list of rows matching your app columns.
    We read competitors -> statistics -> athletes.
    """
    if not summary_json:
        return []

    rows = []
    box = summary_json.get("boxscore", {}) or {}
    players = box.get("players", []) or []

    # ESPN structure: players = [{ "team": {...}, "statistics":[ { "name":.., "labels":[...], "athletes":[...] } ] }]
    for team_block in players:
        team = (team_block.get("team") or {})
        tri = team.get("abbreviation", "")

        for stat_group in (team_block.get("statistics") or []):
            labels = stat_group.get("labels") or []
            athletes = stat_group.get("athletes") or []

            # We want the "starters/bench" group that includes a "stats" list.
            # Each athlete has "stats": list aligned with labels.
            for a in athletes:
                athlete = (a.get("athlete") or {})
                name = athlete.get("displayName", "")

                stats_list = a.get("stats") or []
                m = dict(zip(labels, stats_list))

                # ESPN labels commonly include: MIN, FG, 3PT, FT, OREB, DREB, REB, AST, STL, BLK, TO, PF, PTS
                # FG/3PT/FT are like "7-16" -> split to made/att
                def split_made_att(val):
                    if not val or "-" not in str(val):
                        return 0, 0
                    left, right = str(val).split("-", 1)
                    return _to_int(left), _to_int(right)

                fgm, fga = split_made_att(m.get("FG"))
                tpm, tpa = split_made_att(m.get("3PT"))
                ftm, fta = split_made_att(m.get("FT"))

                rows.append({
                    "name": name,
                    "team": tri,
                    "MIN": m.get("MIN", "0"),
                    "PTS": _to_int(m.get("PTS", 0)),
                    "FGM": fgm, "FGA": fga,
                    "3PM": tpm, "3PA": tpa,
                    "FTM": ftm, "FTA": fta,
                    "OREB": _to_int(m.get("OREB", 0)),
                    "DREB": _to_int(m.get("DREB", 0)),
                    "REB": _to_int(m.get("REB", 0)),
                    "AST": _to_int(m.get("AST", 0)),
                    "STL": _to_int(m.get("STL", 0)),
                    "BLK": _to_int(m.get("BLK", 0)),
                    "TO": _to_int(m.get("TO", 0)),
                    "PF": _to_int(m.get("PF", 0)),
                })

    return rows
