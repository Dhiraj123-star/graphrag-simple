# GraphRAG — Knowledge Graph + LLM Retrieval

A lightweight GraphRAG implementation that extracts a knowledge graph from raw text and uses graph traversal to retrieve structured, relationship-aware context before answering questions with an LLM.

---

## Features

### 🔍 Automatic Knowledge Graph Construction
- Feeds raw text sentences to OpenAI and extracts `(head, relation, tail)` triples automatically
- No manual annotation — the LLM does the entity and relation extraction
- Builds a directed graph using NetworkX with typed, labeled edges

### 🕸️ Graph-Aware Retrieval
- Matches entities in a user query directly to graph nodes using semantic similarity
- Walks the graph up to N hops in both directions from matched nodes
- Collects relational context (not just raw chunks) before passing to the LLM

### 🔗 Multi-Hop Reasoning
- Retrieval depth is configurable — answer questions that span multiple relationships
- Example: *"Who leads the company that partnered with NASA?"* — resolved across 2 hops

### 💬 Grounded LLM Answers
- Answers are generated only from graph-retrieved context, not raw documents
- Reduces hallucination by feeding structured facts instead of fuzzy vector chunks

### 🧠 Semantic Node Matching
- Query is embedded using OpenAI `text-embedding-3-small`
- All graph nodes are pre-embedded once after graph build
- Matched by cosine similarity — handles partial names, synonyms, and paraphrases
- Tunable via `top_k` (how many nodes to retrieve) and `threshold` (minimum similarity score)

### 🔁 Entity Deduplication
- All entity names are normalized (lowercase + strip) before being added to the graph
- An alias map resolves known variants to canonical names (e.g. `"Musk"` → `"Elon Musk"`)
- Prevents duplicate nodes for the same real-world entity
- Fully contained in `graph_builder.py` — no changes required in retrieval or LLM layers

### 🔀 Relation Normalization
- Raw relation variants are mapped to a fixed canonical vocabulary via `RELATION_MAP`
- e.g. `"co-founded"`, `"was founder of"`, `"is founder of"` all resolve to `"founded"`
- e.g. `"became CEO of"`, `"has CEO"` resolve to `"is CEO of"`
- e.g. `"developed"`, `"built"`, `"launched"` resolve to `"created"`
- Cleaner edges improve graph traversal and reduce noisy LLM context

### ⚡ Minimal Setup
- Dependency stack: `openai`, `networkx`, `python-dotenv`, `numpy`
- No vector database, no infrastructure — runs from one terminal command

---

## Quickstart

```bash
# Install dependencies
pip install openai networkx python-dotenv numpy

# Add your OpenAI key
echo "OPENAI_API_KEY=sk-..." > .env

# Run
python main.py
```

---

## Project Structure

```
graphrag-simple/
├── main.py           # Entry point — loads data, runs queries
├── graph_builder.py  # Extracts triples, deduplicates entities, normalizes relations
├── retriever.py      # Semantic node matching and subgraph context collection
├── llm.py            # OpenAI calls (extraction, answering, embeddings)
├── data.py           # Sample text corpus
└── requirements.txt
```

---

## Example Output

```
Building knowledge graph...
  + (Elon Musk) --[founded]--> (SpaceX)
  + (SpaceX) --[created]--> (Falcon 9 rocket)
  + (NASA) --[partners with]--> (SpaceX)
  ...

Graph built: 24 nodes, 25 edges

Computing node embeddings...
  embedded: Elon Musk
  embedded: SpaceX
  ...

Q: What did NASA do with SpaceX?
Matched nodes: ['SpaceX', 'Falcon 9 rocket']
A: NASA partnered with SpaceX and was involved in the Crew Dragon mission.
```

---

## GraphRAG vs Plain RAG

| | Plain RAG | GraphRAG (this project) |
|---|---|---|
| **Retrieval unit** | Text chunk | Graph subgraph |
| **Matching** | Vector similarity | Cosine similarity on graph nodes |
| **Handles partial names** | ❌ | ✅ via embeddings |
| **Relation awareness** | ❌ | ✅ Typed edges |
| **Relation consistency** | ❌ | ✅ Canonical relation map |
| **Multi-hop reasoning** | ❌ | ✅ Configurable depth |
| **Entity deduplication** | ❌ | ✅ Alias map + normalization |
| **Setup complexity** | Vector DB required | NetworkX + numpy only |

---

## Roadmap

- [x] Semantic node matching via OpenAI embeddings and cosine similarity
- [x] Entity deduplication — normalize and alias-map variants to canonical names
- [x] Relation normalization — unify relation variants to a fixed canonical vocabulary
- [ ] Replace NetworkX with Neo4j for persistent, queryable graph storage
- [ ] Community detection for cluster-level summarisation before answering
- [ ] Graph visualisation export (GraphML / interactive HTML)
- [ ] REST API layer (FastAPI) to expose query endpoint
- [ ] Support ingesting PDFs and URLs as document sources

---

## Requirements

- Python 3.10+
- OpenAI API key (`gpt-4o-mini` and `text-embedding-3-small` used by default)