import streamlit as st
from streamlit_folium import st_folium
from data.fetch import fetch_minneapolis_crimes
from map import build_map, offense_color

st.set_page_config(page_title="GeoINT Dashboard", layout="wide")
st.title("Minneapolis Crime Intelligence Dashboard")

@st.cache_data
def load_data():
    return fetch_minneapolis_crimes(limit=2000)

df = load_data()

with st.sidebar:
    st.header("Filters")

    neighborhoods = ["All"] + sorted(df["neighborhood"].dropna().unique().tolist())
    selected_neighborhood = st.selectbox("Neighborhood", neighborhoods)

    categories = ["All"] + sorted(df["offense"].dropna().unique().tolist())
    selected_offense = st.selectbox("Offense type", categories)

    date_range = st.date_input(
        "Date range",
        value=[df["reportedDate"].min(), df["reportedDate"].max()]
    )

filtered = df.copy()

if selected_neighborhood != "All":
    filtered = filtered[filtered["neighborhood"] == selected_neighborhood]

if selected_offense != "All":
    filtered = filtered[filtered["offense"] == selected_offense]

if len(date_range) == 2:
    filtered = filtered[
        (filtered["reportedDate"].dt.date >= date_range[0]) &
        (filtered["reportedDate"].dt.date <= date_range[1])
    ]

col1, col2, col3 = st.columns(3)
col1.metric("Total incidents", len(filtered))
col2.metric("Neighborhoods", filtered["neighborhood"].nunique())
col3.metric("Offense types", filtered["offense"].nunique())

st_folium(build_map(filtered), width=None, height=550, returned_objects=[])

st.subheader("Raw data")
st.dataframe(
    filtered[["reportedDate", "offense", "neighborhood", "address"]].sort_values("reportedDate", ascending=False),
    use_container_width=True
)

st.subheader("Hotspot search")
search = st.text_input("Search neighborhood or offense", placeholder="e.g. Jordan, Weapon, Theft")

if search:
    mask = (
        filtered["neighborhood"].str.contains(search, case=False, na=False) |
        filtered["offense"].str.contains(search, case=False, na=False)
    )
    filtered = filtered[mask]
    st.caption(f"{len(filtered)} incidents matching '{search}'")

import streamlit.components.v1 as components
from graph_view import build_graph

st.subheader("Entity link graph")
st.caption("Red = offense type  |  Blue = neighborhood  |  Green = date")
graph_path = build_graph(filtered.head(50))
with open(graph_path, "r") as f:
    components.html(f.read(), height=560)