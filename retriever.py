import networkx as nx
import numpy as np
from llm import get_embedding


def cosine_similarity(a:list[float],b:list[float]) -> float:
    a,b = np.array(a),np.array(b)
    return float(np.dot(a,b)/ (np.linalg.norm(a)*np.linalg.norm(b)))


def build_node_embeddings(G: nx.DiGraph) -> dict[str,list[float]]:
    """Pre-compute and return embeddings for every node in the graph."""

    print("\nComputing node embeddings....")
    embeddings={}
    for node in G.nodes:
        embeddings[node]= get_embedding(node)
        print(f" embedded: {node}")
    
    return embeddings

def find_relevant_nodes(
    query:str,
    node_embeddings : dict[str,list[float]],
    top_k: int=3,
    threshold: float = 0.4,

)-> list[str]:
    """
    Embed the query and find the top-k most similar nodes
    by cosine similarity. Skip nodes below threshold.
    """
    query_embedding = get_embedding(query)
    scores=[]

    for node, node_emb in node_embeddings.items():
        score = cosine_similarity(query_embedding,node_emb)
        if score >=threshold:
            scores.append((node,score))
    
    scores.sort(key=lambda x: x[1],reverse=True)

    matched = [node for node, _ in scores[:top_k]]
    print(f"\nMatched nodes for query: {matched}")

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