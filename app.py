import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Cavalry Player Heatmap Dashboard", layout="wide")

st.markdown("""
    <style>
        .main { background-color: #f9f9f9; }
        .stDataFrame div[data-testid="stHorizontalBlock"] { background-color: #ffffff; border-radius: 10px; padding: 1rem; }
        .block-container { padding-top: 2rem; }
        .css-1d391kg { padding: 1rem 1rem; }
        .position-badge {
            display: inline-block;
            padding: 0.25em 0.6em;
            font-size: 0.75em;
            font-weight: bold;
            border-radius: 0.5rem;
            color: white;
        }
        .GK { background-color: #28a745; }
        .DF { background-color: #007bff; }
        .MF { background-color: #ffc107; }
        .FW { background-color: #dc3545; }
        .N_A { background-color: #6c757d; }
    </style>
""", unsafe_allow_html=True)

st.title("⚽ Cavalry FC - Player Heatmap Match Dashboard")

# Load match data
@st.cache_data

def load_data():
    df = pd.read_csv("matches.csv")
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
    df = df.sort_values("Date", ascending=False)
    return df.fillna(0)

# Load data
df = load_data()
df["Round"] = df["Round"].astype(str)

# Sidebar filters
with st.sidebar:
    st.header("🔎 Filters")
    round_filter = st.selectbox("Match Round", ["All"] + sorted(df["Round"].unique().tolist()))
    side_filter = st.selectbox("Team Side", ["All"] + sorted(df["Local/Visit"].astype(str).unique().tolist()))
    player_filter = st.selectbox("Player", ["All"] + sorted(df["Player"].astype(str).unique().tolist()))

# Apply filters
df_filtered = df[df["Player"].astype(str) != "0"].copy()
if round_filter != "All":
    df_filtered = df_filtered[df_filtered["Round"] == round_filter]
if side_filter != "All":
    df_filtered = df_filtered[df_filtered["Local/Visit"] == side_filter]
if player_filter != "All":
    df_filtered = df_filtered[df_filtered["Player"] == player_filter]

# Agrupar por posición base (primera letra: GK, D, M, F)
def get_position_group(pos):
    pos = str(pos).upper()
    if pos == "GK": return "GK"
    if pos.startswith("D"): return "DF"
    if pos.startswith("M"): return "MF"
    if pos.startswith("F") or pos.endswith("W") or pos.endswith("CF"): return "FW"
    return "N_A"

# Mostrar tarjetas agrupadas
st.subheader("🧍 Players")
df_filtered["PositionGroup"] = df_filtered["Position"].apply(get_position_group)
position_groups = ["GK", "DF", "MF", "FW"]

for group in position_groups:
    players_pos = df_filtered[df_filtered["PositionGroup"] == group]["Player"].unique()
    if len(players_pos) > 0:
        st.markdown(f"### 🟢 {group}s")
        for i in range(0, len(players_pos), 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                if i + j < len(players_pos):
                    player_name = players_pos[i + j]
                    player_data = df_filtered[df_filtered["Player"] == player_name].iloc[0]
                    try:
                        col.image(player_data["Photo"], use_column_width=True)
                        col.markdown(f"**{player_name}**")
                        col.markdown(f"Team: `{player_data['Team']}`")
                        full_position = str(player_data.get("Position", "N/A"))
                        badge_class = get_position_group(full_position)
                        col.markdown(f'<span class="position-badge {badge_class}">{full_position}</span>', unsafe_allow_html=True)
                    except:
                        col.warning("Image not found")
                    if col.button(f"View Heatmaps - {player_name}"):
                        st.session_state.selected_player = player_name

# Player heatmap evolution
if "selected_player" in st.session_state:
    player_filter = st.session_state.selected_player
    df_player = df[df["Player"] == player_filter].sort_values("Date", ascending=False)
    st.subheader(f"📈 Performance Evolution - {player_filter}")

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
            st.image(image, width=400)
        except:
            st.warning(f"⚠️ Could not load heatmap for Round {row['Round']}")
