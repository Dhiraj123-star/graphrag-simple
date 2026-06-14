import os
import json
import networkx as nx
from llm import extract_entities_and_relations

# ------------------------------
# Normalisation & Deduplication
# ------------------------------

def normalize(text:str) -> str:
    """Lowercase and strip whitespace for consistent node naming."""
    return text.strip().lower()

def canonical_entity(text:str,alias_map: dict[str,str] )-> str:
    """Return the canonical form of an entity using the alias map."""
    key = normalize(text)
    return alias_map.get(key,text.strip())

def canonical_relation(text:str, relation_map: dict[str,str]) ->str:
    """Return the canonical form of a relation using the relation map"""
    key = normalize(text)
    return relation_map.get(key,text.strip())

# --------------------------------------------------
# Alias Map - map known variantes -> canonical map
# ---------------------------------------------------

ALIAS_MAP: dict[str, str] = {
    "musk"          : "Elon Musk",
    "elon musk"     : "Elon Musk",
    "tesla inc"     : "Tesla",
    "tesla motors"  : "Tesla",
    "spacex inc"    : "SpaceX",
    "openai inc"    : "OpenAI",
    "sam"           : "Sam Altman",
    "altman"        : "Sam Altman",
    "gpt4"          : "GPT-4",
    "gpt 4"         : "GPT-4",
}  


# ---------------------------------------------------------------------------
# Relation Map — raw relation variants -> canonical relation
# ---------------------------------------------------------------------------

RELATION_MAP: dict[str, str] = {
    # founding
    "co-founded"                : "founded",
    "was founder of"            : "founded",
    "has founder"               : "founded",
    "is founder of"             : "founded",
    "founded in"                : "founded",

    # ceo / leadership
    "became ceo of"             : "is CEO of",
    "has ceo"                   : "is CEO of",
    "is ceo"                    : "is CEO of",
    "became"                    : "is CEO of",
    "is ceo of"                 : "is CEO of",
    "became ceo in"             : "is CEO of",

    # partnership
    "partnered with"            : "partners with",
    "has partnership with"      : "partners with",

    # involvement
    "involved in"               : "involved in",
    "was involved in"           : "involved in",

    # creation / development
    "developed"                 : "created",
    "built"                     : "created",
    "launched"                  : "created",

    # production
    "produces"                  : "produces",
    "manufactures"              : "produces",
    "makes"                     : "produces",
}

GRAPH_PATH = "graph.json"
# ---------------------------------------------
# Persistence -- save and load graph from disk
# ----------------------------------------------

def save_graph(G: nx.DiGraph) -> None:
    """ Serialize graph to JSON and save to disk. """
    data = nx.node_link_data(G)
    with open(GRAPH_PATH,"w") as f:
        json.dump(data,f,indent=2)
    
    print(f"\nGraph saved to {GRAPH_PATH}")

def load_graph() -> nx.DiGraph | None:
    """Load graph from disk if it exists, else return None"""
    if os.path.exists(GRAPH_PATH):
        with open(GRAPH_PATH,"r") as f:
            data = json.load(f)
        G = nx.node_link_graph(data,directed=True)

        print(f"Graph loaded from {GRAPH_PATH}- skipping rebuild.")
        return G
    
    return None


# -----------------------
# Graph builder 
# -----------------------

def build_graph(documents: list[str]) -> nx.DiGraph:

    # Try loading from disk first
    G  = load_graph()
    if G is not None:
        return G
    print("No saved graph found - building from scratch ......")

    G = nx.DiGraph()

    for doc in documents:
        triples = extract_entities_and_relations(doc)
        for triple in triples:
            raw_head = triple.get("head", "").strip()
            raw_relation = triple.get("relation", "").strip()
            raw_tail = triple.get("tail", "").strip()

            if not raw_head or not raw_relation or not raw_tail:
                continue

            # Deduplicate entity
            head = canonical_entity(raw_head,ALIAS_MAP)
            tail = canonical_entity(raw_tail,ALIAS_MAP)

            # Normalize relation
            relation = canonical_relation(raw_relation,RELATION_MAP)

            if head and relation and tail:
                # Add nodes with label metadata
                G.add_node(head, label=head)
                G.add_node(tail, label=tail)
                # Add edge with relation as attribute
                G.add_edge(head, tail, relation=relation)
                print(f"  + ({head}) --[{relation}]--> ({tail})")
                
    # Save to disk for next run
    save_graph(G)
    return G