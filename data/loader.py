from pathlib import Path

import pandas as pd

from data.fetch import fetch_minneapolis_crimes

_PARQUET = Path(__file__).resolve().parent / "minneapolis_crimes.parquet"


def load_crimes(limit: int = 2000) -> pd.DataFrame:
    """Load crime data with Parquet caching. Fetches remote on cache miss."""
    if _PARQUET.exists():
        df = pd.read_parquet(_PARQUET)
        return df.head(limit)

    df = fetch_minneapolis_crimes(limit=limit)
    try:
        df.to_parquet(_PARQUET, index=False)
    except Exception as exc:
        print(f"Warning: could not write Parquet cache: {exc}")
    return df
