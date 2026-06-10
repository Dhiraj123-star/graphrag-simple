import networkx as nx
from llm import extract_entities_and_relations

def build_graph(documents: list[str]) -> nx.DiGraph:
    G = nx.DiGraph()

    for doc in documents:
        triples = extract_entities_and_relations(doc)
        for triple in triples:
            head = triple.get("head", "").strip()
            relation = triple.get("relation", "").strip()
            tail = triple.get("tail", "").strip()

            if head and relation and tail:
                # Add nodes with label metadata
                G.add_node(head, label=head)
                G.add_node(tail, label=tail)
                # Add edge with relation as attribute
                G.add_edge(head, tail, relation=relation)
                print(f"  + ({head}) --[{relation}]--> ({tail})")

    return G