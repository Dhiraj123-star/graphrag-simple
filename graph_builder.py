import networkx as nx
from llm import extract_entities_and_relations

# ----------------------
# Normalisation
# ----------------------

def normalize(text:str) -> str:
    """Lowercase and strip whitespace for consistent node naming."""
    return text.strip().lower()

def canonical(text:str,alias_map: dict[str,str] )-> str:
    """Return the canonical form of an entity using the alias map."""
    key = normalize(text)
    return alias_map.get(key,text.strip())


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

# -----------------------
# Graph builder 
# -----------------------

def build_graph(documents: list[str]) -> nx.DiGraph:
    G = nx.DiGraph()

    for doc in documents:
        triples = extract_entities_and_relations(doc)
        for triple in triples:
            raw_head = triple.get("head", "").strip()
            relation = triple.get("relation", "").strip()
            raw_tail = triple.get("tail", "").strip()

            if not raw_head or not relation or not raw_tail:
                continue

            # Deduplicate - resolve to canonical names
            head = canonical(raw_head,ALIAS_MAP)
            tail = canonical(raw_tail,ALIAS_MAP)

            if head and relation and tail:
                # Add nodes with label metadata
                G.add_node(head, label=head)
                G.add_node(tail, label=tail)
                # Add edge with relation as attribute
                G.add_edge(head, tail, relation=relation)
                print(f"  + ({head}) --[{relation}]--> ({tail})")

    return G