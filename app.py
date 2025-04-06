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

# Select round
rounds = df["Round"].drop_duplicates().sort_values()
selected_round = st.selectbox("Select a match round:", rounds)

# Filter by round
df_match = df[df["Round"] == selected_round]

# Show player list for the round
st.subheader(f"Players - Round {selected_round}")
st.dataframe(df_match[["Player", "Cavalry/Opponent", "Local/Visit", "Minutes played", "Goals", "Assists"]].reset_index(drop=True))

# Select player to see evolution
players = df["Player"].drop_duplicates().sort_values()
selected_player = st.selectbox("Select a player to view their evolution:", players)

df_player = df[df["Player"] == selected_player].sort_values("Round")

st.subheader(f"Evolution of {selected_player}")

for _, row in df_player.iterrows():
    st.markdown(f"**Round {row['Round']}** - Opponent: {row['Cavalry/Opponent']} | Minutes: {row['Minutes played']} | Goals: {row['Goals']} | Assists: {row['Assists']}")
    try:
        response = requests.get(row["heatmap"])
        st.image(Image.open(BytesIO(response.content)), use_column_width=True)
    except:
        st.warning(f"Could not load heatmap for Round {row['Round']}")

