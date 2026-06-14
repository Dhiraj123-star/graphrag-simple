from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from data import DOCUMENTS
from graph_builder import build_graph
from retriever import build_node_embeddings, find_relevant_nodes, get_subgraph_context
from llm import answer_question

# ---------------------------------------------------------------------------
# App state — graph and embeddings loaded once on startup
# ---------------------------------------------------------------------------

app_state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build graph and embeddings once when the server starts."""
    print("Starting up — loading graph...")
    G = build_graph(DOCUMENTS)
    node_embeddings = build_node_embeddings(G)
    app_state["graph"] = G
    app_state["embeddings"] = node_embeddings
    print("Ready.")
    yield
    app_state.clear()


app = FastAPI(
    title="GraphRAG API",
    description="Knowledge graph powered retrieval and question answering.",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class QueryRequest(BaseModel):
    question: str
    top_k: int = 3
    depth: int = 2


class QueryResponse(BaseModel):
    question: str
    matched_nodes: list[str]
    context: str
    answer: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    """Check if the API is running."""
    return {"status": "ok"}


@app.get("/graph/stats")
def graph_stats():
    """Return basic stats about the loaded graph."""
    G = app_state.get("graph")
    if not G:
        raise HTTPException(status_code=503, detail="Graph not loaded.")
    return {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "node_list": list(G.nodes),
    }


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    """
    Accept a question, retrieve graph context, return answer.
    """
    G           = app_state.get("graph")
    embeddings  = app_state.get("embeddings")

    if not G or not embeddings:
        raise HTTPException(status_code=503, detail="Graph not loaded.")

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    matched_nodes = find_relevant_nodes(
        request.question,
        embeddings,
        top_k=request.top_k,
    )
    context = get_subgraph_context(G, matched_nodes, depth=request.depth)
    answer  = answer_question(request.question, context)

    return QueryResponse(
        question=request.question,
        matched_nodes=matched_nodes,
        context=context,
        answer=answer,
    )