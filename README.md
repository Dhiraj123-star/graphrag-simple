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

### 💾 Persistent Graph Storage
- Graph is saved to `graph.json` after the first build using `nx.node_link_data`
- Subsequent runs load from disk instantly — no OpenAI extraction calls wasted
- `load_graph()` returns `None` if no cache exists, triggering a fresh build automatically
- `graph.json` is gitignored — cache stays local only

### 🚀 REST API (FastAPI)
- Graph and node embeddings are loaded once on server startup via FastAPI lifespan
- `POST /query` — accepts a question, returns matched nodes, context, and answer
- `GET /graph/stats` — returns node count, edge count, and full node list
- `GET /health` — lightweight health check endpoint
- Interactive Swagger UI available at `http://localhost/docs`

### 🎨 Interactive Graph Visualisation
- Generates a standalone `graph.html` from the NetworkX graph using `pyvis`
- Nodes are draggable and zoomable with hover tooltips showing entity names
- Edges display canonical relation labels inline and on hover
- Dark themed UI with physics simulation for a natural graph layout
- Reuses persistent graph cache — no extra API calls on rerun
- Run with `python visualise.py` — open the output in any browser

### 🐳 Dockerized Deployment
- `Dockerfile` builds a lean `python:3.11-slim` image running the FastAPI app via `uvicorn`
- `docker-compose.yml` runs the full stack with one command
- `graph.json` and `graph.html` are mounted as volumes — graph cache persists across container rebuilds
- `.env` is passed via `env_file`, keeping API keys out of the image
- `.dockerignore` keeps the image lean by excluding venvs, caches, and git files

### 🌐 Nginx Reverse Proxy
- `nginx.conf` routes incoming traffic to the FastAPI service via an upstream block
- Nginx is the sole public entry point, exposed on port `80`
- FastAPI container is only reachable inside the Docker network (`expose`, not `ports`)
- Gzip compression enabled for JSON responses
- Forwarded headers (`Host`, `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto`) set for correct proxying
- Health check passthrough available at `/health`

### ⚙️ CI/CD Pipeline (GitHub Actions)
- Workflow triggers automatically on every push to `main`
- Builds the Docker image from the existing `Dockerfile` using `docker/build-push-action`
- Pushes to Docker Hub at `dhiraj918106/graphrag-simple` with two tags: `latest` and the commit SHA
- GitHub Actions cache enabled for faster subsequent builds
- Docker Hub credentials stored as repository secrets — never baked into the image or codebase
- Pull the latest image anytime: `docker pull dhiraj918106/graphrag-simple:latest`

### ⚡ Minimal Setup
- Dependency stack: `openai`, `networkx`, `python-dotenv`, `numpy`, `fastapi`, `uvicorn`, `pyvis`
- No vector database, no infrastructure — runs from one terminal command, or via Docker + Nginx

---

## Quickstart

### Run as a script

```bash
# Install dependencies
pip install openai networkx python-dotenv numpy fastapi uvicorn pyvis

# Add your OpenAI key
echo "OPENAI_API_KEY=sk-..." > .env

# Run
python main.py
```

### Run as an API directly

```bash
uvicorn api:app --reload
```

Then open `http://localhost:8000/docs` for the interactive Swagger UI.

### Generate graph visualisation

```bash
python visualise.py
```

Then open the printed `file://` path in your browser.

### Run with Docker Compose + Nginx

```bash
# create placeholder cache files if they don't exist
touch graph.json graph.html

# build and start the API + Nginx containers
docker compose up --build
```

Access everything via Nginx on port `80`:
```
http://localhost/docs
http://localhost/health
```

Stop the containers:
```bash
docker compose down
```

### Pull from Docker Hub

```bash
docker pull dhiraj918106/graphrag-simple:latest
```

---

## Project Structure

```
graphrag-simple/
├── .github/
│   └── workflows/
│       └── docker-publish.yml  # CI/CD — build and push to Docker Hub on push to main
├── main.py                     # Entry point — loads data, runs queries as a script
├── api.py                      # FastAPI app — exposes /health, /graph/stats, /query
├── visualise.py                # Generates interactive graph.html via pyvis
├── graph_builder.py            # Extracts triples, deduplicates, normalizes, persists graph
├── retriever.py                # Semantic node matching and subgraph context collection
├── llm.py                      # OpenAI calls (extraction, answering, embeddings)
├── data.py                     # Sample text corpus
├── graph.json                  # Auto-generated graph cache (gitignored)
├── graph.html                  # Auto-generated visualisation output (gitignored)
├── Dockerfile                  # Container build definition for the FastAPI app
├── docker-compose.yml          # Orchestrates the API and Nginx containers
├── nginx.conf                  # Reverse proxy configuration routing to the API
├── .dockerignore               # Excludes unnecessary files from the Docker image
└── requirements.txt
```

---

## CI/CD — GitHub Actions

The workflow at `.github/workflows/docker-publish.yml` runs on every push to `main`:

```
push to main
    → checkout code
    → set up Docker Buildx
    → log in to Docker Hub
    → build image from Dockerfile
    → push dhiraj918106/graphrag-simple:latest
    → push dhiraj918106/graphrag-simple:<commit-sha>
```

### Required GitHub Secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Value |
|---|---|
| `DOCKERHUB_USERNAME` | `dhiraj918106` |
| `DOCKERHUB_TOKEN` | Your Docker Hub access token |

---

## API Endpoints

### `GET /health`
```json
{"status": "ok"}
```

### `GET /graph/stats`
```json
{
  "nodes": 24,
  "edges": 25,
  "node_list": ["Elon Musk", "SpaceX", "Tesla", "..."]
}
```

### `POST /query`

Request:
```json
{
  "question": "Who founded SpaceX?",
  "top_k": 3,
  "depth": 2
}
```

Response:
```json
{
  "question": "Who founded SpaceX?",
  "matched_nodes": ["SpaceX", "Elon Musk", "Falcon 9 rocket"],
  "context": "Elon Musk founded SpaceX...",
  "answer": "Elon Musk founded SpaceX in 2002."
}
```

---

## Example Script Output

**First run** — builds and saves the graph:
```
No saved graph found — building from scratch...
  + (Elon Musk) --[founded]--> (SpaceX)
  + (SpaceX) --[created]--> (Falcon 9 rocket)
  + (NASA) --[partners with]--> (SpaceX)
  ...

Graph saved to graph.json

Computing node embeddings...
  embedded: Elon Musk
  embedded: SpaceX
  ...

Q: What did NASA do with SpaceX?
Matched nodes: ['SpaceX', 'Falcon 9 rocket']
A: NASA partnered with SpaceX and was involved in the Crew Dragon mission.
```

**Second run** — loads instantly, zero API extraction calls:
```
Graph loaded from graph.json — skipping rebuild.
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
| **Persistent storage** | ❌ | ✅ JSON cache, skips rebuild |
| **API access** | ❌ | ✅ FastAPI REST endpoints |
| **Graph visualisation** | ❌ | ✅ Interactive HTML via pyvis |
| **Containerized deployment** | ❌ | ✅ Docker + docker-compose |
| **Reverse proxy** | ❌ | ✅ Nginx in front of API |
| **CI/CD pipeline** | ❌ | ✅ GitHub Actions → Docker Hub |
| **Setup complexity** | Vector DB required | NetworkX + numpy only |

---

## Roadmap

- [x] Semantic node matching via OpenAI embeddings and cosine similarity
- [x] Entity deduplication — normalize and alias-map variants to canonical names
- [x] Relation normalization — unify relation variants to a fixed canonical vocabulary
- [x] Persistent graph storage — save/load graph via JSON, skip rebuild on rerun
- [x] REST API layer — FastAPI with /health, /graph/stats, /query endpoints
- [x] Interactive graph visualisation — draggable, zoomable HTML export via pyvis
- [x] Dockerized deployment — Dockerfile + docker-compose for one-command API startup
- [x] Nginx reverse proxy — single public entry point on port 80
- [x] CI/CD pipeline — GitHub Actions builds and pushes image to Docker Hub on merge to main
- [ ] Community detection for cluster-level summarisation before answering
- [ ] Support ingesting PDFs and URLs as document sources

---

## Requirements

- Python 3.10+
- OpenAI API key (`gpt-4o-mini` and `text-embedding-3-small` used by default)
- Docker + Docker Compose (optional, for containerized deployment)