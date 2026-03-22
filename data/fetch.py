import pandas as pd

def fetch_minneapolis_crimes(limit=2000):
    url = "https://opendata.arcgis.com/api/v3/datasets/441d4c0410854e3da692b24347ab6b0d_0/downloads/data?format=csv&spatialRefId=4326"

    print("Downloading Minneapolis crime data...")
    df = pd.read_csv(url)

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

    print(f"Loaded {len(df)} records")
    print(df[["offense", "neighborhood", "lat", "long"]].head())
    return df

if __name__ == "__main__":
    df = fetch_minneapolis_crimes()
    print("\nTop offense types:")
    print(df["offense"].value_counts().head(10))