import streamlit as st
import hmac
import pandas as pd
from data.fetch_live import get_live_games, get_boxscore
from data.normalize import normalize_player_stats

def check_password() -> bool:
    """Simple beta password gate using Streamlit secrets."""
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

st.set_page_config(layout="wide")
st.title("📊 Live Stat Line Tracker (NBA)")

if st.sidebar.button("Log out"):
    st.session_state["password_ok"] = False
    st.rerun()

games = get_live_games()

if not games:
    st.warning("No live games found right now.")
    st.stop()

selected_game = st.selectbox(
    "Select Game",
    options=[(g["gameId"], f'{g['awayTeam']['teamTricode']} @ {g['homeTeam']['teamTricode']}') for g in games],
    format_func=lambda x: x[1]
)

game_id = selected_game[0]
home, away = get_boxscore(game_id)

players = home["players"] + away["players"]
rows = normalize_player_stats(players)
df = pd.DataFrame(rows)

st.dataframe(df.sort_values("FGA", ascending=False), use_container_width=True)
