import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
from st_aggrid import AgGrid, GridOptionsBuilder
from streamlit_extras.metric_cards import style_metric_cards

st.set_page_config(page_title="Cavalry Player Heatmap Dashboard", layout="wide")

st.markdown("""
    <style>
        .main { background-color: #f9f9f9; }
        .stDataFrame div[data-testid="stHorizontalBlock"] { background-color: #ffffff; border-radius: 10px; padding: 1rem; }
        .block-container { padding-top: 2rem; }
        .css-1d391kg { padding: 1rem 1rem; }
    </style>
""", unsafe_allow_html=True)

st.title("⚽ Cavalry FC - Player Match Dashboard")

# Load match data
@st.cache_data
def load_data():
    df = pd.read_csv("matches.csv")
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

# Summary metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Players", df_filtered["Player"].nunique())
col2.metric("Total Goals", int(df_filtered["Goals"].sum()))
col3.metric("Total Assists", int(df_filtered["Assists"].sum()))
style_metric_cards()

# Display filtered table with AgGrid
st.subheader("📋 Filtered Match Data")
gb = GridOptionsBuilder.from_dataframe(df_filtered)
gb.configure_pagination(paginationAutoPageSize=True)
gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, editable=False)
gridOptions = gb.build()
AgGrid(df_filtered[["Round", "Player", "Team", "Cavalry/Opponent", "Local/Visit", "Minutes played", "Goals", "Assists", "Saves", "Goal Against"]], gridOptions=gridOptions, theme='streamlit')

# Player evolution view
if player_filter != "All":
    df_player = df[df["Player"] == player_filter].sort_values("Round")
    st.subheader(f"📈 Performance Evolution - {player_filter}")

    for _, row in df_player.iterrows():
        with st.container():
            st.markdown(f"**Round {row['Round']}** - Opponent: `{row['Cavalry/Opponent']}`")
            st.markdown(f"Minutes: `{row['Minutes played']}` | Goals: `{row['Goals']}` | Assists: `{row['Assists']}` | Saves: `{row['Saves']}` | Goals Against: `{row['Goal Against']}`")
            try:
                response = requests.get(row["heatmap"])
                image = Image.open(BytesIO(response.content))
                st.image(image, width=400)
            except:
                st.warning(f"⚠️ Could not load heatmap for Round {row['Round']}")
