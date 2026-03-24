import streamlit as st
import streamlit.components.v1 as components
from streamlit_folium import st_folium
import pandas as pd

from data.loader import load_crimes
from processing.filters import (
    apply_search,
    filter_by_date,
    filter_by_neighborhood,
    filter_by_type,
)
from visualization.graph_builder import build_graph
from visualization.map_builder import build_animated_heatmap, build_map

st.set_page_config(page_title="GeoINT Dashboard", layout="wide")
st.title("Minneapolis Crime Intelligence Dashboard")


@st.cache_data
def get_data() -> pd.DataFrame:
    return load_crimes(limit=None)


df = get_data()

with st.sidebar:
    st.header("Filters")
    neighborhoods = ["All"] + sorted(df["neighborhood"].dropna().unique().tolist())
    selected_neighborhood = st.selectbox("Neighborhood", neighborhoods)
    categories = ["All"] + sorted(df["offense"].dropna().unique().tolist())
    selected_offense = st.selectbox("Offense type", categories)
    date_range = st.date_input(
        "Date range",
        value=[df["reportedDate"].min(), df["reportedDate"].max()],
    )

filtered = filter_by_neighborhood(df, selected_neighborhood)
filtered = filter_by_type(filtered, selected_offense)
if len(date_range) == 2:
    filtered = filter_by_date(filtered, date_range[0], date_range[1])

col1, col2, col3 = st.columns(3)
col1.metric("Total incidents", len(filtered))
col2.metric("Neighborhoods", filtered["neighborhood"].nunique())
col3.metric("Offense types", filtered["offense"].nunique())

tab_map, tab_anim = st.tabs(["Map View", "Animated View"])

with tab_map:
    st_folium(build_map(filtered), width=None, height=550, returned_objects=[])

    st.subheader("Raw data")
    st.dataframe(
        filtered[["reportedDate", "offense", "neighborhood", "address"]].sort_values(
            "reportedDate", ascending=False
        ),
        use_container_width=True,
    )

    st.subheader("Hotspot search")
    search = st.text_input("Search neighborhood or offense", placeholder="e.g. Jordan, Weapon, Theft")
    if search:
        result = apply_search(filtered, search)
        st.caption(f"{len(result)} incidents matching '{search}'")

    st.subheader("Entity link graph")
    st.caption("Red = offense type  |  Blue = neighborhood  |  Green = date")
    graph_path = build_graph(filtered.head(50))
    with open(graph_path, "r") as f:
        components.html(f.read(), height=560)

with tab_anim:
    st.subheader("Animated Heatmap")
    mode = st.radio(
        "Animate by",
        options=["Monthly", "By Hour of Day"],
        horizontal=True,
    )
    anim_mode = "monthly" if mode == "Monthly" else "hourly"

    caption = (
        "Each frame shows crime density for one calendar month."
        if anim_mode == "monthly"
        else "Each frame shows crime density for one hour of the day (all dates combined)."
    )
    st.caption(caption)
    anim_map = build_animated_heatmap(filtered, mode=anim_mode)
    components.html(anim_map.get_root().render(), height=560)
