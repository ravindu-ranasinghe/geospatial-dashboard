from pathlib import Path

import pandas as pd

def fetch_minneapolis_crimes(limit=2000):
    url = "https://opendata.arcgis.com/api/v3/datasets/441d4c0410854e3da692b24347ab6b0d_0/downloads/data?format=csv&spatialRefId=4326"
    cache_path = Path(__file__).resolve().parent / "minneapolis_crimes_cache.csv"
    source = "remote"

    print("Loading Minneapolis crime data...")
    try:
        df = pd.read_csv(url)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(cache_path, index=False)
    except Exception as exc:
        if cache_path.exists():
            print(f"Remote download failed ({exc}). Using cache at {cache_path}.")
            df = pd.read_csv(cache_path)
            source = "cache"
        else:
            print(f"Remote download failed ({exc}). Using bundled sample records.")
            source = "sample"
            df = pd.DataFrame(
                [
                    {
                        "Latitude": 44.9992,
                        "Longitude": -93.2644,
                        "Offense": "Theft",
                        "Offense_Category": "Property Crime",
                        "Reported_Date": "2026-02-14",
                        "Neighborhood": "Downtown West",
                        "Address": "7th St S & Hennepin Ave",
                        "Precinct": "1",
                    },
                    {
                        "Latitude": 44.9778,
                        "Longitude": -93.2650,
                        "Offense": "Assault",
                        "Offense_Category": "Violent Crime",
                        "Reported_Date": "2026-02-18",
                        "Neighborhood": "Loring Park",
                        "Address": "Nicollet Ave & 15th St",
                        "Precinct": "1",
                    },
                    {
                        "Latitude": 44.9482,
                        "Longitude": -93.2870,
                        "Offense": "Burglary",
                        "Offense_Category": "Property Crime",
                        "Reported_Date": "2026-02-21",
                        "Neighborhood": "Uptown",
                        "Address": "Hennepin Ave S & Lake St W",
                        "Precinct": "5",
                    },
                    {
                        "Latitude": 44.9647,
                        "Longitude": -93.2990,
                        "Offense": "Vehicle Theft",
                        "Offense_Category": "Property Crime",
                        "Reported_Date": "2026-02-25",
                        "Neighborhood": "Near North",
                        "Address": "Plymouth Ave N & Penn Ave N",
                        "Precinct": "4",
                    },
                    {
                        "Latitude": 44.9412,
                        "Longitude": -93.2217,
                        "Offense": "Robbery",
                        "Offense_Category": "Violent Crime",
                        "Reported_Date": "2026-03-01",
                        "Neighborhood": "Longfellow",
                        "Address": "Lake St E & Minnehaha Ave",
                        "Precinct": "3",
                    },
                ]
            )

    df = df.dropna(subset=["Latitude", "Longitude"])
    df = df[df["Latitude"] != 0]

    df = df.rename(columns={
        "Latitude":       "lat",
        "Longitude":      "long",
        "Offense":        "offense",
        "Offense_Category": "category",
        "Reported_Date":  "reportedDate",
        "Neighborhood":   "neighborhood",
        "Address":        "address",
        "Precinct":       "precinct"
    })

    df["reportedDate"] = pd.to_datetime(df["reportedDate"], errors="coerce")
    df = df.head(limit)

    print(f"Loaded {len(df)} records from {source}")
    print(df[["offense", "neighborhood", "lat", "long"]].head())
    return df

if __name__ == "__main__":
    df = fetch_minneapolis_crimes()
    print("\nTop offense types:")
    print(df["offense"].value_counts().head(10))