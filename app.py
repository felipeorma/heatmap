import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

st.set_page_config(layout="wide")

st.title("⚽ Player Match Data Viewer")

# Load match data
@st.cache_data
def load_data():
    df = pd.read_csv("matches.csv")
    return df

# Load data
df = load_data()
df["Round"] = df["Round"].astype(str)

# Filters
rounds = ["All"] + sorted(df["Round"].unique().tolist())
round_filter = st.selectbox("Select match round:", rounds)

sides = ["All"] + sorted(df["Local/Visit"].unique().tolist())
side_filter = st.selectbox("Select team side:", sides)

players = ["All"] + sorted(df["Player"].unique().tolist())
player_filter = st.selectbox("Select player:", players)

# Apply filters
df_filtered = df.copy()
if round_filter != "All":
    df_filtered = df_filtered[df_filtered["Round"] == round_filter]
if side_filter != "All":
    df_filtered = df_filtered[df_filtered["Local/Visit"] == side_filter]
if player_filter != "All":
    df_filtered = df_filtered[df_filtered["Player"] == player_filter]

# Show table
st.subheader("Filtered Match Data")
st.dataframe(df_filtered[["Round", "Player", "Cavalry/Opponent", "Local/Visit", "Minutes played", "Goals", "Assists"]].reset_index(drop=True))

# If a single player selected, show evolution
if player_filter != "All":
    df_player = df[df["Player"] == player_filter].sort_values("Round")

    st.subheader(f"Evolution of {player_filter}")

    for _, row in df_player.iterrows():
        st.markdown(f"**Round {row['Round']}** - Opponent: {row['Cavalry/Opponent']} | Minutes: {row['Minutes played']} | Goals: {row['Goals']} | Assists: {row['Assists']}")
        try:
            response = requests.get(row["heatmap"])
            image = Image.open(BytesIO(response.content))
            st.image(image, width=350)
        except:
            st.warning(f"Could not load heatmap for Round {row['Round']}")
