import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Cavalry Player Heatmap Dashboard", layout="wide")

st.markdown("""
    <style>
        .main { background-color: #f9f9f9; }
        .player-card {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin: 0.5rem;
            padding: 0.5rem;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            width: 120px;
        }
        .player-img {
            border-radius: 50%;
            width: 70px;
            height: 70px;
            object-fit: cover;
        }
        .player-info {
            text-align: center;
            margin-top: 0.3rem;
            font-size: 0.8rem;
        }
        .position-badge {
            display: inline-block;
            padding: 0.25em 0.6em;
            font-size: 0.7em;
            font-weight: bold;
            border-radius: 0.5rem;
            color: white;
        }
        .GK { background-color: #28a745; }
        .DF { background-color: #007bff; }
        .DMF { background-color: #17a2b8; }
        .MF { background-color: #ffc107; color: black; }
        .FW { background-color: #dc3545; }
        .N_A { background-color: #6c757d; }
    </style>
""", unsafe_allow_html=True)

st.title("⚽ Cavalry FC - Player Heatmap Match Dashboard")

@st.cache_data
def load_data():
    df = pd.read_csv("matches.csv")
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
    df = df.sort_values("Date", ascending=False)
    return df.fillna(0)

df = load_data()
df["Round"] = df["Round"].astype(str)

with st.sidebar:
    st.header("🔎 Filters")
    round_filter = st.selectbox("Match Round", ["All"] + sorted(df["Round"].unique().tolist()))
    side_filter = st.selectbox("Team Side", ["All"] + sorted(df["Local/Visit"].astype(str).unique().tolist()))
    opponent_filter = st.selectbox("Opponent", ["All"] + sorted(df["Cavalry/Opponent"].astype(str).unique().tolist()))
    player_filter = st.selectbox("Player", ["All"] + sorted(df["Player"].astype(str).unique().tolist()))
    date_filter = st.selectbox("Match Date", ["All"] + sorted(df["Date"].dt.date.astype(str).unique().tolist()))

df_filtered = df[df["Player"].astype(str) != "0"].copy()
if round_filter != "All":
    df_filtered = df_filtered[df_filtered["Round"] == round_filter]
if side_filter != "All":
    df_filtered = df_filtered[df_filtered["Local/Visit"] == side_filter]
if opponent_filter != "All":
    df_filtered = df_filtered[df_filtered["Cavalry/Opponent"] == opponent_filter]
if player_filter != "All":
    df_filtered = df_filtered[df_filtered["Player"] == player_filter]
if date_filter != "All":
    df_filtered = df_filtered[df_filtered["Date"].dt.date.astype(str) == date_filter]

def get_position_order(pos):
    pos = str(pos).upper()
    if pos == "GK": return 0
    if pos == "DF" or pos == "RB" or pos == "LB": return 1
    if pos == "DMF": return 2
    if pos == "MF" or pos == "AMF" or pos == "CMF": return 3
    if pos == "RW" or pos == "LW": return 4
    if pos == "FW" or pos == "CF" or pos.startswith("F"): return 5
    return 99

def get_position_group(pos):
    pos = str(pos).upper()
    if pos == "GK": return "GK"
    if pos == "DMF": return "DMF"
    if pos.startswith("D"): return "DF"
    if pos.startswith("M"): return "MF"
    if pos.startswith("F") or pos.endswith("W") or pos.endswith("CF"): return "FW"
    return "N_A"

st.subheader("🧍 Players")
df_filtered = df_filtered.sort_values(by="Position", key=lambda x: x.apply(get_position_order))

for match_id, match_group in df_filtered.groupby(["Round", "Date", "Cavalry/Opponent"]):
    round_num, match_date, opponent = match_id
    st.markdown(f"### 📅 Round {round_num} - {match_date.date()} vs {opponent}")

    players_list = match_group["Player"].unique()
    for player_name in players_list:
        player_data = match_group[match_group["Player"] == player_name].iloc[0]
        with st.container():
            cols = st.columns([1, 4])
            with cols[0]:
                try:
                    st.markdown("<div class='player-card'>", unsafe_allow_html=True)
                    st.image(player_data["Photo"], width=70)
                    pos_group = get_position_group(player_data["Position"])
                    st.markdown(f"<div class='player-info'><strong>{player_name}</strong><br>Team: {player_data['Team']}<br><span class='position-badge {pos_group}'>{player_data['Position']}</span></div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                except:
                    st.warning("Image not found")
            with cols[1]:
                st.markdown(f"#### Heatmaps - {player_name}")
                df_player = df[(df["Player"] == player_name) & (df["Round"] == round_num)].sort_values("Date", ascending=False)
                for _, row in df_player.iterrows():
                    st.markdown(f"**Round {row['Round']}** - Date: `{row['Date'].date()}` - Opponent: `{row['Cavalry/Opponent']}`")
                    position = str(row.get("Position", "")).strip().upper()
                    if position == "GK":
                        st.markdown(f"Minutes: `{row['Minutes played']}` | Saves: `{row['Saves']}` | Goals Against: `{row['Goal Against']}`")
                    else:
                        st.markdown(f"Minutes: `{row['Minutes played']}` | Goals: `{row['Goals']}` | Assists: `{row['Assists']}`")
                    try:
                        headers = {"User-Agent": "Mozilla/5.0"}
                        response = requests.get(row["heatmap"], headers=headers)
                        image = Image.open(BytesIO(response.content))
                        st.image(image, width=300)
                    except:
                        st.warning(f"⚠️ Could not load heatmap for Round {row['Round']}")
