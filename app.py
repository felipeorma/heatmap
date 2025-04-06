import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import requests
from io import BytesIO

st.set_page_config(layout="wide")

st.title("⚽ Player Field Visualization")

# Load all match files
@st.cache_data
def load_data():
    files = ["matches_example.csv"]
    df = pd.concat([pd.read_csv(f) for f in files])
    return df

# Load football field image
@st.cache_data
def load_field():
    field_url = "https://raw.githubusercontent.com/tu_usuario/tu_repo/main/campo.png"
    response = requests.get(field_url)
    return Image.open(BytesIO(response.content))

# Data
df = load_data()
field = load_field()

# Select match round
df["Round"] = df["Round"].astype(str)
rounds = df["Round"].drop_duplicates().sort_values()
selected_round = st.selectbox("Select a match round:", rounds)

# Filter players by selected round
df_match = df[df["Round"] == selected_round]

# Dummy positions for plotting
import numpy as np
np.random.seed(42)
df_match["pos_x"] = np.random.randint(10, 90, size=len(df_match))
df_match["pos_y"] = np.random.randint(10, 90, size=len(df_match))

# Display field with players
fig = go.Figure()
fig.add_layout_image(
    dict(
        source=field,
        xref="x",
        yref="y",
        x=0,
        y=100,
        sizex=100,
        sizey=100,
        sizing="stretch",
        opacity=1,
        layer="below"
    )
)

fig.add_trace(go.Scatter(
    x=df_match["pos_x"],
    y=df_match["pos_y"],
    mode='markers+text',
    marker=dict(size=16, color=df_match["Local/Visit"].map({"local": "blue", "visit": "red"})),
    text=df_match["Player"],
    textposition="top center",
    customdata=df_match[["Player", "Goals", "Assists"]],
    hovertemplate="<b>%{customdata[0]}</b><br>Goals: %{customdata[1]} | Assists: %{customdata[2]}<extra></extra>"
))

fig.update_layout(
    xaxis=dict(visible=False, range=[0, 100]),
    yaxis=dict(visible=False, range=[0, 100]),
    height=700,
    margin=dict(l=10, r=10, t=10, b=10),
)

st.plotly_chart(fig, use_container_width=True)

# Select player to see evolution
players = df["Player"].drop_duplicates().sort_values()
selected_player = st.selectbox("Select a player to view their evolution:", players)

df_player = df[df["Player"] == selected_player].sort_values("Round")

st.subheader(f"Evolution of {selected_player}")

for _, row in df_player.iterrows():
    st.markdown(f"**Round {row['Round']}** - Minutes: {row['Minutes played']} | Goals: {row['Goals']} | Assists: {row['Assists']}")
    try:
        response = requests.get(row["heatmap"])
        st.image(Image.open(BytesIO(response.content)), use_column_width=True)
    except:
        st.warning(f"Could not load heatmap for Round {row['Round']}")
