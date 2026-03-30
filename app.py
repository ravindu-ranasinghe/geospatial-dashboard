import streamlit as st
import streamlit.components.v1 as components
from streamlit_folium import st_folium
import pandas as pd

from data.loader import load_crimes
from processing.filters import apply_search, filter_by_date, filter_by_neighborhood, filter_by_type
from visualization.graph_builder import build_graph
from visualization.map_builder import build_animated_heatmap, build_map

st.set_page_config(page_title="Minneapolis Crime", layout="wide", page_icon="🗺️")

st.markdown("## Minneapolis Crime Dashboard")
st.caption("Data: Minneapolis Police Department open data · Updated daily")

@st.cache_data
def get_data() -> pd.DataFrame:
    return load_crimes(limit=None)

df = get_data()

with st.sidebar:
    st.markdown("### Filters")
    selected_neighborhood = st.selectbox("Neighborhood", ["All"] + sorted(df["neighborhood"].dropna().unique().tolist()))
    selected_offense = st.selectbox("Offense", ["All"] + sorted(df["offense"].dropna().unique().tolist()))
    date_range = st.date_input("Date range", value=[df["reportedDate"].min(), df["reportedDate"].max()])
    st.divider()
    st.caption(f"{len(df):,} total records loaded")

filtered = filter_by_neighborhood(df, selected_neighborhood)
filtered = filter_by_type(filtered, selected_offense)
if len(date_range) == 2:
    filtered = filter_by_date(filtered, date_range[0], date_range[1])

c1, c2, c3 = st.columns(3)
c1.metric("Incidents", f"{len(filtered):,}")
c2.metric("Neighborhoods", filtered["neighborhood"].nunique())
c3.metric("Offense types", filtered["offense"].nunique())

tab_map, tab_anim = st.tabs(["Map", "Animated Heatmap"])

with tab_map:
    st_folium(build_map(filtered), width=None, height=560, returned_objects=[])

    search = st.text_input("Search by neighborhood or offense", placeholder="e.g. Jordan, Theft, Weapon")
    if search:
        result = apply_search(filtered, search)
        st.caption(f"{len(result):,} results for '{search}'")
        st.dataframe(result[["reportedDate", "offense", "neighborhood", "address"]].sort_values("reportedDate", ascending=False), use_container_width=True)
    else:
        st.dataframe(filtered[["reportedDate", "offense", "neighborhood", "address"]].sort_values("reportedDate", ascending=False), use_container_width=True)

    st.markdown("#### Relationships")
    st.caption("Red = offense · Blue = neighborhood · Green = date")
    with open(build_graph(filtered.head(50)), "r") as f:
        components.html(f.read(), height=560)

with tab_anim:
    mode = st.radio("Group by", ["Monthly", "Hour of day"], horizontal=True)
    anim_mode = "monthly" if mode == "Monthly" else "hourly"
    st.caption("Monthly — each frame is one calendar month." if anim_mode == "monthly" else "Hour of day — each frame is an hour (across all dates).")
    components.html(build_animated_heatmap(filtered, mode=anim_mode).get_root().render(), height=560)
