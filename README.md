# GraphRAG — Knowledge Graph + LLM Retrieval

A lightweight GraphRAG implementation that extracts a knowledge graph from raw text and uses graph traversal to retrieve structured, relationship-aware context before answering questions with an LLM.

---

## Features

### 🔍 Automatic Knowledge Graph Construction
- Feeds raw text sentences to OpenAI and extracts `(head, relation, tail)` triples automatically
- No manual annotation — the LLM does the entity and relation extraction
- Builds a directed graph using NetworkX with typed, labeled edges

### 🕸️ Graph-Aware Retrieval
- Matches entities in a user query directly to graph nodes
- Walks the graph up to N hops in both directions from matched nodes
- Collects relational context (not just raw chunks) before passing to the LLM

### 🔗 Multi-Hop Reasoning
- Retrieval depth is configurable — answer questions that span multiple relationships
- Example: *"Who leads the company that partnered with NASA?"* — resolved across 2 hops

### 💬 Grounded LLM Answers
- Answers are generated only from graph-retrieved context, not raw documents
- Reduces hallucination by feeding structured facts instead of fuzzy vector chunks

### ⚡ Minimal Setup
- Single dependency stack: `openai`, `networkx`, `python-dotenv`
- No vector database, no embeddings, no infrastructure — runs from one terminal command

---

## Quickstart

```bash
# Install dependencies
pip install openai networkx python-dotenv

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
├── graph_builder.py  # Extracts triples and builds the graph
├── retriever.py      # Node matching and subgraph context collection
├── llm.py            # OpenAI calls (extraction + answering)
├── data.py           # Sample text corpus
└── requirements.txt
```

---

## Example Output

```
Building knowledge graph...
  + (Elon Musk) --[founded]--> (SpaceX)
  + (SpaceX) --[developed]--> (Falcon 9)
  + (NASA) --[partnered with]--> (SpaceX)
  ...

Graph built: 12 nodes, 14 edges

Q: What did NASA do with SpaceX?
A: NASA partnered with SpaceX for the Crew Dragon mission, which
   successfully transported astronauts to the ISS.
```

---

## GraphRAG vs Plain RAG

| | Plain RAG | GraphRAG (this project) |
|---|---|---|
| **Retrieval unit** | Text chunk | Graph subgraph |
| **Matching** | Vector similarity | Entity keyword → node |
| **Relation awareness** | ❌ | ✅ Typed edges |
| **Multi-hop reasoning** | ❌ | ✅ Configurable depth |
| **Setup complexity** | Vector DB required | NetworkX only |

---

## Roadmap

- [ ] Replace NetworkX with Neo4j for persistent, queryable graph storage
- [ ] Add vector embeddings on nodes for semantic (not just keyword) node matching
- [ ] Community detection for cluster-level summarisation before answering
- [ ] Graph visualisation export (GraphML / interactive HTML)
- [ ] REST API layer (FastAPI) to expose query endpoint
- [ ] Support ingesting PDFs and URLs as document sources

---

## Requirements

- Python 3.10+
- OpenAI API key (`gpt-4o-mini` used by default)