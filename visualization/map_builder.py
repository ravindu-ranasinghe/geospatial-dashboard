import folium
from folium.plugins import HeatMap
import pandas as pd

from visualization.styles import HEATMAP_CONFIG, MARKER_CONFIG, OFFENSE_COLORS


def offense_color(offense: str) -> str:
    """Return a hex color string for a given offense label."""
    o = str(offense).lower()
    for key, color in OFFENSE_COLORS.items():
        if key == "default":
            continue
        if key in o:
            return color
    return OFFENSE_COLORS["default"]


def build_map(
    df: pd.DataFrame,
    center: list[float] | None = None,
    zoom: int = 12,
) -> folium.Map:
    """Build a Folium map with a heatmap layer and per-incident circle markers."""
    if center is None:
        center = [44.9778, -93.2650]

    m = folium.Map(location=center, zoom_start=zoom)

    heat_data = df[["lat", "long"]].dropna().values.tolist()
    HeatMap(heat_data, **HEATMAP_CONFIG).add_to(m)

    for _, row in df.head(200).iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["long"]],
            radius=MARKER_CONFIG["radius"],
            color=offense_color(row["offense"]),
            fill=True,
            fill_opacity=MARKER_CONFIG["fill_opacity"],
            popup=folium.Popup(
                f"<b>{row['offense']}</b><br>"
                f"Neighborhood: {row.get('neighborhood', '?')}<br>"
                f"Date: {str(row.get('reportedDate', '?'))[:10]}",
                max_width=200,
            ),
        ).add_to(m)

    return m
