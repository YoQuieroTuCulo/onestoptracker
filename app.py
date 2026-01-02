import hmac
import time
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from data.fetch_live import get_live_games, get_boxscore
from data.normalize import normalize_player_stats


# -----------------------
# Beta Password Gate
# -----------------------
def check_password() -> bool:
    if st.session_state.get("password_ok", False):
        return True

    st.title("🔒 Beta Access")
    st.write("Enter the beta password to continue.")
    pw = st.text_input("Password", type="password")

    if st.button("Enter"):
        secret = st.secrets.get("BETA_PASSWORD", "")
        if secret and hmac.compare_digest(pw, secret):
            st.session_state["password_ok"] = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    return False


if not check_password():
    st.stop()


# -----------------------
# App Settings
# -----------------------
st.set_page_config(page_title="Live Stat Line Tracker", layout="wide")

with st.sidebar:
    st.header("Controls")
    refresh_sec = st.slider("Auto-refresh (seconds)", 5, 60, 15, 5)
    st_autorefresh(interval=refresh_sec * 1000, key="refresh")

    if st.button("Log out"):
        st.session_state["password_ok"] = False
        st.rerun()

    st.divider()
    st.subheader("Watchlist")

st.title("📊 Live Stat Line Tracker (NBA)")
st.caption("Tracking: FGA, 3PTA, TO, PTS")


# -----------------------
# Pull all games + build a single table
# -----------------------
games = get_live_games()
if not games:
    st.warning("No live games found right now (or NBA feed temporarily unavailable).")
    st.stop()

all_rows = []
for g in games:
    gid = g["gameId"]
    home, away = get_boxscore(gid)
    players = home["players"] + away["players"]
    rows = normalize_player_stats(players)

    matchup = f'{away["teamTricode"]} @ {home["teamTricode"]}'
    for r in rows:
        r["matchup"] = matchup
        r["gameId"] = gid
        all_rows.append(r)

df = pd.DataFrame(all_rows)

# Clean sort
df = df.sort_values(["FGA", "3PTA", "TO"], ascending=[False, False, False]).reset_index(drop=True)


# -----------------------
# Watchlist UI
# -----------------------
# Persist watchlist across refreshes
if "watchlist" not in st.session_state:
    st.session_state["watchlist"] = []

player_options = df["name"].dropna().unique().tolist()
stat_options = ["PTS","MIN",
    "FGM","FGA","3PM","3PA","FTM","FTA",
    "REB","OREB","DREB",
    "AST","STL","BLK",
    "TO","PF"]


with st.sidebar:
    sel_player = st.selectbox("Player", options=player_options)
    sel_stat = st.selectbox("Stat", options=stat_options)
    sel_target = st.number_input("Target (optional)", min_value=0.0, value=0.0, step=0.5)

    if st.button("Add to watchlist"):
        st.session_state["watchlist"].append({
            "player": sel_player,
            "stat": sel_stat,
            "target": sel_target if sel_target > 0 else None
        })

    if st.button("Clear watchlist"):
        st.session_state["watchlist"] = []


# -----------------------
# Layout: Watchlist + Full Table
# -----------------------
left, right = st.columns([1, 2], gap="large")

with left:
    st.subheader("⭐ Watchlist")
    if not st.session_state["watchlist"]:
        st.info("Add players + stats on the left sidebar.")
    else:
        watch_rows = []
        for item in st.session_state["watchlist"]:
            p = item["player"]
            stat = item["stat"]
            target = item["target"]

            sub = df[df["name"] == p]
            if sub.empty:
                continue
            row = sub.iloc[0].to_dict()

            current = row.get(stat, 0)
            status = ""
            if target:
                status = "✅ Hit" if current >= target else f"⏳ {current}/{target}"

            watch_rows.append({
                "Player": p,
                "Team": row.get("team", ""),
                "Matchup": row.get("matchup", ""),
                "Stat": stat,
                "Current": current,
                "Target": target if target else "",
                "Status": status
            })

        wdf = pd.DataFrame(watch_rows)
        st.dataframe(wdf, use_container_width=True, hide_index=True)

with right:
    st.subheader("📋 All Live Players")
    cols = ["name","team","matchup","MIN","PTS","FGM","FGA","3PM","3PA","FTM","FTA","REB","AST","STL","BLK","TO","PF"]
st.dataframe(df[cols], use_container_width=True, hide_index=True)
