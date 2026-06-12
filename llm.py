import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()  # reads OPENAI_API_KEY from env

def extract_entities_and_relations(text: str) -> dict:
    """Ask OpenAI to extract (entity, relation, entity) triples from a sentence."""
    prompt = f"""
Extract knowledge graph triples from the sentence below.
Return ONLY a JSON list of objects with keys: "head", "relation", "tail".
If none found, return an empty list [].

Sentence: "{text}"

JSON:"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    parsed = json.loads(raw)

    # handle both {"triples": [...]} and plain [...]
    if isinstance(parsed, list):
        return parsed
    for v in parsed.values():
        if isinstance(v, list):
            return v
    return []


def answer_question(question: str, context: str) -> str:
    """Answer a question given graph-retrieved context."""
    prompt = f"""Use the context below to answer the question.
Be concise and factual.

Context:
{context}

Question: {question}
Answer:"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()

def get_embedding(text:str) ->list[float] :
    """Get vector embeddings for a given text using OpenAI"""
    response = client.embeddings.create(
        model= "text-embedding-3-small",
        input=text.strip(),
    )
    return response.data[0].embedding