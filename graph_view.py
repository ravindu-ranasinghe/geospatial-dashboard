import networkx as nx
from pyvis.network import Network
import pandas as pd

def build_graph(df, top_n=50):
    df = df.head(top_n).copy()
    G = nx.Graph()

    for _, row in df.iterrows():
        offense = str(row["offense"])
        neighborhood = str(row["neighborhood"])
        date = str(row["reportedDate"])[:10]

        G.add_node(offense, label=offense, color="#e74c3c", size=20, group="offense")
        G.add_node(neighborhood, label=neighborhood, color="#3498db", size=15, group="neighborhood")
        G.add_node(date, label=date, color="#2ecc71", size=10, group="date")

        G.add_edge(offense, neighborhood)
        G.add_edge(neighborhood, date)

    net = Network(height="550px", width="100%", bgcolor="#0a0a0a", font_color="white")
    net.from_nx(G)
    net.repulsion(node_distance=150, spring_length=200)
    net.save_graph("graph.html")
    return "graph.html"

if __name__ == "__main__":
    from data.fetch import fetch_minneapolis_crimes
    df = fetch_minneapolis_crimes()
    build_graph(df)
    print("Saved graph.html")