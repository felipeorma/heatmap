import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import requests
from io import BytesIO

st.set_page_config(layout="wide")

st.title("\ud83c\udfc0 Player Field Visualization")

# Load all match files
@st.cache_data

def load_data():
    files = ["data/partido_01.csv", "data/partido_02.csv"]  # Add more if needed
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

# Select match by date
dates = df["fecha"].drop_duplicates().sort_values()
selected_date = st.selectbox("Select a match date:", dates)

# Filter players by selected match
df_match = df[df["fecha"] == selected_date]

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
    marker=dict(size=16, color=df_match["equipo"].map({"Local": "blue", "Visitante": "red"})),
    text=df_match["dorsal"],
    textposition="top center",
    customdata=df_match[["nombre", "info_extra"]],
    hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<extra></extra>"
))

fig.update_layout(
    xaxis=dict(visible=False, range=[0, 100]),
    yaxis=dict(visible=False, range=[0, 100]),
    height=700,
    margin=dict(l=10, r=10, t=10, b=10),
)

st.plotly_chart(fig, use_container_width=True)

# Select player to see evolution
players = df["nombre"].drop_duplicates().sort_values()
selected_player = st.selectbox("Select a player to view their evolution:", players)

df_player = df[df["nombre"] == selected_player].sort_values("fecha")

st.subheader(f"Evolution of {selected_player}")

for _, row in df_player.iterrows():
    st.markdown(f"**{row['fecha']}** - {row['info_extra']}")
    try:
        response = requests.get(row["heatmap_path"])
        st.image(Image.open(BytesIO(response.content)), use_column_width=True)
    except:
        st.warning(f"Could not load heatmap for {row['fecha']}")
