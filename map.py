import folium
from folium.plugins import HeatMap

def build_map(df):
    m = folium.Map(location=[44.9778, -93.2650], zoom_start=12)

    heat_data = df[["lat", "long"]].dropna().values.tolist()
    HeatMap(heat_data, radius=12, blur=15, min_opacity=0.4).add_to(m)

    for _, row in df.head(200).iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["long"]],
            radius=4,
            color=offense_color(row["offense"]),
            fill=True,
            fill_opacity=0.7,
            popup=folium.Popup(
                f"<b>{row['offense']}</b><br>"
                f"Neighborhood: {row.get('neighborhood','?')}<br>"
                f"Date: {str(row.get('reportedDate','?'))[:10]}",
                max_width=200
            )
        ).add_to(m)

    return m

def offense_color(offense):
    offense = str(offense).lower()
    if "assault" in offense:  return "#e74c3c"
    if "theft" in offense:    return "#e67e22"
    if "vehicle" in offense:  return "#f1c40f"
    if "burglary" in offense: return "#9b59b6"
    if "weapon" in offense:   return "#c0392b"
    return "#3498db"

if __name__ == "__main__":
    from data.fetch import fetch_minneapolis_crimes
    df = fetch_minneapolis_crimes()
    m = build_map(df)
    m.save("map.html")
    print("Saved map.html")