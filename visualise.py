import os
from pyvis.network import Network

from data import DOCUMENTS
from graph_builder import build_graph

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

OUTPUT_FILE = "graph.html"


# ---------------------------------------------------------------------------
# Visualiser
# ---------------------------------------------------------------------------

def visualise_graph(G) -> None:
    net = Network(
        height="750px",
        width="100%",
        bgcolor="#0d1117",        # dark background
        font_color="#ffffff",
        directed=True,
    )

    # Physics — makes the graph feel alive and draggable
    net.set_options("""
    {
      "physics": {
        "enabled": true,
        "stabilization": { "iterations": 150 },
        "barnesHut": {
          "gravitationalConstant": -8000,
          "springLength": 200,
          "springConstant": 0.04
        }
      },
      "edges": {
        "smooth": { "type": "dynamic" },
        "arrows": { "to": { "enabled": true, "scaleFactor": 0.6 } },
        "color": { "color": "#58a6ff" },
        "font": { "size": 11, "color": "#8b949e", "align": "middle" }
      },
      "nodes": {
        "shape": "dot",
        "size": 18,
        "font": { "size": 14, "color": "#ffffff" },
        "borderWidth": 2
      }
    }
    """)

    # Add nodes
    for node in G.nodes:
        net.add_node(
            node,
            label=node,
            title=node,        # tooltip on hover
            color="#238636",   # green
        )

    # Add edges with relation as label
    for u, v, data in G.edges(data=True):
        relation = data.get("relation", "related to")
        net.add_edge(
            u, v,
            label=relation,
            title=relation,    # tooltip on hover
        )

    net.save_graph(OUTPUT_FILE)
    print(f"Graph visualisation saved to {OUTPUT_FILE}")
    print(f"Open it in your browser: file://{os.path.abspath(OUTPUT_FILE)}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Loading graph...")
    G = build_graph(DOCUMENTS)
    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    print("Generating visualisation...")
    visualise_graph(G)