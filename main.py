import os
from dotenv import load_dotenv
load_dotenv()

from data import DOCUMENTS
from graph_builder import build_graph
from retriever import find_relevant_nodes, get_subgraph_context
from llm import answer_question

def main():
    print("=" * 50)
    print("Building knowledge graph...")
    print("=" * 50)
    G = build_graph(DOCUMENTS)

    print(f"\nGraph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges\n")

    questions = [
        "Who founded SpaceX?",
        "What is the relationship between Elon Musk and Tesla?",
        "What did NASA do with SpaceX?",
        "Who is the CEO of OpenAI?",
    ]

    print("=" * 50)
    print("Running queries...")
    print("=" * 50)

    for question in questions:
        print(f"\nQ: {question}")
        nodes = find_relevant_nodes(G, question)
        context = get_subgraph_context(G, nodes)
        answer = answer_question(question, context)
        print(f"A: {answer}")
        print("-" * 40)

if __name__ == "__main__":
    main()