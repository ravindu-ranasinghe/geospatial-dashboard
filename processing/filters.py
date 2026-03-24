from datetime import date

import pandas as pd


def filter_by_date(df: pd.DataFrame, start: date, end: date) -> pd.DataFrame:
    """Keep rows whose reportedDate falls within [start, end] inclusive."""
    return df[
        (df["reportedDate"].dt.date >= start) &
        (df["reportedDate"].dt.date <= end)
    ]


def filter_by_type(df: pd.DataFrame, offense_type: str) -> pd.DataFrame:
    """Filter to a single offense type. 'All' returns df unchanged."""
    if offense_type == "All":
        return df
    return df[df["offense"] == offense_type]


def filter_by_neighborhood(df: pd.DataFrame, neighborhood: str) -> pd.DataFrame:
    """Filter to a single neighborhood. 'All' returns df unchanged."""
    if neighborhood == "All":
        return df
    return df[df["neighborhood"] == neighborhood]


def apply_search(df: pd.DataFrame, query: str) -> pd.DataFrame:
    """Case-insensitive substring search across neighborhood and offense columns."""
    if not query:
        return df
    mask = (
        df["neighborhood"].str.contains(query, case=False, na=False) |
        df["offense"].str.contains(query, case=False, na=False)
    )
    return df[mask]
