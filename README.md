# Geospatial Crime Dashboard

An interactive geospatial dashboard for exploring crime incident data across Minneapolis. Built with Python, Streamlit, and Folium — lets you visualize where and when crime occurs across the city on a live, filterable map.

## Why

Public crime data exists but it's hard to make sense of as raw CSVs. This dashboard puts that data on a map so patterns become immediately visible — which neighborhoods see the most incidents, how crime concentrates by type, and how activity shifts over time. Built to practice working with geospatial data and real public datasets end-to-end, from ingestion to interactive visualization.

## Features

**Interactive map** — Folium-powered map with crime incident markers across Minneapolis. Click any marker to see incident type, date, and location details.

**Graph view** — A separate chart view for analyzing trends over time — incident counts by date, category breakdowns, and frequency patterns.

**Filtering** — Filter incidents by crime type, date range, and neighborhood to drill into specific slices of the data.

**Streamlit UI** — Clean single-page dashboard that runs locally with one command, no browser extensions or setup required.

## Quick Start

```bash
git clone https://github.com/ravindu-ranasinghe/geospatial-dashboard.git
cd geospatial-dashboard

pip install -r requirements.txt

streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501).

## Data Source

Crime incident data sourced from the [Minneapolis Police Department Open Data Portal](https://opendata.minneapolismn.gov/). The dataset includes reported incidents with coordinates, offense category, date, and neighborhood.

## Tech Stack

| Component | Technology | Why |
|---|---|---|
| Language | Python | Pandas + geospatial ecosystem |
| Dashboard UI | Streamlit | Fast interactive dashboards with no frontend code |
| Map rendering | Folium | Leaflet.js wrapper — interactive maps in pure Python |
| Data processing | Pandas | Standard for tabular data manipulation |

## Project Structure

```
geospatial-dashboard/
├── app.py              # Main Streamlit app and layout
├── map.py              # Folium map generation and marker logic
├── graph_view.py       # Chart and graph views
├── data/               # Minneapolis crime dataset(s)
├── lib/                # Utility and helper modules
└── requirements.txt    # Python dependencies
```

## Live Demo

Coming soon — deploying on Streamlit Cloud.

## License

MIT
