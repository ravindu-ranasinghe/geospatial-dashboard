import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def chart_by_neighborhood(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Horizontal bar chart of top N neighborhoods by incident count."""
    counts = df["neighborhood"].value_counts().head(top_n).reset_index()
    counts.columns = ["neighborhood", "count"]
    return px.bar(
        counts, x="count", y="neighborhood", orientation="h",
        title=f"Top {top_n} Neighborhoods by Incident Count",
    )


def chart_by_offense(df: pd.DataFrame) -> go.Figure:
    """Pie chart of incidents by offense type."""
    counts = df["offense"].value_counts().reset_index()
    counts.columns = ["offense", "count"]
    return px.pie(counts, names="offense", values="count", title="Offense Type Breakdown")


def chart_by_month(df: pd.DataFrame) -> go.Figure:
    """Line chart of incident count grouped by year-month."""
    tmp = df.copy()
    tmp["month"] = tmp["reportedDate"].dt.to_period("M").astype(str)
    counts = tmp.groupby("month").size().reset_index(name="count").sort_values("month")
    return px.line(counts, x="month", y="count", title="Incidents Over Time (Monthly)")
