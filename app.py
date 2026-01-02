import hmac
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from data.fetch_live import get_live_games, get_boxscore
from data.normalize import normalize_player_stats
from logic.advanced import add_advanced_columns


# -----------------------
# Beta Password Gate (Option A)
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


def advanced_unlocked() -> bool:
    """
    Feature flag for Advanced tab.
    Later: replace this with Stripe subscription check.
    """
    return str(st.secrets.get("ADVANCED_UNLOCKED", "false")).lower() == "true"


if not check_password():
    st.stop()


# -----------------------
# App Shell
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
    st.subheader("⭐ Watchlist")


st.title("📊 Live Stat Line Tracker (NBA)")
st.caption("Box Score is free. Advanced tab is a separate (lockable) feature.")


# -----------------------
# Pull games + build one big DF
# -----------------------
games = get_live_games()
if not games:
    st.warning("No live games found right now (or NBA feed temporarily unavailable).")
    st.stop()


    all_rows = []
skipped = 0

for g in games:
    gid = g["gameId"]
    date = g["date"]

   summary = get_boxscore(gid)
if not summary:
    skipped += 1
    continue

rows = normalize_player_stats(summary)
matchup = f'{g.get("awayTricode","")} @ {g.get("homeTricode","")}'
for r in rows:
    r["matchup"] = matchup
    r["gameId"] = gid
    all_rows.append(r)


if skipped:
    st.sidebar.info(f"Skipped {skipped} game(s) (boxscore not available yet).")

df = pd.DataFrame(all_rows)
if df.empty:
    st.warning("No player stats available yet.")
    st.stop()

# Clean + sort
df = df.sort_values(["PTS", "FGA", "3PA", "TO"], ascending=[False, False, False, False]).reset_index(drop=True)


# -----------------------
# Watchlist (persisted)
# -----------------------
if "watchlist" not in st.session_state:
    st.session_state["watchlist"] = []

player_options = df["name"].dropna().unique().tolist()

# Box-score stats user can watch (safe for free tab)
watch_stats = ["PTS","FGA","3PA","TO","AST","REB","STL","BLK","MIN","FTA","PF"]

with st.sidebar:
    sel_player = st.selectbox("Player", options=player_options)
    sel_stat = st.selectbox("Stat", options=watch_stats)
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
# Tabs
# -----------------------
tab_box, tab_adv = st.tabs(["📋 Box Score", "🧠 Advanced (beta)"])

with tab_box:
    left, right = st.columns([1, 2], gap="large")

    with left:
        st.subheader("⭐ Watchlist")
        if not st.session_state["watchlist"]:
            st.info("Add players + stats from the sidebar.")
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
                if target is not None:
                    status = "✅ Hit" if current >= target else f"⏳ {current}/{target}"

                watch_rows.append({
                    "Player": p,
                    "Team": row.get("team", ""),
                    "Matchup": row.get("matchup", ""),
                    "Stat": stat,
                    "Current": current,
                    "Target": target if target is not None else "",
                    "Status": status,
                })

            wdf = pd.DataFrame(watch_rows)
            st.dataframe(wdf, use_container_width=True, hide_index=True)

    with right:
        st.subheader("📋 All Live Players (Box Score)")
        cols_box = [
            "name","team","matchup","MIN","PTS",
            "FGM","FGA","3PM","3PA","FTM","FTA",
            "REB","AST","STL","BLK","TO","PF"
        ]
        st.dataframe(df[cols_box], use_container_width=True, hide_index=True)

with tab_adv:
    st.subheader("🧠 Advanced Stats")

    if not advanced_unlocked():
        st.info("Advanced stats are locked right now. (Later: paywall/subscription).")
        st.stop()

    adv = add_advanced_columns(df)

    cols_adv = [
        "name","team","matchup","MIN",
        "PRA","PR","PA","RA","STOCKS",
        "USG_PROXY","PTS_PER_USG",
        "FG%","3P%","FT%",
        "PTS","REB","AST","STL","BLK","TO","FGA","3PA","FTA"
    ]
    st.dataframe(adv[cols_adv], use_container_width=True, hide_index=True)
