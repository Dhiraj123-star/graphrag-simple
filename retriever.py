import networkx as nx

def find_relevant_nodes(G: nx.DiGraph, query: str) -> list[str]:
    """Simple keyword match: find nodes mentioned in the query."""
    query_lower = query.lower()
    matched = [
        node for node in G.nodes
        if node.lower() in query_lower
    ]
    return matched


def get_subgraph_context(G: nx.DiGraph, nodes: list[str], depth: int = 2) -> str:
    """
    For each matched node, walk the graph up to `depth` hops.
    Collect all edges as readable text for the LLM context.
    """
    visited_edges = set()
    context_lines = []

    def walk(node, current_depth):
        if current_depth == 0:
            return
        # outgoing edges
        for _, neighbor, data in G.out_edges(node, data=True):
            edge_key = (node, neighbor)
            if edge_key not in visited_edges:
                visited_edges.add(edge_key)
                relation = data.get("relation", "related to")
                context_lines.append(f"{node} {relation} {neighbor}.")
                walk(neighbor, current_depth - 1)
        # incoming edges
        for predecessor, _, data in G.in_edges(node, data=True):
            edge_key = (predecessor, node)
            if edge_key not in visited_edges:
                visited_edges.add(edge_key)
                relation = data.get("relation", "related to")
                context_lines.append(f"{predecessor} {relation} {node}.")
                walk(predecessor, current_depth - 1)

    for node in nodes:
        if node in G:
            walk(node, depth)

    if not context_lines:
        # fallback: dump all edges if nothing matched
        for u, v, data in G.edges(data=True):
            context_lines.append(f"{u} {data.get('relation','related to')} {v}.")

    return "\n".join(context_lines)