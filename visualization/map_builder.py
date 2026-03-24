import json
from pathlib import Path
from typing import Optional

import folium
from folium.plugins import HeatMap, HeatMapWithTime, MarkerCluster
import pandas as pd
import requests

from visualization.styles import HEATMAP_CONFIG, OFFENSE_COLORS

_CENTER = [44.9778, -93.2650]
_GEOJSON_URL = (
    "https://services.arcgis.com/afSMGVsC7QlRK1kZ/arcgis/rest/services/"
    "Minneapolis_Neighborhoods/FeatureServer/0/query"
    "?outFields=*&where=1%3D1&f=geojson"
)
_GEOJSON_CACHE = (
    Path(__file__).resolve().parent.parent / "data" / "minneapolis_neighborhoods.geojson"
)


def offense_color(offense: str) -> str:
    """Return a hex color string for a given offense label."""
    o = str(offense).lower()
    for key, color in OFFENSE_COLORS.items():
        if key == "default":
            continue
        if key in o:
            return color
    return OFFENSE_COLORS["default"]


def _load_geojson(local_path: Optional[str] = None) -> Optional[dict]:
    """Load neighborhood GeoJSON: local path → cache → remote URL."""
    if local_path and Path(local_path).exists():
        with open(local_path) as f:
            return json.load(f)
    if _GEOJSON_CACHE.exists():
        with open(_GEOJSON_CACHE) as f:
            return json.load(f)
    try:
        resp = requests.get(_GEOJSON_URL, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        _GEOJSON_CACHE.parent.mkdir(parents=True, exist_ok=True)
        with open(_GEOJSON_CACHE, "w") as f:
            json.dump(data, f)
        return data
    except Exception as exc:
        print(f"Could not load neighborhood GeoJSON: {exc}")
        return None


def _detect_name_field(geojson: dict) -> Optional[str]:
    """Detect the property key holding the neighborhood name."""
    if not geojson.get("features"):
        return None
    props = geojson["features"][0].get("properties", {})
    for candidate in ["BDNAME", "Name", "NAME", "neighborhood", "NEIGHBORHOOD", "NBHD_NAME"]:
        if candidate in props:
            return candidate
    for k, v in props.items():
        if isinstance(v, str):
            return k
    return None


def _add_choropleth(
    m: folium.Map,
    df: pd.DataFrame,
    geojson_path: Optional[str] = None,
) -> None:
    """Add a choropleth layer shaded by crime count per neighborhood."""
    geojson = _load_geojson(geojson_path)
    if geojson is None:
        return

    name_field = _detect_name_field(geojson)
    if not name_field:
        return

    counts = df.groupby("neighborhood").size().reset_index(name="count")

    # Inject count into GeoJSON properties for the tooltip
    count_map = dict(zip(counts["neighborhood"], counts["count"]))
    for feat in geojson.get("features", []):
        nb = feat.get("properties", {}).get(name_field, "")
        feat["properties"]["crime_count"] = count_map.get(nb, 0)

    choropleth = folium.Choropleth(
        geo_data=geojson,
        data=counts,
        columns=["neighborhood", "count"],
        key_on=f"feature.properties.{name_field}",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Crime Count by Neighborhood",
        name="Neighborhood Crime Rate",
        show=True,
    )
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(
            fields=[name_field, "crime_count"],
            aliases=["Neighborhood:", "Crime count:"],
            style="font-size: 12px;",
        )
    )
    choropleth.add_to(m)


def build_map(
    df: pd.DataFrame,
    center: list[float] | None = None,
    zoom: int = 12,
    geojson_path: Optional[str] = None,
) -> folium.Map:
    """Build a Folium map with three toggleable layers and two basemaps.

    Layers:
      - Crime Density Heatmap (on by default)
      - Individual Incidents via MarkerCluster (off by default)
      - Neighborhood Crime Rate choropleth (on by default, requires GeoJSON)
    """
    if center is None:
        center = _CENTER

    m = folium.Map(location=center, zoom_start=zoom, tiles=None)

    # Basemaps
    folium.TileLayer("CartoDB Positron", name="Light Basemap").add_to(m)
    folium.TileLayer("CartoDB DarkMatter", name="Dark Basemap").add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery",
        name="Satellite",
    ).add_to(m)

    # --- Layer 1: HeatMap ---
    heat_fg = folium.FeatureGroup(name="Crime Density Heatmap", show=True)
    heat_data = df[["lat", "long"]].dropna().values.tolist()
    HeatMap(heat_data, **HEATMAP_CONFIG).add_to(heat_fg)
    heat_fg.add_to(m)

    # --- Layer 2: MarkerCluster (capped at 1000 for performance) ---
    cluster_fg = folium.FeatureGroup(name="Individual Incidents", show=False)
    mc = MarkerCluster()
    for _, row in df.head(1000).iterrows():
        color = offense_color(row["offense"])
        popup_html = (
            f"<b>{row['offense']}</b><br>"
            f"Neighborhood: {row.get('neighborhood', '?')}<br>"
            f"Date: {str(row.get('reportedDate', '?'))[:10]}<br>"
            f"Address: {row.get('address', '?')}"
        )
        folium.CircleMarker(
            location=[row["lat"], row["long"]],
            radius=5,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=240),
        ).add_to(mc)
    mc.add_to(cluster_fg)
    cluster_fg.add_to(m)

    # --- Layer 3: Choropleth ---
    _add_choropleth(m, df, geojson_path)

    folium.LayerControl(collapsed=False).add_to(m)
    return m


def _hour_label(hour: int) -> str:
    if hour == 0:
        return "12:00 AM"
    if hour < 12:
        return f"{hour}:00 AM"
    if hour == 12:
        return "12:00 PM"
    return f"{hour - 12}:00 PM"


def build_animated_heatmap(df: pd.DataFrame, mode: str = "monthly") -> folium.Map:
    """Build an animated HeatMapWithTime.

    Args:
        df: crime DataFrame with lat, long, reportedDate columns.
        mode: "monthly" steps through year-months; "hourly" steps through 0-23.

    Returns:
        A folium.Map with an auto-playing animated heatmap.
    """
    m = folium.Map(location=_CENTER, zoom_start=12, tiles=None)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery",
        name="Satellite",
    ).add_to(m)
    tmp = df.dropna(subset=["lat", "long", "reportedDate"]).copy()

    heat_data: list[list[list[float]]] = []
    index: list[str] = []

    if mode == "monthly":
        tmp["period"] = tmp["reportedDate"].dt.to_period("M")
        for period in sorted(tmp["period"].unique()):
            subset = tmp[tmp["period"] == period]
            heat_data.append(subset[["lat", "long"]].assign(w=1.0).values.tolist())
            index.append(period.strftime("%b %Y"))

    else:  # hourly
        tmp["hour"] = tmp["reportedDate"].dt.hour
        for hour in range(24):
            subset = tmp[tmp["hour"] == hour]
            heat_data.append(subset[["lat", "long"]].assign(w=1.0).values.tolist())
            index.append(_hour_label(hour))

    HeatMapWithTime(
        heat_data,
        index=index,
        auto_play=True,
        max_speed=10,
        min_speed=1,
        radius=15,
    ).add_to(m)

    return m
