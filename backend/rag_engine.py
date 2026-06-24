import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_db = None
_client = None


def get_db():
    global _db
    if _db is None:
        chroma_dir = os.environ.get("CHROMA_DIR")
        if not chroma_dir:
            raise ValueError("CHROMA_DIR not set in .env")
        # Normalize slashes — works on both Windows and Linux
        chroma_dir = os.path.normpath(chroma_dir)
        print(f"[RAG] Loading ChromaDB from: {chroma_dir}")
        if not os.path.exists(chroma_dir):
            raise FileNotFoundError(f"ChromaDB directory not found: {chroma_dir}")
        embedding_model = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        _db = Chroma(persist_directory=chroma_dir, embedding_function=embedding_model)
        count = _db._collection.count()
        print(f"[RAG] ChromaDB loaded. {count} vectors in collection.")
        if count == 0:
            raise RuntimeError("ChromaDB loaded but has 0 vectors. Run store_vectors.py first.")
    return _db


def get_groq_client():
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not set in .env")
        _client = Groq(api_key=api_key)
    return _client


def query_rag(question: str, k: int = 8) -> dict:
    db = get_db()
    client = get_groq_client()

    matching_docs = db.similarity_search(question, k=k)
    context_block = "\n---\n".join([doc.page_content for doc in matching_docs])
    sources = list({doc.metadata.get("source", "unknown") for doc in matching_docs})

    system_prompt = f"""You are an expert Formula 1 analyst with deep knowledge of racing history.

Answer the user's question using the data context provided below. Synthesize across multiple chunks if needed to give a complete answer. Be direct and confident — do not say "based on the context" or "according to the data". Just answer naturally as an F1 expert would.

Only if the context genuinely has zero relevant information should you say you don't have that data. Otherwise, answer fully.

CONTEXT:
{context_block}
"""

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        temperature=0.2,
        max_tokens=1000,
    )

    answer = completion.choices[0].message.content
    return {"answer": answer, "sources": sources}