import pandas as pd

def add_advanced_columns(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()

    # Guard against missing columns
    for c in ["PTS","REB","AST","STL","BLK","TO","FGA","FTA","FGM","3PA","3PM","FTM","MIN"]:
        if c not in d.columns:
            d[c] = 0

    # Simple aggregates
    d["PRA"] = d["PTS"] + d["REB"] + d["AST"]
    d["PR"]  = d["PTS"] + d["REB"]
    d["PA"]  = d["PTS"] + d["AST"]
    d["RA"]  = d["REB"] + d["AST"]
    d["STOCKS"] = d["STL"] + d["BLK"]

    # Shooting percentages (avoid divide-by-zero)
    d["FG%"] = (d["FGM"] / d["FGA"]).where(d["FGA"] > 0, 0.0)
    d["3P%"] = (d["3PM"] / d["3PA"]).where(d["3PA"] > 0, 0.0)
    d["FT%"] = (d["FTM"] / d["FTA"]).where(d["FTA"] > 0, 0.0)

    # “Usage proxy” (very common approximation)
    # Possessions used by a player (rough): FGA + 0.44*FTA + TO
    d["USG_PROXY"] = d["FGA"] + 0.44 * d["FTA"] + d["TO"]

    # Points per shot attempt (efficiency proxy)
    d["PTS_PER_FGA"] = (d["PTS"] / d["FGA"]).where(d["FGA"] > 0, 0.0)
    d["PTS_PER_USG"] = (d["PTS"] / d["USG_PROXY"]).where(d["USG_PROXY"] > 0, 0.0)

    return d
