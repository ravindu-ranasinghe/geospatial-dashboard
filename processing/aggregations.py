import pandas as pd


def count_by_neighborhood(df: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame of (neighborhood, count) sorted descending."""
    return (
        df.groupby("neighborhood")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )


def count_by_hour(df: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame of (hour 0-23, count)."""
    tmp = df.copy()
    tmp["hour"] = tmp["reportedDate"].dt.hour
    return tmp.groupby("hour").size().reset_index(name="count")


def count_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame of (month string YYYY-MM, count) sorted by month."""
    tmp = df.copy()
    tmp["month"] = tmp["reportedDate"].dt.to_period("M").astype(str)
    return (
        tmp.groupby("month")
        .size()
        .reset_index(name="count")
        .sort_values("month")
    )
